# project/app/ml/aggregation/task_difficulty_aggregator.py

"""
Aggregates session-scoped HumanOS summaries into
task-level metrics suitable for ML task difficulty calibration.

This module:
- operates offline / batch
- never touches participant identity
- never links sessions
- outputs schema-compliant ML inputs
"""

from collections import defaultdict
from typing import Dict, List
from project.app.ml.quality.session_quality_monitor import evaluate_session_quality
import math

# -----------------------------
# Quality thresholds
# -----------------------------
MIN_AVG_TIME_THRESHOLD = 0.5   # seconds per question


def aggregate_task_summaries(
    summaries: List[Dict],
    task_metadata_lookup: Dict[str, Dict],
) -> List[Dict]:
    """
    Convert session summaries into ML-ready task difficulty inputs.

    Args:
        summaries: list of validated session summaries
        task_metadata_lookup: mapping task_id -> task metadata

    Returns:
        List of dicts matching task_difficulty_input.schema.json
    """

    # --- bucket summaries by task_id ---
    by_task: Dict[str, List[Dict]] = defaultdict(list)

    for summary in summaries:
        task_id = summary.get("task_id")
        if not task_id:
            continue
        by_task[task_id].append(summary)

    aggregated_outputs: List[Dict] = []

    # --- aggregate per task ---
    for task_id, task_summaries in by_task.items():
        metrics = _aggregate_metrics(task_summaries)

        task_meta = task_metadata_lookup.get(task_id)
        if not task_meta:
            # Skip tasks without metadata (safe failure)
            continue

        aggregated_outputs.append(
            {
                "task_id": task_id,
                "task_metadata": {
                    "declared_difficulty": task_meta["declared_difficulty"],
                    "domain": task_meta["domain"],
                    "structure_version": task_meta["structure_version"],
                },
                "aggregated_metrics": metrics,
            }
        )

    return aggregated_outputs


def _aggregate_metrics(task_summaries: List[Dict]) -> Dict:
    """
    Aggregate numeric metrics across sessions for a single task.
    applies quality filtering before aggregation.

    """

    valid_summaries = []
    filtered_count = 0

    for s in task_summaries:
        quality = evaluate_session_quality(s)

        if quality["eligible_for_aggregation"]:
            valid_summaries.append(s)
        else:
            filtered_count += 1

    if not valid_summaries:
        return {
            "num_sessions": 0,
            "accuracy_mean": 0.0,
            "accuracy_std": 0.0,
            "avg_time_mean": 0.0,
            "avg_time_std": 0.0,
            "time_variance_mean": 0.0,
            "error_rate": 0.0,
            "filtered_sessions": filtered_count,
        }

    accuracies = []
    avg_times = []
    time_variances = []
    error_rates = []

    for s in valid_summaries:
        data = s.get("data", {})

        if "accuracy_ratio" in data:
            accuracies.append(data["accuracy_ratio"])

        if "avg_time_per_question" in data:
            avg_times.append(data["avg_time_per_question"])

        if "time_variance" in data:
            time_variances.append(data["time_variance"])

        if "total_questions" in data and "accuracy_ratio" in data:
            errors = data["total_questions"] * (1 - data["accuracy_ratio"])
            error_rates.append(errors / data["total_questions"])

    return {
        "num_sessions": len(valid_summaries),
        "accuracy_mean": _mean(accuracies),
        "accuracy_std": _std(accuracies),
        "avg_time_mean": _mean(avg_times),
        "avg_time_std": _std(avg_times),
        "time_variance_mean": _mean(time_variances),
        "error_rate": _mean(error_rates),
        "filtered_sessions": filtered_count,
        "accuracy_distribution": accuracies,
    }


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _std(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))

# ------------------------------------------------------------
# Public wrapper function (used by tests and integration layer)
# ------------------------------------------------------------

def aggregate_sessions(
    summaries: List[Dict],
    task_metadata_lookup: Dict[str, Dict] | None = None,
):
    """
    Public API wrapper.

    If task_metadata_lookup is provided:
        → production aggregation (summary → ML input)

    If not provided:
        → simplified aggregation for synthetic stress testing
    """

    # ------------------------------
    # Stress test mode
    # ------------------------------
    if task_metadata_lookup is None:
        if not summaries:
            return {}

        accuracies = [s["accuracy"] for s in summaries]
        response_times = [s["response_time"] for s in summaries]

        accuracy_mean = _mean(accuracies)
        accuracy_std = _std(accuracies)
        avg_time_mean = _mean(response_times)
        avg_time_std = _std(response_times)


        return {
            "num_sessions": len(summaries),
            "accuracy_mean": accuracy_mean,
            "accuracy_std": accuracy_std,
            "avg_time_mean": avg_time_mean,
            "avg_time_std": avg_time_std,
            "time_variance_mean": avg_time_std ** 2,
            "error_rate": 1.0 - accuracy_mean,
        }

    # ------------------------------
    # Production mode
    # ------------------------------
    return aggregate_task_summaries(summaries, task_metadata_lookup)
