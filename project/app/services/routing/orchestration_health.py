from typing import List, Dict, Any

from .signal_schema import RoutingSignal


def evaluate_orchestration_health(
    signals: List[RoutingSignal],
    resolved_routing: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate orchestration readiness and governance activity.

    IMPORTANT:
    Health metrics describe orchestration state only.
    They do not represent permanent participant traits.
    """

    signal_density = len(signals)

    intervention_count = 0

    # =====================================
    # Count governance interventions
    # =====================================

    for key in (
        "stabilize",
        "reduce_difficulty",
        "increase_difficulty"
    ):

        if resolved_routing.get(key):
            intervention_count += 1

    # =====================================
    # Average signal confidence
    # =====================================

    if signal_density > 0:

        average_confidence = sum(
            s.confidence for s in signals
        ) / signal_density

    else:

        average_confidence = 0.0

    # =====================================
    # Conflict penalty
    # =====================================

    conflict_detected = resolved_routing.get(
        "conflict_detected",
        False
    )

    conflict_penalty = 0.15 if conflict_detected else 0.0

    # =====================================
    # Intervention pressure penalty
    # =====================================

    intervention_penalty = (
        intervention_count * 0.05
    )

    # =====================================
    # Weighted readiness score
    # =====================================

    density_score = min(
        signal_density / 5,
        1.0
    )

    readiness_score = (
        (density_score * 0.4)
        +
        (average_confidence * 0.5)
        -
        conflict_penalty
        -
        intervention_penalty
    )

    readiness_score = max(
        min(readiness_score, 1.0),
        0.0
    )

    # =====================================
    # Readiness state
    # =====================================

    orchestration_ready = (
        readiness_score >= 0.55
    )

    # =====================================
    # Determine governance activity state
    # =====================================

    if signal_density == 0:

        activity_state = "inactive"

    elif not orchestration_ready:

        activity_state = "observational"

    elif intervention_count == 0:

        activity_state = "monitoring"

    elif resolved_routing.get("stabilize"):

        activity_state = "stabilizing"

    else:

        activity_state = "active"

    # =====================================
    # Build telemetry payload
    # =====================================

    return {

        "signal_density": signal_density,

        "average_confidence": round(
            average_confidence,
            2
        ),

        "readiness_score": round(
            readiness_score,
            2
        ),

        "orchestration_ready": orchestration_ready,

        "intervention_count": intervention_count,

        "conflict_detected": conflict_detected,

        "activity_state": activity_state
    }
