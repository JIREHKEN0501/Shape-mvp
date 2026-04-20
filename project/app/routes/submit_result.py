# project/app/routes/submit_result.py

from flask import Blueprint, request, jsonify
import json
import time
import os

from project.app.services.tasks import get_task
from project.app.core.scoring import score_task_attempt

submit_result_bp = Blueprint("submit_result", __name__)


@submit_result_bp.route("/submit_result", methods=["POST"])
def submit_result():
    payload = request.get_json(force=True, silent=True) or {}

    task_id = payload.get("task_id")
    if not task_id:
        return jsonify({"ok": False, "error": "task_id is required"}), 400

    task = get_task(task_id, include_answer=True)
    if task is None:
        return jsonify({"ok": False, "error": "unknown task_id"}), 404

    metrics = score_task_attempt(
        task=task,
        submitted_answer=payload.get("answer"),
        started_at_ms=payload.get("started_at_ms"),
        latency_ms=payload.get("latency_ms"),
        retries=payload.get("retries"),
        hesitation=payload.get("hesitation"),
        submitted_at_ms=payload.get("submitted_at_ms"),
    )

    try:
        log_entry = {
            "ts": time.time(),
            "event_type": "task_attempt",
            "participant_id": payload.get("participant_id"),
            "task_id": task_id,
            "metrics": metrics,
        }
        os.makedirs("logs", exist_ok=True)
        with open("logs/data_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass

    return jsonify({"ok": True, "metrics": metrics}), 200
