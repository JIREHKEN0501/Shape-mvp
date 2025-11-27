from flask import Flask, render_template, request, jsonify, make_response, g, session
import uuid, hashlib, json, datetime, os
from functools import wraps

# Security imports
import re
import secrets
import hmac
from flask import abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- QUICK HARDENING CONFIG (Phase 4 Pre-Upgrades) ---
LOG_MAX_BYTES = int(os.environ.get("LOG_MAX_BYTES", 512 * 1024))  # 512KB
LOG_BACKUPS   = int(os.environ.get("LOG_BACKUPS", 5))
LOG_HMAC_KEY  = os.environ.get("LOG_HMAC_KEY", "")  # set to random hex for tamper-evidence

ALLOWED_ORIGIN_HOST = os.environ.get("ALLOWED_ORIGIN_HOST", "127.0.0.1")  # or domain
HONEYPOT_FIELD      = os.environ.get("HONEYPOT_FIELD", "hp_website")


# Import analytics/behavior tracking functions
from project.analyze_events import (
    save_session_result,
    compute_behavioral_metrics,
    compute_cognitive_metrics,
    aggregate_metrics,
    export_all,
    erase_participant,
)


# ---------------------------
# Flask + Security Setup
# ---------------------------
app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=os.environ.get("LIMITER_STORAGE_URI","memory://"), 
    default_limits=["120 per minute"],
    headers_enabled=True
)
limiter.init_app(app)

# ----------------------------
# Admin authentication decorator
# ----------------------------
from functools import wraps
import os
from flask import request, jsonify, redirect, make_response, render_template

def admin_required(f):
    """Decorator to protect sensitive routes using rotating admin token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # helper that returns the currently configured admin token
        token_cfg = get_admin_token()   # make sure get_admin_token() exists
        if not token_cfg:
            return jsonify({"error": "Admin token not configured"}), 500

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            provided = auth.split(" ", 1)[1].strip()
        else:
            provided = (
                request.headers.get("X-ADMIN-TOKEN", "").strip()
                or auth.strip()
                or request.cookies.get("admin_session", "").strip()
            )

        if provided != token_cfg:
            try:
                audit_record(
                    action="admin_access_denied",
                    actor="unknown",
                    subject=request.path,
                    status="denied",
                    extra={"ip": request.remote_addr}
                )
            except Exception:
                pass
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return decorated

# ---- Minimal Admin login page (Phase 4 helper) ----
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """
    Minimal admin login:
      GET  -> render admin_login.html
      POST -> validate token (form), set secure cookie, redirect to dashboard
    """
    if request.method == "GET":
        return render_template("admin_login.html")

    # POST: validate posted token
    token_submitted = request.form.get("token", "").strip()
    real_token = get_admin_token()
    if not real_token:
        return "Admin token not configured", 500
    if token_submitted != real_token:
        return render_template("admin_login.html", error="Invalid token")

    # correct -> set cookie and redirect to dashboard
    resp = make_response(redirect("/admin/dashboard"))
    resp.set_cookie("admin_session", token_submitted, httponly=True, samesite="Lax", max_age=60*60)
    return resp


# -------------------------------
# Dynamic honeypot cookie signing
# -------------------------------
import hmac
import hashlib
import secrets
from typing import Optional

# HMAC key (set in environment). IMPORTANT: set a long random secret in env before deploy.
HMAC_KEY = os.environ.get("HMAC_KEY")  # e.g. 64 hex chars from `secrets.token_hex(32)`
if not HMAC_KEY:
    # fallback for local dev only - strongly prefer setting HMAC_KEY in env
    HMAC_KEY = secrets.token_hex(32)
    # (You should export a proper HMAC_KEY in your shell/environment instead of relying on this.)

def generate_honeypot_field() -> str:
    """Return a short random honeypot field name, e.g. 'hp_ab12cd34'."""
    return "hp_" + secrets.token_hex(4)

def sign_val(val: str) -> str:
    """Return hex HMAC-SHA256 of val using HMAC_KEY."""
    key = HMAC_KEY.encode("utf-8")
    mac = hmac.new(key, val.encode("utf-8"), hashlib.sha256).hexdigest()
    return mac

def verify_val(val: str, sig: str) -> bool:
    """Verify HMAC signature constant-time; return True if match."""
    key = HMAC_KEY.encode("utf-8")
    expected = hmac.new(key, val.encode("utf-8"), hashlib.sha256).hexdigest()
    # use hmac.compare_digest for constant-time comparison
    return hmac.compare_digest(expected, sig)

@app.before_request
def rotate_honeypot_cookie():
    """
    Ensure a signed hp_field cookie exists on each session.
    Cookie format stored: "<field_name>|<sig>"
    - cookie is readable by JS (NOT HttpOnly) because client-side rotation reads it.
    - server verifies signature on use (see bot_tripwire update below).
    """
    try:
        raw = request.cookies.get("hp_field", "")
        valid_name: Optional[str] = None
        if raw and "|" in raw:
            name, sig = raw.split("|", 1)
            if name.startswith("hp_") and verify_val(name, sig):
                valid_name = name

        # If cookie missing or invalid -> generate new signed cookie
        if not valid_name:
            new_name = generate_honeypot_field()
            sig = sign_val(new_name)
            cookie_value = f"{new_name}|{sig}"
            # store for after_request to attach to outgoing response
            # don't directly call make_response here (Flask catch-alls make it messy)
            from flask import g
            g.hp_cookie_to_set = cookie_value
    except Exception:
        # never block user flow if sign/rotate fails
        pass


# -------------------------------
# Dynamic Honeypot Field Helper (Upgrade #4)
# -------------------------------

import secrets

def generate_honeypot_field():
    """Generate a random honeypot field name."""
    return "hp_" + secrets.token_hex(4)

@app.before_request
def rotate_honeypot_cookie():
    """
    Rotate honeypot field name occasionally for better bot resistance.
    Stores field name in user cookie 'hp_field' if missing.
    """
    if not request.cookies.get("hp_field"):
        from flask import g
        g.hp_cookie_to_get = generate_honeypot_field()

@app.after_request
def apply_honeypot_cookie(resp):
    """
    If rotate_honeypot_cookie scheduled a cookie (saved on g.hp_cookie_to_set),
    attach it to the response here so every response carries the cookie.
    """
    from flask import g
    try:
        if hasattr(g, "hp_cookie_to_set") and g.hp_cookie_to_set:
            # IMPORTANT: the cookie must be readable by client-side JS so we do NOT set HttpOnly=True
            resp.set_cookie(
                "hp_field",
                g.hp_cookie_to_set,
                max_age=60 * 60 * 24,   # 1 day
                httponly=False,         # JS needs to read it to set hidden input name
                samesite="Lax",
                path="/"
            )
    except Exception:
        # never block normal flow if cookie attach fails
        pass

    return resp

# ----------------------------
# Rate Limit JSON Handler (Upgrade #1)
# -----------------------------
from flask_limiter.errors import RateLimitExceeded

@app.errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    retry = getattr(e, "reset_in", 1)
    resp = jsonify({"error": "rate_limited", "retry_after": retry})
    resp.status_code = 429
    resp.headers["Retry-After"] = str(retry)
    return resp

# -----------------------------
# Host Allow-List Siteguard (Upgrade #2)
# -----------------------------
@app.before_request
def host_siteguard():
    # If allow-list not configured, skip
    if not ALLOWED_ORIGIN_HOST:
        return

    # Extract host portion without port
    host = (request.host or "").split(":")[0]

    # If mismatched, block + audit
    if host and host != ALLOWED_ORIGIN_HOST:
        audit_record(
            action="host_block",
            status="denied",
            extra={"seen_host": host, "path": request.path}
        )
        return jsonify({"error": "host_not_allowed"}), 403


# ------------------------------------------------------------------
# Honeypot + Bot Tripwire (Upgrade #3) - signed cookie-aware version
# ------------------------------------------------------------------
def bot_tripwire():
    """
    Return Flask response to block if bot is suspected; otherwise return None.
    Uses signed hp_field cookie of form: "<field_name>|<sig>" where sig = HMAC(name).
    Falls back to env HONEYPOT_FIELD if cookie missing/invalid.
    """
    honeypot_val = None
    hp_name = None

    # --- Read and verify signed cookie if present ---
    try:
        raw = request.cookies.get("hp_field", "")
        if raw and "|" in raw:
            name, sig = raw.split("|", 1)
            # accept only names that look like our hp_ prefix and verify signature
            if name.startswith("hp_") and verify_val(name, sig):
                hp_name = name
    except Exception:
        # don't break request flow on verification errors
        hp_name = None

    # Fallback to env/default configured name
    if not hp_name:
        hp_name = os.environ.get("HONEYPOT_FIELD", "hp_website")

    # --- Extract submitted value from possible input types ---
    if request.is_json:
        body = request.get_json(silent=True) or {}
        honeypot_val = (body.get(hp_name) or "").strip()
    else:
        honeypot_val = (request.form.get(hp_name) or "").strip()

    # check querystring as well (rare, but cover all)
    if not honeypot_val:
        honeypot_val = (request.args.get(hp_name) or "").strip()

    # If honeypot field is filled -> suspicious -> log + block
    if honeypot_val:
        try:
            audit_record(
                action="honeypot_trigger",
                actor="unknown",
                subject=request.path,
                status="denied",
                extra={"hp_field": hp_name, "ip": request.remote_addr}
            )
        except Exception:
            pass

        return jsonify({"error": "bot_detected"}), 400

    return None

# ------------------------------
# Fake / Decoy Endpoints + Snare
# ------------------------------
# -------------------------
# LEGACY ROUTE: moved to blueprint
# Old handler moved to: project/app/routes/__init__.py
#
# Legacy shim so `from app import decoy_submit` still works.
try:
    from project.app.routes import decoy_submit as new_decoy_submit
    decoy_submit = new_decoy_submit
except Exception:
    # leave a harmless placeholder if import fails during transitional edits
    def decoy_submit(*a, **kw):
        raise RuntimeError("decoy_submit handler not available (moved to project.app.routes)")
# -------------------------


@app.route("/snare", methods=["POST"])
def snare_endpoint():
    """
    Lightweight API snare used by decoy JS (and test curl). Collects simple
    client-side signals (UA, small payload) and writes an audit log entry.

    This version:
    - Accepts JSON or form-encoded body
    - Redacts common sensitive keys (password, token, secret)
    - Records ip, user-agent, a trimmed header snapshot and the payload
    - Returns {"ok": True} on success
    """
    # Accept JSON (preferred) or form data
    data = request.get_json(silent=True) or {}
    if not data and request.form:
        # convert form MultiDict -> normal dict
        data = {k: request.form.get(k) for k in request.form.keys()}

    try:
        # shallow redact of sensitive field values
        def redact_val(k, v):
            key = k.lower()
            if any(s in key for s in ("password", "secret", "token", "passwd", "pwd", "authorization")):
                return "<redacted>"
            return v

        payload = {k: redact_val(k, v) for k, v in (data.items() if isinstance(data, dict) else [])}

        # small headers snapshot (avoid logging full headers)
        hdrs = {}
        for h in ("User-Agent", "Referer", "X-Forwarded-For"):
            val = request.headers.get(h)
            if val:
                hdrs[h] = val if len(val) < 1000 else val[:1000] + "...(truncated)"

        extra = {
            "ip": request.remote_addr,
            "ua": request.headers.get("User-Agent"),
            "headers": hdrs,
            "payload": payload
        }

        # audit_record is your existing helper that appends to the audit log.
        # Make sure it accepts these kwargs (actor/subject/status/extra).
        audit_record(
            action="snare_trigger",
            actor="unknown",
            subject=request.path,
            status="collected",
            extra=extra
        )
    except Exception:
        # we don't want snare errors to break the site — fail silently
        pass

    return jsonify({"ok": True}), 200


@app.route("/fake-login", methods=["GET", "POST"])
def fake_login():
    """
    A deceptive login page (non-functional). Logs any attempts.
    """
    if request.method == "POST":
        # log attempt but don't authenticate
        username = request.form.get("username", "")
        # purposely don't store raw password - only indicator length/exists
        attempted = {
            "username": username,
            "password_provided": bool(request.form.get("password"))
        }
        try:
            audit_record(
                action="fake_login_attempt",
                actor="unknown",
                subject=request.path,
                status="attempted",
                extra={"ip": request.remote_addr, "attempt": attempted}
            )
        except Exception:
            pass

        # show a benign "processing" page to hold the actor
        return render_template("fake_login_wait.html"), 200

    # GET: show the fake login form
    hp_field = request.cookies.get("hp_field") or os.environ.get("HONEYPOT_FIELD", "hp_website")
    return render_template("fake_login.html", hp_field=hp_field)


# ---- Admin Metrics Endpoint (Phase 4 - D3) ----
@app.route("/admin/metrics/<participant_id>", methods=["GET"])
@admin_required
def admin_metrics(participant_id):
    """
    Compute behavioral + cognitive metrics for a participant.
    """
    try:
        # Collect all records for this participant
        records = _collect_participant_records(participant_id)
        if not records:
            return jsonify({"ok": False, "error": "no_records"}), 404

        # Extract only data_log entries (the puzzle/task results)
        event_payloads = []
        for r in records:
            obj = r.get("record", {})
            if obj.get("action") == "save_session_result":
                payload = obj.get("payload", {})
                event_payloads.append(payload)

        # No puzzle/task events?
        if not event_payloads:
            return jsonify({"ok": False, "error": "no_event_payloads"}), 404

        # Run your analysis stack
        metrics = aggregate_metrics(event_payloads)

        return jsonify({
            "ok": True,
            "participant_id": participant_id,
            "metrics": metrics,
            "events_used": len(event_payloads),
        }), 200

    except Exception as e:
        try:
            audit_record(
                action="metrics_error",
                actor="admin",
                subject=f"metrics:{participant_id}",
                status="error",
                extra={"error": str(e)}
            )
        except:
            pass
        return jsonify({"ok": False, "error": "metrics_failed"}), 500


import hashlib
import shutil
from flask import send_file

# ---------- Participant export + erase endpoints (D3) ----------
# Place this after your /snare route

def _read_jsonl_file(path):
    """Yield parsed JSON objects from a jsonl file (skip broken lines)."""
    import json
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    # skip malformed lines
                    continue
    except FileNotFoundError:
        return
    except PermissionError:
        return

def _collect_participant_records(participant_id):
    """Collect records mentioning participant_id from known log files."""
    files_to_scan = []
    # adjust these names if your module uses different constants
    try:
        files_to_scan = [AUDIT_LOG, CONSENT_LOG, DATA_LOG]
    except Exception:
        # fallback to logs by path if constants missing
        files_to_scan = ["logs/audit_log.jsonl", "logs/consent_log.jsonl", "logs/data_log.jsonl"]

    out = []
    for path in files_to_scan:
        for obj in _read_jsonl_file(path):
            # some logs embed participant_id at top-level or inside 'actor' etc.
            if not isinstance(obj, dict):
                continue
            # quick checks for participant id in common fields
            if obj.get("participant_id") == participant_id:
                out.append({"file": path, "record": obj})
                continue
            # actor might include "participant:xxxx"
            actor = obj.get("actor", "")
            if isinstance(actor, str) and actor.endswith(participant_id):
                out.append({"file": path, "record": obj})
                continue
            # nested extra fields often contain participant_id
            extra = obj.get("extra", {})
            if isinstance(extra, dict) and extra.get("participant_id") == participant_id:
                out.append({"file": path, "record": obj})
                continue
            # a loose search across values
            if any(str(v) == participant_id for v in obj.values()):
                out.append({"file": path, "record": obj})
    return out


@app.route("/admin/export/<participant_id>", methods=["GET"])
@admin_required
def export_participant(participant_id):
    """
    Admin endpoint: export all records for a participant_id as JSON.
    """
    try:
        records = _collect_participant_records(participant_id)
        # record the export action in the audit log
        try:
            audit_record(action="export_requested", actor="admin", subject=f"export:{participant_id}", status="ok", extra={"matches": len(records)})
        except Exception:
            pass

        return jsonify({"ok": True, "participant_id": participant_id, "matches": len(records), "records": records}), 200
    except Exception as e:
        try:
            audit_record(action="export_failed", actor="admin", subject=f"export:{participant_id}", status="error", extra={"error": str(e)})
        except Exception:
            pass
        return jsonify({"ok": False, "error": "export_failed"}), 500


def _anonymize_and_replace_in_file(path, participant_id, replacement_token):
    """
    Read path, write a temp file with participant_id replaced by replacement_token,
    then atomically move the temp file over original (after backup).
    Returns number of lines changed.
    """
    import json, tempfile, os
    changed = 0
    tmp_fd, tmp_path = tempfile.mkstemp(prefix="rewrite_", dir=".")
    os.close(tmp_fd)
    try:
        with open(path, "r", encoding="utf-8") as rf, open(tmp_path, "w", encoding="utf-8") as wf:
            for line in rf:
                if participant_id in line:
                    # attempt safe json load/modify/write, otherwise do text replace
                    try:
                        obj = json.loads(line)
                        modified = False
                        # replace in top-level participant_id if present
                        if obj.get("participant_id") == participant_id:
                            obj["participant_id"] = replacement_token
                            modified = True
                        # replace in actor if matches
                        actor = obj.get("actor")
                        if isinstance(actor, str) and actor.endswith(participant_id):
                            obj["actor"] = actor.replace(participant_id, replacement_token)
                            modified = True
                        # replace in extras recursively (shallow)
                        extra = obj.get("extra", {})
                        if isinstance(extra, dict) and extra.get("participant_id") == participant_id:
                            extra["participant_id"] = replacement_token
                            obj["extra"] = extra
                            modified = True
                        if modified:
                            wf.write(json.dumps(obj, separators=(",", ":"), ensure_ascii=False) + "\n")
                            changed += 1
                            continue
                    except Exception:
                        # fallback to text replace
                        new_line = line.replace(participant_id, replacement_token)
                        if new_line != line:
                            changed += 1
                        wf.write(new_line)
                        continue
                wf.write(line)
    except FileNotFoundError:
        # nothing to do if file missing
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        return 0
    # backup original (timestamped)
    try:
        bak_path = f"{path}.bak-{int(time.time())}"
        shutil.copy2(path, bak_path)
        # replace file atomically
        shutil.move(tmp_path, path)
    except Exception:
        # cleanup tmp if move failed
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise
    return changed


@app.route("/admin/erase/<participant_id>", methods=["POST"])
@admin_required
def erase_participant_admin(participant_id):
    """
    Admin endpoint to anonymize a participant's identifiers in logs.
    Replaces direct participant_id with anonymized:<hash>.
    Note: This is a best-effort pseudonymization that keeps records but removes the clear identifier.
    """
    try:
        # create a deterministic pseudonym to keep ability to link anonymized records
        h = hashlib.sha256(participant_id.encode("utf-8")).hexdigest()[:16]
        replacement = f"anonymized:{h}"
        files_to_scan = []
        try:
            files_to_scan = [AUDIT_LOG, CONSENT_LOG, DATA_LOG]
        except Exception:
            files_to_scan = ["logs/audit_log.jsonl", "logs/consent_log.jsonl", "logs/data_log.jsonl"]

        total_changed = 0
        for path in files_to_scan:
            try:
                changed = _anonymize_and_replace_in_file(path, participant_id, replacement)
                total_changed += changed
            except Exception as e:
                # log failure in audit log but continue
                try:
                    audit_record(action="erase_partial_fail", actor="admin", subject=f"erase:{participant_id}", status="error", extra={"path": path, "error": str(e)})
                except Exception:
                    pass

        # final audit record for the erase action
        try:
            audit_record(action="erase_performed", actor="admin", subject=f"erase:{participant_id}", status="ok", extra={"replacement": replacement, "changed_lines": total_changed})
        except Exception:
            pass

        return jsonify({"ok": True, "participant_id": participant_id, "replacement": replacement, "changed_lines": total_changed}), 200
    except Exception as e:
        try:
            audit_record(action="erase_failed", actor="admin", subject=f"erase:{participant_id}", status="error", extra={"error": str(e)})
        except Exception:
            pass
        return jsonify({"ok": False, "error": "erase_failed"}), 500


@app.route("/erase", methods=["POST"])
def erase_participant_self():
    """
    Participant-initiated erase: requires a participant cookie (participant_id).
    This endpoint anonymizes that participant's records (same strategy as admin erase).
    """
    try:
        part = request.cookies.get("participant_id")
        if not part:
            return jsonify({"ok": False, "error": "no_participant_cookie"}), 400
        # delegate to admin-style erasure (use same replacement)
        # (we don't require admin token here because it's a user self-erase)
        h = hashlib.sha256(part.encode("utf-8")).hexdigest()[:16]
        replacement = f"anonymized:{h}"
        files_to_scan = []
        try:
            files_to_scan = [AUDIT_LOG, CONSENT_LOG, DATA_LOG]
        except Exception:
            files_to_scan = ["logs/audit_log.jsonl", "logs/consent_log.jsonl", "logs/data_log.jsonl"]

        total_changed = 0
        for path in files_to_scan:
            try:
                changed = _anonymize_and_replace_in_file(path, part, replacement)
                total_changed += changed
            except Exception:
                pass

        try:
            audit_record(action="erase_self", actor=f"participant:{part}", subject=f"erase:self", status="ok", extra={"replacement": replacement, "changed_lines": total_changed})
        except Exception:
            pass

        return jsonify({"ok": True, "replacement": replacement, "changed_lines": total_changed}), 200
    except Exception as e:
        try:
            audit_record(action="erase_self_failed", actor="unknown", subject="/erase", status="error", extra={"error": str(e)})
        except Exception:
            pass
        return jsonify({"ok": False, "error": "erase_failed"}), 500

# End D3 endpoints

# ---- Admin dashboard (Phase4 - D1) ----
from flask import send_from_directory, url_for
@app.route("/admin/dashboard", methods=["GET"])
@admin_required
def admin_dashboard():
    # small summary counts (use your existing constants or compute)
    try:
        counts = {
            "audit_log_lines": sum(1 for _ in _read_jsonl_file(AUDIT_LOG)) if 'AUDIT_LOG' in globals() else None,
            "consent_log_lines": sum(1 for _ in _read_jsonl_file(CONSENT_LOG)) if 'CONSENT_LOG' in globals() else None,
            "data_log_lines": sum(1 for _ in _read_jsonl_file(DATA_LOG)) if 'DATA_LOG' in globals() else None,
            "sessions": len(session_data()) if 'session_data' in globals() else None
        }
    except Exception:
        counts = {"audit_log_lines": None, "consent_log_lines": None, "data_log_lines": None, "sessions": None}

    # sample recent events: tail of audit_log (best-effort)
    recent = []
    try:
        for obj in list(_read_jsonl_file(AUDIT_LOG or "logs/audit_log.jsonl"))[-10:]:
            recent.append({
                "ts": obj.get("ts"),
                "action": obj.get("action"),
                "actor": obj.get("actor"),
                "subject": obj.get("subject")
            })
    except Exception:
        recent = []

    return render_template("admin_dashboard.html", counts=counts, recent=recent)


# --------------------------
#  ADMIN TOKEN HELPERS (Section 1)
# --------------------------
def get_admin_token() -> str:
    """Always read the current admin token from env to support live rotation."""
    return os.environ.get("ADMIN_TOKEN", "").strip()

def extract_admin_token_from_request() -> str:
    """Accept Authorization: Bearer <token> or X-ADMIN-TOKEN: <token> (or raw Authorization)."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()
    return (request.headers.get("X-ADMIN-TOKEN", "").strip()
            or auth.strip())

# ---- Admin export download (Phase 4 - D2) ----
from flask import send_file
import json
import tempfile
import os

@app.route("/admin/download/<participant_id>", methods=["GET"])
@admin_required
def admin_download(participant_id):
    """
    Download the exported JSON for a participant.
    This wraps the data into a temporary file and returns it.
    """
    try:
        # reuse your D3 export helper
        records = _collect_participant_records(participant_id)

        # create temp file
        tmp_fd, tmp_path = tempfile.mkstemp(prefix=f"export-{participant_id}-", suffix=".json")
        os.close(tmp_fd)

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump({
                "ok": True,
                "participant_id": participant_id,
                "matches": len(records),
                "records": records
            }, f, indent=2, ensure_ascii=False)

        # send as file
        return send_file(
            tmp_path,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"export-{participant_id}.json"
        )

    except Exception as e:
        try:
            audit_record(
                action="export_download_failed",
                actor="admin",
                subject=f"download:{participant_id}",
                status="error",
                extra={"error": str(e)}
            )
        except Exception:
            pass
        
        return jsonify({"ok": False, "error": "download_failed"}), 500


# --------------------------
#  APP INITIALIZATION
# --------------------------

# Guardrail 2: Limit max request body to 1 MB
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


CONSENT_VERSION = "v1.0"
CORRECT_ANSWER = "23"  # change logic later if needed

# Folder setup
BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

CONSENT_LOG = os.path.join(LOG_DIR, "consent_log.jsonl")
DATA_LOG = os.path.join(LOG_DIR, "data_log.jsonl")
AUDIT_LOG = os.path.join(LOG_DIR, "audit_log.jsonl")

# Set admin token via environment
def get_admin_token():
    # Primary: environment
    token = os.environ.get("ADMIN_TOKEN")
    if token:
        return token.strip()

    # Secondary: optional file fallback
    token_path = os.environ.get("ADMIN_TOKEN_FILE") or os.path.join(LOG_DIR, "admin_token.txt")
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            token = f.read().strip()
            return token or None
    except Exception:
        return None

# --------------------------
#  UTILITIES
# --------------------------
# ---------- Secure JSONL logging with rotation + tamper-evident chain ----------

def _lim(val, default):
    try:
        return int(val)
    except Exception:
        return default

LOG_MAX_BYTES = _lim(os.environ.get("LOG_MAX_BYTES", 512 * 1024), 512 * 1024)  # 512 KB default
LOG_BACKUPS   = _lim(os.environ.get("LOG_BACKUPS", 5), 5)                     # keep 5 backups
LOG_HMAC_KEY_HEX = os.environ.get("LOG_HMAC_KEY", "").strip()                 # set to random hex for tamper-evidence

def _rotate_file_if_needed(path: str):
    try:
        if not os.path.exists(path):
            return
        if os.path.getsize(path) <= LOG_MAX_BYTES:
            return
        # rotate: .4 -> .5, .3 -> .4, ... path -> .1
        for i in range(LOG_BACKUPS, 0, -1):
            src = f"{path}.{i}" if i > 1 else path
            dst = f"{path}.{i+1}" if i > 0 else None
            if os.path.exists(src):
                if i == LOG_BACKUPS:
                    try:
                        os.remove(f"{path}.{LOG_BACKUPS+1}")
                    except Exception:
                        pass
                os.rename(src, f"{path}.{i+1}")
        # create fresh file
        open(path, "a", encoding="utf-8").close()
    except Exception as e:
        # last resort: don't crash app because rotation failed
        print(f"[WARN] rotation failed for {path}: {e}")

def _last_chain_hmac(path: str) -> str | None:
    """Read last JSONL line's _h value to chain HMACs; return None if unavailable."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            # read from the end in small chunk
            step = min(4096, size)
            f.seek(max(0, size - step))
            tail = f.read().decode("utf-8", errors="ignore")
        lines = [ln for ln in tail.strip().splitlines() if ln.strip()]
        if not lines:
            return None
        last = lines[-1]
        try:
            j = json.loads(last)
            return j.get("_h")
        except Exception:
            return None
    except Exception:
        return None

def _sign_line(payload_bytes: bytes, prev_h: str | None) -> str | None:
    """Return hex HMAC over (prev_h||payload) if LOG_HMAC_KEY_HEX is set."""
    if not LOG_HMAC_KEY_HEX:
        return None
    try:
        key = bytes.fromhex(LOG_HMAC_KEY_HEX)
    except ValueError:
        return None
    hm = hmac.new(key, digestmod=hashlib.sha256)
    if prev_h:
        hm.update(prev_h.encode("utf-8"))
    hm.update(payload_bytes)
    return hm.hexdigest()

def append_jsonl_secure(path: str, obj: dict):
    """
    Append one JSON object per line with:
      - size-based rotation
      - optional tamper-evident hash chain (_h with previous link _p)
    """
    _rotate_file_if_needed(path)

    # prepare
    prev_h = _last_chain_hmac(path)
    # attach signed fields non-destructively
    to_write = dict(obj)
    if LOG_HMAC_KEY_HEX:
        # NOTE: we compute HMAC over the line WITHOUT _h, then store _h and _p
        payload_bytes = json.dumps(to_write, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        h = _sign_line(payload_bytes, prev_h)
        to_write["_p"] = prev_h  # previous hash (or None)
        to_write["_h"] = h       # current hash (or None if key invalid)

    line = json.dumps(to_write, ensure_ascii=False)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()

def ip_hash(ip):
    if not ip:
        return ""
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()

def bot_tripwire():
    """
    Return a Flask Response to block if bot is suspected; otherwise return None.
    Uses a dynamic honeypot field name stored in cookie 'hp_field' if present,
    otherwise falls back to HONEYPOT_FIELD (env/default).
    """
    honeypot_val = None

    # Determine expected honeypot field name (cookie preferred)
    hp_name = request.cookies.get("hp_field") or os.environ.get("HONEYPOT_FIELD", "hp_website")

    # Handle JSON bodies (API-style)
    if request.is_json:
        body = request.get_json(silent=True) or {}
        honeypot_val = (body.get(hp_name) or "").strip()
    else:
        # Form submissions
        honeypot_val = (request.form.get(hp_name) or "").strip()

    # If honeypot field is filled -> suspicious -> block + audit
    if honeypot_val:
        try:
            audit_record(
                action="honeypot_trigger",
                actor="unknown",
                subject=request.path,
                status="denied",
                extra={"hp_field": hp_name, "ip": request.remote_addr}
            )
        except Exception:
            pass

        return jsonify({"error": "bot_detected"}), 400

    return None

def audit_record(action: str,
                 actor: str = None,
                 subject: str = None,
                 status: str = None,
                 extra: dict | None = None,
                 notes: str | None = None):
    """Append a structured audit line to AUDIT_LOG (JSONL)."""
    # Back-compat: allow callers to pass notes=... (string)
    if notes:
        if isinstance(extra, dict) and extra:
            extra = {"notes": notes, **extra}
        else:
            extra = {"notes": notes}

    try:
        rec = {
            "ts": now_iso(),
            "ip": request.remote_addr if request else None,
            "action": action,
            "actor": actor,
            "subject": subject,
            "status": status,
            "extra": extra or {},
        }
    except RuntimeError:
        rec = {
            "ts": now_iso(),
            "ip": None,
            "action": action,
            "actor": actor,
            "subject": subject,
            "status": status,
            "extra": extra or {},
        }

    append_jsonl_secure(AUDIT_LOG, rec)

def require_admin(f):
    """Decorator identical to admin_required (compatibility)."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token_cfg = get_admin_token()
        if not token_cfg:
            return jsonify({"error": "Admin token not configured"}), 500

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            provided = auth.split(" ", 1)[1].strip()
        else:
            provided = request.headers.get("X-ADMIN-TOKEN", "").strip() or auth.strip()

        if provided != token_cfg:
            try:
                audit_record(
                    action="admin_access_denied",
                    actor="unknown",
                    subject=request.path,
                    status="denied",
                    extra={"ip": request.remote_addr}
                )
            except Exception:
                pass
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return wrapper

# keep compatibility with routes using @admin_required
admin_required = require_admin

#  VALIDATION HELPERS
def validate_json_field(data, field, expected_type):
    """Return (True, value) or (False, error message)."""
    if field not in data:
        return False, f"Missing field: {field}"
    if not isinstance(data[field], expected_type):
        return False, f"Field '{field}' must be {expected_type.__name__}"
    return True, data[field]

def require_json(f):
    """Ensure request is JSON."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        return f(*args, **kwargs)
    return wrapper

def validate_behavioral_session(s: dict):
    req = ["participant_id", "task_id", "start_ts", "end_ts", "events"]
    for k in req:
        if k not in s: return False, f"missing '{k}'"
    if not isinstance(s["events"], list): return False, "'events' must be a list"
    for i, e in enumerate(s["events"]):
        if not isinstance(e, dict): return False, f"event[{i}] must be object"
        if "type" not in e or "ts" not in e: return False, f"event[{i}] missing 'type' or 'ts'"
        if not isinstance(e["type"], str): return False, f"event[{i}].type must be string"
        if not isinstance(e["ts"], int): return False, f"event[{i}].ts must be int (ms)"
    return True, None

def validate_cognitive_session(s: dict):
    if "participant_id" not in s: return False, "missing 'participant_id'"
    if "task_id" not in s: return False, "missing 'task_id'"
    if "modules" not in s or not isinstance(s["modules"], list):
        return False, "'modules' must be a list"
    for mi, m in enumerate(s["modules"]):
        if not isinstance(m, dict): return False, f"modules[{mi}] must be object"
        if "module_name" not in m: return False, f"modules[{mi}] missing 'module_name'"
        qs = m.get("questions", [])
        if not isinstance(qs, list): return False, f"modules[{mi}].questions must be list"
        for qi, q in enumerate(qs):
            if not isinstance(q, dict): return False, f"q[{qi}] in module[{mi}] must be object"
            for k in ["question_id", "correct", "time_taken_seconds"]:
                if k not in q: return False, f"q[{qi}] in module[{mi}] missing '{k}'"
    return True, None


# --------------------------
#  MAIN ROUTES
# --------------------------
@limiter.limit("30 per minute")
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    user_answer = ""
    participant_id = request.cookies.get("participant_id")

    if request.method == 'POST':
        # Require consent
        if not participant_id:
            result = "no_consent"
            user_answer = request.form.get('answer', '').strip()
            ok = (user_answer == CORRECT_ANSWER)
            result = "correct" if ok else "wrong"

            # Log event (anonymized answer)
            log = {
                "participant_id": participant_id,
                "timestamp": now_iso(),
                "task_id": "sequence_test_001",
                "answer_hash": hashlib.sha256(user_answer.encode("utf-8")).hexdigest(),
                "result": result
            }
            append_jsonl_secure(DATA_LOG, log)
            audit_record(
                action="submit_answer",
                actor=f"participant:{participant_id}",
                subject="sequence_test_001",
                status="ok" if result == "correct" else "wrong",
                extra={"target_id": participant_id, "result": result},
            )
    return render_template(
        'index.html',
        result=result,
        user_answer=user_answer,
        hp_field=request.cookies.get("hp_field") or HONEYPOT_FIELD or "hp_website"
    )


@limiter.limit("5 per minute")
@app.route('/consent', methods=['POST'])
def consent():
    trip = bot_tripwire()
    if trip:
        return trip
    """Record participant consent."""
    ip = request.remote_addr or ""
    participant_id = str(uuid.uuid4())

    record = {
        "participant_id": participant_id,
        "timestamp": now_iso(),
        "consent_version": CONSENT_VERSION,
        "consent_given": True,
        "ip_hash": ip_hash(ip)
    }

    append_jsonl_secure(CONSENT_LOG, record)
    audit_record(actor=f"participant:{participant_id}", action="consent_given")

    resp = make_response(jsonify({"ok": True, "participant_id": participant_id}))
    resp.set_cookie("participant_id", participant_id, max_age=60*60*24*365, httponly=True, samesite="Lax")
    return resp


# ============================================================
# ANALYTICS ROUTES
# ============================================================
@app.route("/submit_result", methods=["POST"])
@limiter.limit("20 per minute") 
def submit_result():
    trip = bot_tripwire()
    if trip:
        return trip
    """
    Accepts JSON body with a session object.
    Automatically detects type (behavioral or cognitive)
    and computes the correct metrics.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    session = request.get_json()


    # -------------------------------------------
    # VALIDATION LAYER: reject malformed sessions
    # -------------------------------------------
    if isinstance(session, dict) and "events" in session:
        ok, msg = validate_behavioral_session(session)
        if not ok:
            return jsonify({"error": msg}), 400

    elif isinstance(session, dict) and "modules" in session:
        ok, msg = validate_cognitive_session(session)
        if not ok:
            return jsonify({"error": msg}), 400
    # -------------------------------------------


    saved = save_session_result(session)

    # detect session type and compute metrics
    if isinstance(saved, dict) and "events" in saved:
        metrics = compute_behavioral_metrics(saved)
        session_type = "behavioral"
    elif isinstance(saved, dict) and "modules" in saved:
        metrics = compute_cognitive_metrics(saved)
        session_type = "cognitive"
    else:
        metrics = {"note": "Unknown data type; no metrics computed"}
        session_type = "unknown"
    # ✅ AUDIT LOG HERE
    audit_record(
        actor=f"participant:{saved.get('participant_id', 'unknown')}",
        action="submit_result",
        target_id=saved.get("task_id"),
        notes=f"type={session_type}"
    )
    return jsonify({"saved": saved, "metrics": metrics}), 201

# -----------------------------------------
# AUDIT LOG ROUTE
# -----------------------------------------
@app.route("/audit/last/<int:n>", methods=["GET"])
@admin_required
@limiter.limit("10 per minute") 
def last_audit(n):
    try:
        entries = []
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                entries.append(json.loads(line))
        return jsonify({"audit": entries[-n:]}), 200
    except Exception as e:
        return jsonify({"error": "failed to read audit log", "detail": str(e)}), 500

@app.route("/metrics", methods=["GET"])
@admin_required
@limiter.limit("2 per second")
def metrics():
    """Return aggregated metrics."""
    try:
        agg = aggregate_metrics()
     
        # ✅ AUDIT LOG: admin requested aggregated metrics
        audit_record(
            actor="admin",
            action="view_metrics",
            notes=f"returned_items={len(agg)}"
        )

        return jsonify(agg), 200
    except Exception as e:
        return jsonify({"error": "metrics computation failed", "detail": str(e)}), 500

@app.route("/export", methods=["GET"])
@admin_required
@limiter.limit("5 per minute") 
def export():
    """Return all stored session rows (admin only)."""
    rows = export_all()


    #AUDIT LOG: admin exported data
    audit_record(
        actor="admin",
        action="export_all_data",
        notes=f"rows={len(rows)}"
    )

    return jsonify(rows), 200


@app.route("/erase/<participant_id>", methods=["DELETE"])
@admin_required
@limiter.limit("3 per minute")
def erase(participant_id):
    """Delete data for a participant ID (admin only)."""
    removed = erase_participant(participant_id)

     # ✅ AUDIT LOG: admin erased participant data
    audit_record(
        actor="admin",
        action="erase_participant",
        target_id=participant_id,
        notes=f"removed={removed}"
    )


    return jsonify({"removed": removed}), 200

@app.route("/data_type_summary", methods=["GET"])
@admin_required
@limiter.limit("20 per minute")
def data_type_summary():
    """Counts behavioral vs cognitive sessions."""
    try:
        rows = export_all()
    except Exception as e:
        return jsonify({"error": "failed to read data", "detail": str(e)}), 500

    behavioral = cognitive = unknown = 0

    for r in rows:
        if isinstance(r, dict) and "events" in r:
            behavioral += 1
        elif isinstance(r, dict) and "modules" in r:
            cognitive += 1
        else:
            unknown += 1

    return jsonify({
        "behavioral_sessions": behavioral,
        "cognitive_sessions": cognitive,
        "unknown_sessions": unknown,
        "total": behavioral + cognitive + unknown
    }), 200


@app.route("/export/dashboard", methods=["GET"])
@admin_required
@limiter.limit("10 per minute")
def export_dashboard():
    """
    Returns chart-ready metrics for plotting progress over time.
    - Cognitive sessions -> accuracy%, avg time, avg hesitation, avg retries
    - Behavioral sessions -> performance_score, total_time, hints, retries, hesitation
    """
    try:
        rows = export_all()   # already implemented in your project
    except Exception as e:
        return jsonify({"error": "failed to read data", "detail": str(e)}), 500

    # Structures to hold chart series
    cognitive = {
        "index": [],
        "accuracy_pct": [],
        "avg_time_s": [],
        "avg_hesitation_s": [],
        "avg_retries": [],
    }

    behavioral = {
        "index": [],
        "performance_score": [],
        "total_time_s": [],
        "hints": [],
        "retries": [],
        "hesitation_s": [],
    }

    cog_i = beh_i = 0

    # Loop through every session record
    for entry in rows:

        # ==========================================================
        # COGNITIVE SESSION (modules → questions)
        # ==========================================================
        if isinstance(entry, dict) and "modules" in entry:
            modules = entry.get("modules", [])

            total_questions = 0
            correct = 0
            total_time = 0.0
            total_hesitation = 0.0
            total_retries = 0.0

            for m in modules:
                for q in m.get("questions", []):
                    total_questions += 1
                    if q.get("correct"):
                        correct += 1
                    total_time += q.get("time_taken_seconds", 0) or 0
                    total_hesitation += q.get("hesitation_seconds", 0) or 0
                    total_retries += q.get("retries", 0) or 0

            if total_questions > 0:
                cog_i += 1
                cognitive["index"].append(cog_i)
                cognitive["accuracy_pct"].append(round((correct / total_questions) * 100, 2))
                cognitive["avg_time_s"].append(round(total_time / total_questions, 2))
                cognitive["avg_hesitation_s"].append(round(total_hesitation / total_questions, 2))
                cognitive["avg_retries"].append(round(total_retries / total_questions, 2))


        # ==========================================================
        # BEHAVIORAL SESSION (events → timestamps)
        # ==========================================================
        elif isinstance(entry, dict) and "events" in entry:

            start = entry.get("start_ts")
            end = entry.get("end_ts")
            total_ms = max(0, (end - start)) if (start and end) else None
            events = entry.get("events", [])

            # Count hints + retries
            hints = sum(1 for e in events if e.get("type") == "hint")
            retries = sum(1 for e in events if e.get("type") == "retry")

            # Hesitation calculation (gaps > 1500ms)
            timestamps = sorted([e.get("ts") for e in events if isinstance(e.get("ts"), (int, float))])
            hesitation_ms = 0
            for a, b in zip(timestamps, timestamps[1:]):
                gap = b - a
                if gap > 1500:
                    hesitation_ms += gap

            # Performance score (lightweight version of compute_behavioral_metrics)
            score = 100
            if total_ms is not None:
                score -= (total_ms / 1000.0) * 0.5
            score -= hints * 5
            score -= retries * 3
            score = round(max(0, score), 2)

            beh_i += 1
            behavioral["index"].append(beh_i)
            behavioral["performance_score"].append(score)
            behavioral["total_time_s"].append(round(total_ms / 1000.0, 3) if total_ms else None)
            behavioral["hints"].append(hints)
            behavioral["retries"].append(retries)
            behavioral["hesitation_s"].append(round(hesitation_ms / 1000.0, 3))

        # ==========================================================
        # UNKNOWN ENTRY (should not happen but safe to ignore)
        # ==========================================================
        else:
            continue

    return jsonify({
        "cognitive": cognitive,
        "behavioral": behavioral
    }), 200


# ============================================================
# HEALTH CHECK / STATUS
# ============================================================

def _count_jsonl_lines(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return None  # unreadable or missing

def _read_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return True, json.load(f)
    except FileNotFoundError:
        return False, None
    except Exception:
        return True, None  # exists but invalid JSON

@limiter.limit("30 per minute")
@app.route("/status", methods=["GET"])
def status():
    # Uses variables you already defined earlier in app.py:
    # BASE_DIR, LOG_DIR, CONSENT_LOG, DATA_LOG, AUDIT_LOG
    session_file = os.path.join(BASE_DIR, "session_data.json")

    exists = {
        "log_dir": os.path.isdir(LOG_DIR),
        "session_data_json": os.path.isfile(session_file),
        "consent_log_jsonl": os.path.isfile(CONSENT_LOG),
        "data_log_jsonl": os.path.isfile(DATA_LOG),
        "audit_log_jsonl": os.path.isfile(AUDIT_LOG),
    }

    session_exists, session_data = _read_json_file(session_file)
    session_parsable = (session_data is not None) if session_exists else False

    consent_count = _count_jsonl_lines(CONSENT_LOG) if exists["consent_log_jsonl"] else None
    audit_count = _count_jsonl_lines(AUDIT_LOG) if exists["audit_log_jsonl"] else None
    data_log_count = _count_jsonl_lines(DATA_LOG) if exists["data_log_jsonl"] else None

    writable = {
        "log_dir_writable": os.access(LOG_DIR, os.W_OK),
        "base_dir_writable": os.access(BASE_DIR, os.W_OK),
    }

    admin_token_configured = bool(get_admin_token())

    if isinstance(session_data, list):
        session_count = len(session_data)
    elif isinstance(session_data, dict):
        session_count = 1
    else:
        session_count = 0 if session_parsable else None

    ok_flags = [
        exists["log_dir"],
        writable["log_dir_writable"],
        session_exists,
        session_parsable,
        admin_token_configured,
    ]
    status_level = "ok" if all(ok_flags) else "degraded"

    return jsonify({
        "status": status_level,
        "files": exists,
        "writable": writable,
        "admin_token_configured": admin_token_configured,
        "counts": {
            "sessions": session_count,
            "consent_log_lines": consent_count,
            "audit_log_lines": audit_count,
            "data_log_lines": data_log_count,
        },
    }), 200


# --------------------------
#  COMPLIANCE ENDPOINTS
# --------------------------

def anonymize_data_for_participant(pid):
    """Replace participant_id in DATA_LOG with 'erased_' token (keeps audit)."""
    erased_token = f"erased_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    temp_path = DATA_LOG + ".tmp"

    if not os.path.exists(DATA_LOG):
        return False, "No data log found."

    try:
        with open(DATA_LOG, "r", encoding="utf-8") as fin, open(temp_path, "w", encoding="utf-8") as fout:
            for line in fin:
                try:
                    j = json.loads(line)
                except:
                    fout.write(line)
                    continue
                if j.get("participant_id") == pid:
                    j["participant_id"] = erased_token
                    j["erased"] = True
                    j["erasure_timestamp"] = now_iso()
                fout.write(json.dumps(j, ensure_ascii=False) + "\n")

        backup = DATA_LOG + ".bak." + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        os.rename(DATA_LOG, backup)
        os.rename(temp_path, DATA_LOG)
        return True, f"Entries anonymized; backup at {backup}"
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False, str(e)


@app.route('/export/<participant_id>', methods=['GET'])
def export_data(participant_id):
    """Allow admin or participant to export their data."""
    # Always read current admin token (supports rotation)
    token_cfg = get_admin_token()

    # Accept Authorization: Bearer <token> OR X-ADMIN-TOKEN: <token>
    provided = extract_admin_token_from_request()

    cookie_pid = request.cookies.get("participant_id")
    if token_cfg and provided and hmac.compare_digest(provided, token_cfg):
        actor = "admin"
    elif cookie_pid == participant_id:
        actor = f"participant:{participant_id}"
    else:
        audit_record(actor="unauthorized", action="export_attempt", subject=participant_id, status="denied",
                     extra={"ip": request.remote_addr})
        return jsonify({"error": "Unauthorized"}), 401

    results = []
    if os.path.exists(DATA_LOG):
        with open(DATA_LOG, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    j = json.loads(line)
                    if j.get("participant_id") == participant_id:
                        results.append(j)
                except Exception:
                    pass

    audit_record(actor=actor, action="export", subject=participant_id,
                 status="ok", extra={"count": len(results)})
    return jsonify({"participant_id": participant_id, "events": results})


@app.route('/erase', methods=['POST'])
def erase_self():
    """Participant-initiated erasure (anonymizes logs)."""
    pid = request.cookies.get("participant_id")
    if not pid:
        return jsonify({"error": "No participant cookie found"}), 400

    data = request.get_json() or {}
    if not data.get("confirm"):
        return jsonify({"error": "Please confirm erasure by sending {\"confirm\": true}"}), 400

    ok, msg = anonymize_data_for_participant(pid)
    audit_record(actor=f"participant:{pid}", action="erase_request", notes=msg)
    if ok:
        resp = jsonify({"ok": True, "message": "Your data has been anonymized."})
        resp.set_cookie("participant_id", "", expires=0)
        return resp
    else:
        return jsonify({"error": "Erase failed", "details": msg}), 500


@app.route('/admin/delete_participant/<participant_id>', methods=['POST'])
@require_admin
def admin_delete(participant_id):
    """Admin-only permanent delete (backed up before removal)."""
    if not os.path.exists(DATA_LOG):
        return jsonify({"error": "No data log"}), 400

    backup = DATA_LOG + ".bak." + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    try:
        os.rename(DATA_LOG, backup)
        kept, removed = 0, 0
        with open(backup, "r", encoding="utf-8") as fin, open(DATA_LOG, "w", encoding="utf-8") as fout:
            for line in fin:
                try:
                    j = json.loads(line)
                    if j.get("participant_id") == participant_id:
                        removed += 1
                        continue
                    fout.write(json.dumps(j, ensure_ascii=False) + "\n")
                    kept += 1
                except:
                    fout.write(line)
                    kept += 1
        audit_record(actor="admin", action="delete_participant",
                     target_id=participant_id, notes=f"removed {removed} entries; backup at {backup}")
        return jsonify({"ok": True, "removed": removed, "backup": backup})
    except Exception as e:
        if os.path.exists(backup) and not os.path.exists(DATA_LOG):
            os.rename(backup, DATA_LOG)
        return jsonify({"error": "Failed delete", "details": str(e)}), 500


# --------------------------
#  METADATA ENDPOINT (HTML + JSON)
# --------------------------

@app.route('/metadata', methods=['GET'])
def metadata():
    """Expose compliance and model metadata (HTML for browser, JSON for API)."""
    dpiapath = os.path.join(BASE_DIR, "DPIA.md")
    modelpath = os.path.join(BASE_DIR, "model_card.md")

    def safe_read(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read(2000)
        except FileNotFoundError:
            return "N/A"

    dpia_text = safe_read(dpiapath)
    model_text = safe_read(modelpath)

    # If the user requested JSON explicitly
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            "project": "Cognitive-Behavioral Analytics MVP",
            "dpiaversion": "1.0",
            "model_version": "1.0",
            "consent_version": CONSENT_VERSION,
            "contact": "jirehkenneth2001@gmail.com",
            "maintainer": "Jireh Kenneth-Usen",
            "location": "Lagos, Nigeria",
            "license": "Internal research / educational prototype",
            "last_review": datetime.datetime.now().strftime("%Y-%m-%d"),
            "dpia_excerpt": dpia_text[:300],
            "modelcard_excerpt": model_text[:300]
        })

    # Otherwise, return a pretty HTML view
    html = f"""
    <html>
    <head>
        <title>System Metadata – Compliance Overview</title>
        <link rel="stylesheet" href="/static/style.css">
        <style>
            body {{ background:#f8f9fa; color:#222; font-family:Inter, sans-serif; padding:2rem; }}
            h1 {{ color:#d6336c; }}
            pre {{ background:#fff; padding:1rem; border-radius:0.5rem; overflow-x:auto; }}
            .card {{ background:white; box-shadow:0 2px 6px rgba(0,0,0,0.1); border-radius:1rem; padding:1.5rem; margin-bottom:2rem; }}
            .meta-title {{ color:#444; font-size:1.2rem; font-weight:600; margin-bottom:0.5rem; }}
        </style>
    </head>
    <body>
        <h1>Compliance & Model Metadata</h1>

        <div class="card">
            <div class="meta-title">Project:</div>
            Cognitive-Behavioral Analytics MVP<br>
            <b>Maintainer:</b> Jireh Kenneth-Usen<br>
            <b>Contact:</b> jirehkenneth2001@gmail.com<br>
            <b>Consent Version:</b> {CONSENT_VERSION}<br>
            <b>DPIA Version:</b> 1.0<br>
            <b>Model Version:</b> 1.0<br>
            <b>Last Review:</b> {datetime.datetime.now().strftime("%Y-%m-%d")}<br>
        </div>

        <div class="card">
            <div class="meta-title">DPIA Excerpt</div>
            <pre>{dpia_text[:600]}</pre>
        </div>

        <div class="card">
            <div class="meta-title">Model Card Excerpt</div>
            <pre>{model_text[:600]}</pre>
        </div>

        <p style="text-align:center; color:#888;">© 2025 Jireh Kenneth-Usen – Internal Research Prototype</p>
    </body>
    </html>
    """

    return html

# --------------------------
#  RUN SERVER
# --------------------------

if __name__ == "__main__":
    print("✅ Flask app running on http://127.0.0.1:5000")
    print("Admin token set:", bool(get_admin_token()))
    app.run(host="127.0.0.1", port=5000, debug=False)

