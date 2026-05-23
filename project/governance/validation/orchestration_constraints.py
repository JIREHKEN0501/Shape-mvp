from dataclasses import dataclass, field
from typing import List

from .governance_envelope import (
    GovernanceEnvelope,
)

@dataclass(frozen=True)
class OrchestrationConstraintResult:
    """
    Governance-mediated orchestration
    constraint synthesis result.

    Represents operational boundaries
    exposed safely to orchestration layers.
    """

    authority_ceiling: float

    escalation_permitted: bool

    restoration_permitted: bool

    reevaluation_required: bool

    blocked_operations: List[str] = field(
        default_factory=list
    )

    active_constraints: List[str] = field(
        default_factory=list
    )

    governance_warning: str = ""

def apply_governance_constraints(
    governance_envelope: GovernanceEnvelope,
) -> OrchestrationConstraintResult:
    """
    Apply governance envelope constraints
    into orchestration-safe operational
    boundaries.

    Governance constrains orchestration
    behavior without directly controlling
    orchestration decisions.
    """

    blocked_operations: List[str] = []

    escalation_permitted = True

    restoration_permitted = True

    governance_warning = ""

    if governance_envelope.authority_ceiling < 0.5:

        escalation_permitted = False

        blocked_operations.append(
            "aggressive_escalation"
        )

    if governance_envelope.reevaluation_required:

        blocked_operations.append(
            "unchecked_continuation"
        )

    if (
        governance_envelope.topology_integrity
        != "stable"
    ):

        restoration_permitted = False

        blocked_operations.append(
            "topology_transition"
        )

    if governance_envelope.arbitration_active:

        governance_warning = (
            "constitutional arbitration active"
        )

    return OrchestrationConstraintResult(
        authority_ceiling=(
            governance_envelope.authority_ceiling
        ),

        escalation_permitted=(
            escalation_permitted
        ),

        restoration_permitted=(
            restoration_permitted
        ),

        reevaluation_required=(
            governance_envelope.reevaluation_required
        ),

        blocked_operations=(
            blocked_operations
        ),

        active_constraints=list(
            governance_envelope.active_constraints
        ),

        governance_warning=(
            governance_warning
        ),
    )


