# project/app/utils/experience_progression.py

import json
from pathlib import Path

from project.app.tasks.task_registry import TASK_SEQUENCE
from project.app.utils.logging import LOG_DIR
from project.app.utils.storage import load_session_by_id


EXPERIENCE_EVENTS_LOG = str(
    Path(LOG_DIR) / "experience_events.jsonl"
)


def _load_events(experience_id: str) -> list[dict]:
    """Load valid events for one experience in append order."""
    if not experience_id:
        return []

    events = []

    try:
        with open(
            EXPERIENCE_EVENTS_LOG,
            "r",
            encoding="utf-8",
        ) as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if event.get("experience_id") == experience_id:
                    events.append(event)

    except FileNotFoundError:
        return []

    return events


def load_experience_progression(
    experience_id: str,
) -> dict | None:
    """
    Derive the current progression state for an experience
    from its append-only event history.
    """
    events = _load_events(experience_id)

    if not events:
        return None

    created = next(
        (
            event
            for event in events
            if event.get("event") == "experience_created"
        ),
        None,
    )

    if created is None:
        return None

    completed_tasks = []
    progression_error = None

    for event in events:
        if event.get("event") != "task_completed":
            continue

        task_id = event.get("task_id")

        if not task_id:
            progression_error = "invalid_progression_history"
            break

        session_id = event.get("session_id")

        if not session_id:
            progression_error = "invalid_progression_history"
            break

        session = load_session_by_id(session_id)

        if session is None:
            progression_error = "invalid_progression_history"
            break

        if task_id in completed_tasks:
            progression_error = "invalid_progression_history"
            break

        next_expected_index = len(completed_tasks)

        if next_expected_index >= len(TASK_SEQUENCE):
            progression_error = "invalid_progression_history"
            break

        expected_task = TASK_SEQUENCE[next_expected_index]

        if task_id != expected_task:
            progression_error = "invalid_progression_history"
            break

        completed_tasks.append(task_id)
    experience_completed = any(
        event.get("event") == "experience_completed"
        for event in events
    )

    if progression_error is not None:
        return {
            "experience_id": created.get("experience_id"),
            "participant_id": created.get("participant_id"),
            "sequence_version": created.get(
                "sequence_version"
            ),
            "status": "invalid",
            "completed_tasks": completed_tasks,
            "expected_task": None,
            "error": progression_error,
        }

    expected_task = None

    if not experience_completed:
        for task_id in TASK_SEQUENCE:
            if task_id not in completed_tasks:
                expected_task = task_id
                break

    return {
        "experience_id": created.get("experience_id"),
        "participant_id": created.get("participant_id"),
        "sequence_version": created.get(
            "sequence_version"
        ),
        "status": (
            "completed"
            if experience_completed
            else "active"
        ),
        "completed_tasks": completed_tasks,
        "expected_task": expected_task,
    }

def validate_task_progression(
    experience_id: str,
    submitted_task_id: str,
) -> dict:
    """
    Validate a submitted task against the task currently
    expected by the experience progression state.
    """
    state = load_experience_progression(experience_id)

    if state is None:
        return {
            "valid": False,
            "error": "experience_not_found",
            "expected_task": None,
        }

    if state.get("status") == "invalid":
        return {
            "valid": False,
            "error": state.get(
                "error",
                "invalid_progression_history",
            ),
            "expected_task": None,
        }

    if state["status"] == "completed":
        return {
            "valid": False,
            "error": "experience_not_active",
            "expected_task": None,
        }

    expected_task = state["expected_task"]

    if submitted_task_id != expected_task:
        return {
            "valid": False,
            "error": "task_not_expected",
            "expected_task": expected_task,
        }

    return {
        "valid": True,
        "error": None,
        "expected_task": expected_task,
    }
