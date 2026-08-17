from dataclasses import dataclass

from project.governance.validation.governance_envelope import (
    GovernanceEnvelope,
)

@dataclass(frozen=True)
class GovernedAdaptationResult:
    """
    Governance-mediated adaptation result.

    Represents constitutionally bounded
    difficulty adaptation shaping.
    """

    permitted_difficulty: int

    escalation_constrained: bool

    recovery_constrained: bool

    governance_reason: str

def mediate_difficulty_adjustment(
    base_difficulty: int,

    proposed_difficulty: int,

    governance_envelope: GovernanceEnvelope,

) -> GovernedAdaptationResult:
    """
    Apply governance-mediated constraints
    to orchestration difficulty adaptation.

    Governance shapes progression intensity
    without directly controlling task
    selection behavior.
    """

    permitted_difficulty = proposed_difficulty

    escalation_constrained = False

    recovery_constrained = False

    governance_reason = (
        "adaptation permitted under "
        "current governance state"
    )

    difficulty_shift = (
        proposed_difficulty
        - base_difficulty
    )

    # =====================================
    # Arbitration instability constrains
    # aggressive escalation
    # =====================================

    if (
        governance_envelope.arbitration_active
        and difficulty_shift > 1
    ):

        permitted_difficulty = (
            base_difficulty + 1
        )

        escalation_constrained = True

        governance_reason = (
            "constitutional arbitration "
            "bounded escalation intensity"
        )

    # =====================================
    # Low authority ceilings prevent
    # aggressive progression
    # =====================================

    if (
        governance_envelope.authority_ceiling
        < 0.5
        and difficulty_shift > 0
    ):

        permitted_difficulty = (
            min(
                permitted_difficulty,
                base_difficulty + 1
            )
        )

        escalation_constrained = True

        governance_reason = (
            "authority ceiling constrained "
            "difficulty escalation"
        )

    # =====================================
    # Reevaluation continuity prevents
    # destabilizing recovery collapse
    # =====================================

    if (
        governance_envelope.reevaluation_required
        and difficulty_shift < -1
    ):

        permitted_difficulty = (
            base_difficulty - 1
        )

        recovery_constrained = True

        governance_reason = (
            "reevaluation continuity "
            "bounded recovery intensity"
        )

    # =====================================
    # Topology instability freezes
    # progression escalation
    # =====================================

    if (
        governance_envelope.topology_integrity
        != "stable"
        and difficulty_shift > 0
    ):

        permitted_difficulty = (
            base_difficulty
        )

        escalation_constrained = True

        governance_reason = (
            "topology instability prevented "
            "progression escalation"
        )

    # =====================================
    # Final difficulty range invariant
    # =====================================
    #
    # The governance mediation layer is the
    # final authority over permitted difficulty.
    # No upstream proposal may escape the
    # canonical task difficulty range.

    permitted_difficulty = max(
        1,
        min(permitted_difficulty, 3)
    )

    return GovernedAdaptationResult(
        permitted_difficulty=(
            permitted_difficulty
        ),

        escalation_constrained=(
            escalation_constrained
        ),

        recovery_constrained=(
            recovery_constrained
        ),

        governance_reason=(
            governance_reason
        ),
    )


