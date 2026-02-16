# project/app/ml/stability/cohort_shift.py

from typing import List, Dict
import math


SHIFT_THRESHOLD = 0.12


def detect_cohort_shift(
    baseline: Dict,
    current: Dict,
) -> Dict:
    """
    Compare two population snapshots to detect distribution shifts.

    baseline: historical aggregate snapshot
    current:  new aggregate snapshot

    Returns shift analysis (population-level only).
    """

    accuracy_diff = current["aggregated_metrics"].get("accuracy_mean", 0.0) - \
                    baseline["aggregated_metrics"].get("accuracy_mean", 0.0)

    time_diff = current["aggregated_metrics"].get("avg_time_mean", 0.0) - \
                baseline["aggregated_metrics"].get("avg_time_mean", 0.0)

    difficulty_diff = current.get("empirical_difficulty", 0.0) - \
                      baseline.get("empirical_difficulty", 0.0)

    flags = []

    if abs(accuracy_diff) > SHIFT_THRESHOLD:
        flags.append("accuracy_distribution_shift")

    if abs(time_diff) > SHIFT_THRESHOLD:
        flags.append("time_distribution_shift")

    if abs(difficulty_diff) > SHIFT_THRESHOLD:
        flags.append("difficulty_shift")

    status = "shift_detected" if flags else "stable_population"

    return {
        "status": status,
        "accuracy_difference": round(accuracy_diff, 4),
        "time_difference": round(time_diff, 4),
        "difficulty_difference": round(difficulty_diff, 4),
        "flags": flags,
        "population_level_only": True,
    }

