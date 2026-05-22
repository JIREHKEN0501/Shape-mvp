from project.governance.validation.arbitration import (
    ConstitutionalPrinciple,
    GovernanceContradiction,
    synthesize_arbitration,
)

from project.governance.validation.governance_envelope import (
    synthesize_governance_envelope,
)

from project.governance.validation.persistence_envelope import (
    create_persistence_envelope,
)

contradiction = GovernanceContradiction(
    contradiction_id="persistence_conflict",

    conflicting_principles=[
        ConstitutionalPrinciple.RESTRICTION_PRECEDENCE,
        ConstitutionalPrinciple.EVIDENCE_VALIDITY,
    ],

    description=(
        "Recovery pressure conflicts with "
        "bounded legitimacy restoration."
    ),

    unresolved_ambiguities=[
        "legitimacy remains partially unstable"
    ],
)

arbitration_result = synthesize_arbitration(
    contradiction
)

governance_envelope = (
    synthesize_governance_envelope(
        governance_status="degraded",

        topology_integrity="stable",

        arbitration_results=[
            arbitration_result
        ],
    )
)

persistence_envelope = (
    create_persistence_envelope(
        governance_envelope
    )
)

print("\n=== PERSISTENCE ENVELOPE ===\n")

print(
    "governance_status:",
    persistence_envelope.governance_status,
)

print(
    "topology_integrity:",
    persistence_envelope.topology_integrity,
)

print(
    "authority_ceiling:",
    persistence_envelope.authority_ceiling,
)

print(
    "reevaluation_required:",
    persistence_envelope.reevaluation_required,
)

print(
    "arbitration_active:",
    persistence_envelope.arbitration_active,
)

print(
    "active_constraints:",
    persistence_envelope.active_constraints,
)

print(
    "active_contradictions:",
    persistence_envelope.active_contradictions,
)

print(
    "unresolved_ambiguities:",
    persistence_envelope.unresolved_ambiguities,
)

print(
    "persistence_version:",
    persistence_envelope.persistence_version,
)

print(
    "replay_safe:",
    persistence_envelope.replay_safe,
)
