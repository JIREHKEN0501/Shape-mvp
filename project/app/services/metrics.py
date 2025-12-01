# project/app/services/metrics.py

"""
Metrics helpers for sessions.
For now, only basic behavioral metrics are implemented.
"""


def compute_behavioral_metrics(session: dict):
    """
    Very simple behavioral metrics placeholder.
    For now:
      - event_count: number of events
    """
    events = session.get("events") or []
    if not isinstance(events, list):
        events = []

    return {
        "event_count": len(events),
    }

def evaluate_task_answer(session: dict):
    """
    Evaluate a single-task result payload.

    Expects:
      - session["task_id"]
      - session["answer"]

    Looks up the task in the catalog and compares the provided
    answer to the correct answer.
    """
    task_id = session.get("task_id")
    provided = session.get("answer")

    from project.app.services.tasks import get_task  # local import to avoid cycles

    if not task_id:
        return {
            "type": "single_task",
            "valid_task": False,
            "error": "missing_task_id",
        }

    task = get_task(task_id)
    if not task:
        return {
            "type": "single_task",
            "task_id": task_id,
            "valid_task": False,
            "error": "unknown_task_id",
        }

    correct = task.get("answer")
    # compare as strings to be forgiving
    provided_str = "" if provided is None else str(provided).strip()
    correct_str = "" if correct is None else str(correct).strip()
    is_correct = bool(correct_str) and (provided_str == correct_str)

    return {
        "type": "single_task",
        "task_id": task_id,
        "valid_task": True,
        "is_correct": is_correct,
        "provided_answer": provided,
        "correct_answer": correct,
        "category": task.get("category"),
        "difficulty": task.get("difficulty"),
    }

