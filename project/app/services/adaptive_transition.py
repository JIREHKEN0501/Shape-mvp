"""
Authorized adaptive transition execution.

An adaptive transition changes the progression path of an explicitly
authorized adaptive experience.

This service does not perform task selection. The routing layer selects
the candidate; the eligibility boundary determines whether it may execute;
this service persists the authorized transition.
"""

from typing import Any, Dict

from project.app.services.adaptive_task_eligibility import (
    resolve_adaptive_task_eligibility,
)
from project.app.services.experience_authorization import (
    resolve_adaptive_authorization,
)
from project.app.utils.experience_progression import (
    load_experience_progression,
)
from project.app.services.experience_progression_service import (
    _append_experience_event,
    _experience_lock,
)


def execute_adaptive_transition(
    experience_id: str,
    participant_id: str,
    from_task_id: str,
    to_task_id: str,
) -> Dict[str, Any]:
    """
    Persist an authorized adaptive transition.

    The transition is valid only when:

    - the experience exists;
    - the participant owns the experience;
    - adaptive execution is explicitly authorized;
    - the candidate task is eligible;
    - progression is valid;
    - from_task_id is the task currently completed in progression;
    - the candidate is not already completed in this experience.

    This function does not select tasks.
    """

    if not experience_id:
        return {
            "ok": False,
            "error": "experience_id_required",
        }

    if not participant_id:
        return {
            "ok": False,
            "error": "participant_id_required",
        }

    if not from_task_id:
        return {
            "ok": False,
            "error": "from_task_id_required",
        }

    if not to_task_id:
        return {
            "ok": False,
            "error": "to_task_id_required",
        }

    with _experience_lock(experience_id):
        authorization = resolve_adaptive_authorization(
            participant_id,
            experience_id,
        )

        if authorization.get("authorized") is not True:
            return {
                "ok": False,
                "error": authorization.get(
                    "reason",
                    "adaptive_transition_not_authorized",
                ),
            }

        progression = load_experience_progression(
            experience_id
        )

        if progression is None:
            return {
                "ok": False,
                "error": "experience_not_found",
            }

        if progression.get("status") == "invalid":
            return {
                "ok": False,
                "error": progression.get(
                    "error",
                    "invalid_progression_history",
                ),
            }

        if progression.get("participant_id") != participant_id:
            return {
                "ok": False,
                "error": "experience_not_owned",
            }

        expected_from_task = (
            progression.get("completed_tasks", [])[-1]
            if progression.get("completed_tasks")
            else None
        )

        if from_task_id != expected_from_task:
            return {
                "ok": False,
                "error": "invalid_adaptive_transition_source",
                "expected_from_task": expected_from_task,
            }

        eligibility = resolve_adaptive_task_eligibility(
            experience_id,
            to_task_id,
        )

        if eligibility.get("eligible") is not True:
            return {
                "ok": False,
                "error": eligibility.get(
                    "reason",
                    "adaptive_task_not_eligible",
                ),
            }

        event = {
            "event": "adaptive_transition",
            "event_version": "1.0",
            "experience_id": experience_id,
            "participant_id": participant_id,
            "sequence_version": progression.get(
                "sequence_version",
                "1.0",
            ),
            "from_task_id": from_task_id,
            "to_task_id": to_task_id,
        }

        try:
            _append_experience_event(event)
        except Exception:
            return {
                "ok": False,
                "error": "adaptive_transition_persistence_failed",
            }

        state = load_experience_progression(
            experience_id
        )

        if state is None:
            return {
                "ok": False,
                "error": "progression_state_unavailable",
            }

        if state.get("status") == "invalid":
            return {
                "ok": False,
                "error": state.get(
                    "error",
                    "invalid_progression_history",
                ),
            }

        return {
            "ok": True,
            "event": event,
            "progression": state,
        }
