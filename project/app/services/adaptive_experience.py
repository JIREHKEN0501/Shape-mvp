from project.app.utils.consent_loader import (
    load_consent_by_participant,
)
from project.app.utils.experience_lifecycle import (
    create_experience,
)


def create_authorized_adaptive_experience(
    participant_id: str,
) -> dict | None:
    """
    Create an adaptive experience only when the participant's
    latest consent record explicitly authorizes adaptive routing.

    General consent alone is insufficient.
    """

    if not participant_id:
        return None

    consent = load_consent_by_participant(participant_id)

    if consent is None:
        return None

    if consent.get("consent_given") is not True:
        return None

    if consent.get("adaptive_routing_authorized") is not True:
        return None

    return create_experience(
        participant_id,
        mode="adaptive",
        adaptive_authorized=True,
        authorization_source="consent",
    )
