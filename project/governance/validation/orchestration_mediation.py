from dataclasses import dataclass

from .orchestration_constraints import (
    OrchestrationConstraintResult,
)

@dataclass(frozen=True)
class OperationMediationResult:
    """
    Governance-mediated orchestration
    operation result.

    Represents whether orchestration
    operation remains constitutionally
    permitted under current governance
    constraints.
    """

    operation: str

    operation_permitted: bool

    mediation_reason: str

    governance_warning: str = ""

def mediate_orchestration_operation(
    operation: str,

    constraint_result: (
        OrchestrationConstraintResult
    ),

) -> OperationMediationResult:
    """
    Mediate orchestration operation against
    governance-derived operational
    constraints.

    Governance constrains orchestration
    permissions without directly executing
    orchestration behavior.
    """

    if (
        operation
        in constraint_result.blocked_operations
    ):

        return OperationMediationResult(
            operation=operation,

            operation_permitted=False,

            mediation_reason=(
                f"{operation} blocked by "
                "governance constraints"
            ),

            governance_warning=(
                constraint_result
                .governance_warning
            ),
        )

    if (
        not constraint_result
        .escalation_permitted
        and operation == "aggressive_escalation"
    ):

        return OperationMediationResult(
            operation=operation,

            operation_permitted=False,

            mediation_reason=(
                "authority ceiling insufficient "
                "for escalation"
            ),

            governance_warning=(
                constraint_result
                .governance_warning
            ),
        )

    if (
        not constraint_result
        .restoration_permitted
        and operation == "topology_transition"
    ):

        return OperationMediationResult(
            operation=operation,

            operation_permitted=False,

            mediation_reason=(
                "topology integrity violation "
                "prevents transition"
            ),

            governance_warning=(
                constraint_result
                .governance_warning
            ),
        )

    return OperationMediationResult(
        operation=operation,

        operation_permitted=True,

        mediation_reason=(
            "operation permitted under "
            "current governance state"
        ),

        governance_warning=(
            constraint_result
            .governance_warning
        ),
    )


