# Fatigue Signal Remediation Design

Date: 2026-06-28

Status: implemented(validatio ongoing)

Area: Temporal Behavior / Routing

Related

- Finding 09 — Fatigue Risk Trigger Was Over-Sensitive
- Finding 14 — Effort and Fatigue Represent Distinct Behavioral Constructs
- Finding 15 — Fatigue Routing Introduces Dependency Duplication
- 2026-06-16_fatigue_risk_audit.md
- 2026-06-27_routing_signal_dependency_audit.md

---

# Purpose

This document proposes a redesign of the HumanOS fatigue signal following a series of validation audits and architectural reviews.

The existing fatigue model successfully introduced temporal awareness into adaptive routing but revealed two important limitations:

1. Latency increase alone is not sufficient evidence of participant fatigue.

2. The routing pipeline currently allows fatigue assessments to coexist with their contributing temporal signals, creating a confirmed dependency duplication.

The objective of this redesign is to establish a fatigue model that:

- remains evidence-constrained,
- distinguishes fatigue from effort,
- improves routing interpretability,
- preserves HumanOS transparency principles, and
- defines clear validation criteria before implementation.

This document specifies the intended architecture only.

Implementation details will follow after the proposed design has been reviewed and validated.

---

Validation Note: The retry-dependent Elevated pathway is architecturally implemented but has not yet been empirically exercised in Validation Trial 01 due to negligible retry variation.

---
# Design Principles

The redesigned fatigue signal shall adhere to the following principles.

## Principle 1 — Evidence Before Interpretation

Fatigue assessments must only be generated from observable participant behavior.

No fatigue classification may be based on assumptions about motivation, personality, intelligence, or intent.

---

## Principle 2 — Multiple Independent Indicators

No single behavioral signal is sufficient evidence of fatigue.

Fatigue classification requires corroborating observations from multiple independent behavioral indicators.

---

## Principle 3 — Effort and Fatigue Are Distinct Constructs

Increasing response time while maintaining performance shall not be interpreted as fatigue.

Observable effort and observable fatigue represent different behavioral constructs and require independent assessment.

---

## Principle 4 — Routing Transparency

Every fatigue assessment must be explainable through the observations that produced it.

Routing decisions must remain traceable to their supporting evidence.

---

## Principle 5 — Dependency Awareness

Derived behavioral signals must not unintentionally amplify the influence of their parent observations within adaptive routing.

Signal relationships should remain explicit and architecturally traceable.

---

## Principle 6 — Validation Before Deployment

Changes to fatigue classification shall not be integrated into HumanOS until they have successfully completed:

- synthetic validation,
- evaluator review,
- regression testing, and
- routing validation.

---

# Existing Limitations

The current fatigue model introduced temporal awareness into HumanOS routing and successfully demonstrated that participant behavior can change over the course of a session.

Subsequent validation and architectural audits identified several limitations that should be addressed before further expansion.

## Limitation 1 — Latency Is Ambiguous

An increase in response time is not, by itself, sufficient evidence of fatigue.

Slower responses may also reflect:

- increased task difficulty,
- deliberate problem solving,
- increased engagement,
- greater cognitive effort.

Latency therefore requires corroborating behavioral evidence before supporting a fatigue interpretation.

---

## Limitation 2 — Effort and Fatigue Are Conflated

Validation Trial 01 identified participants who demonstrated:

- increasing response time,
- stable accuracy,
- stable confidence.

Independent evaluator review interpreted these cases as increasing effort rather than fatigue.

The current fatigue model does not explicitly distinguish these constructs.

---

## Limitation 3 — Routing Dependency Duplication

The routing signal dependency audit identified one confirmed dependency duplication.

The fatigue signal is derived from temporal observations that are simultaneously routed as independent signals.

This allows the same underlying participant observations to influence routing decisions through multiple pathways.

The audit found no evidence that this behavior is systemic elsewhere within the routing architecture.

---

# Proposed Fatigue Model

The redesigned fatigue model separates observable fatigue from other forms of behavioral change by requiring corroborating evidence before assigning a fatigue classification.

The model remains observational and does not infer internal psychological states.

## Fatigue States

### Low

No meaningful behavioral evidence of fatigue is present.

Routing proceeds normally.

---

### Moderate

Behavioral observations suggest the possibility of emerging fatigue but the available evidence remains limited.

Moderate fatigue should be interpreted as an observation requiring continued monitoring rather than confirmation of fatigue.

---

### Elevated

Multiple independent behavioral observations consistently indicate fatigue-related behavioral degradation.

Elevated fatigue represents the strongest fatigue assessment available within the HumanOS routing pipeline and may trigger adaptive stabilization strategies.

---

## Required Evidence

Fatigue assessments shall be based on multiple independent observations.

Examples of candidate evidence include:

- increasing response latency,
- declining accuracy,
- increasing retry behaviour,
- increasing hesitation.

The specific evidence combinations and thresholds shall be determined through validation rather than assumption.

No individual observation shall independently trigger a fatigue classification.

---

## Explicit Separation From Effort

The redesigned model distinguishes observable effort from observable fatigue.

For example:

Increasing response latency accompanied by stable accuracy may indicate increased effort, deliberate reasoning, or greater task engagement.

This observation alone shall not be classified as fatigue.

Future versions of HumanOS may introduce an independent effort signal to describe these behavioral patterns without conflating them with fatigue.

---

# Validation Strategy

The redesigned fatigue model shall not replace the existing implementation until it satisfies predefined validation criteria.

Validation shall include:

## Synthetic Validation

Candidate fatigue thresholds shall be evaluated against representative simulated participant trajectories to verify expected classifications.

---

## Evaluator Validation

Independent evaluators shall review representative participant trajectories to determine whether fatigue classifications align with observed participant behaviour.

Evaluator disagreement shall be documented and used to refine fatigue criteria where appropriate.

---

## Regression Testing

Existing routing behaviour unrelated to fatigue shall remain unchanged.

The redesign must not introduce unintended behavioural regressions elsewhere within the HumanOS routing pipeline.

---

## Routing Validation

Routing decisions generated from the redesigned fatigue model shall remain transparent and explainable.

Every stabilization decision should be traceable to observable supporting evidence.

---

# Implementation Roadmap

The fatigue signal redesign will proceed in the following stages.

## Phase 1

Complete architecture and validation design.

Status: Completed.

---

## Phase 2

Implement redesigned fatigue classification logic.

Status: Completed.

---

## Phase 3

Validate the redesigned model using synthetic datasets and evaluator review.

Status: In progress.

---

## Phase 4

Integrate the redesigned fatigue model into adaptive routing.

Status: Pending.

---

## Phase 5

Review routing behaviour following deployment and document any additional findings.

Status: Pending.
