# project/app/utils/experience_progression.py

import json
from pathlib import Path

from project.app.tasks.task_registry import TASK_SEQUENCE
from project.app.utils.logging import LOG_DIR
from project.app.utils.storage import load_session_by_id
from project.app.utils.experience_loader import (
    load_experience_by_id,
    resolve_experience_authorization,
)

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


def _resolve_adaptive_transition(
    experience_id: str,
    event: dict,
) -> tuple[str, str | None]:
    """
    Resolve whether an adaptive transition event may affect
    progression state.

    Returns:
        ("ignore", None)
            for bounded/legacy experiences.

        ("apply", None)
            for explicitly authorized adaptive experiences.

        ("reject", error)
            for malformed or unauthorized adaptive transitions.
    """
    if not isinstance(event, dict):
        return "reject", "invalid_progression_history"

    experience = load_experience_by_id(experience_id)

    # Legacy experiences without an experience record are treated
    # as bounded for progression replay.
    if experience is None:
        return "ignore", None

    mode_state = resolve_experience_authorization(experience)

    if mode_state.get("mode") == "bounded":
        return "ignore", None

    if mode_state.get("authorized") is not True:
        return "reject", "adaptive_transition_not_authorized"

    from_task_id = event.get("from_task_id")
    to_task_id = event.get("to_task_id")

    if not from_task_id or not to_task_id:
        return "reject", "invalid_progression_history"

    return "apply", None


def load_experience_progression(
    experience_id: str,
) -> dict | None:
    """
    Derive the current progression state for an experience
    from its append-only event history.

    Bounded experiences use TASK_SEQUENCE as their authoritative
    progression order.

    Authorized adaptive experiences use explicit adaptive_transition
    events to establish the next expected task. Transition events do
    not count a task as completed; only task_completed events do that.
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

    experience = load_experience_by_id(experience_id)

    # Legacy experiences without an experience record are treated
    # as bounded for progression replay.
    if experience is None:
        mode = "bounded"
        adaptive_authorized = False
    else:
        mode_state = resolve_experience_authorization(experience)
        mode = mode_state.get("mode", "bounded")
        adaptive_authorized = (
            mode_state.get("authorized") is True
        )

    completed_tasks = []
    progression_error = None
    experience_completed = False
    expected_task = None

    if mode == "adaptive":
        expected_task = TASK_SEQUENCE[0]
    else:
        expected_task = None

    for event in events:
        event_type = event.get("event")

        if event_type == "experience_completed":
            if mode == "bounded":
                # Bounded completion remains tied to the canonical
                # fixed sequence.
                if completed_tasks != TASK_SEQUENCE:
                    progression_error = (
                        "invalid_progression_history"
                    )
                    break

            elif mode == "adaptive":
                # Adaptive completion is not yet governed by a
                # completion policy. Until that policy exists,
                # completion events are invalid rather than inferred.
                if not adaptive_authorized:
                    progression_error = (
                        "adaptive_transition_not_authorized"
                    )
                    break

                if expected_task is not None:
                    progression_error = (
                        "invalid_progression_history"
                    )
                    break

            # A second completion event is invalid.
            if experience_completed:
                progression_error = (
                    "invalid_progression_history"
                )
                break

            experience_completed = True
            expected_task = None
            continue

        if event_type == "adaptive_transition":
            transition_status, transition_error = (
                _resolve_adaptive_transition(
                    experience_id,
                    event,
                )
            )

            if transition_status == "reject":
                progression_error = transition_error
                break

            if transition_status == "ignore":
                continue

            from_task_id = event.get("from_task_id")
            to_task_id = event.get("to_task_id")

            if from_task_id != (
                completed_tasks[-1]
                if completed_tasks
                else None
            ):
                progression_error = (
                    "invalid_progression_history"
                )
                break

            # A transition establishes the next expected task.
            # It does NOT mean that task has already been completed.
            if expected_task is not None:
                progression_error = (
                    "invalid_progression_history"
                )
                break

            if to_task_id in completed_tasks:
                progression_error = (
                    "invalid_progression_history"
                )
                break

            expected_task = to_task_id
            continue

        if event_type != "task_completed":
            continue

        # No task events are allowed after experience completion.
        if experience_completed:
            progression_error = (
                "invalid_progression_history"
            )
            break

        task_id = event.get("task_id")

        if not task_id:
            progression_error = (
                "invalid_progression_history"
            )
            break

        session_id = event.get("session_id")

        if not session_id:
            progression_error = (
                "invalid_progression_history"
            )
            break

        session = load_session_by_id(session_id)

        if session is None:
            progression_error = (
                "invalid_progression_history"
            )
            break

        if (
            session.get("participant_id")
            != event.get("participant_id")
            or session.get("experience_id")
            != event.get("experience_id")
            or session.get("task_id") != task_id
            or session.get("session_complete") is not True
        ):
            progression_error = (
                "invalid_progression_history"
            )
            break

        if task_id in completed_tasks:
            progression_error = (
                "invalid_progression_history"
            )
            break

        if mode == "adaptive":
            # In adaptive mode, the task must be the task established
            # by the most recent authorized transition.
            if expected_task != task_id:
                progression_error = (
                    "invalid_progression_history"
                )
                break

            completed_tasks.append(task_id)
            expected_task = None
            continue

        # Bounded mode retains the existing canonical sequence
        # validation.
        next_expected_index = len(completed_tasks)

        if next_expected_index >= len(TASK_SEQUENCE):
            progression_error = (
                "invalid_progression_history"
            )
            break

        expected_sequence_task = TASK_SEQUENCE[
            next_expected_index
        ]

        if task_id != expected_sequence_task:
            progression_error = (
                "invalid_progression_history"
            )
            break

        completed_tasks.append(task_id)

    if progression_error is not None:
        return {
            "experience_id": created.get("experience_id"),
            "participant_id": created.get("participant_id"),
            "sequence_version": created.get(
                "sequence_version"
            ),
            "mode": mode,
            "adaptive_authorized": adaptive_authorized,
            "status": "invalid",
            "completed_tasks": completed_tasks,
            "expected_task": None,
            "error": progression_error,
        }

    if mode == "bounded":
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
        "mode": mode,
        "adaptive_authorized": adaptive_authorized,
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
