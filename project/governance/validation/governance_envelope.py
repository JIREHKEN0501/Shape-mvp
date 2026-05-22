from dataclasses import dataclass, field
from typing import List

from .arbitration import (
    ArbitrationResult,
)

@dataclass(frozen=True)
class GovernanceEnvelope:
    """
    Canonical synthesized governance operating
    envelope produced from constitutional validation
    and arbitration layers.
    """

    governance_status: str

    topology_integrity: str

    authority_ceiling: float = 0.5

    reevaluation_required: bool = False

    arbitration_active: bool = False

    active_constraints: List[str] = field(
        default_factory=list
    )

    unresolved_ambiguities: List[str] = field(
        default_factory=list
    )

    active_contradictions: List[str] = field(
        default_factory=list
    )

def synthesize_governance_envelope(
    governance_status: str,

    topology_integrity: str,

    arbitration_results: List[
        ArbitrationResult
    ] | None = None,

) -> GovernanceEnvelope:
    """
    Produce synthesized constitutional governance
    operating envelope.
    """

    authority_ceiling = 0.5

    reevaluation_required = False

    arbitration_active = False

    active_constraints: List[str] = []

    unresolved_ambiguities: List[str] = []

    active_contradictions: List[str] = []

    if arbitration_results:

        arbitration_active = True

        authority_ceiling = min(
            result.authority_ceiling
            for result in arbitration_results
        )

        reevaluation_required = any(
            result.reevaluation_required
            for result in arbitration_results
        )

        for result in arbitration_results:

            active_contradictions.extend(
                contradiction.contradiction_id
                for contradiction in (
                    result.contradictions
                )
            )

            unresolved_ambiguities.extend(
                result.unresolved_ambiguities
            )

            active_constraints.extend(
                constraint.constraint_type
                for constraint in (
                    result.constraints
                )
            )

    return GovernanceEnvelope(
        governance_status=governance_status,

        topology_integrity=(
            topology_integrity
        ),

        authority_ceiling=(
            authority_ceiling
        ),

        reevaluation_required=(
            reevaluation_required
        ),

        arbitration_active=(
            arbitration_active
        ),

        active_constraints=(
            active_constraints
        ),

        unresolved_ambiguities=(
            unresolved_ambiguities
        ),

        active_contradictions=(
            active_contradictions
        ),
    )


