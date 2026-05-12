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
    # Determine orchestration readiness
    # =====================================

    orchestration_ready = signal_density >= 3

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

        "orchestration_ready": orchestration_ready,

        "intervention_count": intervention_count,

        "conflict_detected": resolved_routing.get(
            "conflict_detected",
            False
        ),

        "activity_state": activity_state
    }
