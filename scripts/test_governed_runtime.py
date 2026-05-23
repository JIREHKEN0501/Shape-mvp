from project.app.services.routing.governed_runtime import (
    execute_runtime_operation,
)

from project.governance.validation.governance_envelope import (
    GovernanceEnvelope,
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

blocked_runtime = (
    execute_runtime_operation(
        "aggressive_escalation",

        degraded_envelope,
    )
)

allowed_runtime = (
    execute_runtime_operation(
        "bounded_recovery",

        degraded_envelope,
    )
)

print(
    "\n=== BLOCKED RUNTIME EXECUTION ===\n"
)

print(
    "operation:",
    blocked_runtime.operation,
)

print(
    "execution_completed:",
    blocked_runtime.execution_completed,
)

print(
    "execution_reason:",
    blocked_runtime.execution_reason,
)

print(
    "governance_warning:",
    blocked_runtime.governance_warning,
)

print(
    "\n=== ALLOWED RUNTIME EXECUTION ===\n"
)

print(
    "operation:",
    allowed_runtime.operation,
)

print(
    "execution_completed:",
    allowed_runtime.execution_completed,
)

print(
    "execution_reason:",
    allowed_runtime.execution_reason,
)

print(
    "governance_warning:",
    allowed_runtime.governance_warning,
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
    execute_runtime_operation(
        "topology_transition",

        topology_failure_envelope,
    )
)

print(
    "\n=== BLOCKED TOPOLOGY RUNTIME ===\n"
)

print(
    "operation:",
    blocked_transition.operation,
)

print(
    "execution_completed:",
    blocked_transition.execution_completed,
)

print(
    "execution_reason:",
    blocked_transition.execution_reason,
)

print(
    "governance_warning:",
    blocked_transition.governance_warning,
)


