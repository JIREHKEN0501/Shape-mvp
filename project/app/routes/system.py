# project/app/routes/system.py

import os, json, datetime
from flask import Blueprint, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from project.app.utils.logging import (
    AUDIT_LOG, CONSENT_LOG, DATA_LOG,
)
from project.app.utils.helpers import (
    _count_jsonl_lines, _read_json_file,
)
from project.app.routes.security import get_admin_token

system_bp = Blueprint("system", __name__)
limiter = Limiter(key_func=get_remote_address)

# Base paths (these are set in app.py)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")


# ============================================================
# /status  — HEALTH CHECK
# ============================================================

@system_bp.route("/status", methods=["GET"])
@limiter.limit("30 per minute")
def status():
    """Return health check status for monitoring & CI."""
    
    session_file = os.path.join(BASE_DIR, "session_data.json")

    exists = {
        "log_dir": os.path.isdir(LOG_DIR),
        "session_data_json": os.path.isfile(session_file),
        "consent_log_jsonl": os.path.isfile(CONSENT_LOG),
        "data_log_jsonl": os.path.isfile(DATA_LOG),
        "audit_log_jsonl": os.path.isfile(AUDIT_LOG),
    }

    # session file readable?
    session_exists, session_data = _read_json_file(session_file)
    session_parsable = (session_data is not None) if session_exists else False

    # counts
    consent_count = _count_jsonl_lines(CONSENT_LOG) if exists["consent_log_jsonl"] else None
    audit_count   = _count_jsonl_lines(AUDIT_LOG) if exists["audit_log_jsonl"] else None
    data_count    = _count_jsonl_lines(DATA_LOG) if exists["data_log_jsonl"] else None

    # writable flags
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
            "consent": consent_count,
            "audit": audit_count,
            "data": data_count,
        },
    }), 200



# ============================================================
# /metadata — COMPLIANCE + MODEL INFO
# ============================================================

@system_bp.route("/metadata", methods=["GET"])
def metadata():
    """Expose compliance, DPIA, model card, project info."""

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

    # If user asks for JSON explicitly
    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "project": "Cognitive-Behavioral Analytics MVP",
            "dpiaversion": "1.0",
            "model_version": "1.0",
            "consent_version": os.environ.get("CONSENT_VERSION", "1"),
            "contact": "jirehkenneth2001@gmail.com",
            "maintainer": "Jireh Kenneth-Usen",
            "location": "Lagos, Nigeria",
            "license": "Internal research / educational prototype",
            "last_review": datetime.datetime.now().strftime("%Y-%m-%d"),
            "dpia_excerpt": dpia_text[:300],
            "modelcard_excerpt": model_text[:300],
        }), 200

    # Otherwise, return HTML summary
    return render_template(
        "metadata.html",
        dpia_excerpt=dpia_text,
        modelcard_excerpt=model_text,
    )

