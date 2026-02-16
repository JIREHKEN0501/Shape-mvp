# project/app/ml/stability/drift_detector.py

"""
Drift detection for task-level empirical difficulty.

Purpose:
- Detect statistically significant shifts in task difficulty over time
- Operates ONLY on population-level aggregated difficulty values
- Never touches individual session data
"""

from typing import List, Dict
import math


DRIFT_Z_THRESHOLD = 2.0        # Moderate drift
STRONG_DRIFT_Z_THRESHOLD = 3.0 # Strong drift


def detect_drift(
    historical_difficulties: List[float],
    current_difficulty: float,
) -> Dict:
    """
    Detect drift using z-score comparison.

    Args:
        historical_difficulties: prior empirical difficulty values
        current_difficulty: most recent empirical difficulty

    Returns:
        dict with drift diagnostics
    """

    if not historical_difficulties:
        return {
            "drift_detected": False,
            "drift_magnitude": 0.0,
            "drift_direction": "none",
            "z_score": 0.0,
            "confidence": "insufficient_history",
        }

    mean_hist = _mean(historical_difficulties)
    std_hist = _std(historical_difficulties)

    if std_hist == 0:
        return {
            "drift_detected": False,
            "drift_magnitude": 0.0,
            "drift_direction": "none",
            "z_score": 0.0,
            "confidence": "no_variance_in_history",
        }

    z = (current_difficulty - mean_hist) / std_hist
    drift_magnitude = abs(current_difficulty - mean_hist)

    if abs(z) >= STRONG_DRIFT_Z_THRESHOLD:
        confidence = "strong"
        drift_detected = True
    elif abs(z) >= DRIFT_Z_THRESHOLD:
        confidence = "moderate"
        drift_detected = True
    else:
        confidence = "stable"
        drift_detected = False

    if current_difficulty > mean_hist:
        direction = "increase"
    elif current_difficulty < mean_hist:
        direction = "decrease"
    else:
        direction = "none"

    return {
        "drift_detected": drift_detected,
        "drift_magnitude": round(drift_magnitude, 4),
        "drift_direction": direction,
        "z_score": round(z, 4),
        "confidence": confidence,
    }


def _mean(values: List[float]) -> float:
    return sum(values) / len(values)


def _std(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))

