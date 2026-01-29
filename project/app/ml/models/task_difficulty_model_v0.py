# project/app/ml/models/task_difficulty_model_v0.py

"""
Task Difficulty Calibration Model v0

This model computes an empirical difficulty score for tasks based on
aggregated, identity-free metrics.

Design principles:
- task-centric, not learner-centric
- descriptive, not predictive
- transparent weighting
- uncertainty-aware
"""

from typing import Dict, List


# -----------------------------
# Configuration (explicit)
# -----------------------------

WEIGHTS = {
    "accuracy": 0.40,
    "error_rate": 0.25,
    "avg_time": 0.20,
    "time_variance": 0.15,
}

# Thresholds for calibration flags
DELTA_THRESHOLD = 0.15
LOW_CONFIDENCE_THRESHOLD = 0.4


# -----------------------------
# Public API
# -----------------------------

def compute_task_difficulty(task_input: Dict) -> Dict:
    """
    Compute empirical difficulty for a single task.

    Args:
        task_input: dict matching task_difficulty_input.schema.json

    Returns:
        dict containing calibrated difficulty outputs
    """

    task_id = task_input["task_id"]
    declared = task_input["task_metadata"]["declared_difficulty"]
    metrics = task_input["aggregated_metrics"]

    signals = _compute_signals(metrics)
    empirical = _weighted_difficulty(signals)
    confidence = _compute_confidence(metrics)
    delta = empirical - declared

    return {
        "task_id": task_id,
        "declared_difficulty": declared,
        "empirical_difficulty": round(empirical, 4),
        "difficulty_delta": round(delta, 4),
        "confidence": round(confidence, 4),
        "calibration_flag": _calibration_flag(delta, confidence),
        "notes": _notes(signals, confidence),
    }


def compute_batch(task_inputs: List[Dict]) -> List[Dict]:
    """
    Compute difficulty calibration for multiple tasks.
    """
    return [compute_task_difficulty(task) for task in task_inputs]


# -----------------------------
# Internal helpers
# -----------------------------

def _compute_signals(metrics: Dict) -> Dict:
    """
    Convert raw metrics into normalized difficulty signals ∈ [0,1].
    """

    accuracy_signal = 1.0 - _clamp(metrics["accuracy_mean"])
    error_signal = _clamp(metrics["error_rate"])
    avg_time_signal = _normalize_positive(metrics["avg_time_mean"])
    variance_signal = _normalize_positive(metrics["time_variance_mean"])

    return {
        "accuracy": accuracy_signal,
        "error_rate": error_signal,
        "avg_time": avg_time_signal,
        "time_variance": variance_signal,
    }


def _weighted_difficulty(signals: Dict) -> float:
    """
    Compute weighted difficulty score.
    """
    score = 0.0
    for key, weight in WEIGHTS.items():
        score += weight * signals.get(key, 0.0)
    return _clamp(score)


def _compute_confidence(metrics: Dict) -> float:
    """
    Confidence decreases with low sample size and high variance.
    """

    n = metrics["num_sessions"]

    # Sample size confidence (asymptotic)
    sample_conf = min(1.0, n / 30.0)

    # Variance penalty
    variance_penalty = min(
        1.0,
        (metrics["accuracy_std"] + metrics["avg_time_std"]) / 2.0
    )

    confidence = sample_conf * (1.0 - variance_penalty)
    return _clamp(confidence)


def _calibration_flag(delta: float, confidence: float) -> str:
    """
    Produce a human-safe calibration label.
    """

    if confidence < LOW_CONFIDENCE_THRESHOLD:
        return "low_confidence"

    if delta > DELTA_THRESHOLD:
        return "underestimated"
    elif delta < -DELTA_THRESHOLD:
        return "overestimated"
    else:
        return "aligned"


def _notes(signals: Dict, confidence: float) -> List[str]:
    """
    Generate explanatory notes for humans.
    """

    notes = []

    if signals["accuracy"] > 0.6:
        notes.append("low accuracy observed")

    if signals["time_variance"] > 0.6:
        notes.append("high response time variance")

    if confidence < LOW_CONFIDENCE_THRESHOLD:
        notes.append("insufficient data for stable calibration")

    return notes


# -----------------------------
# Utility
# -----------------------------

def _normalize_positive(value: float) -> float:
    """
    Normalize positive values with soft saturation.
    """
    if value <= 0:
        return 0.0
    return value / (value + 1.0)


def _clamp(value: float) -> float:
    """
    Clamp value into [0,1].
    """
    return max(0.0, min(1.0, value))
