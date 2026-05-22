from project.governance.validation.arbitration import (
    ArbitrationResult,
    ConstitutionalPrinciple,
    GovernanceContradiction,
    synthesize_arbitration,
)

topology_contradiction = GovernanceContradiction(
    contradiction_id="topology_restoration_conflict",

    conflicting_principles=[
        ConstitutionalPrinciple.TOPOLOGY_LEGALITY,
        ConstitutionalPrinciple.EVIDENCE_VALIDITY,
    ],

    description=(
        "Transition legality exists while "
        "legitimacy evidence remains weak."
    ),

    unresolved_ambiguities=[
        "legitimacy remains insufficient"
    ],
)

restriction_contradiction = GovernanceContradiction(
    contradiction_id="bounded_rehabilitation_conflict",

    conflicting_principles=[
        ConstitutionalPrinciple.RESTRICTION_PRECEDENCE,
        ConstitutionalPrinciple.EVIDENCE_VALIDITY,
    ],

    description=(
        "Recovery progression pressure conflicts "
        "with bounded restoration doctrine."
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

print("\n=== TOPOLOGY ARBITRATION ===\n")

print(
    "dominant_principle:",
    topology_result.dominant_principle,
)

print(
    "authority_ceiling:",
    topology_result.authority_ceiling,
)

print(
    "arbitration_confidence:",
    topology_result.arbitration_confidence,
)

print(
    "unresolved_ambiguities:",
    topology_result.unresolved_ambiguities,
)

print("\n=== RESTRICTION PRECEDENCE ===\n")

print(
    "dominant_principle:",
    restriction_result.dominant_principle,
)

print(
    "authority_ceiling:",
    restriction_result.authority_ceiling,
)

print(
    "arbitration_confidence:",
    restriction_result.arbitration_confidence,
)

print(
    "unresolved_ambiguities:",
    restriction_result.unresolved_ambiguities,
)
