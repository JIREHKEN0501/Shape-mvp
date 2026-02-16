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
import math
import random
from project.app.ml.stability.drift_detector import detect_drift

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
STABILITY_WIDTH_THRESHOLD = 0.25   # wide interval = unstable
DELTA_TOLERANCE = 0.05             # small difference = negligible

# -----------------------------
# Public API
# -----------------------------
def _confidence_interval_95(estimate: float, std: float, n: int):
    """
    Approximate 95% confidence interval using normal approximation.
    """

    if n < 5:
        return (estimate, estimate)

    if std == 0:
        return (estimate, estimate)

    se = std / math.sqrt(n)
    margin = 1.96 * se

    lower = max(0.0, estimate - margin)
    upper = min(1.0, estimate + margin)

    return (round(lower, 4), round(upper, 4))

def _bootstrap_confidence_interval(
    empirical: float,
    std: float,
    n: int,
    num_bootstrap: int = 500,
):
    """
    Bootstrap 95% confidence interval for empirical difficulty.
    """

    if n < 5 or std == 0:
        return (empirical, empirical)

    samples = []

    for _ in range(num_bootstrap):
        # simulate bootstrap resample
        simulated = random.gauss(empirical, std)
        samples.append(simulated)

    samples.sort()

    lower_index = int(0.025 * num_bootstrap)
    upper_index = int(0.975 * num_bootstrap)

    lower = max(0.0, samples[lower_index])
    upper = min(1.0, samples[upper_index])

    return (lower, upper)

def _confidence_level(n: int) -> str:
    """
    Simple confidence heuristic based on sample size.
    """

    if n >= 500:
        return "high"
    elif n >= 100:
        return "moderate"
    else:
        return "low"

def compute_task_difficulty(
    task_input: Dict,
    historical_difficulties: list[float] | None = None,
) -> Dict:
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
    n = metrics.get("num_sessions", 0)
    std = metrics.get("accuracy_std", 0.0)

    accuracy_distribution = metrics.get("accuracy_distribution")

    if accuracy_distribution and len(accuracy_distribution) > 1:
        ci_95 = bootstrap_confidence_interval(accuracy_distribution)
    else:
        ci_95 = _bootstrap_confidence_interval(empirical, std, n)

    ci_lower, ci_upper = ci_95
    ci_width = ci_upper - ci_lower

    confidence_level = _confidence_level(n)

    #STABILITY LOGIC
    stability = _stability_adjustment(
        empirical=empirical,
        declared=declared,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        confidence=confidence,
    )

    adjusted_delta = delta
    adjusted_confidence = confidence

    if stability == "unstable_estimate":
        adjusted_confidence *= 0.8  # slight downgrade

    # Keep calibration taxonomy stable
    final_flag = _calibration_flag(adjusted_delta, adjusted_confidence)

    # -----------------------------
    # Optional Drift Detection
    # -----------------------------
    drift_info = None

    if historical_difficulties is not None:
        drift_info = detect_drift(historical_difficulties, empirical)

    return {
        "task_id": task_id,
        "declared_difficulty": declared,
        "empirical_difficulty": round(empirical, 4),
        "difficulty_delta": round(delta, 4),

        # existing confidence score
        "confidence": round(confidence, 4),

        # NEW uncertainty fields
        "confidence_interval_95": ci_95,
        "sample_size": n,
        "confidence_level": confidence_level,

        "calibration_flag": final_flag,
        "notes": _notes(signals, confidence),
        "drift": drift_info,
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

def _stability_adjustment(
    empirical: float,
    declared: float,
    ci_lower: float,
    ci_upper: float,
    confidence: float,
):
    """
    Adjust calibration flag based on statistical stability.
    """

    # Case 1: CI overlaps declared difficulty
    if ci_lower <= declared <= ci_upper:
        return "within_tolerance"

    # Case 2: CI too wide (unstable estimate)
    if (ci_upper - ci_lower) > STABILITY_WIDTH_THRESHOLD:
        return "unstable_estimate"


    return None


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
