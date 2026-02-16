# project/app/ml/stability/temporal_drift.py

from typing import List, Dict
import math


DRIFT_THRESHOLD = 0.08         # meaningful shift in difficulty
METRIC_DRIFT_THRESHOLD = 0.10  # meaningful shift in accuracy/time
MIN_PERIODS = 3                # minimum time windows required


def detect_temporal_drift(
    history: List[Dict],
) -> Dict:
    """
    Detect population-level drift over time.

    history:
        List of ordered snapshots (oldest → newest)
        Each snapshot must contain:
            - empirical_difficulty
            - aggregated_metrics (accuracy_mean, avg_time_mean, etc.)

    Returns:
        Drift analysis summary
    """

    if len(history) < MIN_PERIODS:
        return {
            "status": "insufficient_data",
            "reason": "Not enough historical windows",
        }

    difficulties = [h["empirical_difficulty"] for h in history]
    accuracies = [
        h["aggregated_metrics"].get("accuracy_mean", 0.0)
        for h in history
    ]
    times = [
        h["aggregated_metrics"].get("avg_time_mean", 0.0)
        for h in history
    ]

    difficulty_trend = _trend(difficulties)
    accuracy_trend = _trend(accuracies)
    time_trend = _trend(times)

    drift_flags = []

    if abs(difficulty_trend) > DRIFT_THRESHOLD:
        drift_flags.append("difficulty_drift")

    if abs(accuracy_trend) > METRIC_DRIFT_THRESHOLD:
        drift_flags.append("accuracy_drift")

    if abs(time_trend) > METRIC_DRIFT_THRESHOLD:
        drift_flags.append("time_drift")

    if not drift_flags:
        status = "stable"
    else:
        status = "drift_detected"

    return {
        "status": status,
        "difficulty_trend": round(difficulty_trend, 4),
        "accuracy_trend": round(accuracy_trend, 4),
        "time_trend": round(time_trend, 4),
        "flags": drift_flags,
        "windows_analyzed": len(history),
        "population_level_only": True,
    }


def _trend(values: List[float]) -> float:
    """
    Simple slope approximation using linear regression formula.
    """

    n = len(values)
    x_vals = list(range(n))
    x_mean = sum(x_vals) / n
    y_mean = sum(values) / n

    numerator = sum(
        (x_vals[i] - x_mean) * (values[i] - y_mean)
        for i in range(n)
    )

    denominator = sum(
        (x - x_mean) ** 2 for x in x_vals
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator
