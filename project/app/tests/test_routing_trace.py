from project.app.services.routing.routing_trace import (
    generate_routing_trace,
)
from project.app.services.routing.signal_schema import RoutingSignal


def make_signal(
    signal_type,
    value,
    *,
    confidence=1.0,
    priority=1,
    metadata=None,
):
    return RoutingSignal(
        signal_type=signal_type,
        value=value,
        confidence=confidence,
        priority=priority,
        source="test",
        metadata=metadata or {},
    )


def test_routing_trace_preserves_evidence_authority():

    signals = [
        make_signal(
            "fatigue_risk",
            "moderate",
            metadata={
                "evidence_class": "interpretation",
            },
        ),
        make_signal(
            "risk_under_time_pressure",
            "increase_difficulty",
            metadata={
                "evidence_class": "prediction",
            },
        ),
        make_signal(
            "strategy_decision",
            "escalate",
            metadata={
                "evidence_class": "observation",
            },
        ),
    ]

    arbitration_result = {
        "stabilize": True,
        "reduce_difficulty": False,
        "increase_difficulty": False,
        "conflict_detected": False,
        "reasons": [
            "Fatigue risk triggered stabilization",
        ],
        "routing_authority": {
            "fatigue_risk": {
                "routing_authorized": True,
                "authorized_directive": "stabilize",
            },
            "risk_under_time_pressure": {
                "routing_authorized": False,
                "authorized_directive": None,
            },
            "strategy_decision": {
                "routing_authorized": False,
                "authorized_directive": None,
            },
        },
    }

    trace = generate_routing_trace(
        signals,
        arbitration_result,
    )

    assert trace["routing_authority"]["fatigue_risk"][
        "routing_authorized"
    ] is True

    assert trace["routing_authority"]["fatigue_risk"][
        "authorized_directive"
    ] == "stabilize"

    assert trace["routing_authority"][
        "risk_under_time_pressure"
    ]["routing_authorized"] is False

    assert trace["routing_authority"][
        "strategy_decision"
    ]["routing_authorized"] is False


def test_routing_trace_preserves_directives_and_reasoning():

    signals = [
        make_signal(
            "fatigue_risk",
            "moderate",
        ),
    ]

    arbitration_result = {
        "stabilize": True,
        "reduce_difficulty": False,
        "increase_difficulty": False,
        "conflict_detected": False,
        "reasons": [
            "Fatigue risk triggered stabilization",
        ],
        "routing_authority": {
            "fatigue_risk": {
                "routing_authorized": True,
                "authorized_directive": "stabilize",
            },
        },
    }

    trace = generate_routing_trace(
        signals,
        arbitration_result,
    )

    assert trace["routing_directives"]["stabilize"] is True
    assert trace["routing_directives"][
        "increase_difficulty"
    ] is False

    assert (
        "Fatigue risk triggered stabilization"
        in trace["reasoning"]
    )
