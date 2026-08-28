# project/app/utils/experience_lifecycle.py

from uuid import uuid4

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

from project.app.services.experience_progression_service import (
    _append_experience_event,
)

def create_experience(
    participant_id: str,
) -> dict | None:
    """
    Create a new active experience for an existing participant.

    A new experience receives its own identity while preserving
    the participant identity.

    Returns the created experience record.
    """

    if not participant_id:
        return None

    experience_id = str(uuid4())
    created_ts = now_iso()

    experience_record = {
        "experience_id": experience_id,
        "participant_id": participant_id,
        "status": "active",
        "sequence_version": "1.0",
        "created_ts": created_ts,
        "completed_ts": None,
    }

    persisted = append_jsonl_secure(
        EXPERIENCE_LOG,
        experience_record,
    )

    if not persisted:
        return None

    experience_created_event = {
        "event": "experience_created",
        "event_version": "1.0",
        "experience_id": experience_id,
        "participant_id": participant_id,
        "sequence_version": "1.0",
        "ts": created_ts,
    }

    _append_experience_event(
        experience_created_event
    )

    return experience_record


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

    persisted = append_jsonl_secure(
        EXPERIENCE_LOG,
        completed,
    )

    if not persisted:
        return None

    return completed
