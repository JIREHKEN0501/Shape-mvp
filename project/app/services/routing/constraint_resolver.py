from typing import Dict, Any


def resolve_governance_constraints(
    governance_state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resolve effective runtime governance constraints.

    IMPORTANT:
    Constraint resolution governs orchestration behavior,
    not permanent participant characteristics.
    """

    constraints = governance_state.get(
        "constraints",
        {}
    )

    resolved = {

        "max_difficulty_shift": None,

        "confidence_cap": None,

        "freeze_category_switching": False,

        "suppress_overrides": False
    }

    # =====================================
    # Difficulty shift resolution
    # =====================================

    if "max_difficulty_shift" in constraints:

        resolved["max_difficulty_shift"] = (
            constraints["max_difficulty_shift"]
        )

    # =====================================
    # Confidence cap resolution
    # =====================================

    if "confidence_cap" in constraints:

        resolved["confidence_cap"] = (
            constraints["confidence_cap"]
        )

    # =====================================
    # Freeze category switching
    # =====================================

    if constraints.get(
        "freeze_category_switching"
    ):

        resolved[
            "freeze_category_switching"
        ] = True

    # =====================================
    # Suppression override logic
    # =====================================

    if constraints.get(
        "suppress_overrides"
    ):

        resolved[
            "suppress_overrides"
        ] = True

    return resolved
