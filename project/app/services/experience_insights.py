from typing import Dict, Any, List


def generate_experience_insights(
    summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate evidence-bounded participant insights from one
    completed experience summary.

    This layer does not diagnose, assign permanent traits,
    or infer stable psychological characteristics.

    It describes observed performance and decisions within
    the supplied experience only.
    """

    if not isinstance(summary, dict):
        return {
            "has_insights": False,
            "message": "invalid_summary",
        }

    if not summary.get("has_data"):
        return {
            "has_insights": False,
            "message": summary.get(
                "message",
                "no_experience_data",
            ),
        }

    attempts: List[Dict[str, Any]] = summary.get(
        "attempts",
        [],
    )

    objective_attempts = [
        attempt
        for attempt in attempts
        if attempt.get("correct") is not None
    ]

    decision_observations = [
        attempt
        for attempt in attempts
        if attempt.get("correct") is None
    ]

    performance = []

    objective_accuracy = summary.get(
        "objective_accuracy"
    )

    if objective_accuracy is not None:
        performance.append({
            "dimension": "objective_performance",
            "result": (
                f"{summary.get('correct_objective_questions', 0)} "
                f"of {summary.get('objective_questions', 0)} "
                "objective questions answered correctly"
            ),
            "accuracy": objective_accuracy,
            "evidence_type": "objective",
        })

    observations = []

    for attempt in decision_observations:
        observations.append({
            "task_id": attempt.get("task_id"),
            "question_id": attempt.get("question_id"),
            "selected_option": attempt.get("user_answer"),
            "time_taken_seconds": attempt.get(
                "time_taken_seconds"
            ),
            "evidence_type": "decision_observation",
        })

    evidence_limits = [
        (
            "This reflection describes behavior observed "
            "within this experience only."
        ),
        (
            "The available evidence is insufficient to "
            "establish a stable personal trait or weakness."
        ),
    ]

    next_experiment = {
        "type": "comparable_experience",
        "reason": (
            "A repeated or varied experience would provide "
            "evidence for comparison over time."
        ),
    }

    return {
        "has_insights": True,
        "experience_id": summary.get("experience_id"),
        "performance": performance,
        "observations": observations,
        "evidence_limits": evidence_limits,
        "next_experiment": next_experiment,
    }
