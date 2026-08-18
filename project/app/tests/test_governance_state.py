from project.app.services.routing.governance_state import (
    build_governance_state,
)


def test_governance_state_below_low_authority_threshold():
    result = build_governance_state(
        {"oscillation_score": 0.29}
    )

    assert result["active_modes"] == []
    assert result["authority_level"] == 1.0
    assert result["constraints"] == {}
    assert result["recovery_status"] == "stable"
    assert result["review_flagged"] is False


def test_governance_state_enters_low_authority_at_boundary():
    result = build_governance_state(
        {"oscillation_score": 0.30}
    )

    assert result["active_modes"] == [
        "low_authority"
    ]
    assert result["authority_level"] == 0.7
    assert result["constraints"] == {
        "max_difficulty_shift": 1,
        "confidence_cap": 0.7,
    }
    assert result["recovery_status"] == "monitoring"
    assert result["review_flagged"] is False


def test_governance_state_enters_stabilization_at_boundary():
    result = build_governance_state(
        {"oscillation_score": 0.50}
    )

    assert result["active_modes"] == [
        "low_authority",
        "stabilization",
    ]
    assert result["authority_level"] == 0.5
    assert result["constraints"] == {
        "max_difficulty_shift": 0,
        "confidence_cap": 0.7,
        "freeze_category_switching": True,
    }
    assert result["recovery_status"] == "stabilizing"
    assert result["review_flagged"] is False


def test_governance_state_enters_suppression_at_boundary():
    result = build_governance_state(
        {"oscillation_score": 0.80}
    )

    assert result["active_modes"] == [
        "low_authority",
        "stabilization",
        "suppression",
    ]
    assert result["authority_level"] == 0.2
    assert result["constraints"] == {
        "max_difficulty_shift": 0,
        "confidence_cap": 0.7,
        "freeze_category_switching": True,
        "suppress_overrides": True,
    }
    assert result["recovery_status"] == "suppressed"
    assert result["review_flagged"] is True


def test_governance_precedence_tightens_without_removing_prior_constraints():
    low = build_governance_state(
        {"oscillation_score": 0.30}
    )
    stabilization = build_governance_state(
        {"oscillation_score": 0.50}
    )
    suppression = build_governance_state(
        {"oscillation_score": 0.80}
    )

    assert (
        stabilization["authority_level"]
        < low["authority_level"]
    )

    assert (
        stabilization["constraints"]
        ["max_difficulty_shift"]
        < low["constraints"]
        ["max_difficulty_shift"]
    )

    assert (
        stabilization["constraints"]
        ["confidence_cap"]
        == low["constraints"]
        ["confidence_cap"]
    )

    assert (
        stabilization["constraints"]
        ["freeze_category_switching"]
        is True
    )

    assert (
        suppression["authority_level"]
        < stabilization["authority_level"]
    )

    assert (
        suppression["constraints"]
        ["max_difficulty_shift"]
        == stabilization["constraints"]
        ["max_difficulty_shift"]
    )

    assert (
        suppression["constraints"]
        ["confidence_cap"]
        == stabilization["constraints"]
        ["confidence_cap"]
    )

    assert (
        suppression["constraints"]
        ["freeze_category_switching"]
        is True
    )

    assert (
        suppression["constraints"]
        ["suppress_overrides"]
        is True
    )

    assert (
        suppression["review_flagged"]
        is True
    )


def test_governance_state_defaults_missing_oscillation_score_to_stable():
    result = build_governance_state({})

    assert result["active_modes"] == []
    assert result["authority_level"] == 1.0
    assert result["constraints"] == {}
    assert result["recovery_status"] == "stable"
    assert result["review_flagged"] is False
