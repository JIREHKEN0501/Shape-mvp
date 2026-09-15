from project.app.services.experience_authorization import (
    resolve_adaptive_authorization,
)


def resolve_experience_execution(
    participant_id: str,
    experience_id: str,
) -> dict:
    """
    Resolve whether adaptive routing consequences may execute
    for the supplied experience.

    This is an execution boundary only. It does not select,
    mutate, or persist a next task.
    """

    authorization = resolve_adaptive_authorization(
        participant_id,
        experience_id,
    )

    if authorization.get("authorized") is True:
        return {
            "execution_allowed": True,
            "mode": "adaptive",
            "adaptive_authorized": True,
            "reason": "adaptive_execution_authorized",
        }

    mode = authorization.get("mode") or {}
    resolved_mode = mode.get("mode", "bounded")
    adaptive_authorized = mode.get(
        "adaptive_authorized",
        False,
    )

    return {
        "execution_allowed": False,
        "mode": resolved_mode,
        "adaptive_authorized": adaptive_authorized,
        "reason": authorization.get(
            "reason",
            "adaptive_execution_not_authorized",
        ),
    }
