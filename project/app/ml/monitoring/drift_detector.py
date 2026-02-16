# project/app/ml/monitoring/drift_detector.py

"""
Drift detection for task-level calibration metrics.

Detects statistically meaningful shifts across time snapshots.
Operates strictly at task level.
"""

from typing import List, Dict
import math


DRIFT_THRESHOLD = 0.10
ACCURACY_DRIFT_THRESHOLD = 0.08
TIME_DRIFT_THRESHOLD = 0.20


def detect_task_drift(snapshots: List[Dict]) -> Dict:
    """
    Compare earliest and latest snapshots.

    Returns structured drift analysis.
    """

    if len(snapshots) < 2:
        return {"status": "insufficient_history"}

    first = snapshots[0]
    last = snapshots[-1]

    difficulty_drift = last["empirical_difficulty"] - first["empirical_difficulty"]
    accuracy_drift = last.get("accuracy_mean", 0) - first.get("accuracy_mean", 0)
    time_drift = last.get("avg_time_mean", 0) - first.get("avg_time_mean", 0)

    difficulty_flag = abs(difficulty_drift) > DRIFT_THRESHOLD
    accuracy_flag = abs(accuracy_drift) > ACCURACY_DRIFT_THRESHOLD
    time_flag = abs(time_drift) > TIME_DRIFT_THRESHOLD

    overall_status = "stable"

    if difficulty_flag or accuracy_flag or time_flag:
        overall_status = "drift_detected"

    return {
        "difficulty_drift": round(difficulty_drift, 4),
        "accuracy_drift": round(accuracy_drift, 4),
        "time_drift": round(time_drift, 4),
        "difficulty_flag": difficulty_flag,
        "accuracy_flag": accuracy_flag,
        "time_flag": time_flag,
        "overall_status": overall_status,
    }

