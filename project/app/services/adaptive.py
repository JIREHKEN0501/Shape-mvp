# project/app/services/adaptive.py

"""
Simple adaptive task selection engine.

Uses:
- task catalog (project/app/services/tasks)
- participant summary (project/app/services/analytics)

Strategies:
- If participant has no attempts -> pick an easy starter task.
- Otherwise:
    - Use overall accuracy and last attempted task to adjust difficulty.
"""

from typing import Dict, Any, List, Optional

from project.app.services.tasks import list_tasks, get_task
from project.app.services.analytics import generate_participant_summary


def _pick_initial_task(tasks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Pick a default starter task:
      - difficulty == 1 if available
      - otherwise the first task in the catalog.
    """
    if not tasks:
        return None

    # prefer easiest tasks
    easy = [t for t in tasks if t.get("difficulty") == 1]
    if easy:
        # you could also filter by category here, e.g. pattern_recognition
        # but for now we just take the first easy one.
        return sorted(easy, key=lambda t: str(t.get("task_id") or t.get("id") or ""))[0]

    # fallback: just take the first in sorted order
    return sorted(tasks, key=lambda t: str(t.get("task_id") or t.get("id") or ""))[0]


def suggest_next_task(participant_id: str) -> Dict[str, Any]:
    """
    Suggest the next task for a participant based on their history.

    Returns a dict:
      {
        "ok": True/False,
        "reason": "...",
        "strategy": "initial" | "adaptive",
        "participant_id": "...",
        "global_accuracy": float or None,
        "base_task_id": "...",
        "target_difficulty": int or None,
        "task": { ... }  # the chosen task, if any
      }
    """
    tasks = list_tasks()
    if not tasks:
        return {
            "ok": False,
            "reason": "no_tasks_available",
            "participant_id": participant_id,
            "task": None,
        }

    summary = generate_participant_summary(participant_id)

    # case 1: no data at all for this participant
    if not summary.get("has_data") or summary.get("total_attempts", 0) == 0:
        starter = _pick_initial_task(tasks)
        return {
            "ok": starter is not None,
            "reason": "initial_task" if starter else "no_tasks_available",
            "strategy": "initial",
            "participant_id": participant_id,
            "global_accuracy": None,
            "base_task_id": None,
            "target_difficulty": starter.get("difficulty") if starter else None,
            "task": starter,
        }

    # case 2: we have some history -> adaptive
    accuracy = summary.get("accuracy")
    by_task = summary.get("by_task") or {}

    # find last attempted task via last_ts
    last_task_id = None
    last_ts = None
    for task_id, entry in by_task.items():
        ts = entry.get("last_ts")
        if ts is None:
            continue
        if last_ts is None or ts > last_ts:
            last_ts = ts
            last_task_id = task_id

    base_task = get_task(last_task_id) if last_task_id else None
    base_diff = base_task.get("difficulty") if base_task else 1
    base_cat = base_task.get("category") if base_task else None

    # decide target difficulty
    if accuracy is None:
        target_diff = base_diff
    elif accuracy >= 0.8:
        target_diff = (base_diff or 1) + 1
    elif accuracy <= 0.5 and (base_diff or 1) > 1:
        target_diff = (base_diff or 1) - 1
    else:
        target_diff = base_diff or 1

    # candidate tasks by category + difficulty
    candidates = [
        t
        for t in tasks
        if (base_cat is None or t.get("category") == base_cat)
        and t.get("difficulty") == target_diff
    ]

    # if none in same category, relax category constraint
    if not candidates:
        candidates = [t for t in tasks if t.get("difficulty") == target_diff]

    # if still none, just fall back to initial strategy
    if not candidates:
        starter = _pick_initial_task(tasks)
        return {
            "ok": starter is not None,
            "reason": "fallback_to_initial",
            "strategy": "initial",
            "participant_id": participant_id,
            "global_accuracy": accuracy,
            "base_task_id": last_task_id,
            "target_difficulty": starter.get("difficulty") if starter else None,
            "task": starter,
        }

    # avoid repeating the exact same task if we have options
    non_repeat = [t for t in candidates if t.get("task_id") != last_task_id]
    chosen = (non_repeat or candidates)[0]

    return {
        "ok": True,
        "reason": "adaptive_selection",
        "strategy": "adaptive",
        "participant_id": participant_id,
        "global_accuracy": accuracy,
        "base_task_id": last_task_id,
        "target_difficulty": target_diff,
        "task": chosen,
    }

