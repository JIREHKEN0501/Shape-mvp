from project.app.services.routing.calibration_adapter import (
    calibration_result_to_signal,
    calibration_results_to_signals,
)
from project.app.services.routing.signal_arbitrator import SignalArbitrator


def calibration_result(task_id="pattern_recognition_v1"):
    return {
        "task_id": task_id,
        "model_version": "1.0.0",
        "declared_difficulty": 0.5,
        "empirical_difficulty": 0.7,
        "difficulty_delta": 0.2,
        "confidence": 0.85,
        "confidence_interval_95": (0.6, 0.8),
        "sample_size": 40,
        "confidence_level": "low",
        "calibration_flag": "underestimated",
        "notes": ["low accuracy observed"],
        "drift": None,
    }


def test_calibration_result_becomes_task_calibration_signal():
    signal = calibration_result_to_signal(
        calibration_result(),
        {"pattern_recognition_v1"},
    )

    assert signal is not None
    assert signal.signal_type == "task_calibration"
    assert signal.source == "task_calibration"
    assert signal.metadata["evidence_class"] == "calibration"
    assert signal.metadata["task_id"] == "pattern_recognition_v1"

    assert signal.value["empirical_difficulty"] == 0.7
    assert signal.value["difficulty_delta"] == 0.2
    assert signal.value["confidence_interval_95"] == (0.6, 0.8)
    assert signal.value["sample_size"] == 40


def test_out_of_scope_calibration_is_rejected():
    signal = calibration_result_to_signal(
        calibration_result("unrelated_task"),
        {"pattern_recognition_v1"},
    )

    assert signal is None


def test_malformed_calibration_is_rejected():
    assert calibration_result_to_signal(
        {},
        {"pattern_recognition_v1"},
    ) is None

    assert calibration_result_to_signal(
        None,
        {"pattern_recognition_v1"},
    ) is None


def test_batch_adapter_preserves_only_in_scope_results():
    results = [
        calibration_result("pattern_recognition_v1"),
        calibration_result("strategy_under_constraint_v1"),
        calibration_result("unrelated_task"),
    ]

    signals = calibration_results_to_signals(
        results,
        {
            "pattern_recognition_v1",
            "strategy_under_constraint_v1",
        },
    )

    assert len(signals) == 2
    assert {
        signal.value["task_id"]
        for signal in signals
    } == {
        "pattern_recognition_v1",
        "strategy_under_constraint_v1",
    }

def test_calibration_signal_enters_evidence_without_routing_authority():
    from project.app.services.routing.evidence_builder import EvidenceBuilder
    from project.app.services.routing.signal_arbitrator import SignalArbitrator

    signal = calibration_result_to_signal(
        calibration_result(),
        {"pattern_recognition_v1"},
    )

    assert signal is not None

    context = EvidenceBuilder().build([signal])

    assert len(context.calibration.observations) == 1
    assert (
        context.calibration.observations[0].value["task_id"]
        == "pattern_recognition_v1"
    )

    result = SignalArbitrator().resolve([signal])

    assert result["stabilize"] is False
    assert result["reduce_difficulty"] is False
    assert result["increase_difficulty"] is False

    authority = result["routing_authority"]["task_calibration"]

    assert authority["routing_authorized"] is False
    assert authority["authorized_directive"] is None


def test_malformed_confidence_is_rejected_safely():
    result = calibration_result()
    result["confidence"] = "not-a-number"

    signal = calibration_result_to_signal(
        result,
        {"pattern_recognition_v1"},
    )

    assert signal is None


def test_out_of_range_confidence_is_rejected_safely():
    result = calibration_result()
    result["confidence"] = 1.5

    signal = calibration_result_to_signal(
        result,
        {"pattern_recognition_v1"},
    )

    assert signal is None

def test_low_confidence_calibration_is_preserved_without_routing_authority():
    result = calibration_result()
    result["confidence"] = 0.2
    result["confidence_level"] = "low"

    signal = calibration_result_to_signal(
        result,
        {"pattern_recognition_v1"},
    )

    assert signal is not None
    assert signal.confidence == 0.2

    result = SignalArbitrator().resolve([signal])

    assert result["stabilize"] is False
    assert result["reduce_difficulty"] is False
    assert result["increase_difficulty"] is False

    assert (
        result["routing_authority"]["task_calibration"]["routing_authorized"]
        is False
    )
