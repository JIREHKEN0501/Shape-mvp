from dataclasses import dataclass

from project.governance.validation.longitudinal_simulation import (
    LongitudinalSessionState,
)

from project.governance.validation.oscillation_analysis import (
    OscillationAnalysis,
)
CAUTIOUS_STABILIZATION_VARIANTS = [

    (
        "Recovery patterns became gradually "
        "more consistent when pacing adjustments "
        "slowed, though stabilization still "
        "appeared to require sustained support continuity."
    ),

    (
        "Progression stability improved when "
        "challenge escalation became more gradual, "
        "though recovery continuity still remained "
        "sensitive to sustained pressure."
    ),
]

SUSTAINED_OVERLOAD_VARIANTS = [

    (
        "Sustained overload continued disrupting "
        "progression, and recovery patterns remained "
        "inconsistent despite support adjustments."
    ),

    (
        "Challenge pressure continued exceeding "
        "stable recovery capacity, limiting "
        "progression continuity despite pacing adjustments."
    ),
]

FRAGILE_CONTINUITY_VARIANTS = [

    (
        "Recovery patterns improved temporarily "
        "when pacing adjustments became more gradual, "
        "though stabilization continuity remained "
        "difficult to sustain under renewed challenge pressure."
    ),

    (
        "Support adjustments briefly improved "
        "recovery consistency, though progression "
        "stability weakened again when challenge "
        "pressure increased."
    ),
]

STRENGTHENING_RECOVERY_VARIANTS = [

    (
        "Recovery behavior became increasingly "
        "consistent over time, particularly "
        "when pacing changes remained gradual "
        "and support continuity stayed stable."
    ),

    (
        "Progression continuity strengthened "
        "as pacing stability improved, suggesting "
        "recovery patterns were becoming more durable."
    ),
]

ADAPTIVE_RESPONSIVENESS_VARIANTS = [

    (
        "Progression remained responsive to "
        "pacing adjustments, and recovery "
        "continuity stayed relatively stable "
        "throughout the learning cycle."
    ),

    (
        "Support pacing remained effective "
        "throughout the learning cycle, allowing "
        "progression continuity to remain stable."
    ),
]

UNSTABLE_PROGRESSION_VARIANTS = [

    (
        "Progression continuity remained difficult "
        "to stabilize consistently under sustained "
        "challenge pressure."
    ),

    (
        "Recovery patterns remained inconsistent, "
        "suggesting pacing adjustments may still "
        "require additional stabilization support."
    ),
]

def select_narrative_variant(

    variants: list[str],

    states: list[LongitudinalSessionState],

) -> str:

    index = (
        len(states)
        + int(
            states[-1].instability_level * 10
        )
    ) % len(variants)

    return variants[index]

@dataclass
class ProgressionInterpretation:

    progression_summary: str

    narrative_archetype: str

    pacing_condition: str

    stabilization_condition: str

    governance_condition: str

    interpretation_confidence: str


def interpret_progression_behavior(

    states: list[LongitudinalSessionState],

    oscillation_analysis: OscillationAnalysis,

) -> ProgressionInterpretation:

    final_state = states[-1]

    avg_confidence = round(

        sum(
            state.stabilization_confidence
            for state in states
        )
        / len(states),

        2
    )

    # =====================================
    # Stabilization relapse detection
    # =====================================

    stabilization_emerged = any(

        state.stabilization_streak > 0

        for state in states
    )

    stabilization_relapsed = False

    relapse_events = 0

    for index in range(1, len(states)):

        previous_state = states[index - 1]

        current_state = states[index]

        if (

            previous_state.stabilization_streak > 0

            and current_state.stabilization_streak == 0

            and current_state.instability_level
            > previous_state.instability_level
        ):

            stabilization_relapsed = True

            relapse_events += 1

    max_stabilization_streak = max(

        state.stabilization_streak

        for state in states
    )

    stabilization_cycles = sum(

        1

        for state in states

        if state.stabilization_trend
        == "stabilizing"
    )

    critical_cycles = sum(

        1

        for state in states

        if state.governance_status
        == "critical"
    )

    recovery_strength_score = round(

        (
            max_stabilization_streak
            * 0.30
        )

        +

        (
            avg_confidence
            * 0.40
        )

        +

        (
            stabilization_cycles
            * 0.10
        )

        -

        (
            relapse_events
            * 0.15
        )

        -

        (
            critical_cycles
            * 0.20
        ),

        2
    )
        
    # =====================================
    # Pacing condition
    # =====================================

    if final_state.instability_level >= 0.85:

        pacing_condition = (
            "Sustained overload pressure detected."
        )

    elif final_state.instability_level >= 0.60:

        pacing_condition = (
            "Adaptive pacing strain remains elevated."
        )

    else:

        pacing_condition = (
            "Adaptive pacing remained manageable."
        )

    # =====================================
    # Stabilization condition
    # =====================================

    if avg_confidence >= 0.60:

        stabilization_condition = (
            "Stabilization behavior became increasingly durable."
        )

    elif avg_confidence >= 0.35:

        stabilization_condition = (
            "Partial stabilization behavior emerged intermittently."
        )

    else:

        stabilization_condition = (
            "Stabilization continuity remained limited."
        )

    # =====================================
    # Governance condition
    # =====================================

    if (
        oscillation_analysis
        .oscillation_pattern
        == "destabilizing_oscillation"
    ):

        governance_condition = (
            "Governance mediation remained under prolonged strain."
        )

    else:

        governance_condition = (
            "Governance mediation remained bounded and adaptive."
        )

    # =====================================
    # Interpretation confidence
    # =====================================

    if (
        final_state.stabilization_confidence
        >= 0.60
    ):

        interpretation_confidence = (
            "strengthening"
        )

    elif (
        final_state.stabilization_confidence
        >= 0.35
    ):

        interpretation_confidence = (
            "emerging"
        )

    else:

        interpretation_confidence = (
            "unstable"
        )

    # =====================================
    # Narrative archetype synthesis
    # =====================================

    if (
        oscillation_analysis.oscillation_pattern
        == "destabilizing_oscillation"

        and critical_cycles > stabilization_cycles
    ):

        narrative_archetype = (
            "sustained_overload"
        )

        progression_summary = (
            select_narrative_variant(
                SUSTAINED_OVERLOAD_VARIANTS,
                states,
            )
        )

    elif (

        recovery_strength_score >= 0.90

        and max_stabilization_streak >= 3

        and not (
            stabilization_relapsed
            and critical_cycles > 0
        )
    ):

        narrative_archetype = (
            "strengthening_recovery"
        )

        progression_summary = (
            select_narrative_variant(
                STRENGTHENING_RECOVERY_VARIANTS,
                states,
            )
        )

    elif (
        stabilization_emerged

        and stabilization_relapsed

        and (
            critical_cycles > 0
            or recovery_strength_score < 0.75
        )
    ):

        narrative_archetype = (
            "fragile_continuity"
        )

        progression_summary = (
            select_narrative_variant(
                FRAGILE_CONTINUITY_VARIANTS,
                states,
            )
        )

    elif (
        oscillation_analysis.oscillation_pattern
        == "bounded_oscillation"
        and avg_confidence >= 0.35
    ):

        narrative_archetype = (
            "cautious_stabilization"
        )

        progression_summary = (
            select_narrative_variant(
                CAUTIOUS_STABILIZATION_VARIANTS,
                states,
            )
        )

    elif (
        final_state.stabilization_confidence
        < 0.35
    ):

        narrative_archetype = (
            "unstable_progression"
        )

        progression_summary = (
            select_narrative_variant(
                UNSTABLE_PROGRESSION_VARIANTS,
                states,
            )
        )

    else:

        narrative_archetype = (
            "adaptive_responsiveness"
        )

        progression_summary = (
            select_narrative_variant(
                ADAPTIVE_RESPONSIVENESS_VARIANTS,
                states,
            )
        )

    return ProgressionInterpretation(

        progression_summary=(
            progression_summary
        ),

        narrative_archetype=(
            narrative_archetype
        ),

        pacing_condition=(
            pacing_condition
        ),

        stabilization_condition=(
            stabilization_condition
        ),

        governance_condition=(
            governance_condition
        ),

        interpretation_confidence=(
            interpretation_confidence
        ),
    )
