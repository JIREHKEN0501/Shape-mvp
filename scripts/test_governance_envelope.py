from project.governance.validation.arbitration import (
    ConstitutionalPrinciple,
    GovernanceContradiction,
    synthesize_arbitration,
)

from project.governance.validation.governance_envelope import (
    synthesize_governance_envelope,
)

topology_contradiction = GovernanceContradiction(
    contradiction_id="topology_conflict",

    conflicting_principles=[
        ConstitutionalPrinciple.TOPOLOGY_LEGALITY,
        ConstitutionalPrinciple.EVIDENCE_VALIDITY,
    ],

    description=(
        "Topology legality conflicts with "
        "weak legitimacy evidence."
    ),

    unresolved_ambiguities=[
        "legitimacy remains unstable"
    ],
)


restriction_contradiction = GovernanceContradiction(
    contradiction_id="rehabilitation_conflict",

    conflicting_principles=[
        ConstitutionalPrinciple.RESTRICTION_PRECEDENCE,
        ConstitutionalPrinciple.EVIDENCE_VALIDITY,
    ],

    description=(
        "Restriction precedence constrains "
        "recovery acceleration."
    ),

    unresolved_ambiguities=[
        "rehabilitation remains partially unstable"
    ],
)

topology_result = synthesize_arbitration(
    topology_contradiction
)

restriction_result = synthesize_arbitration(
    restriction_contradiction
)

governance_envelope = (
    synthesize_governance_envelope(
        governance_status="degraded",

        topology_integrity="stable",

        arbitration_results=[
            topology_result,
            restriction_result,
        ],
    )
)

print("\n=== GOVERNANCE ENVELOPE ===\n")

print(
    "governance_status:",
    governance_envelope.governance_status,
)

print(
    "topology_integrity:",
    governance_envelope.topology_integrity,
)

print(
    "authority_ceiling:",
    governance_envelope.authority_ceiling,
)

print(
    "reevaluation_required:",
    governance_envelope.reevaluation_required,
)

print(
    "arbitration_active:",
    governance_envelope.arbitration_active,
)

print(
    "active_constraints:",
    governance_envelope.active_constraints,
)

print(
    "active_contradictions:",
    governance_envelope.active_contradictions,
)

print(
    "unresolved_ambiguities:",
    governance_envelope.unresolved_ambiguities,
)


