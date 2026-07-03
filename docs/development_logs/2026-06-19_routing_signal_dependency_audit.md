# Routing Signal Dependency Audit

Date: 2026-06-19

Status: Investigation

Area: Routing / Signal Arbitration

Related Findings:

* Finding 09 — Fatigue Risk Trigger Was Over-Sensitive
* Finding 14 — Effort And Fatigue Are Distinct Signals

---

## Purpose

This audit investigates whether HumanOS routing decisions are treating derived signals and source signals as independent evidence.

The investigation emerged during remediation work for Finding 09.

---

## Background

Validation Trial 01 identified a participant exhibiting:

* 100% accuracy
* no incorrect responses
* stable performance
* minimal hesitation

Despite this, HumanOS produced:

```text
latency_trend = slowing_down
fatigue_risk = moderate
```

Routing traces showed:

```text
stabilize = true
reduce_difficulty = true
```

This raised concerns that routing behavior may be influenced by a fatigue signal that is itself derived from latency observations.

---

## Inspection Results

### Analytics Layer

Current fatigue logic:

```python
if (
    accuracy_trend == "declining"
    and latency_trend == "slowing_down"
):
    fatigue_risk = "elevated"

elif (
    latency_trend == "slowing_down"
    or confidence_trend == "fluctuating"
):
    fatigue_risk = "moderate"
```

Observation:

Latency alone can produce:

```text
fatigue_risk = moderate
```

---

### Signal Extraction Layer

Inspection of:

```text
project/app/services/routing/signal_extractor.py
```

revealed that both:

```text
fatigue_risk
```

and

```text
latency_trend
```

are emitted as independent routing signals.

Example:

```text
fatigue_risk = moderate
latency_trend = slowing_down
```

Both are added to the routing signal set.

No dependency awareness exists between the two signals.

---

### Arbitration Layer

Inspection of:

```text
project/app/services/routing/signal_arbitrator.py
```

revealed:

Fatigue rule:

```python
if fatigue in ["moderate", "elevated"]:
    decisions["stabilize"] = True
```

Latency rule:

```python
if latency == "slowing_down":
    decisions["reduce_difficulty"] = True
```

These rules operate independently.

---

## Observed Dependency Chain

Current behavior:

```text
latency_trend = slowing_down
        ↓
fatigue_risk = moderate
        ↓
routing signal

AND

latency_trend = slowing_down
        ↓
routing signal
```

Result:

A single latency observation can influence routing through two separate pathways.

---

## Key Observation

The routing system currently treats:

```text
fatigue_risk
```

and

```text
latency_trend
```

as independent pieces of evidence.

However:

```text
fatigue_risk
```

may be partially or entirely derived from:

```text
latency_trend
```

under current analytics logic.

This creates a risk that the same underlying observation contributes multiple times to routing decisions.

---

## Potential Consequences

### Signal Inflation

Routing confidence may appear stronger than warranted because multiple signals originate from the same underlying evidence.

---

### Stabilization Bias

Participants exhibiting increased deliberation, effort, or challenge engagement may receive stabilization directives despite stable performance.

---

### Difficulty Reduction Bias

Latency increases may reduce difficulty even when accuracy remains stable or improving.

---

### Validation Distortion

Evaluator disagreement may originate from signal architecture rather than behavioral interpretation.

---

## Open Questions

1. Should routing receive both source signals and derived signals?

2. Should derived signals contain dependency metadata?

3. Should arbitration discount signals originating from the same evidence source?

4. Should latency alone influence difficulty adaptation?

5. Should fatigue-based stabilization require performance degradation before activation?

---

## Preliminary Assessment

The issue appears distinct from Finding 09.

Finding 09 concerns fatigue classification thresholds.

This audit concerns signal dependency and routing architecture.

Although related, the two issues may require separate remediation.

---

## Status

Investigation ongoing.

No implementation changes recommended until dependency handling and routing ownership boundaries are clarified.

