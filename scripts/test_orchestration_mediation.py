from project.governance.validation.governance_envelope import (
    GovernanceEnvelope,
)

from project.governance.validation.orchestration_constraints import (
    apply_governance_constraints,
)

from project.governance.validation.orchestration_mediation import (
    mediate_orchestration_operation,
)

governance_envelope = GovernanceEnvelope(
    governance_status="degraded",

    topology_integrity="stable",

    authority_ceiling=0.4,

    reevaluation_required=True,

    arbitration_active=True,

    active_constraints=[
        "restoration_constraint",
    ],
)

constraint_result = (
    apply_governance_constraints(
        governance_envelope
    )
)

blocked_escalation = (
    mediate_orchestration_operation(
        "aggressive_escalation",

        constraint_result,
    )
)

allowed_operation = (
    mediate_orchestration_operation(
        "bounded_recovery",

        constraint_result,
    )
)

print(
    "\n=== BLOCKED ESCALATION ===\n"
)

print(
    "operation:",
    blocked_escalation.operation,
)

print(
    "operation_permitted:",
    blocked_escalation.operation_permitted,
)

print(
    "mediation_reason:",
    blocked_escalation.mediation_reason,
)

print(
    "governance_warning:",
    blocked_escalation.governance_warning,
)

print(
    "\n=== ALLOWED OPERATION ===\n"
)

print(
    "operation:",
    allowed_operation.operation,
)

print(
    "operation_permitted:",
    allowed_operation.operation_permitted,
)

print(
    "mediation_reason:",
    allowed_operation.mediation_reason,
)

print(
    "governance_warning:",
    allowed_operation.governance_warning,
)

topology_failure_envelope = GovernanceEnvelope(
    governance_status="critical",

    topology_integrity="violated",

    authority_ceiling=0.3,

    reevaluation_required=True,

    arbitration_active=True,
)

topology_constraint_result = (
    apply_governance_constraints(
        topology_failure_envelope
    )
)

blocked_transition = (
    mediate_orchestration_operation(
        "topology_transition",

        topology_constraint_result,
    )
)

print(
    "\n=== BLOCKED TOPOLOGY TRANSITION ===\n"
)

print(
    "operation:",
    blocked_transition.operation,
)

print(
    "operation_permitted:",
    blocked_transition.operation_permitted,
)

print(
    "mediation_reason:",
    blocked_transition.mediation_reason,
)

print(
    "governance_warning:",
    blocked_transition.governance_warning,
)


