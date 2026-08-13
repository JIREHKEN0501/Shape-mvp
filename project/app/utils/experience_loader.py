# project/app/utils/experience_loader.py

import json

from project.app.utils.logging import EXPERIENCE_LOG

def load_experience_by_id(experience_id: str) -> dict | None:
    """
    Load the latest participant experience state by experience_id.

    Returns:
        dict if found
        None if not found
    """
    if not experience_id:
        return None

    latest = None

    try:
        with open(EXPERIENCE_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if record.get("experience_id") == experience_id:
                    latest = record

    except FileNotFoundError:
        return None

    return latest

def is_experience_active(experience: dict) -> bool:
    """
    Return True only for an explicitly active experience.
    """
    return (
        isinstance(experience, dict)
        and experience.get("status") == "active"
    )


def experience_belongs_to_participant(
    experience: dict,
    participant_id: str,
) -> bool:
    """
    Verify that an experience belongs to the participant.
    """
    return (
        isinstance(experience, dict)
        and bool(participant_id)
        and experience.get("participant_id") == participant_id
    )
