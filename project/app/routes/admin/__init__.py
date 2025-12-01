# project/app/routes/admin/__init__.py

from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
    send_file,
)
from functools import wraps
import os
import json
import glob
import tempfile
import time

from project.app.helpers import audit_record, get_admin_token
from project.app.extensions.limiter import limiter

admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Decorator to protect sensitive admin routes using rotating admin token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token_cfg = get_admin_token()
        if not token_cfg:
            return jsonify({"error": "Admin token not configured"}), 500

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            provided = auth.split(" ", 1)[1].strip()
        else:
            provided = (
                request.headers.get("X-ADMIN-TOKEN", "")
                or auth
                or request.cookies.get("admin_session", "")
            ).strip()

        if provided != token_cfg:
            try:
                audit_record(
                    action="admin_access_denied",
                    actor="unknown",
                    subject=request.path,
                    status="denied",
                    extra={"ip": request.remote_addr},
                )
            except Exception:
                pass
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)

    return decorated


@admin.route("/dashboard", methods=["GET"])
@admin_required
@limiter.limit("10 per minute")
def admin_dashboard():
    """
    Simple admin dashboard showing recent audit log entries
    and basic counts.
    """
    try:
        counts = {
            "audit_log_lines": sum(
                1
                for _ in open("logs/audit_log.jsonl", "r", encoding="utf-8")
            )
            if os.path.exists("logs/audit_log.jsonl")
            else None,
            "consent_log_lines": sum(
                1
                for _ in open("logs/consent_log.jsonl", "r", encoding="utf-8")
            )
            if os.path.exists("logs/consent_log.jsonl")
            else None,
            "data_log_lines": sum(
                1
                for _ in open("logs/data_log.jsonl", "r", encoding="utf-8")
            )
            if os.path.exists("logs/data_log.jsonl")
            else None,
            "sessions": None,
        }
    except Exception:
        counts = {
            "audit_log_lines": None,
            "consent_log_lines": None,
            "data_log_lines": None,
            "sessions": None,
        }

    recent = []
    try:
        if os.path.exists("logs/audit_log.jsonl"):
            with open("logs/audit_log.jsonl", "r", encoding="utf-8") as fh:
                tail = fh.readlines()[-10:]
            for line in tail:
                try:
                    o = json.loads(line)
                    recent.append(
                        {
                            "ts": o.get("ts"),
                            "action": o.get("action"),
                            "actor": o.get("actor"),
                            "subject": o.get("subject"),
                        }
                    )
                except Exception:
                    continue
    except Exception:
        recent = []

    # if you prefer pure JSON, you can swap this to jsonify(...)
    return render_template("admin/dashboard.html", counts=counts, recent=recent)


@admin.route("/export/<participant_id>", methods=["GET"])
@admin_required
@limiter.limit("20 per minute")
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

        return jsonify(
            {
                "ok": True,
                "participant_id": participant_id,
                "matches": len(records),
                "records": records,
            }
        )
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@admin.route("/download/<participant_id>", methods=["GET"])
@admin_required
@limiter.limit("10 per minute")
def admin_download(participant_id):
    """Create a small JSON file and send as attachment."""
    # Re-use admin_export logic
    from flask import current_app

    with current_app.test_request_context():
        res = admin_export(participant_id)
    data, status = res
    if status != 200:
        return jsonify({"ok": False, "error": "no records"}), 404

    res_json = data.get_json(force=True)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    try:
        tmp.write(json.dumps(res_json, indent=2).encode("utf-8"))
        tmp.flush()
        tmp.close()
        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=f"export-{participant_id}.json",
        )
    finally:
        # temp file will eventually be cleaned up externally; okay for small exports
        pass


@admin.route("/erase/<participant_id>", methods=["POST"])
@admin_required
@limiter.limit("5 per minute")
def admin_erase(participant_id):
    """
    Best-effort anonymize in logs by replacing participant_id in data_log.jsonl.
    """
    path = "logs/data_log.jsonl"
    if not os.path.exists(path):
        return jsonify({"ok": False, "error": "no_data_log"}), 404

    tmp_path = path + ".tmp"
    repl = f"anonymized:{int(time.time() * 1000)}"
    changed = 0
    try:
        with open(path, "r", encoding="utf-8") as inf, open(
            tmp_path, "w", encoding="utf-8"
        ) as outf:
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
            audit_record(
                action="erase_performed",
                actor="admin",
                subject=f"erase:{participant_id}",
                status="ok",
                extra={"replacement": repl, "changed_lines": changed},
            )
        except Exception:
            pass

        return jsonify(
            {
                "ok": True,
                "participant_id": participant_id,
                "replacement": repl,
                "changed_lines": changed,
            }
        )
    except Exception as e:
        try:
            audit_record(
                action="erase_partial_fail",
                actor="admin",
                subject=f"erase:{participant_id}",
                status="error",
                extra={"error": str(e)},
            )
        except Exception:
            pass
        return jsonify({"ok": False, "error": str(e)}), 500

