from typing import Dict, Any, List


def build_governance_state(
    oscillation_state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build orchestration governance state.

    IMPORTANT:
    Governance states describe orchestration control behavior,
    not permanent participant characteristics.
    """

    active_modes: List[str] = []

    constraints: Dict[str, Any] = {}

    authority_level = 1.0

    recovery_status = "stable"

    review_flagged = False

    oscillation_score = (
        oscillation_state.get(
            "oscillation_score",
            0.0
        )
    )

    # =====================================
    # Low-authority orchestration mode
    # =====================================

    if oscillation_score >= 0.3:

        active_modes.append(
            "low_authority"
        )

        authority_level = min(
            authority_level,
            0.7
        )

        constraints.update({

            "max_difficulty_shift": 1,

            "confidence_cap": 0.7
        })

        recovery_status = "monitoring"

    # =====================================
    # Stabilization fallback mode
    # =====================================

    if oscillation_score >= 0.5:

        active_modes.append(
            "stabilization"
        )

        authority_level = min(
            authority_level,
            0.5
        )

        constraints.update({

            "freeze_category_switching": True,

            "max_difficulty_shift": 0
        })

        recovery_status = "stabilizing"

    # =====================================
    # Orchestration suppression mode
    # =====================================

    if oscillation_score >= 0.8:

        active_modes.append(
            "suppression"
        )

        authority_level = min(
            authority_level,
            0.2
        )

        constraints.update({

            "suppress_overrides": True
        })

        recovery_status = "suppressed"

        review_flagged = True

    return {

        "active_modes": active_modes,

        "authority_level": round(
            authority_level,
            2
        ),

        "constraints": constraints,

        "recovery_status": recovery_status,

        "review_flagged": review_flagged
    }
