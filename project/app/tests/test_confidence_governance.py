from project.app.services.routing.confidence_engine import (
    build_orchestration_confidence,
)


def test_governance_confidence_cap_limits_final_score():
    result = build_orchestration_confidence(
        orchestration_health={
            "signal_density": 10,
            "readiness_score": 1.0,
        },
        governance_state={
            "active_modes": [],
        },
        oscillation_state={
            "oscillation_score": 0.0,
        },
        history_depth=10,
        resolved_constraints={
            "confidence_cap": 0.7,
        },
    )

    assert result["score"] <= 0.7
    assert result["governance"]["confidence_cap"] == 0.7
    assert result["governance"]["confidence_cap_active"] is True
    # The existing confidence band definition treats
    # 0.7 as the lower boundary of the high band.
    assert result["band"] == "high"


def test_missing_confidence_cap_preserves_existing_behavior():
    result = build_orchestration_confidence(
        orchestration_health={
            "signal_density": 10,
            "readiness_score": 1.0,
        },
        governance_state={
            "active_modes": [],
        },
        oscillation_state={
            "oscillation_score": 0.0,
        },
        history_depth=10,
        resolved_constraints={
            "confidence_cap": None,
        },
    )

    assert result["score"] > 0.7
    assert result["governance"]["confidence_cap"] is None
    assert result["governance"]["confidence_cap_active"] is False
    assert result["band"] == "high"
