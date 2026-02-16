# project/app/ml/quality/session_quality_monitor.py

"""
Session-level data quality monitor.

Purpose:
- Detect anomalous or low-integrity sessions
- Prevent corrupted sessions from entering aggregation
- Operates purely on session metrics (no identity)
"""

from typing import Dict


MIN_RESPONSE_TIME = 0.3          # seconds
MAX_REASONABLE_TIME = 120.0      # seconds
MIN_ACCURACY = 0.0
MAX_ACCURACY = 1.0
MIN_QUESTIONS = 3


def evaluate_session_quality(session_summary: Dict) -> Dict:
    """
    Evaluate whether a session summary is suitable for aggregation.
    """

    data = session_summary.get("data", {})

    issues = []

    # Accuracy bounds
    accuracy = data.get("accuracy_ratio")
    if accuracy is not None:
        if not (MIN_ACCURACY <= accuracy <= MAX_ACCURACY):
            issues.append("invalid_accuracy_range")

    # Time sanity
    avg_time = data.get("avg_time_per_question")
    if avg_time is not None:
        if avg_time < MIN_RESPONSE_TIME:
            issues.append("implausibly_fast_responses")
        if avg_time > MAX_REASONABLE_TIME:
            issues.append("implausibly_slow_responses")

    # Minimum engagement
    total_questions = data.get("total_questions")
    if total_questions is not None:
        if total_questions < MIN_QUESTIONS:
            issues.append("insufficient_engagement")

    quality_status = "valid" if not issues else "flagged"

    return {
        "quality_status": quality_status,
        "issues_detected": issues,
        "eligible_for_aggregation": quality_status == "valid",
    }
