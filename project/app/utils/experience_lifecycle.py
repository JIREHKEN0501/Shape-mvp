# project/app/utils/experience_lifecycle.py

from project.app.utils.logging import (
    EXPERIENCE_LOG,
    append_jsonl_secure,
    now_iso,
)
from project.app.utils.experience_loader import (
    load_experience_by_id,
    experience_belongs_to_participant,
    is_experience_active,
)


def complete_experience(
    experience_id: str,
    participant_id: str,
) -> dict | None:
    """
    Mark an active participant experience as completed.

    The existing experience record is preserved.
    A new completed lifecycle record is appended to the
    experience log.

    Returns:
        Completed experience record if successful.
        None if the experience cannot be completed.
    """

    experience = load_experience_by_id(experience_id)

    if experience is None:
        return None

    if not experience_belongs_to_participant(
        experience,
        participant_id,
    ):
        return None

    if not is_experience_active(experience):
        return None

    completed = dict(experience)

    completed["status"] = "completed"
    completed["completed_ts"] = now_iso()

    append_jsonl_secure(
        EXPERIENCE_LOG,
        completed,
    )

    return completed
