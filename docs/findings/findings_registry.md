# HumanOS Findings Registry

## Purpose

This registry tracks significant findings discovered during HumanOS development, auditing, validation, and testing.

A finding represents an observation that materially affects:

* system behavior
* interpretation quality
* validation quality
* evaluator agreement
* governance
* roadmap prioritization

Findings should be tracked independently from development logs.

Development logs capture history.

The Findings Registry captures knowledge.

---

# Finding 01

Title:
Patterns Describe Populations, Not Individuals

Status:
Integrated

Severity:
Critical

Area:
Ethics / Interpretation

Summary:

Behavioral patterns observed within HumanOS must never be interpreted as permanent participant characteristics.

Patterns describe observed behavior within a specific observation window and should not be generalized to the individual outside that context.

Outcome:

Integrated into:

* Ethics documentation
* Governance documentation
* Internal design principles
* Investor roadmap

---

# Finding 02

Title:
Session-Level Observations Must Remain Non-Diagnostic

Status:
Integrated

Severity:
Critical

Area:
Interpretation / Governance

Summary:

HumanOS outputs should remain observational and non-diagnostic.

System outputs must not imply:

* intelligence
* personality
* mental health
* capability ceilings
* future outcomes

Outcome:

Interpretation boundaries added across participant summaries.

---

# Finding 03

Title:
Trajectory Dynamics Deserves Independent Signal Ownership

Status:
Integrated

Severity:
High

Area:
Temporal Analysis

Summary:

Temporal behavior contains meaningful signals independent of static performance metrics.

Trajectory Dynamics introduced:

* trajectory_shape
* trajectory_state
* hesitation_trend
* accuracy_range

Outcome:

Integrated into temporal behavior pipeline.

---

# Finding 04

Title:
Latency And Hesitation Measure Different Phenomena

Status:
Integrated

Severity:
High

Area:
Telemetry

Summary:

Latency measures task duration.

Hesitation measures decision friction.

The two should not be merged into a single signal.

Outcome:

Both retained as separate behavioral signals.

---

# Finding 05

Title:
Speed Claims Were Not Supported By Available Evidence

Status:
Resolved

Severity:
High

Area:
Interpretation Layer

Summary:

Pattern generator labeled participants as:

"responds quickly and correctly"

The logic only had access to:

* accuracy
* hesitation

No speed signal was available.

Outcome:

Pattern replaced with:

"Accurate with minimal observable hesitation..."

---

# Finding 06

Title:
Evidence-Constrained Interpretation Principle

Status:
Integrated

Severity:
Critical

Area:
Interpretation Layer

Summary:

Interpretations must remain constrained by available evidence.

Allowed:

Evidence → Interpretation

Disallowed:

Evidence → Assumption → Interpretation

Outcome:

Adopted as a standing HumanOS design principle.

---

# Finding 07

Title:
Top Category Ranking Produced False Differentiation

Status:
Resolved

Severity:
Medium

Area:
Insights

Summary:

When multiple categories shared identical performance scores, one category was arbitrarily labeled:

"Strongest performing category"

This introduced unsupported ranking.

Outcome:

Top-category tie handling implemented.

---

# Finding 08

Title:
Cross-Domain Insights Were Template-Driven Rather Than Evidence-Driven

Status:
Open

Severity:
Medium

Area:
Cross-Signal Reasoning

Summary:

Cross-domain insights generated identical statements:

"Taking more time improves accuracy..."

without verifying that the relationship actually existed.

Outcome:

Logged for future redesign.

Future Direction:

Evidence-based cross-domain reasoning engine.

---

# Finding 09

Title:
Fatigue Risk Trigger Was Over-Sensitive

Status:
Open

Severity:
Medium

Area:
Temporal Analysis

Summary:

Fatigue risk could be elevated solely by latency increases.

Example:

* Stable accuracy
* Stable retries
* Slowing latency

Result:

Moderate fatigue risk

Issue:

Latency increase alone may not indicate fatigue.

Future Direction:

Require multiple supporting signals before fatigue escalation.

---

# Finding 10

Title:
Behavioral Tension Detection Is Too Narrow

Status:
Open

Severity:
Medium

Area:
Interpretation Layer

Summary:

Behavioral tension currently only detects:

Speed vs Accuracy conflict

Other tensions remain invisible:

* increasing effort with stable performance
* increasing hesitation with stable performance
* compensatory strategies

Future Direction:

Expand tension framework beyond speed-accuracy tradeoffs.

---

# Finding 11

Title:
Interpretation Layer Compresses Signal Diversity

Status:
Observed

Severity:
Medium

Area:
Interpretation Layer

Summary:

Many downstream interpretations depend on a small set of category labels:

* fast but inaccurate
* deliberate and accurate
* balanced

Potentially meaningful signal differences may be compressed before interpretation.

Future Direction:

Investigate richer intermediate representations.

---

# Validation Evidence 01

Title:
First Independent Evaluator Comparison

Status:
Completed

Date:
2026-06-12

Summary:

Two independent evaluators reviewed the same participant artifact.

Agreement:

* Stability
* Challenge Retention
* Observed Friction

Disagreement:

* Stable vs Plateauing classification

Key Result:

Disagreement emerged from category-boundary interpretation rather than conflicting observations.

Implication:

Future validation should focus on evaluator calibration and classification definitions.

---

# Registry Maintenance Rules

1. Findings are never deleted.
2. Findings may change status.
3. Findings should reference supporting logs.
4. Resolved findings remain in the registry.
5. Validation evidence receives its own section.
6. Roadmap priorities should be traceable to findings.
7. Major design principles should originate from findings where possible.


Finding 12 — Pattern resolution compression

Current behavioral pattern generation collapses a wide performance range (70%-100%) into a single "high accuracy" bucket.

Impact:

Internally consistent.
Explainable.
May reduce sensitivity to meaningful differences between strong and exceptional performance.

Status:

Future Enhancement

Not Sprint 01.

Not urgent.

Fifth observation — Finding 13

Look at:

cross_insights

"Taking more time improves accuracy..."

appearing everywhere again.

Even though:

logical_reasoning = 83%
moral_dilemma = 80%

and there is no demonstrated causal evidence.

This is the exact issue we logged earlier.

The system is still producing:

Taking more time improves accuracy

based on:

slow_correct > fast_wrong

which is correlation-ish evidence being elevated into causal language.

So Finding 13 becomes:

Finding 13 — Cross-insight causal wording persists

Current cross-domain insights still use causal language ("improves accuracy") despite only observing co-occurrence of latency and outcomes.

Recommended future wording:

Higher accuracy was observed alongside longer response times

or

Correct responses were frequently associated with longer response times

# Finding 14

Title:

Effort And Fatigue Are Distinct Signals

Status:

Observed

Severity:

High

Area:

Temporal Analysis

Summary:

Validation Trial 01 and subsequent signal audits suggest that increasing latency may represent multiple phenomena, including:

* increasing effort
* deliberation
* adaptation
* fatigue

Current HumanOS fatigue classification allows latency increases to contribute directly to fatigue risk escalation, even when:

* accuracy remains stable
* retries remain stable
* hesitation remains stable

This creates a false-positive risk.

A participant demonstrating effort-related latency increases may currently receive a moderate fatigue classification despite showing no observable performance degradation.

Latency alone is insufficient evidence of fatigue.

Latency establishes that a participant is slowing down.

Additional corroborating evidence is required before fatigue becomes a defensible interpretation.

Implications:

* Participant summaries may overstate fatigue risk.
* Evaluator comparisons may be influenced by unsupported fatigue classifications.
* Validation studies may measure disagreement caused by interpretation design rather than genuine signal disagreement.
* Strong performers may be incorrectly characterized when maintaining accuracy under increasing effort.

Validation Evidence:

Validation Trial 01 produced a participant profile demonstrating:

* 100% accuracy
* zero incorrect responses
* stable performance
* minimal hesitation

HumanOS output:

* latency_trend = slowing_down
* fatigue_risk = moderate

Independent evaluators interpreted the pattern primarily as increasing effort rather than fatigue.

This discrepancy motivated a formal audit of fatigue classification logic.

Outcome:

* Fatigue Risk Audit completed.
* Effort Signal Design proposal created.
* Fatigue remediation design initiated.

Future Direction:

Separate effort-related observations from fatigue-related observations.

Future fatigue escalation should require multiple supporting indicators rather than latency trends alone.

Related Findings:

* Finding 08 — Cross-Domain Insights Were Template-Driven Rather Than Evidence-Driven
* Finding 09 — Fatigue Risk Trigger Was Over-Sensitive

```

Status Notes:

Finding 14 does not propose a solution.

It records an observed limitation discovered through validation evidence.

Implementation decisions remain pending future validation and remediation work.
```

# Finding 15

Title:

Derived Signals Can Be Double-Counted During Routing

Status:

Observed

Severity:

High

Area:

Routing / Signal Arbitration

Summary:

Routing inspections revealed that HumanOS currently treats certain derived signals and source signals as independent routing evidence.

A notable example exists between:

* latency_trend
* fatigue_risk

Current analytics logic allows fatigue_risk to be generated from latency observations.

However, both signals are independently emitted into the routing pipeline and independently influence arbitration decisions.

This creates a dependency violation.

The routing layer may interpret a single underlying observation as multiple pieces of evidence.

Observed Dependency Chain:

```text
latency_trend
        ↓
fatigue_risk
        ↓
routing signal

AND

latency_trend
        ↓
routing signal
```

Result:

A single latency observation may contribute to:

* stabilization decisions
* difficulty reduction decisions

through multiple pathways.

Implications:

* Signal confidence may be inflated.
* Routing decisions may appear supported by multiple signals when only one underlying observation exists.
* Participants demonstrating increased effort or deliberation may receive unnecessary stabilization.
* Validation results may be distorted by signal architecture rather than behavioral evidence.

Validation Evidence:

Routing Signal Dependency Audit

Date:

2026-06-19

Supporting Inspection:

* signal_extractor.py
* signal_arbitrator.py
* routing_trace_log.jsonl

Outcome:

Dependency audit initiated.

Routing ownership and signal dependency relationships under review.

Future Direction:

Investigate dependency-aware routing.

Consider:

* source vs derived signal distinction
* signal lineage tracking
* arbitration de-duplication
* dependency-aware confidence calculations

Status Notes:

This finding is distinct from:

* Finding 09 (fatigue threshold sensitivity)
* Finding 14 (effort versus fatigue interpretation)

This finding concerns routing architecture and evidence handling.

# Finding 16

Title:

Trial 01 Did Not Meaningfully Exercise Retry Trend

Status:

Observed

Severity:

Medium

Area:

Temporal Behavior Analysis

Summary:

The newly introduced `retry_trend` observational signal was validated across all available Trial 01 participants.

Validation completed successfully with no implementation failures or runtime regressions.

Across all observed participants:

* retry_trend = stable

No participants produced:

* retry_trend = increasing
* retry_trend = decreasing

Inspection of participant retry histories showed negligible effective retry variation throughout the observed sessions.

Observed Pattern:

```text
effective retries

0
0
0
0
0
0

↓

early average = 0
late average = 0

↓

retry_trend = stable
```

Result:

The implementation behaved as designed.

The available Trial 01 dataset did not meaningfully exercise the retry_trend signal.

Implications:

* retry_trend implementation is functioning correctly.
* Current validation data cannot evaluate the discriminative capability of retry_trend.
* The Elevated fatigue pathway cannot yet be empirically exercised through retry behavior.
* Additional validation using datasets with greater retry variation will be required.

Validation Evidence:

Retry Trend Validation

Date:

2026-06-28

Supporting Inspection:

* analytics.py
* generate_participant_summary()
* Trial 01 participant summaries (n = 98)

Outcome:

Implementation verified.

Behavioral validation remains limited by dataset characteristics.

Future Direction:

Investigate retry behavior during Trial 02.

Potential areas for investigation include:

* task characteristics
* interface behavior
* participant strategy
* validation dataset composition

No single explanation is currently supported by the available evidence.

Status Notes:

This finding extends:

* Finding 09 (fatigue threshold sensitivity)
* Finding 14 (effort versus fatigue separation)

This finding concerns validation coverage rather than implementation correctness.

Sprint Outcome

Objective

Replace the fatigue classifier with an evidence-based runtime contract.

Result

Completed.

Implementation

Added retry-based corroboration pathway.
Removed confidence-derived fatigue inference.
Introduced independent fatigue classification logic.
Preserved observation-first architecture.

Validation

Regression successful.
98 participants evaluated.
No implementation regressions observed.
Expected classification changes confirmed.

Remaining limitation

Trial 01 does not meaningfully exercise retry-dependent Elevated fatigue classification.

Future validation required.
