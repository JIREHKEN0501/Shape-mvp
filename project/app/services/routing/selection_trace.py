from typing import Dict, Any, List


def build_selection_trace(
    target_category: str,
    selected_category: str,
    selection_reasons: List[str],
    difficulty_adjustment: int,
    governance_state: Dict[str, Any],
    resolved_constraints: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build orchestration selection explainability trace.

    IMPORTANT:
    Selection traces describe orchestration behavior only.
    They do not represent permanent participant traits.
    """

    category_deviation = (
        target_category != selected_category
    )

    deviation_reasons = []

    if category_deviation:

        deviation_reasons.append(
            "Higher-ranked task selected outside target category"
        )

    difficulty_reasoning = []

    if difficulty_adjustment > 0:

        difficulty_reasoning.append(
            "Difficulty increased through adaptive orchestration"
        )

    elif difficulty_adjustment < 0:

        difficulty_reasoning.append(
            "Difficulty reduced through adaptive orchestration"
        )

    else:

        difficulty_reasoning.append(
            "Difficulty remained stable"
        )

    governance_influence = []

    active_modes = governance_state.get(
        "active_modes",
        []
    )

    if active_modes:

        governance_influence.append(
            f"Governance modes active: {active_modes}"
        )

    if resolved_constraints.get(
        "max_difficulty_shift"
    ) == 0:

        governance_influence.append(
            "Difficulty adaptation constrained by governance"
        )

    if resolved_constraints.get(
        "freeze_category_switching"
    ):
        governance_influence.append(
            "Category switching restricted by stabilization governance"
        )

    if governance_state.get(
        "reevaluation_required"
    ):
        governance_influence.append(
            "Runtime reevaluation required by governance"
        )

    reasoning_parts = []

    if category_deviation:

        reasoning_parts.append(

            f"{selected_category} selected "
            f"over {target_category}"
        )

    else:

        reasoning_parts.append(

            f"{selected_category} selected "
            "as target-aligned category"
        )

    if selection_reasons:

        reasoning_parts.append(
            selection_reasons[0]
        )

    if governance_influence:

        reasoning_parts.append(
            "under active governance constraints"
        )

    final_selection_reason = (
        ". ".join(reasoning_parts) + "."
    )

    return {

        "target_category": target_category,

        "selected_category": selected_category,

        "category_deviation": category_deviation,

        "deviation_reasons": deviation_reasons,

        "difficulty_reasoning": difficulty_reasoning,

        "governance_influence": governance_influence,

        "selection_factors": selection_reasons,

        "final_selection_reason":
            final_selection_reason
    }
