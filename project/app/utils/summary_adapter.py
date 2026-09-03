# project/app/utils/summary_adapter.py

from project.app.utils.session_summaries import (
    build_cognitive_session_summary,
)
from project.app.utils.summary_validator import validate_summary_schema
from project.app.services.tasks import get_task

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

    # Strategy tasks
    if task_id == "strategy_under_constraint_v1":
        task_definition = get_task(
            task_id,
            include_answer=True,
        )

        if task_definition is None:
            return None

        decision_code_mapping = task_definition.get(
            "decision_code_mapping",
            {},
        )

        decisions = []

        for module in session.get("modules", []):
            for question in module.get("questions", []):
                question_id = question.get("question_id")
                selected_option = question.get("user_answer")

                question_mapping = decision_code_mapping.get(
                    question_id,
                    {},
                )

                decision_code = question_mapping.get(
                    selected_option
                )

                decisions.append(
                    {
                        "question_id": question_id,
                        "selected_option": selected_option,
                        "decision_code": decision_code,
                        "time_taken_seconds": question.get(
                            "time_taken_seconds"
                        ),
                    }
                )

        return {
            "summary_version": SUMMARY_VERSION,
            "summary_type": "strategy",
            "data": {
                "decisions": decisions,
            },
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
