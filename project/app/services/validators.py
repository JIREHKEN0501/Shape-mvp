# project/app/services/validators.py

"""
Validation helpers for session payloads.
Kept very simple for now: just presence + basic types.
"""


def validate_behavioral_session(session: dict):
    """
    Minimal validation for a behavioral session.
    Expects:
      - participant_id (str)
      - task_id (str)
      - events (list)
    """
    if not isinstance(session, dict):
        return False, "Session must be a JSON object"

    required = ["participant_id", "task_id", "events"]
    for key in required:
        if key not in session:
            return False, f"Missing required field: {key}"

    if not isinstance(session["events"], list):
        return False, "events must be a list"

    return True, "ok"


def validate_cognitive_session(session: dict):
    """
    Minimal validation for a cognitive session.
    Expects:
      - participant_id (str)
      - task_id (str)
      - modules (list)
    """
    if not isinstance(session, dict):
        return False, "Session must be a JSON object"

    required = ["participant_id", "task_id", "modules"]
    for key in required:
        if key not in session:
            return False, f"Missing required field: {key}"

    if not isinstance(session["modules"], list):
        return False, "modules must be a list"

    return True, "ok"

