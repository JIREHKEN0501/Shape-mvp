# project/app/ml/monitoring/task_drift_monitor.py

from typing import List, Dict
import math


# -----------------------------
# Configuration
# -----------------------------

MIN_POINTS_REQUIRED = 4
SLOPE_THRESHOLD_GRADUAL = 0.01
SLOPE_THRESHOLD_ABRUPT = 0.05


# -----------------------------
# Public API
# -----------------------------

def detect_task_drift(time_series: List[Dict]) -> Dict:
    """
    Detect trend drift in empirical task difficulty over time.

    time_series format:
    [
        {"period": "2025-01", "empirical_difficulty": 0.62},
        ...
    ]
    """

    if len(time_series) < MIN_POINTS_REQUIRED:
        return {
            "trend": "insufficient_data",
            "slope": 0.0,
            "drift_flag": "unknown",
            "points_analyzed": len(time_series),
        }

    values = [p["empirical_difficulty"] for p in time_series]
    slope = _linear_regression_slope(values)

    magnitude = values[-1] - values[0]

    trend = _classify_trend(slope)

    return {
        "trend": trend,
        "slope": round(slope, 4),
        "magnitude": round(magnitude, 4),
        "drift_flag": _drift_flag(slope),
        "points_analyzed": len(values),
    }


# -----------------------------
# Internal Helpers
# -----------------------------

def _linear_regression_slope(values: List[float]) -> float:
    """
    Compute simple linear regression slope over index positions.
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
        (x_vals[i] - x_mean) ** 2
        for i in range(n)
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator


def _classify_trend(slope: float) -> str:
    if abs(slope) < SLOPE_THRESHOLD_GRADUAL:
        return "stable"

    if abs(slope) < SLOPE_THRESHOLD_ABRUPT:
        return "gradual_shift"

    return "abrupt_shift"


def _drift_flag(slope: float) -> str:
    if abs(slope) < SLOPE_THRESHOLD_GRADUAL:
        return "no_drift"

    if slope > 0:
        return "drift_up"
    else:
        return "drift_down"

