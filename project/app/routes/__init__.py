# project/app/routes/__init__.py  (top of file)
from flask import Blueprint, request, jsonify, render_template, make_response, send_file, redirect
from functools import wraps
from flask import current_app
import os
import json
import glob
import tempfile
import time

# prefer helpers module for audit_record / get_admin_token
from project.app.helpers import audit_record, get_admin_token
# limiter import (adjust if you keep a different layout)
try:
    from project.app.extensions.limiter import limiter
except Exception:
    # fallback if you put limiter in a different location - keep code working
    limiter = None

main = Blueprint("main", __name__)

def admin_required(f):
    """Decorator to protect sensitive routes using rotating admin token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token_cfg = get_admin_token()
        if not token_cfg:
            return jsonify({"error": "Admin token not configured"}), 500

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            provided = auth.split(" ", 1)[1].strip()
        else:
            provided = (request.headers.get("X-ADMIN-TOKEN", "") or auth or request.cookies.get("admin_session", "")).strip()

        if provided != token_cfg:
            try:
                audit_record(action="admin_access_denied", actor="unknown", subject=request.path, status="denied", extra={"ip": request.remote_addr})
            except Exception:
                pass
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return decorated


@main.route("/", methods=["GET"])
def index():
    return "Shape MVP - running"


@main.route("/admin/dashboard", methods=["GET"])
@admin_required
def admin_dashboard():
    try:
        counts = {
            "audit_log_lines": sum(1 for _ in open("logs/audit_log.jsonl", "r", encoding="utf-8")) if os.path.exists("logs/audit_log.jsonl") else None,
            "consent_log_lines": sum(1 for _ in open("logs/consent_log.jsonl", "r", encoding="utf-8")) if os.path.exists("logs/consent_log.jsonl") else None,
            "data_log_lines": sum(1 for _ in open("logs/data_log.jsonl", "r", encoding="utf-8")) if os.path.exists("logs/data_log.jsonl") else None,
            "sessions": None
        }
    except Exception:
        counts = {"audit_log_lines": None, "consent_log_lines": None, "data_log_lines": None, "sessions": None}

    recent = []
    try:
        if os.path.exists("logs/audit_log.jsonl"):
            with open("logs/audit_log.jsonl", "r", encoding="utf-8") as fh:
                tail = fh.readlines()[-10:]
            for line in tail:
                try:
                    o = json.loads(line)
                    recent.append({"ts": o.get("ts"), "action": o.get("action"), "actor": o.get("actor"), "subject": o.get("subject")})
                except Exception:
                    continue
    except Exception:
        recent = []

    return render_template("admin/dashboard.html", counts=counts, recent=recent)


@main.route("/admin/export/<participant_id>", methods=["GET"])
@admin_required
def admin_export(participant_id):
    """Return JSON export of a participant (scan logs/*.jsonl)."""
    records = []
    try:
        for fname in glob.glob("logs/*.jsonl"):
            with open(fname, "r", encoding="utf-8") as fh:
                for line in fh:
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if obj.get("participant_id") == participant_id:
                        records.append({"file": fname, "record": obj})
        return jsonify({"ok": True, "participant_id": participant_id, "matches": len(records), "records": records})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@main.route("/admin/download/<participant_id>", methods=["GET"])
@admin_required
def admin_download(participant_id):
    """Create a small JSON file and send as attachment."""
    res = admin_export(participant_id).get_json(force=True)
    if not res.get("ok"):
        return jsonify({"ok": False, "error": "no records"}), 404

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    try:
        tmp.write(json.dumps(res, indent=2).encode("utf-8"))
        tmp.flush()
        tmp.close()
        return send_file(tmp.name, as_attachment=True, download_name=f"export-{participant_id}.json")
    finally:
        # note: temp file will remain until rotated by system or manually removed; that's fine for small exports
        pass


@main.route("/admin/erase/<participant_id>", methods=["POST"])
@admin_required
def admin_erase(participant_id):
    """Best-effort anonymize in logs by replacing participant_id in data_log.jsonl."""
    path = "logs/data_log.jsonl"
    if not os.path.exists(path):
        return jsonify({"ok": False, "error": "no_data_log"}), 404

    tmp_path = path + ".tmp"
    repl = f"anonymized:{int(time.time()*1000)}"
    changed = 0
    try:
        with open(path, "r", encoding="utf-8") as inf, open(tmp_path, "w", encoding="utf-8") as outf:
            for line in inf:
                try:
                    obj = json.loads(line)
                except Exception:
                    outf.write(line)
                    continue
                if obj.get("participant_id") == participant_id:
                    obj["participant_id"] = repl
                    changed += 1
                outf.write(json.dumps(obj) + "\n")
        os.replace(tmp_path, path)
        try:
            audit_record(action="erase_performed", actor="admin", subject=f"erase:{participant_id}", status="ok", extra={"replacement": repl, "changed_lines": changed})
        except Exception:
            pass
        return jsonify({"ok": True, "participant_id": participant_id, "replacement": repl, "changed_lines": changed})
    except Exception as e:
        try:
            audit_record(action="erase_partial_fail", actor="admin", subject=f"erase:{participant_id}", status="error", extra={"error": str(e)})
        except Exception:
            pass
        return jsonify({"ok": False, "error": str(e)}), 500

# add near other routes in project/app/routes/__init__.py

@main.route("/decoy_submit", methods=["POST"])
def decoy_submit():
    """
    Accept either JSON or form POST. If the honeypot field is present (bot),
    log a decoy_hit via audit_record and show decoy_thanks.html.
    Otherwise record a normal decoy_hit (seen) and still show the thank you page.
    """
    # Gather request data (shallow)
    body = request.get_json(silent=True) or {}
    form = request.form.to_dict() or {}
    fields = {}
    # JSON body should not overwrite form unless JSON has keys; update in this order so JSON & form both included
    fields.update(form)
    fields.update(body)

    # honeypot field from config, fallback to the hp you provided
    hp_field = current_app.config.get("HONEY_POT_FIELD", "hp_1aa74582")

    # Basic extra info for audit
    extra = {
        "ip": request.remote_addr,
        "via": "form_or_json",
        "fields": {k: ("<redacted>" if "password" in k.lower() else v) for k, v in fields.items()}
    }

    try:
        if hp_field in fields and fields.get(hp_field):
            # Bot/honeypot hit
            audit_record(action="decoy_hit", actor="unknown", subject=request.path, status="collected", extra=extra)
        else:
            # Legit / normal interaction — we still log 'seen'
            audit_record(action="decoy_hit", actor="unknown", subject=request.path, status="seen", extra=extra)
    except Exception:
        # don't break the flow if audit_record fails
        pass

    # Return the decoy thank-you page (same as old behavior)
    return render_template("decoy_thanks.html"), 200

