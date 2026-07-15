# ADR-009 Implementation Design

Status: Draft

Date: 2026-07-13

Related

- ADR-009 — Dependency-Aware Evidence Consumption
- ADR-009 Architectural Conformance Review

---

# Purpose

Describe the minimum implementation required to achieve ADR-009 compliance while preserving the existing routing architecture.

Implementation shall extend the current routing pipeline rather than redesign it.

---

# Current Architecture

The current routing architecture is already modular and largely compliant with ADR-009.

Current implementation status:

- RoutingSignal Schema — Compliant
- Signal Extractor — Metadata enrichment required
- Signal Arbitrator — Dependency-aware interpretation required
- tasks.py — Compliant

No structural redesign of the routing pipeline is required.

---

# Work Package 1

## Governance Metadata Population

Component

Signal Extractor

Objective

Populate the existing RoutingSignal metadata field with governance information required for dependency-aware runtime reasoning.

Required metadata:

- Evidence Class
- Dependency Identity
- Independent Evidence Set

---

# Work Package 2

## Dependency-Aware Arbitration

Component

Signal Arbitrator

Objective

Interpret governance metadata during runtime arbitration to preserve dependency-aware evidence consumption.

Implementation shall consume governance metadata without altering the existing routing pipeline.

---

# Validation

Implementation is complete when:

- Governance metadata is populated during signal extraction.
- Runtime arbitration consumes governance metadata.
- Routing behaviour remains deterministic.
- ADR-009 compliance criteria are satisfied.

---

# Rollback Condition

Implementation shall preferentially use the existing RoutingSignal metadata extension point.

If dependency-aware governance cannot be implemented without introducing breaking changes to the RoutingSignal schema, implementation shall be limited to metadata enrichment and remaining arbitration enhancements deferred pending architectural review.
