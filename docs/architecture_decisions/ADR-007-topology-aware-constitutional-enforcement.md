# ADR-007 — Topology-Aware Constitutional Enforcement

## Status
Accepted

## Context

Phase 3B.5 governance freeze stabilization introduced
explicit constitutional topology enforcement semantics
within the governance validation runtime.

Prior governance architecture established:
- governance invariants
- runtime normalization
- reevaluation semantics
- constitutional reporting
- rehabilitation pacing protections

However, governance transitions themselves remained
structurally under-constrained.

This created risk of:
- illegal authority restoration
- governance bypass escalation
- unstable recovery progression
- topology inconsistency
- replay instability
- transition audit ambiguity

Transition semantics were previously implicit rather
than machine-enforceable.

Additionally, runtime normalization initially failed
to preserve transition-state semantics during typed
runtime conversion.

This produced silent topology validation degradation,
where illegal transitions could appear constitutionally
valid after normalization.

The issue was identified during freeze-stage
stabilization before replay-oriented infrastructure
was introduced.

## Decision

The governance runtime adopts topology-aware
constitutional enforcement semantics.

This includes:

- explicit transition-state representation
- previous_state/current_state runtime semantics
- topology legality validation
- transition-aware constitutional assertions
- topology-specific governance reporting
- topology integrity observability surfaces

Topology integrity is treated as a distinct governance
dimension separate from:
- severity classification
- legitimacy integrity
- reevaluation integrity
- rehabilitation integrity

The runtime now exposes:

- governance_status
- topology_integrity

as independent constitutional observability surfaces.

## Consequences

### Positive

- illegal governance restoration becomes detectable
- recovery progression becomes structurally enforceable
- replay foundations become more stable
- governance auditability improves
- topology corruption becomes observable
- constitutional reasoning becomes more explicit
- future domain governance isolation becomes safer

### Negative

- runtime complexity increases modestly
- normalization integrity becomes more critical
- governance topology maintenance burden increases

## Architectural Discipline

Replay-oriented governance systems were intentionally
deferred during this phase.

The architecture explicitly avoided:
- replay DAG infrastructure
- historical governance graphing
- adaptive legality inference
- causal governance reconstruction
- self-modifying topology systems

This preserves freeze-stage architectural stability
while constitutional semantics mature incrementally.

## Rationale

Topology-aware governance enforcement represents a
constitutional stabilization milestone rather than
feature expansion.

The goal is not adaptive governance complexity.

The goal is structurally enforceable governance
coherence.\n