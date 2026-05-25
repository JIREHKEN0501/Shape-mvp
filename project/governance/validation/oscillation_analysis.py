from dataclasses import dataclass

@dataclass
class OscillationAnalysis:

    oscillation_pattern: str

    governance_transitions: int

    stabilization_cycles: int

    critical_cycles: int

    interpretation: str

def classify_oscillation_behavior(
    states,
) -> OscillationAnalysis:
    """
    Classify longitudinal governance
    oscillation behavior.

    Used to distinguish bounded adaptive
    stabilization from destabilizing
    governance dynamics.
    """

    governance_transitions = 0

    stabilization_cycles = 0

    critical_cycles = 0

    previous_status = (
        states[0].governance_status
    )

    for state in states:

        if (
            state.stabilization_trend
            == "stabilizing"
        ):

            stabilization_cycles += 1

        if (
            state.governance_status
            == "critical"
        ):

            critical_cycles += 1

        if (
            state.governance_status
            != previous_status
        ):

            governance_transitions += 1

        previous_status = (
            state.governance_status
        )

    # =====================================
    # Oscillation interpretation
    # =====================================

    oscillation_pattern = (
        "bounded_oscillation"
    )

    interpretation = (
        "Governance mediation remained "
        "adaptive and bounded."
    )

    # Excessive instability
    if critical_cycles >= 4:

        oscillation_pattern = (
            "destabilizing_oscillation"
        )

        interpretation = (
            "Governance entered prolonged "
            "critical instability."
        )

    # Excessive switching
    elif governance_transitions >= 7:

        oscillation_pattern = (
            "chaotic_transitioning"
        )

        interpretation = (
            "Governance transitions became "
            "excessively unstable."
        )

    # Over-suppression
    elif (
        stabilization_cycles >= 5
        and critical_cycles == 0
    ):

        oscillation_pattern = (
            "rigid_stabilization"
        )

        interpretation = (
            "Governance stabilization may "
            "be overly suppressive."
        )

    return OscillationAnalysis(

        oscillation_pattern=(
            oscillation_pattern
        ),

        governance_transitions=(
            governance_transitions
        ),

        stabilization_cycles=(
            stabilization_cycles
        ),

        critical_cycles=(
            critical_cycles
        ),

        interpretation=(
            interpretation
        ),
    )


