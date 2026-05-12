from typing import Dict, Any, List

from .signal_schema import RoutingSignal


def generate_routing_trace(
    signals: List[RoutingSignal],
    arbitration_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate explainable routing trace.

    IMPORTANT:
    Trace explanations describe session-level adaptation decisions only.
    They must NOT be interpreted as permanent psychological judgments.
    """

    signal_trace = []

    # -----------------------------------
    # Serialize signals
    # -----------------------------------

    for signal in signals:

        signal_trace.append({
            "signal_type": signal.signal_type,
            "value": signal.value,
            "confidence": signal.confidence,
            "priority": signal.priority,
            "source": signal.source
        })

    # -----------------------------------
    # Determine dominant signals
    # -----------------------------------

    dominant_signals = sorted(
        signal_trace,
        key=lambda s: (
            s["priority"],
            s["confidence"]
        ),
        reverse=True
    )[:3]

    # -----------------------------------
    # Build transparency trace
    # -----------------------------------

    trace = {
        "routing_status": "resolved",

        "signals_considered": signal_trace,

        "dominant_signals": dominant_signals,

        "routing_directives": {
            "stabilize": arbitration_result.get("stabilize"),
            "reduce_difficulty": arbitration_result.get("reduce_difficulty"),
            "increase_difficulty": arbitration_result.get("increase_difficulty"),
        },

        "conflict_detected": arbitration_result.get(
            "conflict_detected",
            False
        ),

        "reasoning": arbitration_result.get(
            "reasons",
            []
        ),

        "transparency_note": (
            "Routing traces describe adaptive session-level orchestration "
            "behavior and should not be interpreted as permanent personal characteristics."
        )
    }

    return trace
