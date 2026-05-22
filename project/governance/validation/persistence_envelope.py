from dataclasses import dataclass, field
from typing import List

from .governance_envelope import (
    GovernanceEnvelope,
)

@dataclass(frozen=True)
class GovernancePersistenceEnvelope:
    """
    Replay-safe persistence representation of
    synthesized constitutional governance state.
    """

    governance_status: str

    topology_integrity: str

    authority_ceiling: float

    reevaluation_required: bool

    arbitration_active: bool

    active_constraints: List[str] = field(
        default_factory=list
    )

    unresolved_ambiguities: List[str] = field(
        default_factory=list
    )

    active_contradictions: List[str] = field(
        default_factory=list
    )

    persistence_version: str = "v1"

    replay_safe: bool = True

def create_persistence_envelope(
    governance_envelope: GovernanceEnvelope,
) -> GovernancePersistenceEnvelope:
    """
    Convert governance envelope into replay-safe
    persistence representation.
    """

    return GovernancePersistenceEnvelope(
        governance_status=(
            governance_envelope.governance_status
        ),

        topology_integrity=(
            governance_envelope.topology_integrity
        ),

        authority_ceiling=(
            governance_envelope.authority_ceiling
        ),

        reevaluation_required=(
            governance_envelope.reevaluation_required
        ),

        arbitration_active=(
            governance_envelope.arbitration_active
        ),

        active_constraints=list(
            governance_envelope.active_constraints
        ),

        unresolved_ambiguities=list(
            governance_envelope.unresolved_ambiguities
        ),

        active_contradictions=list(
            governance_envelope.active_contradictions
        ),
    )
