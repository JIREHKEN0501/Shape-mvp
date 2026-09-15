from project.app.utils.consent_loader import load_consent_by_participant
from project.app.utils.logging import append_jsonl_secure, CONSENT_LOG, now_iso


def authorize_adaptive_routing(participant_id: str) -> bool:
    if not participant_id:
        return False

    consent = load_consent_by_participant(participant_id)

    if consent is None:
        return False

    if consent.get("consent_given") is not True:
        return False

    record = {
        "participant_id": participant_id,
        "timestamp": now_iso(),
        "consent_version": consent.get("consent_version", 1),
        "consent_given": True,
        "adaptive_routing_authorized": True,
    }

    return append_jsonl_secure(CONSENT_LOG, record)
