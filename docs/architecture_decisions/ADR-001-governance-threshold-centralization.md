
# ADR-001 — Governance Threshold Centralization

## Status

Accepted

---

## Context

As runtime governance evaluators expanded beyond a single
constitutional assertion, threshold consistency became a
growing architectural concern.

Early evaluators initially relied on locally interpreted
threshold semantics such as:

- authority restoration boundaries
- legitimacy confidence requirements
- evidence sufficiency expectations

Without shared governance threshold definitions, future
evaluators risked introducing:

- evaluator semantic drift
- contradictory constitutional interpretations
- inconsistent authority semantics
- unstable governance outcomes

Particular concern emerged around:
- INV-001 restriction precedence semantics
- INV-002 legitimacy confidence semantics
- future rehabilitation and reevaluation evaluators

---

## Decision

Governance threshold semantics were centralized into:

project/governance/validation/constants.py

Shared evaluator thresholds now include:

- FULL_AUTHORITY_LEVEL
- HIGH_AUTHORITY_THRESHOLD
- SUFFICIENT_EVIDENCE_SCORE
- HIGH_CONFIDENCE_THRESHOLD

Evaluators now import shared constitutional semantics
rather than defining local threshold assumptions.

---

## Consequences

### Positive

- reduces evaluator semantic drift
- preserves constitutional consistency
- stabilizes cross-evaluator interpretation
- improves future governance maintainability
- supports future severity coordination

### Negative

- introduces centralized semantic dependency
- future threshold modifications may affect multiple evaluators
- threshold semantics may eventually require contextualization

---

## Deferred Concerns

The following concerns were intentionally deferred:

- contextual threshold interpretation
- adaptive governance thresholds
- temporal threshold adjustment
- governance-profile-specific semantics
- dynamic authority calibration

Current architecture intentionally preserves:
- flat threshold semantics
- evaluator simplicity
- explainability
- deterministic governance interpretation

until broader orchestration pressure-testing occurs.

---

## Notes

Current architecture treats threshold semantics as:
- constitutional constants

rather than:
- adaptive governance policy

Future governance evolution may revisit this assumption
once temporal governance semantics and longitudinal
reevaluation systems mature.
