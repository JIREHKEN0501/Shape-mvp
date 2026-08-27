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

    objective_by_task: Dict[str, List[Dict[str, Any]]] = {}

    for attempt in objective_attempts:
        task_id = attempt.get("task_id") or "unknown"
        objective_by_task.setdefault(task_id, []).append(attempt)

    for task_id, task_attempts in objective_by_task.items():
        task_correct = sum(
            1
            for attempt in task_attempts
            if (
                str(attempt.get("user_answer")).strip()
                == str(attempt.get("correct")).strip()
            )
        )

        task_count = len(task_attempts)

        task_accuracy = (
            task_correct / float(task_count)
            if task_count > 0
            else None
        )

        performance.append({
            "task_id": task_id,
            "dimension": "objective_performance",
            "result": (
                f"{task_correct} of {task_count} "
                "objective questions answered correctly"
            ),
            "accuracy": task_accuracy,
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
