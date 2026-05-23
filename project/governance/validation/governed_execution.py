from dataclasses import dataclass

from .governance_envelope import (
    GovernanceEnvelope,
)

from .orchestration_constraints import (
    apply_governance_constraints,
)

from .orchestration_mediation import (
    mediate_orchestration_operation,
)

@dataclass(frozen=True)
class GovernedExecutionResult:
    """
    Governance-mediated orchestration
    execution result.

    Represents constitutionally bounded
    runtime execution outcome.
    """

    operation: str

    execution_permitted: bool

    execution_reason: str

    governance_warning: str = ""

def execute_governed_operation(
    operation: str,

    governance_envelope: GovernanceEnvelope,

) -> GovernedExecutionResult:
    """
    Execute orchestration operation under
    governance-mediated constitutional
    constraints.

    Governance constrains runtime execution
    boundaries without directly mutating
    orchestration behavior.
    """

    constraint_result = (
        apply_governance_constraints(
            governance_envelope
        )
    )

    mediation_result = (
        mediate_orchestration_operation(
            operation,
            constraint_result,
        )
    )

    if not mediation_result.operation_permitted:

        return GovernedExecutionResult(
            operation=operation,

            execution_permitted=False,

            execution_reason=(
                mediation_result
                .mediation_reason
            ),

            governance_warning=(
                mediation_result
                .governance_warning
            ),
        )

    return GovernedExecutionResult(
        operation=operation,

        execution_permitted=True,

        execution_reason=(
            "operation executed within "
            "governance boundaries"
        ),

        governance_warning=(
            mediation_result
            .governance_warning
        ),
    )


