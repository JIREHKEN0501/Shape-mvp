# project/app/utils/summary_adapter.py

from project.app.utils.session_summaries import (
    build_cognitive_session_summary,
)

def build_session_summary(session: dict) -> dict | None:
    """
    Unified adapter for session summaries.
    Returns None if session is incomplete.
    """

    if not session.get("session_complete"):
        return None

    task_id = session.get("task_id")

    # Strategy tasks (future-safe)
    if task_id == "strategy_under_constraint_v1":
        # placeholder for later
        return {
            "note": "strategy summary not yet implemented"
        }

    # Cognitive tasks
    if "modules" in session:
        return build_cognitive_session_summary(session)

    return None

