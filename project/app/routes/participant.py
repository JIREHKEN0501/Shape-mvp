# project/app/routes/participant.py

import uuid, hashlib
from flask import (
    Blueprint, request, jsonify, render_template,
    make_response
)
from functools import wraps

from project.app.routes.security import bot_tripwire
from project.app.utils.logging import (
    append_jsonl_secure, audit_record,
    CONSENT_LOG, EXPERIENCE_LOG, DATA_LOG
)
from project.app.utils.helpers import now_iso, ip_hash
from project.app.utils.metrics import (
    compute_behavioral_metrics,
    compute_cognitive_metrics,
)
from project.app.extensions.limiter import limiter
from project.app.tasks.task_registry import get_next_task
from project.app.tasks.task_registry import TASK_SEQUENCE
from project.app.services.tasks import get_task
from project.app.utils.session_loader import load_session_by_id
from project.app.utils.session_loader import (
    get_schema_version,
    is_schema_supported,
)
from project.app.utils.experience_loader import (
    load_experience_by_id,
    experience_belongs_to_participant,
    is_experience_active,
)
from project.app.utils.experience_progression import (
    load_experience_progression,
)
from project.app.utils.experience_lifecycle import (
    complete_experience,
    create_experience,
)
from project.app.utils.summary_adapter import build_session_summary
from project.app.utils.summary_validator import validate_summary_schema
from project.app.utils.session_summaries import build_cognitive_session_summary
from project.app.services.experience_progression_service import (
    complete_task_progression,
    _append_experience_event,
)
from project.app.services.analytics import (
    generate_experience_summary,
)
from project.app.services.experience_insights import (
    generate_experience_insights,
)

participant_bp = Blueprint("participant", __name__)


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
            for k in ["question_id", "user_answer", "time_taken_seconds"]:
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

@participant_bp.route("/consent", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def consent():
    trip = bot_tripwire()
    if trip:
        return trip

    ip = request.remote_addr or ""
    participant_id = str(uuid.uuid4())
    experience_id = str(uuid.uuid4())

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

    experience_record = {
        "experience_id": experience_id,
        "participant_id": participant_id,
        "status": "active",
        "sequence_version": "1.0",
        "created_ts": now_iso(),
        "completed_ts": None,
    }

    append_jsonl_secure(
        EXPERIENCE_LOG,
        experience_record,
    )

    experience_created_event = {
        "event": "experience_created",
        "event_version": "1.0",
        "experience_id": experience_id,
        "participant_id": participant_id,
        "sequence_version": "1.0",
        "ts": experience_record["created_ts"],
    }

    _append_experience_event(
        experience_created_event
    )
    resp = make_response(jsonify({"ok": True, "participant_id": participant_id, "experience_id": experience_id,}))
    resp.set_cookie(
        "participant_id",
        participant_id,
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        samesite="Lax",
    )

    resp.set_cookie(
        "experience_id",
        experience_id,
        max_age=60 * 60 * 24,
        httponly=True,
        samesite="Lax",
    )

    return resp

# ================================
# START NEW EXPERIENCE
# ================================

@participant_bp.route(
    "/participant/experience/new",
    methods=["POST"],
)
@limiter.limit("5 per minute")
def start_new_experience():

    participant_id = request.cookies.get(
        "participant_id"
    )

    if not participant_id:
        return jsonify({
            "error": "no_participant_cookie"
        }), 401

    experience = create_experience(
        participant_id
    )

    if experience is None:
        return jsonify({
            "error": "experience_creation_failed"
        }), 500

    response = jsonify({
        "ok": True,
        "participant_id": participant_id,
        "experience_id": experience["experience_id"],
        "next_task_id": TASK_SEQUENCE[0],
    })

    response.set_cookie(
        "experience_id",
        experience["experience_id"],
        max_age=60 * 60 * 24,
        httponly=True,
        samesite="Lax",
    )

    audit_record(
        actor=f"participant:{participant_id}",
        action="start_new_experience",
        subject=experience["experience_id"],
        notes="participant_started_new_experience",
    )

    return response, 201


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

    experience_id = request.cookies.get("experience_id")
    if not experience_id:
        return jsonify({"error": "no_experience_cookie"}), 401

    experience = load_experience_by_id(experience_id)

    if experience is None:
        return jsonify({"error": "experience_not_found"}), 404

    if not experience_belongs_to_participant(
        experience,
        participant_id,
    ):
        audit_record(
            actor=f"participant:{participant_id}",
            action="experience_membership_rejected",
            subject=experience_id,
            status="rejected",
            notes="experience_does_not_belong_to_participant",
        )
        return jsonify({"error": "experience_not_owned"}), 403

    if not is_experience_active(experience):
        return jsonify({"error": "experience_not_active"}), 409

    data["participant_id"] = participant_id
    data["experience_id"] = experience_id
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

    # ---- Phase C: append-only task progression ----

    task_id = session.get("task_id")

    progression_result = complete_task_progression(
        experience_id=experience_id,
        participant_id=participant_id,
        session=session,
    )

    if not progression_result.get("ok"):
        error = progression_result.get(
            "error",
            "progression_failed",
        )

        if error == "task_not_expected":
            audit_record(
                actor=f"participant:{participant_id}",
                action="task_progression_rejected",
                subject=experience_id,
                status="rejected",
                notes=(
                    f"submitted_task={task_id}, "
                    f"expected_task="
                    f"{progression_result.get('expected_task')}"
                ),
            )

            return jsonify({
                "error": error,
                "expected_task": progression_result.get(
                    "expected_task"
                ),
            }), 409

        return jsonify({
            "error": error,
        }), 409

    saved = progression_result["saved_session"]

    is_complete = True
    next_task_id = progression_result.get(
        "next_task_id"
    )

    final_task = progression_result.get(
        "final_task",
        False,
    )

    experience_complete = False

    # Experience lifecycle remains separate from task progression.
    if final_task:
        completed_experience = complete_experience(
            experience_id,
            participant_id,
        )

        if completed_experience is None:
            audit_record(
                actor="system",
                action="experience_completion_failed",
                subject=experience_id,
                status="error",
                notes=(
                    "final_task_submitted_but_"
                    "experience_transition_failed"
                ),
            )
        else:
            experience_complete = True

    # ---- Phase 11A-3: unified session summary adapter ----
    session_summary = build_session_summary(saved)

    # ---- Phase 12A-4: fail-closed summary enforcement ----
    if session_summary is not None:
        summary_valid, _ = validate_summary_schema(session_summary)

        if not summary_valid:
            audit_record(
                actor="system",
                action="drop_invalid_summary",
                subject=saved.get("session_id"),
                notes="summary_schema_validation_failed"
            )
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
        notes=(
            f"type={t}, "
            f"session_complete={is_complete}, "
            f"experience_complete={experience_complete}"
        ),
    )

    return jsonify({
        "saved": saved,
        "metrics": metrics,
        "session_complete": is_complete,
        "experience_complete": experience_complete,
        "next_task_id": next_task_id,
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
# PARTICIPANT EXPERIENCE SUMMARY
# (experience-scoped, privacy-safe)
# ================================

@participant_bp.route(
    "/participant/experience/<experience_id>/summary",
    methods=["GET"],
)
@limiter.limit("10 per minute")
def get_participant_experience_summary(experience_id):

    participant_id = request.cookies.get("participant_id")

    if not participant_id:
        return jsonify({
            "error": "no_participant_cookie"
        }), 401

    experience = load_experience_by_id(experience_id)

    if experience is None:
        return jsonify({
            "error": "experience_not_found"
        }), 404

    if not experience_belongs_to_participant(
        experience,
        participant_id,
    ):
        return jsonify({
            "error": "unauthorized"
        }), 403

    if experience.get("status") != "completed":
        return jsonify({
            "error": "experience_not_completed"
        }), 409

    summary = generate_experience_summary(
        experience_id
    )

    if not summary.get("has_data"):
        return jsonify({
            "error": summary.get(
                "message",
                "experience_summary_unavailable",
            )
        }), 404

    required_summary_fields = {
        "experience_id",
        "has_data",
        "total_questions",
        "objective_questions",
        "decision_observations",
        "correct_objective_questions",
        "objective_accuracy",
        "tasks",
        "sessions",
        "attempts",
    }

    if not required_summary_fields.issubset(summary):
        return jsonify({
            "error": "invalid_experience_summary"
        }), 422

    insights = generate_experience_insights(
        summary
    )

    response = dict(summary)
    response["insights"] = insights

    audit_record(
        actor=f"participant:{participant_id}",
        action="retrieve_experience_summary",
        subject=experience_id,
        notes="participant_self_access_experience_summary",
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
    Universal participant task loader.
    Loads the client-safe canonical task through the task service
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

    # ---- Experience context ----
    experience_id = request.cookies.get("experience_id")
    if not experience_id:
        return jsonify({"error": "no_experience_cookie"}), 401

    experience = load_experience_by_id(experience_id)
    if experience is None:
        return jsonify({"error": "experience_not_found"}), 404

    if not experience_belongs_to_participant(
        experience,
        participant_id,
    ):
        return jsonify({"error": "experience_not_owned"}), 403

    if not is_experience_active(experience):
        return jsonify({"error": "experience_not_active"}), 409

    progression = load_experience_progression(
        experience_id
    )

    if progression is None:
        return jsonify({
            "error": "progression_state_unavailable"
        }), 409

    if progression.get("status") == "invalid":
        return jsonify({
            "error": progression.get(
                "error",
                "invalid_progression_history",
            )
        }), 409

    expected_task = progression.get("expected_task")

    if expected_task is None:
        return jsonify({
            "error": "experience_complete"
        }), 409

    if task_id != expected_task:
        return jsonify({
            "error": "task_not_expected",
            "expected_task": expected_task,
        }), 409

    # ---- Load client-safe canonical task ----
    task = get_task(task_id, include_answer=False)

    if task is None:
        return jsonify({
            "error": "task_not_found",
            "task": task_id,
        }), 404

    # ---- Honeypot field ----
    hp_field = request.cookies.get("hp_field") or "hp_website"

    next_task_id = get_next_task(task_id)
    is_last_task = next_task_id is None

    return render_template(
        "cog_task.html",
        task=task,
        participant_id=participant_id,
        task_id=task_id,
        experience_id=experience_id,
        next_task_id=next_task_id,
        is_last_task=is_last_task,
        hp_field=hp_field
    )
