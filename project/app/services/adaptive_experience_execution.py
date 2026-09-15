"""
Authorized adaptive experience execution.

This service connects the existing adaptive task selector to the
experience-scoped execution boundary.

It does not replace the adaptive routing engine.

Flow:

    participant history
        -> adaptive selector
        -> candidate task
        -> experience-scoped eligibility
        -> authorized adaptive transition
"""

from typing import Any, Dict

from project.app.services.adaptive_task_eligibility import (
    resolve_adaptive_task_eligibility,
)
from project.app.services.adaptive_transition import (
    execute_adaptive_transition,
)
from project.app.services.experience_authorization import (
    resolve_adaptive_authorization,
)
from project.app.services.tasks import (
    get_next_task_for_participant,
)


def execute_next_adaptive_task(
    participant_id: str,
    experience_id: str,
    from_task_id: str,
) -> Dict[str, Any]:
    """
    Select and execute the next adaptive task for an experience.

    Selection remains the responsibility of the existing adaptive
    routing engine.

    Experience authorization and experience-scoped task eligibility
    are enforced before an adaptive transition is persisted.

    No adaptive transition is created when authorization, selection,
    eligibility, or persistence fails.
    """

    if not participant_id:
        return {
            "ok": False,
            "error": "participant_id_required",
        }

    if not experience_id:
        return {
            "ok": False,
            "error": "experience_id_required",
        }

    if not from_task_id:
        return {
            "ok": False,
            "error": "from_task_id_required",
        }

    authorization = resolve_adaptive_authorization(
        participant_id,
        experience_id,
    )

    if authorization.get("authorized") is not True:
        return {
            "ok": False,
            "error": authorization.get(
                "reason",
                "adaptive_execution_not_authorized",
            ),
        }

    selected = get_next_task_for_participant(
        participant_id,
        experience_id=experience_id,
    )

    if not isinstance(selected, dict):
        return {
            "ok": False,
            "error": "adaptive_selection_failed",
        }

    if selected.get("ok") is False:
        return {
            "ok": False,
            "error": selected.get(
                "message",
                "adaptive_selection_failed",
            ),
        }

    candidate_task_id = selected.get("task_id")

    if not candidate_task_id:
        return {
            "ok": False,
            "error": "adaptive_selection_missing_task_id",
        }

    eligibility = resolve_adaptive_task_eligibility(
        experience_id,
        candidate_task_id,
    )

    if eligibility.get("eligible") is not True:
        return {
            "ok": False,
            "error": eligibility.get(
                "reason",
                "adaptive_task_not_eligible",
            ),
            "candidate_task_id": candidate_task_id,
        }

    transition = execute_adaptive_transition(
        experience_id=experience_id,
        participant_id=participant_id,
        from_task_id=from_task_id,
        to_task_id=candidate_task_id,
    )

    if transition.get("ok") is not True:
        return {
            "ok": False,
            "error": transition.get(
                "error",
                "adaptive_transition_failed",
            ),
            "candidate_task_id": candidate_task_id,
        }

    return {
        "ok": True,
        "experience_id": experience_id,
        "from_task_id": from_task_id,
        "next_task_id": candidate_task_id,
        "task": selected,
        "transition": transition,
    }
