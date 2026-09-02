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
from project.app.utils.experience_progression import load_experience_progression



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
    Return the authoritative next task for the participant's
    active experience.

    Canonical experience progression takes precedence over the
    general adaptive task selector. The adaptive selector remains
    available when no active experience progression exists.
    """
    try:
        cookie_participant_id = request.cookies.get("participant_id")
        experience_id = request.cookies.get("experience_id")

        # Do not allow a participant to request another participant's
        # canonical experience progression.
        if (
            cookie_participant_id
            and cookie_participant_id != participant_id
        ):
            return jsonify({
                "ok": False,
                "error": "participant_mismatch",
            }), 403

        # ---------------------------------------------------------
        # Canonical experience progression
        # ---------------------------------------------------------
        if experience_id:
            progression = load_experience_progression(
                experience_id
            )

            if progression is not None:
                # The progression history itself is authoritative.
                if progression.get("participant_id") != participant_id:
                    return jsonify({
                        "ok": False,
                        "error": "experience_not_owned",
                    }), 403

                if progression.get("status") == "invalid":
                    return jsonify({
                        "ok": False,
                        "error": "invalid_progression_history",
                    }), 409

                expected_task_id = progression.get("expected_task")

                # All canonical tasks have been completed.
                if expected_task_id is None:
                    return jsonify({
                        "ok": False,
                        "message": "Session complete",
                        "experience_complete": True,
                    }), 200

                task = get_task(
                    expected_task_id,
                    include_answer=False,
                )

                if task is None:
                    return jsonify({
                        "ok": False,
                        "error": "expected_task_not_found",
                        "task_id": expected_task_id,
                    }), 500

                return jsonify({
                    "ok": True,
                    "task": task,
                    "experience_id": experience_id,
                    "canonical_progression": True,
                }), 200

        # ---------------------------------------------------------
        # General adaptive fallback
        # ---------------------------------------------------------
        task = get_next_task_for_participant(participant_id)

        if not task.get("ok", True):
            return jsonify({
                "ok": False,
                "message": task.get(
                    "message",
                    "No tasks available"
                ),
            })

        return jsonify({
            "ok": True,
            "task": task,
        })

    except Exception:
        return jsonify({
            "ok": False,
            "error": "internal_error",
        }), 500

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

