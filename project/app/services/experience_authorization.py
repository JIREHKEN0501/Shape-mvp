# project/app/services/experience_authorization.py

from project.app.utils.consent_loader import (
    load_consent_by_participant,
)
from project.app.utils.experience_loader import (
    load_experience_by_id,
    experience_belongs_to_participant,
    resolve_experience_mode,
)


def resolve_adaptive_authorization(
    participant_id: str,
    experience_id: str,
) -> dict:
    """
    Determine whether a participant's experience is explicitly
    authorized to operate in adaptive mode.

    Authorization requires agreement between:
        - participant consent
        - experience operating mode
        - experience adaptive authorization state

    This function is read-only and does not mutate experience,
    consent, routing, or task state.

    Fails closed for missing, malformed, or contradictory state.
    """

    if not participant_id:
        return {
            "authorized": False,
            "reason": "participant_id_required",
        }

    if not experience_id:
        return {
            "authorized": False,
            "reason": "experience_id_required",
        }

    consent = load_consent_by_participant(
        participant_id
    )

    if consent is None:
        return {
            "authorized": False,
            "reason": "consent_not_found",
        }

    if consent.get("consent_given") is not True:
        return {
            "authorized": False,
            "reason": "consent_not_given",
        }

    if (
        consent.get("adaptive_routing_authorized")
        is not True
    ):
        return {
            "authorized": False,
            "reason": "adaptive_routing_not_authorized_by_consent",
        }

    experience = load_experience_by_id(
        experience_id
    )

    if experience is None:
        return {
            "authorized": False,
            "reason": "experience_not_found",
        }

    if not experience_belongs_to_participant(
        experience,
        participant_id,
    ):
        return {
            "authorized": False,
            "reason": "experience_not_owned",
        }

    mode = resolve_experience_mode(
        experience
    )

    if mode["mode"] != "adaptive":
        return {
            "authorized": False,
            "reason": "experience_not_in_adaptive_mode",
            "mode": mode,
        }

    if mode["adaptive_authorized"] is not True:
        return {
            "authorized": False,
            "reason": "experience_adaptive_authorization_missing",
            "mode": mode,
        }

    if (
        mode["authorization_source"]
        != "consent"
    ):
        return {
            "authorized": False,
            "reason": "invalid_adaptive_authorization_source",
            "mode": mode,
        }

    return {
        "authorized": True,
        "reason": "explicit_adaptive_consent_and_experience_authorization",
        "mode": mode,
    }
