# project/app/utils/summary_adapter.py

from project.app.utils.session_summaries import (
    build_cognitive_session_summary,
)

SUMMARY_VERSION = "1.0"


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
        return {
            "summary_version": SUMMARY_VERSION,
            "summary_type": "strategy",
            "data": {
                "note": "strategy summary not yet implemented"
            }
        }

    # Cognitive tasks
    if "modules" in session:
        return {
            "summary_version": SUMMARY_VERSION,
            "summary_type": "cognitive",
            "data": build_cognitive_session_summary(session),
        }

    return None
