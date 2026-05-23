from dataclasses import dataclass

from project.governance.validation.governance_envelope import (
    GovernanceEnvelope,
)

from project.governance.validation.governed_execution import (
    execute_governed_operation,
)

@dataclass(frozen=True)
class RuntimeExecutionResult:
    """
    Governance-aware runtime execution result.

    Represents orchestration execution outcome
    after constitutional governance mediation.
    """

    operation: str

    execution_completed: bool

    execution_reason: str

    governance_warning: str = ""

def execute_runtime_operation(
    operation: str,

    governance_envelope: GovernanceEnvelope,

) -> RuntimeExecutionResult:
    """
    Execute orchestration runtime operation
    through governance-mediated execution
    gateway.

    Governance constrains runtime execution
    boundaries without directly mutating
    orchestration behavior.
    """

    governed_result = (
        execute_governed_operation(
            operation,
            governance_envelope,
        )
    )

    if not governed_result.execution_permitted:

        return RuntimeExecutionResult(
            operation=operation,

            execution_completed=False,

            execution_reason=(
                governed_result
                .execution_reason
            ),

            governance_warning=(
                governed_result
                .governance_warning
            ),
        )

    return RuntimeExecutionResult(
        operation=operation,

        execution_completed=True,

        execution_reason=(
            "runtime execution permitted "
            "under governance mediation"
        ),

        governance_warning=(
            governed_result
            .governance_warning
        ),
    )


