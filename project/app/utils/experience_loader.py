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

def resolve_experience_mode(experience: dict) -> dict:
    """
    Resolve the operating-mode contract for an experience.

    Missing or malformed mode state fails closed to bounded mode
    with adaptive authorization disabled.
    """

    if not isinstance(experience, dict):
        return {
            "mode": "bounded",
            "adaptive_authorized": False,
            "mode_version": "1.0",
            "authorization_source": "system",
        }

    mode = experience.get("mode")
    adaptive_authorized = experience.get("adaptive_authorized")
    mode_version = experience.get("mode_version")
    authorization_source = experience.get("authorization_source")

    if mode not in {"bounded", "adaptive"}:
        mode = "bounded"

    if not isinstance(adaptive_authorized, bool):
        adaptive_authorized = False

    if mode == "bounded":
        adaptive_authorized = False

    if mode_version != "1.0":
        mode_version = "1.0"

    if authorization_source not in {"consent", "system"}:
        authorization_source = "system"

    return {
        "mode": mode,
        "adaptive_authorized": adaptive_authorized,
        "mode_version": mode_version,
        "authorization_source": authorization_source,
    }

def resolve_experience_authorization(experience: dict) -> dict:
    """
    Resolve whether an experience is explicitly authorized
    to operate in adaptive mode.

    Adaptive operation requires all of:
        - mode == "adaptive"
        - adaptive_authorized is True
        - authorization_source == "consent"

    All other states fail closed.
    """

    mode_state = resolve_experience_mode(experience)

    authorized = (
        mode_state["mode"] == "adaptive"
        and mode_state["adaptive_authorized"] is True
        and mode_state["authorization_source"] == "consent"
    )

    return {
        "mode": mode_state["mode"],
        "adaptive_authorized": mode_state["adaptive_authorized"],
        "mode_version": mode_state["mode_version"],
        "authorization_source": mode_state["authorization_source"],
        "authorized": authorized,
    }

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
