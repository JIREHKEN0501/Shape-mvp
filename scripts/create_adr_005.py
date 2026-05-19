from pathlib import Path


ADR_PATH = Path(
    "docs/architecture_decisions/"
    "ADR-005-constrained-temporal-governance-adoption.md"
)


ADR_CONTENT = """
# ADR-005 — Constrained Temporal Governance Adoption

## Status

Accepted

---

## Context

Governance infrastructure previously operated primarily
on state-based constitutional evaluation semantics.

Existing invariants validated:

- governance visibility
- restriction precedence
- legitimacy integrity
- rehabilitation pacing

However, governance persistence over time introduced
additional constitutional risks including:

- governance inertia
- stale restriction persistence
- reevaluation drift
- flash-crash adaptivity
- compounded historical bias
- contextual audit fragility
- state-transition ambiguity

A temporal governance layer became necessary to ensure
governance states remain periodically reevaluation-
sensitive.

At the same time, immediate expansion into fully
historical governance systems introduced substantial
architectural risk.

---

## Decision

Initial temporal governance adoption will remain
intentionally constrained.

The first implementation of INV-007 introduces:

- temporal governance primitives
- reevaluation-sensitive runtime semantics
- stale reevaluation detection
- temporal governance thresholds

without introducing:

- replay DAG infrastructure
- causal lineage systems
- probabilistic governance memory
- historical inference engines
- temporal graph orchestration

Temporal governance currently focuses only on:

periodic reevaluation integrity.

---

## Rationale

Constrained temporal adoption preserves:

- architectural stability
- evaluator simplicity
- governance clarity
- migration discipline
- replay sequencing flexibility

while avoiding premature introduction of:

- speculative memory systems
- causality inference complexity
- excessive replay infrastructure
- temporal overengineering

The architecture prioritizes:

minimal constitutional temporal awareness

before:

historical governance intelligence.

---

## Consequences

### Positive

- governance persistence now observable
- stale governance detection introduced
- reevaluation-sensitive semantics established
- temporal governance foundation stabilized
- future replay systems remain possible

### Negative

- causal replay analysis deferred
- governance lineage unresolved
- historical inference intentionally absent
- advanced temporal threat mitigation deferred

---

## Deferred Concerns

The following concerns remain intentionally deferred:

- retroactive profile reconstruction
- causality inversion analysis
- replay-native governance memory
- historical legitimacy weighting
- temporal governance lineage graphs
- probabilistic temporal inference
- adaptive replay reconciliation

These concerns remain documented constitutional threat
models but are not yet considered implementation
requirements.

---

## Notes

This ADR establishes the first temporal constitutional
governance layer.

Temporal governance is currently treated as:

reevaluation-sensitive constitutional stabilization

rather than:

full historical governance intelligence.

Future replay-aware governance systems are expected to
evolve incrementally from this constrained foundation.
"""


ADR_PATH.parent.mkdir(parents=True, exist_ok=True)

ADR_PATH.write_text(ADR_CONTENT)

print("ADR-005 created successfully.")
