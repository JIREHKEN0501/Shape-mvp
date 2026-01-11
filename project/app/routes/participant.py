# project/app/routes/participant.py

import os, uuid, hashlib
import statistics
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
from project.app.tasks.task_registry import get_next_task
from project.app.tasks.task_registry import TASK_SEQUENCE
from project.app.tasks.task_registry import get_next_task
from project.app.utils.session_loader import load_session_by_id
from project.app.utils.session_loader import (
    get_schema_version,
    is_schema_supported,
)

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

def build_session_summary(saved: dict) -> dict:
    """
    Build a safe, numeric session summary from a completed session.
    Phase 8C-3: no inference, no labels.
    """

    participant_id = saved.get("participant_id")
    task_id = saved.get("task_id")
    modules = saved.get("modules", [])

    questions = [
        q
        for m in modules
        for q in m.get("questions", [])
    ]

    total_questions = len(questions)
    correct_answers = sum(1 for q in questions if q.get("correct") is True)

    times = [q.get("time_taken_seconds", 0) for q in questions if q.get("time_taken_seconds") is not None]
    total_time = sum(times)

    summary = {
        "participant_id": participant_id,
        "session_complete": saved.get("session_complete", False),

        "tasks_completed": 1,
        "task_ids": [task_id] if task_id else [],

        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "accuracy": (correct_answers / total_questions) if total_questions else None,

        "total_time_seconds": round(total_time, 2),
        "avg_time_per_question": round(total_time / total_questions, 2) if total_questions else None,
        "min_time_per_question": round(min(times), 2) if times else None,
        "max_time_per_question": round(max(times), 2) if times else None,
        "decision_time_std": round(statistics.stdev(times), 2) if len(times) > 1 else 0.0,

        "summary_validity": {
            "tasks_observed": 1,
            "questions_observed": total_questions,
            "confidence_level": "low"
        },

        "completed_at": now_iso()
    }

    return summary


def build_cognitive_session_summary(session: dict) -> dict:
    """
    Build safe, descriptive metrics for a cognitive task session.
    Non-diagnostic. Non-inferential.
    """

    modules = session.get("modules", [])
    questions = []

    for m in modules:
        questions.extend(m.get("questions", []))

    total = len(questions)
    if total == 0:
        return {
            "total_questions": 0,
            "accuracy_ratio": None,
            "avg_time_per_question": None,
            "median_time_per_question": None,
            "time_variance": None,
            "speed_accuracy_profile": "insufficient_data",
        }

    correct_count = 0
    for q in questions:
        correct = q.get("correct")
        user_answer = q.get("user_answer")

        if (
            correct is not None
            and user_answer is not None
            and str(correct).strip() == str(user_answer).strip()
        ):
            correct_count += 1

    times = [
        q["time_taken_seconds"]
        for q in questions
        if isinstance(q, dict)
        and isinstance(q.get("time_taken_seconds"), (int, float))
    ]

    avg_time = round(statistics.mean(times), 3) if len(times) >= 1 else None
    median_time = round(statistics.median(times), 3) if len(times) >= 1 else None
    variance = round(statistics.pvariance(times), 3) if len(times) >= 2 else 0.0

    accuracy_ratio = round(correct_count / total, 3)

    # --- Speed–Accuracy Profile (simple & explainable) ---
    if avg_time is None:
        profile = "insufficient_data"
    elif accuracy_ratio >= 0.75 and avg_time <= 6:
        profile = "fast_accurate"
    elif accuracy_ratio >= 0.75:
        profile = "slow_accurate"
    elif avg_time <= 6:
        profile = "fast_inaccurate"
    else:
        profile = "slow_inaccurate"

    return {
        "total_questions": total,
        "accuracy_ratio": accuracy_ratio,
        "avg_time_per_question": round(avg_time, 3) if avg_time is not None else None,
        "median_time_per_question": round(median_time, 3) if median_time is not None else None,
        "time_variance": round(variance, 3),
        "speed_accuracy_profile": profile,
    }

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

@participant_bp.route("/consent", methods=["GET", "POST"])
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


# NOTE:
# A "session" represents a single task interaction only.
# It is contextual, immutable once saved, and must not be
# interpreted as a stable personal attribute.

# ================================
#  SUBMIT RESULT
# ================================

@participant_bp.route("/participant/submit_result", methods=["POST"])
@limiter.limit("20 per minute")
def submit_result():

    trip = bot_tripwire()
    if trip:
        return trip

    if not request.is_json:
        print("❌ NOT JSON")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    participant_id = request.cookies.get("participant_id")
    if not participant_id:
        return jsonify({"error": "no_participant_cookie"}), 401

    data["participant_id"] = participant_id
    session = data

    # ---- Phase 9D-1: session identity (ADD THIS BLOCK) ----
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    # validation
    if isinstance(session, dict) and "events" in session:
        ok, msg = validate_behavioral_session(session)
        if not ok:
            return jsonify({"error": msg}), 400

    elif isinstance(session, dict) and "modules" in session:
        ok, msg = validate_cognitive_session(session)
        if not ok:
            return jsonify({"error": msg}), 400

    # ---- Phase 9D-4-B: session metadata (non-identifying) ----
    session.setdefault("schema_version", "1.0")

    # Task versioning (safe default)
    if "task_version" not in session:
        session["task_version"] = "v1"

    # Coarse client context (NOT fingerprinting)
    session["client_context"] = {
        "user_agent_family": (
            "mobile" if "Mobile" in (request.headers.get("User-Agent") or "")
            else "desktop"
        ),
        "timezone_offset_min": request.headers.get("X-Timezone-Offset")
    }

    saved = save_session_result(session)
 
    # ---- Phase 8C-1: session completion detection ----
    task_id = saved.get("task_id")
    is_complete = get_next_task(task_id) is None

    saved["session_complete"] = is_complete

    # ---- Phase 9A-2: build cognitive session summary ----
    session_summary = None
    if is_complete is True and "modules" in saved:
        session_summary = build_cognitive_session_summary(saved)

    # Safety: summary must NEVER exist if session is not complete
    if session_summary is not None and is_complete is not True:
        session_summary = None

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
        notes=f"type={t}, complete={is_complete}",
    )

    return jsonify({
        "saved": saved,
        "metrics": metrics,
        "session_complete": is_complete,
        "session_summary": session_summary
    }), 201
   

# ================================
#  PARTICIPANT SESSION RETRIEVAL
#  (summary-first, privacy-safe)
# ================================

@participant_bp.route("/participant/session/<session_id>", methods=["GET"])
@limiter.limit("10 per minute")
def get_participant_session(session_id):
    participant_id = request.cookies.get("participant_id")
    if not participant_id:
        return jsonify({"error": "no_participant_cookie"}), 401

    session = load_session_by_id(session_id)
    if not session:
        return jsonify({"error": "session_not_found"}), 404

    # ---- Phase 9D-4-C-3: schema guard ----
    schema_version = get_schema_version(session)
    if not is_schema_supported(schema_version):
        return jsonify({
            "error": "unsupported_schema_version",
            "schema_version": schema_version
        }), 400

    # Ownership check
    if session.get("participant_id") != participant_id:
        return jsonify({"error": "unauthorized"}), 403

    # Summary-first response
    response = {
        "session_id": session.get("session_id"),
        "task_id": session.get("task_id"),
        "saved_ts": session.get("saved_ts"),
        "metrics": None,
        "session_summary": None,
    }

    # Metrics (safe)
    if "modules" in session:
        response["metrics"] = compute_cognitive_metrics(session)
    elif "events" in session:
        response["metrics"] = compute_behavioral_metrics(session)

    # Summary only if session was complete
    if session.get("session_complete") is True:
        if "modules" in session:
            response["session_summary"] = build_cognitive_session_summary(session)

    # 🔐 Audit log (participant self-access)
    audit_record(
        actor=f"participant:{participant_id}",
        action="retrieve_session",
        subject=session_id,
        notes="participant_self_access_summary_only",
    )

    return jsonify(response), 200


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

    # ---- Phase 8B-2-A: progression guard ----
    if task_id not in TASK_SEQUENCE:
        return jsonify({
            "error": "invalid_task_sequence",
            "task": task_id
        }), 400

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

    next_task_id = get_next_task(task_id)
    is_last_task = next_task_id is None

    return render_template(
        "cog_task.html",
        task=task,
        participant_id=participant_id,
        task_id=task_id,
        next_task_id=next_task_id,
        is_last_task=is_last_task,
        hp_field=hp_field
    )

