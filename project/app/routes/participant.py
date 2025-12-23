# project/app/routes/participant.py

import os, uuid, hashlib
from flask import (
    Blueprint, request, jsonify, render_template,
    make_response
)
from functools import wraps

from project.app.routes.security import bot_tripwire
from project.app.utils.logging import (
    append_jsonl_secure, audit_record,
    CONSENT_LOG, DATA_LOG
)
from project.app.utils.helpers import now_iso, ip_hash
from project.app.utils.metrics import (
    compute_behavioral_metrics,
    compute_cognitive_metrics,
)
from project.app.utils.storage import save_session_result

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

participant_bp = Blueprint("participant", __name__)
limiter = Limiter(key_func=get_remote_address)


# ================================
#  VALIDATION HELPERS
# ================================

def validate_behavioral_session(s: dict):
    req = ["participant_id", "task_id", "start_ts", "end_ts", "events"]
    for k in req:
        if k not in s:
            return False, f"missing '{k}'"

    if not isinstance(s["events"], list):
        return False, "'events' must be a list"

    for i, e in enumerate(s["events"]):
        if not isinstance(e, dict):
            return False, f"event[{i}] must be object"
        if "type" not in e or "ts" not in e:
            return False, f"event[{i}] missing 'type' or 'ts'"
        if not isinstance(e["type"], str):
            return False, f"event[{i}].type must be string"
        if not isinstance(e["ts"], int):
            return False, f"event[{i}].ts must be int (ms)"

    return True, None


def validate_cognitive_session(s: dict):
    if "participant_id" not in s:
        return False, "missing 'participant_id'"
    if "task_id" not in s:
        return False, "missing 'task_id'"
    if "modules" not in s or not isinstance(s["modules"], list):
        return False, "'modules' must be a list"

    for mi, m in enumerate(s["modules"]):
        if not isinstance(m, dict):
            return False, f"modules[{mi}] must be object"
        if "module_name" not in m:
            return False, f"modules[{mi}] missing 'module_name'"

        qs = m.get("questions", [])
        if not isinstance(qs, list):
            return False, f"modules[{mi}].questions must be list"

        for qi, q in enumerate(qs):
            if not isinstance(q, dict):
                return False, f"q[{qi}] in module[{mi}] must be object"
            for k in ["question_id", "correct", "time_taken_seconds"]:
                if k not in q:
                    return False, f"q[{qi}] in module[{mi}] missing '{k}'"

    return True, None



# ================================
#  ROOT PUZZLE ROUTE
# ================================

@participant_bp.route("/test", methods=["GET", "POST"])
@limiter.limit("30 per minute")
def index():
    participant_id = request.cookies.get("participant_id")
    result = None
    user_answer = ""

    if request.method == "POST":
        # require consent
        if not participant_id:
            result = "no_consent"
        else:
            user_answer = request.form.get("answer", "").strip()
            CORRECT_ANSWER = "21"  # existing logic
            ok = (user_answer == CORRECT_ANSWER)
            result = "correct" if ok else "wrong"

            # log
            log = {
                "participant_id": participant_id,
                "timestamp": now_iso(),
                "task_id": "sequence_test_001",
                "answer_hash": hashlib.sha256(user_answer.encode()).hexdigest(),
                "result": result,
            }
            append_jsonl_secure(DATA_LOG, log)

            audit_record(
                action="submit_answer",
                actor=f"participant:{participant_id}",
                subject="sequence_test_001",
                status="ok" if result == "correct" else "wrong",
                extra={"result": result},
            )

    hp_field = request.cookies.get("hp_field") or "hp_website"
    return render_template(
        "index.html",
        result=result,
        user_answer=user_answer,
        hp_field=hp_field
    )



# ================================
#  CONSENT ROUTE
# ================================

@participant_bp.route("/consent", methods=["POST"])
@limiter.limit("5 per minute")
def consent():
    trip = bot_tripwire()
    if trip:
        return trip

    ip = request.remote_addr or ""
    participant_id = str(uuid.uuid4())

    record = {
        "participant_id": participant_id,
        "timestamp": now_iso(),
        "consent_version": 1,
        "consent_given": True,
        "ip_hash": ip_hash(ip),
    }

    append_jsonl_secure(CONSENT_LOG, record)
    audit_record(
        actor=f"participant:{participant_id}",
        action="consent_given",
    )

    resp = make_response(jsonify({"ok": True, "participant_id": participant_id}))
    resp.set_cookie(
        "participant_id",
        participant_id,
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        samesite="Lax",
    )
    return resp



# ================================
#  SUBMIT RESULT
# ================================

@participant_bp.route("/submit_result", methods=["POST"])
@limiter.limit("20 per minute")
def submit_result():
    trip = bot_tripwire()
    if trip:
        return trip

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    session = request.get_json()

    # validation
    if isinstance(session, dict) and "events" in session:
        ok, msg = validate_behavioral_session(session)
        if not ok:
            return jsonify({"error": msg}), 400

    elif isinstance(session, dict) and "modules" in session:
        ok, msg = validate_cognitive_session(session)
        if not ok:
            return jsonify({"error": msg}), 400

    saved = save_session_result(session)

    # metrics
    if "events" in saved:
        metrics = compute_behavioral_metrics(saved)
        t = "behavioral"
    elif "modules" in saved:
        metrics = compute_cognitive_metrics(saved)
        t = "cognitive"
    else:
        metrics = {"note": "Unknown format"}
        t = "unknown"

    audit_record(
        actor=f"participant:{saved.get('participant_id','unknown')}",
        action="submit_result",
        subject=saved.get("task_id"),
        notes=f"type={t}",
    )

    return jsonify({"saved": saved, "metrics": metrics}), 201



# ================================
#  SELF-ERASE
# ================================

@participant_bp.route("/erase", methods=["POST"])
def erase_self():
    """Participant deletes their own ID from logs."""
    part = request.cookies.get("participant_id")
    if not part:
        return jsonify({"ok": False, "error": "no_participant_cookie"}), 400

    from hashlib import sha256
    h = sha256(part.encode()).hexdigest()[:16]
    replacement = f"anonymized:{h}"

    from project.app.utils.logging import AUDIT_LOG, CONSENT_LOG, DATA_LOG
    files = [AUDIT_LOG, CONSENT_LOG, DATA_LOG]

    total = 0
    for path in files:
        from project.app.utils.helpers import _anonymize_and_replace_in_file
        total += _anonymize_and_replace_in_file(path, part, replacement)

    audit_record(
        actor=f"participant:{part}",
        action="erase_self",
        subject="erase:self",
        extra={"changed_lines": total, "replacement": replacement},
    )

    return jsonify({"ok": True, "replacement": replacement, "changed": total})

# ================================
#  UNIVERSAL TASK LOADER
# ================================
from flask import render_template, request, jsonify, abort
import os
import json

@participant_bp.route("/task/<task_id>", methods=["GET"])
@limiter.limit("30 per minute")
def load_task(task_id):
    """
    Universal task loader.
    Loads task JSON from app/tasks/<task_id>.json
    Renders via cog_task.html
    """

    # ---- Consent check ----
    participant_id = request.cookies.get("participant_id")
    if not participant_id:
        return jsonify({"error": "no_consent"}), 401

    # ---- Task JSON path ----
    tasks_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "tasks")
    )
    task_file = os.path.join(tasks_dir, f"{task_id}.json")

    if not os.path.isfile(task_file):
        return jsonify({"error": "task_not_found", "task": task_id}), 404

    # ---- Load task ----
    with open(task_file, "r", encoding="utf-8") as f:
        task = json.load(f)

    # ---- Honeypot field ----
    hp_field = request.cookies.get("hp_field") or "hp_website"

    return render_template(
        "cog_task.html",
        task=task,
        participant_id=participant_id,
        task_id=task_id,
        hp_field=hp_field
    )

