"""
Adaptive task eligibility boundary.

This service determines whether a task selected by the adaptive
routing layer may be executed as an adaptive transition for a
specific experience.

It does not select tasks, perform routing, or mutate progression.

Experience progression events are authoritative for determining
which tasks have already been completed within the experience.

Participant-level history is deliberately not used for completion
or eligibility checks.
"""

from typing import Any, Dict

from project.app.services.tasks import list_tasks
from project.app.utils.experience_loader import (
    load_experience_by_id,
    resolve_experience_authorization,
)
from project.app.utils.experience_progression import (
    load_experience_progression,
)


def _get_completed_task_ids(experience_id: str) -> set[str]:
    """
    Return task IDs completed within this experience.

    Experience progression is the authoritative source.
    Participant-level history is deliberately not consulted.
    """
    progression = load_experience_progression(experience_id)

    if not isinstance(progression, dict):
        return set()

    completed_tasks = progression.get("completed_tasks", [])

    if not isinstance(completed_tasks, list):
        return set()

    return {
        task_id
        for task_id in completed_tasks
        if isinstance(task_id, str) and task_id
    }


def _adaptive_catalog_contains(candidate_task_id: str) -> bool:
    """
    Return whether the candidate belongs to the general adaptive
    task catalog.

    This deliberately uses list_tasks(), which reads the general
    adaptive catalog, rather than get_task(), which also resolves
    canonical experience-task definitions.
    """
    return any(
        isinstance(task, dict)
        and task.get("task_id") == candidate_task_id
        for task in list_tasks(include_answer=False)
    )


def resolve_adaptive_task_eligibility(
    experience_id: str,
    candidate_task_id: str,
) -> Dict[str, Any]:
    """
    Determine whether a candidate task may execute adaptively
    within the supplied experience.

    Routing remains responsible for selecting the candidate.
    Governance remains responsible for routing permissions.

    This boundary determines only whether the selected candidate
    may execute as an adaptive transition.
    """

    if not experience_id:
        return {
            "eligible": False,
            "reason": "experience_id_required",
        }

    if not candidate_task_id:
        return {
            "eligible": False,
            "reason": "candidate_task_id_required",
        }

    experience = load_experience_by_id(experience_id)

    if experience is None:
        return {
            "eligible": False,
            "reason": "experience_not_found",
        }

    authorization = resolve_experience_authorization(experience)

    if authorization.get("authorized") is not True:
        return {
            "eligible": False,
            "reason": "adaptive_execution_not_authorized",
            "mode": authorization.get("mode", "bounded"),
            "adaptive_authorized": authorization.get(
                "adaptive_authorized",
                False,
            ),
        }

    if not _adaptive_catalog_contains(candidate_task_id):
        return {
            "eligible": False,
            "reason": "unknown_task",
        }

    completed_task_ids = _get_completed_task_ids(experience_id)

    if candidate_task_id in completed_task_ids:
        return {
            "eligible": False,
            "reason": "already_completed",
            "completed_task_ids": sorted(completed_task_ids),
        }

    return {
        "eligible": True,
        "reason": "adaptive_task_eligible",
        "experience_id": experience_id,
        "candidate_task_id": candidate_task_id,
    }
