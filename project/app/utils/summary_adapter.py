# project/app/utils/summary_adapter.py

from project.app.utils.session_summaries import (
    build_cognitive_session_summary,
)
from project.app.utils.summary_validator import validate_summary_schema

SUMMARY_VERSION = "1.0"
# IMPORTANT:
# Summary adapters must NEVER mutate historical summaries.
# Forward compatibility is achieved by branching on summary_version,
# not by rewriting stored session data.

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
    ok, err = validate_summary_schema(summary)
    if not ok:
        raise ValueError(f"Invalid session summary: {err}")
    
    return summary
