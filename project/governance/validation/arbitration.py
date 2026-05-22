from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ConstitutionalRole(str, Enum):
    """
    Canonical constitutional governance roles.
    """

    STRUCTURAL_BOUNDARY = (
        "structural_boundary"
    )

    RESTORATION_GOVERNOR = (
        "restoration_governor"
    )

    LEGITIMACY_VALIDATOR = (
        "legitimacy_validator"
    )

    CONTINUITY_GUARDIAN = (
        "continuity_guardian"
    )

    OBSERVABILITY_GUARDIAN = (
        "observability_guardian"
    )


class ConstitutionalPrinciple(str, Enum):
    """
    Canonical constitutional governance principles.
    """

    TOPOLOGY_LEGALITY = (
        "topology_legality"
    )

    RESTRICTION_PRECEDENCE = (
        "restriction_precedence"
    )

    EVIDENCE_VALIDITY = (
        "evidence_validity"
    )

    REEVALUATION_CONTINUITY = (
        "reevaluation_continuity"
    )

    OBSERVABILITY_PRESERVATION = (
        "observability_preservation"
    )

    REVERSIBILITY_PRESERVATION = (
        "reversibility_preservation"
    )


CONSTITUTIONAL_ROLE_MAP = {

    ConstitutionalPrinciple.TOPOLOGY_LEGALITY:
        ConstitutionalRole.STRUCTURAL_BOUNDARY,

    ConstitutionalPrinciple.RESTRICTION_PRECEDENCE:
        ConstitutionalRole.RESTORATION_GOVERNOR,

    ConstitutionalPrinciple.EVIDENCE_VALIDITY:
        ConstitutionalRole.LEGITIMACY_VALIDATOR,

    ConstitutionalPrinciple.REEVALUATION_CONTINUITY:
        ConstitutionalRole.CONTINUITY_GUARDIAN,

    ConstitutionalPrinciple.OBSERVABILITY_PRESERVATION:
        ConstitutionalRole.OBSERVABILITY_GUARDIAN,

    ConstitutionalPrinciple.REVERSIBILITY_PRESERVATION:
        ConstitutionalRole.CONTINUITY_GUARDIAN,
}


@dataclass(frozen=True)
class GovernanceContradiction:
    """
    Represents simultaneous constitutional tensions
    requiring arbitration synthesis.
    """

    contradiction_id: str

    conflicting_principles: List[
        ConstitutionalPrinciple
    ]

    description: str

    active_constraints: List[str] = field(
        default_factory=list
    )

    unresolved_ambiguities: List[str] = field(
        default_factory=list
    )


@dataclass(frozen=True)
class ArbitrationConstraint:
    """
    Represents bounded governance constraints
    produced through constitutional arbitration.
    """

    constraint_type: str

    description: str

    constrained_dimension: str

    severity: str = "moderate"


@dataclass(frozen=True)
class ArbitrationResult:
    """
    Canonical arbitration synthesis result.
    """

    dominant_principle: (
        ConstitutionalPrinciple
    )

    contradictions: List[
        GovernanceContradiction
    ]

    constraints: List[
        ArbitrationConstraint
    ]

    allowed_progressions: List[str] = field(
        default_factory=list
    )

    authority_ceiling: float = 0.5

    reevaluation_required: bool = False

    unresolved_ambiguities: List[str] = field(
        default_factory=list
    )

    arbitration_confidence: float = 0.0


CONSTITUTIONAL_ROLE_PRECEDENCE = {

    ConstitutionalRole.STRUCTURAL_BOUNDARY: 100,

    ConstitutionalRole.RESTORATION_GOVERNOR: 95,

    ConstitutionalRole.LEGITIMACY_VALIDATOR: 90,

    ConstitutionalRole.CONTINUITY_GUARDIAN: 80,

    ConstitutionalRole.OBSERVABILITY_GUARDIAN: 75,
}


def synthesize_arbitration(
    contradiction: GovernanceContradiction,
) -> ArbitrationResult:
    """
    Produce bounded constitutional arbitration
    synthesis from governance contradiction state.
    """

    dominant_principle = max(
        contradiction.conflicting_principles,

        key=lambda principle: (
            CONSTITUTIONAL_ROLE_PRECEDENCE.get(
                CONSTITUTIONAL_ROLE_MAP[
                    principle
                ],
                0,
            )
        ),
    )

    constraints = []

    authority_ceiling = 0.5

    reevaluation_required = True

    arbitration_confidence = 0.4

    if (
        dominant_principle
        == ConstitutionalPrinciple.TOPOLOGY_LEGALITY
    ):

        constraints.append(
            ArbitrationConstraint(
                constraint_type="topology_constraint",

                description=(
                    "Illegal governance restoration "
                    "must remain constrained."
                ),

                constrained_dimension=(
                    "authority_restoration"
                ),

                severity="high",
            )
        )

        authority_ceiling = 0.4

        arbitration_confidence = 0.75

    elif (
        dominant_principle
        == ConstitutionalPrinciple.RESTRICTION_PRECEDENCE
    ):

        constraints.append(
            ArbitrationConstraint(
                constraint_type="restoration_constraint",

                description=(
                    "Recovery progression remains "
                    "bounded until legitimacy "
                    "stabilizes sufficiently."
                ),

                constrained_dimension=(
                    "rehabilitation_progression"
                ),

                severity="high",
            )
        )

        authority_ceiling = 0.5

        arbitration_confidence = 0.7

    elif (
        dominant_principle
        == ConstitutionalPrinciple.EVIDENCE_VALIDITY
    ):

        constraints.append(
            ArbitrationConstraint(
                constraint_type="evidence_constraint",

                description=(
                    "Authority recovery remains "
                    "bounded until legitimacy "
                    "evidence improves."
                ),

                constrained_dimension=(
                    "rehabilitation_progression"
                ),

                severity="moderate",
            )
        )

        authority_ceiling = 0.6

        arbitration_confidence = 0.65

    return ArbitrationResult(
        dominant_principle=(
            dominant_principle
        ),

        contradictions=[contradiction],

        constraints=constraints,

        authority_ceiling=(
            authority_ceiling
        ),

        reevaluation_required=(
            reevaluation_required
        ),

        unresolved_ambiguities=(
            contradiction.unresolved_ambiguities
        ),

        arbitration_confidence=(
            arbitration_confidence
        ),
    )
