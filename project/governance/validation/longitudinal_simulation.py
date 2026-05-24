from dataclasses import dataclass

@dataclass
class LongitudinalSessionState:
    """
    Represents a single longitudinal
    orchestration-governance cycle.

    Tracks adaptive instability evolution
    and governance-mediated stabilization
    behavior over time.
    """

    cycle_index: int

    instability_level: float

    instability_velocity: float

    escalation_pressure: float

    governance_status: str

    arbitration_active: bool

    topology_integrity: str

    authority_ceiling: float

    reevaluation_required: bool

    stabilization_trend: str

    difficulty_shift: int

def evaluate_stabilization_trend(
    instability_level: float,
    previous_instability: float,
) -> str:
    """
    Evaluate whether orchestration instability
    is stabilizing, escalating, or remaining
    unstable longitudinally.
    """

    if instability_level < previous_instability:
        return "stabilizing"

    if instability_level > previous_instability:
        return "escalating"

    return "stable"

def initialize_longitudinal_state(
    cycle_index: int = 0,
) -> LongitudinalSessionState:
    """
    Initialize early-session orchestration
    state with low governance pressure.
    """

    return LongitudinalSessionState(

        cycle_index=cycle_index,

        instability_level=0.1,

        instability_velocity=0.0,

        escalation_pressure=0.1,

        governance_status="stable",

        arbitration_active=False,

        topology_integrity="stable",

        authority_ceiling=1.0,

        reevaluation_required=False,

        stabilization_trend="stable",

        difficulty_shift=0,
    )


def evolve_longitudinal_state(
    previous_state: LongitudinalSessionState,
) -> LongitudinalSessionState:
    """
    Evolve orchestration-governance state
    longitudinally through accumulated
    instability pressure and governance
    mediation.

    This models bounded orchestration
    adaptation rather than autonomous
    cognition or psychology.
    """

    next_cycle = (
        previous_state.cycle_index + 1
    )

    instability_level = (
        previous_state.instability_level
    )

    escalation_pressure = (
        previous_state.escalation_pressure
    )

    # =====================================
    # Escalation pressure evolution
    # =====================================

    pressure_growth = 0.15

    # Governance stabilization damping
    if previous_state.arbitration_active:

        pressure_growth -= 0.05

    if previous_state.authority_ceiling < 0.7:

        pressure_growth -= 0.03

    if previous_state.reevaluation_required:

        pressure_growth -= 0.02

    # =====================================
    # Anticipatory stabilization damping
    # =====================================

    if previous_state.instability_velocity > 0.08:

        pressure_growth -= 0.03

    if previous_state.instability_velocity > 0.12:

        pressure_growth -= 0.02
        # Prevent negative escalation collapse
        pressure_growth = max(
            pressure_growth,
            0.02
        )

    escalation_pressure += pressure_growth

    # =====================================
    # Instability accumulation
    # =====================================

    instability_delta = (
        escalation_pressure * 0.2
    )

    # Stabilization recovery pressure
    if previous_state.arbitration_active:

        instability_delta -= 0.05

    if previous_state.topology_integrity == "violated":

        instability_delta -= 0.08

    instability_level += instability_delta

    # Prevent invalid negative instability
    instability_level = max(
        instability_level,
        0.05
    )
    # =====================================
    # Governance response thresholds
    # =====================================

    governance_status = "stable"

    arbitration_active = False

    authority_ceiling = 1.0

    reevaluation_required = False

    topology_integrity = "stable"

    difficulty_shift = 1

    # Moderate instability
    if instability_level >= 0.5:

        governance_status = "degraded"

        arbitration_active = True

        authority_ceiling = 0.6

        reevaluation_required = True

        difficulty_shift = 0

    # High instability
    if instability_level >= 0.8:

        governance_status = "critical"

        arbitration_active = True

        authority_ceiling = 0.3

        reevaluation_required = True

        topology_integrity = "violated"

        difficulty_shift = -1

        # Governance stabilization pressure
        instability_level -= 0.2

    instability_velocity = round(
        instability_level
        - previous_state.instability_level,
        2
    )

    stabilization_trend = (
        evaluate_stabilization_trend(
            instability_level,
            previous_state.instability_level,
        )
    )

    return LongitudinalSessionState(

        cycle_index=next_cycle,

        instability_level=round(
            instability_level,
            2
        ),

        instability_velocity=(
            instability_velocity
        ),

        escalation_pressure=round(
            escalation_pressure,
            2
        ),

        governance_status=(
            governance_status
        ),

        arbitration_active=(
            arbitration_active
        ),

        topology_integrity=(
            topology_integrity
        ),

        authority_ceiling=(
            authority_ceiling
        ),

        reevaluation_required=(
            reevaluation_required
        ),

        stabilization_trend=(
            stabilization_trend
        ),

        difficulty_shift=(
            difficulty_shift
        ),
    )

def run_longitudinal_simulation(
    total_cycles: int = 10,
) -> list[LongitudinalSessionState]:
    """
    Run longitudinal orchestration-governance
    evolution across multiple sequential cycles.

    Used to validate whether governance-mediated
    adaptation stabilizes coherently over time.
    """

    states = []

    current_state = (
        initialize_longitudinal_state()
    )

    states.append(current_state)

    for _ in range(total_cycles - 1):

        current_state = (
            evolve_longitudinal_state(
                current_state
            )
        )

        states.append(current_state)

    return states

def print_simulation_summary(
    states: list[LongitudinalSessionState],
) -> None:
    """
    Print longitudinal governance evolution
    summary for behavioral inspection.
    """

    print(
        "\n=== LONGITUDINAL GOVERNANCE "
        "SIMULATION ===\n"
    )

    for state in states:

        print(
            f"cycle: {state.cycle_index}"
        )

        print(
            f"instability_level: "
            f"{state.instability_level}"
        )

        print(
            f"escalation_pressure: "
            f"{state.escalation_pressure}"
        )

        print(
            f"governance_status: "
            f"{state.governance_status}"
        )

        print(
            f"arbitration_active: "
            f"{state.arbitration_active}"
        )

        print(
            f"topology_integrity: "
            f"{state.topology_integrity}"
        )

        print(
            f"authority_ceiling: "
            f"{state.authority_ceiling}"
        )

        print(
            f"reevaluation_required: "
            f"{state.reevaluation_required}"
        )

        print(
            f"stabilization_trend: "
            f"{state.stabilization_trend}"
        )

        print(
            f"difficulty_shift: "
            f"{state.difficulty_shift}"
        )

        print("---")


def generate_longitudinal_insights(
    states: list[LongitudinalSessionState],
) -> list[str]:
    """
    Generate interpretable longitudinal
    governance observations from simulation
    behavior over time.
    """

    insights = []

    critical_cycles = [
        s for s in states
        if s.governance_status == "critical"
    ]

    degraded_cycles = [
        s for s in states
        if s.governance_status == "degraded"
    ]

    stabilizing_cycles = [
        s for s in states
        if s.stabilization_trend
        == "stabilizing"
    ]

    # =====================================
    # Governance escalation observations
    # =====================================

    if degraded_cycles:

        insights.append(
            f"Governance degradation emerged "
            f"across {len(degraded_cycles)} "
            f"cycles."
        )

    if critical_cycles:

        insights.append(
            f"Critical governance pressure "
            f"occurred across "
            f"{len(critical_cycles)} cycles."
        )

    # =====================================
    # Stabilization observations
    # =====================================

    if stabilizing_cycles:

        insights.append(
            f"Stabilization behavior emerged "
            f"during {len(stabilizing_cycles)} "
            f"cycles."
        )

    # =====================================
    # Oscillation observations
    # =====================================

    governance_transitions = 0

    previous_status = (
        states[0].governance_status
    )

    for state in states[1:]:

        if (
            state.governance_status
            != previous_status
        ):

            governance_transitions += 1

        previous_status = (
            state.governance_status
        )

    insights.append(
        f"Governance state transitioned "
        f"{governance_transitions} times "
        f"longitudinally."
    )

    # =====================================
    # Final instability interpretation
    # =====================================

    final_state = states[-1]

    if final_state.instability_level < 0.5:

        insights.append(
            "Longitudinal instability "
            "remained bounded."
        )

    elif final_state.instability_level < 0.8:

        insights.append(
            "Longitudinal instability "
            "partially stabilized under "
            "governance mediation."
        )

    else:

        insights.append(
            "Longitudinal instability "
            "remained critically elevated."
        )

    return insights
