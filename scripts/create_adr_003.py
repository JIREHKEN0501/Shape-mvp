from pathlib import Path


ADR_PATH = Path(
    "docs/architecture_decisions/"
    "ADR-003-incremental-runtime-schema-hardening.md"
)


ADR_CONTENT = """
# ADR-003 — Incremental Runtime Schema Hardening

## Status

Accepted

---

## Context

Initial governance evaluators operated primarily on:

Dict[str, Any]

runtime contexts.

This approach accelerated early evaluator iteration but
introduced increasing architectural risk as governance
infrastructure expanded.

Concerns included:

- schema ambiguity
- hidden runtime assumptions
- evaluator inconsistency
- replay instability
- serialization fragility
- future temporal governance complexity

A canonical runtime governance schema was introduced
through RuntimeGovernanceContext and related state
dataclasses.

However, immediately forcing all evaluators to adopt the
typed schema simultaneously risked:

- migration instability
- orchestration breakage
- brittle test transitions
- unnecessary implementation shock

---

## Decision

Governance runtime migration will proceed incrementally.

Evaluators will gradually evolve from:

Dict-based runtime access

toward:

typed RuntimeGovernanceContext semantics.

During migration, evaluators temporarily support both:

- legacy dictionary runtime contexts
- typed runtime governance contexts

This dual-mode compatibility is intentional.

---

## Rationale

Incremental schema hardening preserves:

- evaluator stability
- migration safety
- orchestration continuity
- test compatibility
- governance semantic consistency

while progressively reducing:

- implicit runtime assumptions
- schema fragility
- governance ambiguity

The architecture prioritizes:

safe constitutional evolution

over:

aggressive schema enforcement.

---

## Consequences

### Positive

- reduces migration risk
- preserves evaluator continuity
- enables gradual schema stabilization
- improves governance explicitness
- supports future replay infrastructure

### Negative

- temporary dual-runtime complexity
- evaluator implementations remain partially transitional
- dictionary semantics persist temporarily

---

## Deferred Concerns

The following concerns remain deferred:

- full typed-runtime enforcement
- runtime schema validation layers
- replay-native runtime structures
- temporal governance serialization
- runtime versioning semantics

These concerns are expected to mature alongside future
temporal governance infrastructure.

---

## Notes

Current governance migration strategy treats schema
hardening as:

an architectural stabilization process

rather than:

a one-step refactor operation.

Migration sequencing is considered constitutionally
important because governance evaluators increasingly act
as safety-critical infrastructure.
"""


ADR_PATH.parent.mkdir(parents=True, exist_ok=True)

ADR_PATH.write_text(ADR_CONTENT)

print("ADR-003 created successfully.")
