# project/app/utils/consent_loader.py

import json

from project.app.utils.logging import CONSENT_LOG


def load_consent_by_participant(
    participant_id: str,
) -> dict | None:
    """
    Load the latest consent state for a participant.

    Returns:
        dict if a matching consent record exists
        None if no valid matching record exists
    """

    if not participant_id:
        return None

    latest = None

    try:
        with open(
            CONSENT_LOG,
            "r",
            encoding="utf-8",
        ) as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if (
                    isinstance(record, dict)
                    and record.get("participant_id")
                    == participant_id
                ):
                    latest = record

    except FileNotFoundError:
        return None

    return latest
