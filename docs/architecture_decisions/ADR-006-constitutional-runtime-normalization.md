
# ADR-006 — Constitutional Runtime Normalization

## Status

Accepted

---

## Context

Governance evaluators originally supported both:

- dictionary-based runtime payloads
- typed RuntimeGovernanceContext objects

during the incremental runtime migration phase.

This compatibility approach preserved migration safety
but introduced growing architectural duplication.

Evaluator-local compatibility handling risked creating:

- distributed schema coercion
- inconsistent runtime assumptions
- replay instability
- evaluator divergence
- normalization drift

A centralized normalization layer became necessary.

---

## Decision

Runtime governance payloads will now pass through a
canonical normalization layer before evaluator execution.

The normalization layer is responsible for:

- schema coercion
- default initialization
- compatibility stabilization
- typed runtime construction
- canonical runtime guarantees

Evaluators should increasingly assume normalized
RuntimeGovernanceContext input semantics.

---

## Rationale

Centralized normalization preserves:

- evaluator simplicity
- replay compatibility
- schema consistency
- runtime stability
- migration discipline

while reducing:

- evaluator-local compatibility duplication
- distributed runtime assumptions
- schema drift risk
- replay coercion ambiguity

Normalization establishes:

constitutional runtime ingress control.

---

## Consequences

### Positive

- canonical runtime semantics established
- evaluator consistency improved
- replay readiness improved
- runtime coercion centralized
- future topology enforcement simplified

### Negative

- normalization layer becomes infrastructure-critical
- runtime schema evolution now requires ingress review
- evaluator assumptions become more tightly coupled
  to canonical runtime structure

---

## Deferred Concerns

The following concerns remain intentionally deferred:

- runtime schema version negotiation
- replay migration engines
- adaptive schema reconciliation
- historical runtime compatibility layers
- distributed runtime federation semantics

These concerns may evolve during future replay-aware
governance phases.

---

## Notes

This ADR formalizes the transition from:

distributed evaluator compatibility handling

to:

centralized constitutional runtime normalization.

Normalization is treated as foundational governance
infrastructure rather than evaluator-specific behavior.
