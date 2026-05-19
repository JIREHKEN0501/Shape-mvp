from pathlib import Path


ADR_PATH = Path(
    "docs/architecture_decisions/"
    "ADR-004-constitutional-runtime-schema-adoption.md"
)


ADR_CONTENT = """
# ADR-004 — Constitutional Runtime Schema Adoption

## Status

Accepted

---

## Context

Initial governance validation infrastructure operated
primarily on loosely structured runtime dictionaries.

This accelerated early constitutional evaluator
development but introduced increasing architectural risk
as governance infrastructure matured.

Risks included:

- implicit runtime assumptions
- schema ambiguity
- evaluator inconsistency
- replay fragility
- serialization instability
- governance semantic drift

A canonical typed governance runtime schema was
introduced through:

- RuntimeGovernanceContext
- GovernanceState
- LegitimacyState
- EvidenceState
- GovernanceTrace

However, immediate hard enforcement across all
evaluators was intentionally deferred to avoid migration
instability.

Incremental schema hardening was adopted instead.

---

## Decision

All active constitutional evaluators now support:

- RuntimeGovernanceContext
- legacy dictionary runtime contexts

The following evaluators completed typed runtime
migration:

- INV-004
- INV-001
- INV-002
- INV-008

Governance evaluation now operates against explicit
constitutional runtime structures while preserving
temporary backward compatibility.

---

## Rationale

Typed runtime adoption improves:

- governance explicitness
- evaluator consistency
- replay readiness
- serialization safety
- runtime stability
- architectural clarity

The migration prioritized:

safe constitutional stabilization

over:

aggressive runtime enforcement.

Migration was intentionally completed before:

- temporal governance expansion
- reevaluation cadence systems
- replay persistence infrastructure
- governance memory systems

to reduce future architectural migration complexity.

---

## Consequences

### Positive

- governance semantics now explicitly structured
- evaluator assumptions reduced
- replay compatibility improved
- constitutional runtime coherence increased
- migration stability preserved

### Negative

- temporary dual-runtime support complexity
- transitional evaluator implementations remain
- dictionary compatibility persists temporarily

---

## Deferred Concerns

The following concerns remain intentionally deferred:

- mandatory typed runtime enforcement
- runtime schema validation layers
- runtime version negotiation
- temporal governance persistence semantics
- replay-native governance storage structures

These concerns are expected to evolve alongside future
temporal governance infrastructure.

---

## Notes

This ADR represents completion of the first major
constitutional runtime stabilization phase.

Governance infrastructure is now considered:

schema-aware constitutional infrastructure

rather than:

loosely structured evaluator orchestration.

This transition materially changes future governance
evolution strategy and replay-readiness assumptions.
"""


ADR_PATH.parent.mkdir(parents=True, exist_ok=True)

ADR_PATH.write_text(ADR_CONTENT)

print("ADR-004 created successfully.")
