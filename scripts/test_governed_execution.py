from project.governance.validation.governance_envelope import (
    GovernanceEnvelope,
)

from project.governance.validation.governed_execution import (
    execute_governed_operation,
)

degraded_envelope = GovernanceEnvelope(
    governance_status="degraded",

    topology_integrity="stable",

    authority_ceiling=0.4,

    reevaluation_required=True,

    arbitration_active=True,

    active_constraints=[
        "restoration_constraint",
    ],
)

blocked_execution = (
    execute_governed_operation(
        "aggressive_escalation",

        degraded_envelope,
    )
)

allowed_execution = (
    execute_governed_operation(
        "bounded_recovery",

        degraded_envelope,
    )
)

print(
    "\n=== BLOCKED EXECUTION ===\n"
)

print(
    "operation:",
    blocked_execution.operation,
)

print(
    "execution_permitted:",
    blocked_execution.execution_permitted,
)

print(
    "execution_reason:",
    blocked_execution.execution_reason,
)

print(
    "governance_warning:",
    blocked_execution.governance_warning,
)

print(
    "\n=== ALLOWED EXECUTION ===\n"
)

print(
    "operation:",
    allowed_execution.operation,
)

print(
    "execution_permitted:",
    allowed_execution.execution_permitted,
)

print(
    "execution_reason:",
    allowed_execution.execution_reason,
)

print(
    "governance_warning:",
    allowed_execution.governance_warning,
)

topology_failure_envelope = GovernanceEnvelope(
    governance_status="critical",

    topology_integrity="violated",

    authority_ceiling=0.3,

    reevaluation_required=True,

    arbitration_active=True,

    active_constraints=[
        "topology_constraint",
    ],
)

blocked_transition = (
    execute_governed_operation(
        "topology_transition",

        topology_failure_envelope,
    )
)

print(
    "\n=== BLOCKED TOPOLOGY EXECUTION ===\n"
)

print(
    "operation:",
    blocked_transition.operation,
)

print(
    "execution_permitted:",
    blocked_transition.execution_permitted,
)

print(
    "execution_reason:",
    blocked_transition.execution_reason,
)

print(
    "governance_warning:",
    blocked_transition.governance_warning,
)


