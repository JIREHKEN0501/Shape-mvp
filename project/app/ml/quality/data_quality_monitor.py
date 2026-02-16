"""
HumanOS Data Quality Monitor v1

Protects calibration pipeline from statistically unstable
or anomalous aggregated metrics.

Operates at task-level aggregation.
Never touches individual identities.
"""

from typing import Dict


# -----------------------------
# Threshold Configuration
# -----------------------------

MIN_SESSIONS = 25
MAX_TIME_STD = 15.0
MAX_VARIANCE_MEAN = 20.0
ZERO_VARIANCE_TOLERANCE = 1e-6


def evaluate_aggregation_quality(aggregated_metrics: Dict) -> Dict:
    """
    Evaluate aggregated task metrics for statistical anomalies.

    Returns:
        {
            "is_valid": bool,
            "quality_flags": List[str]
        }
    """

    flags = []

    n = aggregated_metrics.get("num_sessions", 0)
    accuracy_std = aggregated_metrics.get("accuracy_std", 0.0)
    avg_time_std = aggregated_metrics.get("avg_time_std", 0.0)
    time_variance_mean = aggregated_metrics.get("time_variance_mean", 0.0)

    # -----------------------------
    # 1. Sample Size Check
    # -----------------------------
    if n < MIN_SESSIONS:
        flags.append("insufficient_sample_size")

    # -----------------------------
    # 2. Zero Variance Check
    # -----------------------------
    if abs(accuracy_std) < ZERO_VARIANCE_TOLERANCE:
        flags.append("zero_accuracy_variance")

    # -----------------------------
    # 3. Excessive Time Dispersion
    # -----------------------------
    if avg_time_std > MAX_TIME_STD:
        flags.append("excessive_time_std")

    # -----------------------------
    # 4. Extreme Variance Mean
    # -----------------------------
    if time_variance_mean > MAX_VARIANCE_MEAN:
        flags.append("extreme_time_variance")

    return {
        "is_valid": len(flags) == 0,
        "quality_flags": flags,
    }
