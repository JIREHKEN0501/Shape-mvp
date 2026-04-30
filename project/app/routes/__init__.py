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
from project.app.helpers import audit_record, DATA_LOG, generate_participant_id

# bot detection stub
from project.app.security import bot_tripwire
from project.app.services.validators import (
    validate_behavioral_session,
    validate_cognitive_session,
)
from project.app.services.metrics import compute_behavioral_metrics, evaluate_task_answer
from project.app.services.sessions import save_session_result
from project.app.services.analytics import (
    generate_participant_summary,
    generate_global_summary,
)
from project.app.services.adaptive import suggest_next_task
from project.app.services.reports import build_participant_report
from project.app.services.tasks import (
    list_tasks,
    get_task,
    get_next_task_for_participant,
)
from project.app.core.scoring import score_task_attempt



# limiter import (adjust if you keep a different layout)
try:
    from project.app.extensions.limiter import limiter
except Exception:
    # fallback if you put limiter in a different location - keep code working
    limiter = None

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    from flask import jsonify
    return jsonify({"name": "Shape MVP", "status": "running", "version": "0.1.0", "docs": "/metadata", "health": "/status"}), 200

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

# -------------------------
# Public API routes restored from old app.py
# -------------------------

@main.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "ok", "version": "0.1.0"}), 200


@main.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Universal analytics dashboard (works for any industry).
    """
    return render_template("dashboard.html")


@main.route("/demo", methods=["GET"])
def demo():
    """
    Simple browser demo for adaptive tasks.
    """
    return render_template("demo.html")


@main.route("/erase/<participant_id>", methods=["DELETE"])
def erase_participant(participant_id):
    """Public erase endpoint (non-admin). Best-effort anonymization."""
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
        return jsonify({"ok": True, "participant_id": participant_id, "replacement": repl, "changed_lines": changed}), 200

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@main.route("/export/<participant_id>", methods=["GET"])
def export_participant(participant_id):
    """Public export endpoint."""
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

        return jsonify({"ok": True, "participant_id": participant_id, "matches": len(records), "records": records}), 200

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@main.route("/export/dashboard", methods=["GET"])
def export_dashboard():
    """Simplified dashboard export."""
    try:
        data = {"logs": {}}

        for fname in glob.glob("logs/*.jsonl"):
            with open(fname, "r", encoding="utf-8") as fh:
                data["logs"][fname] = [json.loads(line) for line in fh if line.strip()]

        return jsonify({"ok": True, "data": data}), 200

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@main.route("/tasks", methods=["GET"])
def tasks_index():
    """
    Return the task catalog as JSON.

    Optional query parameters:
      - category: filter by task category (e.g. 'memory_test', 'attention')
      - difficulty: filter by difficulty level (int)
    """
    # Base list (answers hidden by default)
    tasks = list_tasks()

    # Optional filters
    category = request.args.get("category")
    difficulty = request.args.get("difficulty", type=int)

    if category:
        tasks = [t for t in tasks if t.get("category") == category]

    if difficulty is not None:
        tasks = [t for t in tasks if t.get("difficulty") == difficulty]

    return jsonify({"ok": True, "count": len(tasks), "tasks": tasks}), 200


@main.route("/tasks/<task_id>", methods=["GET"])
def task_detail(task_id):
    """
    Return a single task by id, or 404 if not found.
    """
    task = get_task(task_id)
    if not task:
        return jsonify({"ok": False, "error": "task_not_found"}), 404
    return jsonify({"ok": True, "task": task}), 200


@main.route("/tasks/next/<participant_id>")
def tasks_next(participant_id):
    """
    Adaptive next-task endpoint.

    Uses the participant's history (from logs/data_log.jsonl) plus
    the current TASK_CATALOG to pick a suitable next task.
    """
    task = get_next_task_for_participant(participant_id)

    # 🚨 If no task available (end of session), return cleanly
    if not task.get("ok", True):
        return jsonify({
            "ok": False,
            "message": task.get("message", "No tasks available")
        })

    return jsonify({"ok": True, "task": task})


@main.route("/metrics/summary/<participant_id>", methods=["GET"])
def metrics_summary(participant_id):
    """
    Return a detailed metrics summary for a single participant.
    """
    summary = generate_participant_summary(participant_id)

    mode = request.args.get("mode", "education")

    return jsonify({
        "ok": True,
        "participant_id":participant_id,
        "summary": summary,
        "system_mode": mode
    }), 200

@main.route("/metrics/global", methods=["GET"])
def metrics_global():
    """
    Return a global metrics summary across all participants.
    """
    summary = generate_global_summary()
    status = 200 if summary.get("has_data") else 404
    return jsonify(summary), status


@main.route("/metrics/report/<participant_id>", methods=["GET"])
def metrics_report(participant_id):
    """
    Teacher-friendly participant report.
    """
    report = build_participant_report(participant_id)
    status = 200 if report.get("ok") else 404
    return jsonify(report), status


@main.route("/start_session", methods=["POST"])
@limiter.limit("10 per minute")
def start_session():
    """
    Create a new participant session.

    - Generates a participant_id if one is not provided.
    - Logs a 'session_start' event into DATA_LOG.
    - Returns the participant_id to the client.
    """
    body = request.get_json(silent=True) or {}

    participant_id = body.get("participant_id") or generate_participant_id()
    consent_version = body.get("consent_version")
    source = body.get("source", "unknown")

    task_id = body.get("task_id")
    task_def = None
    if task_id:
        # validate that the task exists in the catalog
        task_def = get_task(task_id)
        if not task_def:
            return jsonify({"ok": False, "error": "unknown_task_id", "task_id": task_id}), 400

    session_record = {
        "ts": time.time(),
        "event_type": "session_start",
        "participant_id": participant_id,
        "consent_version": consent_version,
        "source": source,
        "task_id": task_id,
        "task_meta": {
            "id": task_def.get("task_id") if task_def else None,
            "category": task_def.get("category") if task_def else None,
            "difficulty": task_def.get("difficulty") if task_def else None,
         } if task_def else None,
         "meta": body, 
    }

    try:
        os.makedirs("logs", exist_ok=True)
        with open(DATA_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(session_record) + "\n")

        try:
            audit_record(
                action="session_start",
                actor=f"participant:{participant_id}",
                subject=None,
                status="ok",
                extra={"source": source, "consent_version": consent_version},
            )
        except Exception:
            pass

        return jsonify(
            {
                "ok": True,
                "participant_id": participant_id,
                "task_id": task_id,
                "task": task_def,
            }
        ), 201

    except Exception as e:
        try:
            audit_record(
                action="session_start_error",
                actor="unknown",
                subject=None,
                status="error",
                extra={"error": str(e)},
            )
        except Exception:
            pass

        return jsonify({"ok": False, "error": "internal_error"}), 500

# ⚠️ LEGACY ROUTE — DISABLED
# This submit endpoint is deprecated.
# Replaced by governed registry-aware endpoint in:
# project/app/routes/submit_result.py
#@main.route("/submit_result", methods=["POST"])
#@limiter.limit("20 per minute")
#def submit_result():
#   trip = bot_tripwire()
#    if trip:
#        return trip

#    """
#   Accepts JSON body with a session object.
#   Automatically detects type (behavioral or cognitive)
#   and computes the correct metrics.
#    """
#    if not request.is_json:
#        return jsonify({"error": "Request must be JSON"}), 400

#    session = request.get_json()

    # -------------------------------------------
    # VALIDATION LAYER: reject malformed sessions
    # -------------------------------------------
#    if isinstance(session, dict) and "events" in session:
#        ok, msg = validate_behavioral_session(session)
#        if not ok:
#            return jsonify({"error": msg}), 400

#    elif isinstance(session, dict) and "modules" in session:
#        ok, msg = validate_cognitive_session(session)
#        if not ok:
#            return jsonify({"error": msg}), 400

    # -------------------------------------------

#    saved = save_session_result(session)

    # detect session type and compute metrics
#    if isinstance(saved, dict) and "events" in saved:
#        metrics = compute_behavioral_metrics(saved)
#        session_type = "behavioral"

#    elif isinstance(saved, dict) and "modules" in saved:
#        # TODO: add cognitive metrics when those are defined
#        metrics = {"note": "Cognitive session; metrics TBD"}
#        session_type = "cognitive"

#    elif isinstance(saved, dict) and saved.get("task_id") and "answer" in saved:
#        task = get_task(saved.get("task_id"), include_answer=True)

#        if not task:
#            metrics = {"error": "task_not_found"}
#        else:
 
#            metrics = score_task_attempt(
#                task=task,
#                submitted_answer=saved.get("answer"),
#                started_at_ms=saved.get("started_at_ms"),
#                submitted_at_ms=saved.get("submitted_at_ms"),
#            )

#        session_type = "single_task"

#    else:
#        metrics = {"note": "Unknown data type; no metrics computed"}
#        session_type = "unknown"

    # ✅ AUDIT LOG HERE (updated to new helper signature)
#    try:
#        audit_record(
#            action="submit_result",
#            actor=f"participant:{saved.get('participant_id', 'unknown')}",
#            subject=saved.get("task_id"),
#            status="ok",
#            extra={"session_type": session_type},
#        )
#    except Exception:
#       pass

#    return jsonify({"saved": saved, "metrics": metrics}), 201

