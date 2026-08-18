from project.app.services.routing.selection_trace import (
    build_selection_trace,
)


def test_reevaluation_required_is_exposed_in_governance_influence():
    result = build_selection_trace(
        target_category="attention",
        selected_category="attention",
        selection_reasons=["Target category scored highest"],
        difficulty_adjustment=0,
        governance_state={
            "active_modes": [],
            "reevaluation_required": True,
        },
        resolved_constraints={},
    )

    assert (
        "Runtime reevaluation required by governance"
        in result["governance_influence"]
    )


def test_reevaluation_not_required_preserves_existing_trace():
    result = build_selection_trace(
        target_category="attention",
        selected_category="attention",
        selection_reasons=["Target category scored highest"],
        difficulty_adjustment=0,
        governance_state={
            "active_modes": [],
            "reevaluation_required": False,
        },
        resolved_constraints={},
    )

    assert result["governance_influence"] == []
