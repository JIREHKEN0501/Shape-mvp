from typing import List, Dict, Any


def detect_orchestration_oscillation(
    orchestration_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Detect orchestration instability patterns.

    IMPORTANT:
    Oscillation metrics describe orchestration behavior,
    not permanent participant characteristics.
    """

    if len(orchestration_history) < 3:

        return {
            "oscillation_detected": False,
            "oscillation_score": 0.0,
            "reasons": [
                "Insufficient orchestration history"
            ]
        }

    readiness_values = []
    activity_states = []
    intervention_counts = []

    # =====================================
    # Extract telemetry history
    # =====================================

    for entry in orchestration_history:

        health = entry.get("health", {})

        readiness_values.append(
            health.get("readiness_score", 0.0)
        )

        activity_states.append(
            health.get("activity_state", "inactive")
        )

        intervention_counts.append(
            health.get("intervention_count", 0)
        )

    reasons = []

    oscillation_score = 0.0

    # =====================================
    # Readiness volatility detection
    # =====================================

    readiness_range = (
        max(readiness_values)
        -
        min(readiness_values)
    )

    if readiness_range >= 0.5:

        oscillation_score += 0.4

        reasons.append(
            "High readiness volatility detected"
        )

    # =====================================
    # Governance state volatility
    # =====================================

    unique_states = len(
        set(activity_states)
    )

    if unique_states >= 3:

        oscillation_score += 0.3

        reasons.append(
            "Governance activity instability detected"
        )

    # =====================================
    # Intervention volatility
    # =====================================

    intervention_range = (
        max(intervention_counts)
        -
        min(intervention_counts)
    )

    if intervention_range >= 2:

        oscillation_score += 0.3

        reasons.append(
            "Intervention volatility detected"
        )

    oscillation_detected = (
        oscillation_score >= 0.5
    )

    return {

        "oscillation_detected": oscillation_detected,

        "oscillation_score": round(
            oscillation_score,
            2
        ),

        "reasons": reasons
    }
