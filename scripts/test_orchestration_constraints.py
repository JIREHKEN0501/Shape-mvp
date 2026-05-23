from project.governance.validation.governance_envelope import (
    GovernanceEnvelope,
)

from project.governance.validation.orchestration_constraints import (
    apply_governance_constraints,
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

    active_contradictions=[
        "rehabilitation_conflict",
    ],

    unresolved_ambiguities=[
        "legitimacy remains unstable",
    ],
)

constraint_result = (
    apply_governance_constraints(
        governance_envelope
    )
)

print(
    "\n=== ORCHESTRATION CONSTRAINTS ===\n"
)

print(
    "authority_ceiling:",
    constraint_result.authority_ceiling,
)

print(
    "escalation_permitted:",
    constraint_result.escalation_permitted,
)

print(
    "restoration_permitted:",
    constraint_result.restoration_permitted,
)

print(
    "reevaluation_required:",
    constraint_result.reevaluation_required,
)

print(
    "blocked_operations:",
    constraint_result.blocked_operations,
)

print(
    "active_constraints:",
    constraint_result.active_constraints,
)

print(
    "governance_warning:",
    constraint_result.governance_warning,
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

topology_failure_result = (
    apply_governance_constraints(
        topology_failure_envelope
    )
)

print(
    "\n=== TOPOLOGY FAILURE ===\n"
)

print(
    "restoration_permitted:",
    topology_failure_result.restoration_permitted,
)

print(
    "blocked_operations:",
    topology_failure_result.blocked_operations,
)

print(
    "governance_warning:",
    topology_failure_result.governance_warning,
)


