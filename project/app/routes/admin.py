# project/app/routes/admin.py

import os
import json
import datetime
from functools import wraps
from flask import (
    Blueprint, request, jsonify, render_template,
    make_response, redirect
)

# utils
from project.app.utils.logging import (
    audit_record,
    append_jsonl_secure,
    DATA_LOG,
    CONSENT_LOG,
    AUDIT_LOG
)

from project.app.utils.helpers import (
    now_iso,
    _read_jsonl_file,
    _anonymize_and_replace_in_file
)

from project.app.utils.metrics import (
    aggregate_metrics
)

# admin token provider
from project.app.routes.security import get_admin_token


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ==============================
#   AUTH DECORATOR
# ==============================
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        real = get_admin_token()
        if not real:
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

        if provided != real:
            audit_record(
                action="admin_access_denied",
                actor="unknown",
                subject=request.path,
                status="denied",
                extra={"ip": request.remote_addr}
            )
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return decorated


# ==============================
#   LOGIN PAGE
# ==============================
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")

    token_submitted = request.form.get("token", "").strip()
    real_token = get_admin_token()

    if not real_token:
        return "Admin token not configured", 500

    if token_submitted != real_token:
        return render_template("admin_login.html", error="Invalid token")

    resp = make_response(redirect("/admin/dashboard"))
    resp.set_cookie(
        "admin_session",
        token_submitted,
        httponly=True,
        samesite="Lax",
        max_age=3600,
    )
    return resp


# ==============================
#   DASHBOARD
# ==============================
@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def admin_dashboard():
    try:
        counts = {
            "audit_log_lines": sum(1 for _ in _read_jsonl_file(AUDIT_LOG)),
            "consent_log_lines": sum(1 for _ in _read_jsonl_file(CONSENT_LOG)),
            "data_log_lines": sum(1 for _ in _read_jsonl_file(DATA_LOG)),
        }
    except Exception:
        counts = {
            "audit_log_lines": None,
            "consent_log_lines": None,
            "data_log_lines": None
        }

    recent = []
    try:
        recent = list(_read_jsonl_file(AUDIT_LOG))[-10:]
    except Exception:
        pass

    display_recent = [
        {
            "ts": r.get("ts"),
            "action": r.get("action"),
            "actor": r.get("actor"),
            "subject": r.get("subject"),
        }
        for r in recent
    ]

    return render_template("admin_dashboard.html", counts=counts, recent=display_recent)


# ==============================
#       EXPORT ALL LOGS
# ==============================
@admin_bp.route("/export", methods=["GET"])
@admin_required
def export_all_logs():
    try:
        with open(DATA_LOG, "r", encoding="utf-8") as f:
            rows = [json.loads(line) for line in f]
    except Exception as e:
        return jsonify({"error": "failed to read data", "detail": str(e)}), 500

    audit_record(
        actor="admin",
        action="export_all_data",
        notes=f"rows={len(rows)}"
    )
    return jsonify(rows), 200

# ==============================
#   EXPORT PARTICIPANT DATA
# ==============================

@admin_bp.route("/export/<participant_id>", methods=["GET"])
@admin_required
def export_participant_admin(participant_id):
    records = []

    try:
        for path in (DATA_LOG, CONSENT_LOG, AUDIT_LOG):
            for obj in _read_jsonl_file(path):
                if obj.get("participant_id") == participant_id:
                    records.append({
                        "file": path,
                        "record": obj,
                    })

        audit_record(
            actor="admin",
            action="export_participant_data",
            subject=participant_id,
            notes=f"matches={len(records)}",
        )

        return jsonify({
            "ok": True,
            "participant_id": participant_id,
            "matches": len(records),
            "records": records,
        }), 200

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": "failed to export participant data",
            "detail": str(e),
        }), 500
