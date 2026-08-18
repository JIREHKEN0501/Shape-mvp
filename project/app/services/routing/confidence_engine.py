from typing import Dict, Any


TEMPORAL_MIN_HISTORY = 5

TEMPORAL_CONFIDENCE_CEILING = 0.5


def build_orchestration_confidence(
    orchestration_health: Dict[str, Any],
    governance_state: Dict[str, Any],
    oscillation_state: Dict[str, Any],
    history_depth: int,

    resolved_constraints: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Evaluate orchestration evidential reliability.

    IMPORTANT:
    Confidence scores describe orchestration reliability only.
    They do not represent participant truthfulness,
    intelligence, or permanent behavioral characteristics.
    """

    # =====================================
    # Contribution initialization
    # =====================================

    signal_density_contribution = 0.0
    arbitration_contribution = 0.0
    temporal_consistency_contribution = None

    governance_penalty = 0.0
    instability_penalty = 0.0

    if resolved_constraints is None:
        resolved_constraints = {}

    confidence_cap = resolved_constraints.get(
        "confidence_cap"
    )

    # =====================================
    # Signal density contribution
    # =====================================

    signal_density = orchestration_health.get(
        "signal_density",
        0
    )

    signal_density_contribution = min(
        signal_density * 0.08,
        0.24
    )

    # =====================================
    # Arbitration contribution
    # =====================================

    readiness_score = orchestration_health.get(
        "readiness_score",
        0.0
    )

    arbitration_contribution = min(
        readiness_score * 0.4,
        0.3
    )

    # =====================================
    # Temporal consistency contribution
    # =====================================

    temporal_ceiling_active = False

    temporal_legitimacy_ready = (

        history_depth >= TEMPORAL_MIN_HISTORY

        and signal_density >= 1

        and readiness_score > 0
    )

    if temporal_legitimacy_ready:

        oscillation_score = oscillation_state.get(
            "oscillation_score",
            0.0
        )

        temporal_consistency_contribution = max(
            0.0,
            0.25 - (oscillation_score * 0.25)
        )

    else:

        temporal_ceiling_active = True

    # =====================================
    # Governance penalties
    # =====================================

    active_modes = governance_state.get(
        "active_modes",
        []
    )

    if "low_authority" in active_modes:
        governance_penalty += 0.10

    if "stabilization" in active_modes:
        governance_penalty += 0.15

    if "cooldown" in active_modes:
        governance_penalty += 0.10

    if "suppression" in active_modes:
        governance_penalty += 0.30

    # =====================================
    # Instability penalties
    # =====================================

    oscillation_score = oscillation_state.get(
        "oscillation_score",
        0.0
    )

    instability_penalty = (
        oscillation_score * 0.25
    )

    # =====================================
    # Compute confidence score
    # =====================================

    confidence_score = (
        signal_density_contribution
        + arbitration_contribution
        - governance_penalty
        - instability_penalty
    )

    if (
        temporal_consistency_contribution
        is not None
    ):

        confidence_score += (
            temporal_consistency_contribution
        )

    confidence_score = max(
        0.0,
        min(1.0, confidence_score)
    )

    # =====================================
    # Temporal ceiling enforcement
    # =====================================

    if temporal_ceiling_active:

        confidence_score = min(
            confidence_score,
            TEMPORAL_CONFIDENCE_CEILING
        )

    # =====================================
    # Confidence banding
    # =====================================

    if confidence_score < 0.3:

        confidence_band = "low"

    elif confidence_score < 0.7:

        confidence_band = "moderate"

    else:

        confidence_band = "high"

    # =====================================
    # Confidence note synthesis
    # =====================================

    if temporal_ceiling_active:

        note = (
            "Confidence capped pending sufficient "
            "longitudinal orchestration consistency."
        )

    elif governance_penalty > 0:

        note = (
            "Confidence reduced due to active "
            "governance stabilization constraints."
        )

    elif instability_penalty > 0.15:

        note = (
            "Confidence reduced due to orchestration "
            "instability patterns."
        )

    elif signal_density < 2:

        note = (
            "Confidence limited by insufficient "
            "orchestration evidence."
        )

    else:

        note = (
            "Confidence supported by stable "
            "orchestration behavior and "
            "consistent routing signals."
        )

    # =====================================
    # Operational presence floor
    # =====================================

    suppression_active = (
        "suppression" in governance_state.get(
            "active_modes",
            []
        )
    )

    if (

        confidence_score == 0.0

        and temporal_ceiling_active

        and not suppression_active
    ):

        confidence_score = 0.05




    # =====================================
    # Governance confidence cap
    # =====================================

    confidence_cap_active = (
        confidence_cap is not None
    )

    if confidence_cap_active:
        confidence_score = min(
            confidence_score,
            float(confidence_cap)
        )

    # Recompute confidence band after all
    # final confidence ceilings are applied.
    if confidence_score < 0.3:
        confidence_band = "low"
    elif confidence_score < 0.7:
        confidence_band = "moderate"
    else:
        confidence_band = "high"
# =====================================
    # Final confidence payload
    # =====================================

    return {

        "score": round(
            confidence_score,
            3
        ),

        "band": confidence_band,

        "governance": {
            "confidence_cap": confidence_cap,
            "confidence_cap_active": confidence_cap_active,
        },

        "components": {

            "signal_density_contribution":
                round(
                    signal_density_contribution,
                    3
                ),

            "arbitration_contribution":
                round(
                    arbitration_contribution,
                    3
                ),

            "temporal_consistency_contribution":
                (
                    round(
                        temporal_consistency_contribution,
                        3
                    )
                    if temporal_consistency_contribution
                    is not None
                    else None
                ),

            "governance_penalty":
                round(
                    governance_penalty,
                    3
                ),

            "instability_penalty":
                round(
                    instability_penalty,
                    3
                )
        },

        "constraints": {

            "temporal_ceiling_active":
                temporal_ceiling_active
        },

        "note": note
    }
