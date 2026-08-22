from project.app.services.routing.signal_arbitrator import SignalArbitrator
from project.app.services.routing.signal_schema import RoutingSignal


def make_signal(
    signal_type,
    value,
    *,
    confidence=1.0,
    priority=1,
    source="test",
    metadata=None,
):
    return RoutingSignal(
        signal_type=signal_type,
        value=value,
        confidence=confidence,
        priority=priority,
        source=source,
        metadata=metadata or {},
    )


def test_strategy_decision_is_evidence_only():
    signal = make_signal(
        "strategy_decision",
        "escalate",
        metadata={
            "question_id": "q1",
            "selected_option": "A",
            "evidence_class": "observation",
        },
    )

    result = SignalArbitrator().resolve([signal])

    assert result["strategy_policy"]["routing_authorized"] is False
    assert result["strategy_policy"]["authorized_directives"] == []

    assert result["stabilize"] is False
    assert result["reduce_difficulty"] is False
    assert result["increase_difficulty"] is False


def test_prediction_signals_do_not_acquire_routing_authority():
    signals = [
        make_signal(
            "likely_response_style",
            "deliberate",
            metadata={"evidence_class": "prediction"},
        ),
        make_signal(
            "risk_under_time_pressure",
            "high",
            metadata={"evidence_class": "prediction"},
        ),
    ]

    result = SignalArbitrator().resolve(signals)

    assert result["stabilize"] is False
    assert result["reduce_difficulty"] is False
    assert result["increase_difficulty"] is False


def test_authorized_temporal_signal_can_still_route():
    signal = make_signal(
        "fatigue_risk",
        "moderate",
        metadata={"evidence_class": "observation"},
    )

    result = SignalArbitrator().resolve([signal])

    assert result["stabilize"] is True


def test_unknown_signal_does_not_acquire_routing_authority():
    signal = make_signal(
        "unknown_signal",
        "increase_difficulty",
        metadata={"evidence_class": "prediction"},
    )

    result = SignalArbitrator().resolve([signal])

    assert result["stabilize"] is False
    assert result["reduce_difficulty"] is False
    assert result["increase_difficulty"] is False

from project.app.services.routing.evidence_authority import (
    evaluate_routing_authority,
)


def test_fatigue_has_explicit_stabilization_authority():
    result = evaluate_routing_authority(
        "fatigue_risk",
        "interpretation",
    )

    assert result["routing_authorized"] is True
    assert result["authorized_directive"] == "stabilize"


def test_latency_has_explicit_reduction_authority():
    result = evaluate_routing_authority(
        "latency_trend",
        "observation",
    )

    assert result["routing_authorized"] is True
    assert result["authorized_directive"] == "reduce_difficulty"


def test_accuracy_has_explicit_escalation_authority():
    result = evaluate_routing_authority(
        "accuracy_trend",
        "observation",
    )

    assert result["routing_authorized"] is True
    assert result["authorized_directive"] == "increase_difficulty"


def test_prediction_has_no_routing_authority():
    result = evaluate_routing_authority(
        "risk_under_time_pressure",
        "prediction",
    )

    assert result["routing_authorized"] is False
    assert result["authorized_directive"] is None


def test_strategy_has_no_direct_routing_authority():
    result = evaluate_routing_authority(
        "strategy_decision",
        "observation",
    )

    assert result["routing_authorized"] is False
    assert result["authorized_directive"] is None


def test_unknown_signal_has_no_routing_authority():
    result = evaluate_routing_authority(
        "unknown_signal",
        "observation",
    )

    assert result["routing_authorized"] is False
    assert result["authorized_directive"] is None

def test_non_authoritative_signal_cannot_route_by_value():
    signal = make_signal(
        "risk_under_time_pressure",
        "increase_difficulty",
        metadata={"evidence_class": "prediction"},
    )

    result = SignalArbitrator().resolve([signal])

    assert result["increase_difficulty"] is False
    assert result["stabilize"] is False
    assert result["reduce_difficulty"] is False

    authority = result["routing_authority"][
        "risk_under_time_pressure"
    ]

    assert authority["routing_authorized"] is False
    assert authority["authorized_directive"] is None

def test_non_authoritative_prediction_cannot_drive_runtime_escalation(
    monkeypatch,
):
    """
    Prove that a prediction signal whose value looks like a routing
    directive cannot cause the runtime to escalate difficulty.
    """

    from project.app.services import tasks

    monkeypatch.setattr(
        tasks,
        "_load_participant_events",
        lambda participant_id: [],
    )

    monkeypatch.setattr(
        tasks,
        "_build_catalog_index",
        lambda: {
            "attention": [
                {
                    "task_id": "difficulty_1",
                    "category": "attention",
                    "difficulty": 1,
                    "instruction": "Difficulty one",
                    "options": ["A", "B"],
                },
                {
                    "task_id": "difficulty_2",
                    "category": "attention",
                    "difficulty": 2,
                    "instruction": "Difficulty two",
                    "options": ["A", "B"],
                },
                {
                    "task_id": "difficulty_3",
                    "category": "attention",
                    "difficulty": 3,
                    "instruction": "Difficulty three",
                    "options": ["A", "B"],
                },
            ]
        },
    )

    monkeypatch.setattr(
        tasks,
        "generate_participant_summary",
        lambda participant_id: {
            "patterns": [],
            "behavior_prediction": {
                "likely_response_style": "deliberate",
                "risk_under_time_pressure": "increase_difficulty",
                "expected_accuracy_trend": "stable",
            },
            "temporal_behavior": {
                "fatigue_risk": None,
                "latency_trend": None,
                "accuracy_trend": None,
                "confidence_trend": None,
            },
        },
    )

    monkeypatch.setattr(
        tasks,
        "_choose_category",
        lambda summary, by_category: "attention",
    )

    monkeypatch.setattr(
        tasks,
        "_choose_difficulty_for_category",
        lambda category, summary, by_category: 2,
    )

    result = tasks.get_next_task_for_participant(
        "prediction-authority-runtime"
    )

    assert isinstance(result, dict)
    assert result["difficulty"] <= 2

    orchestration = result["meta"]["orchestration"]

    assert orchestration["governed_adaptation"][
        "permitted_difficulty"
    ] == 2
