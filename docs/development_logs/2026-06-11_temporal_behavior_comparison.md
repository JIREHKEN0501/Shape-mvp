# 2026-06-11 — Temporal Behavior Comparison

## Objective

Compare the existing HumanOS temporal behavior analytics implementation against the newly developed Trajectory Dynamics engine.

The goal of this review is to determine whether Trajectory Dynamics should replace, extend, or remain independent from the current analytics pipeline.

---

## Systems Compared

### Temporal Behavior V1

Location:

```text
project/app/services/analytics.py
```

Function:

```python
_analyze_temporal_behavior(...)
```

Current outputs:

* accuracy_trend
* latency_trend
* confidence_trend
* fatigue_risk

Methodology:

* Split session into Early and Late segments
* Compare behavioral changes across halves

---

### Trajectory Dynamics V3

Location:

```text
project/app/utils/trajectory_dynamics.py
```

Current outputs:

* accuracy_trend
* hesitation_trend
* trajectory_shape
* trajectory_state
* accuracy_range

Methodology:

* Split session into Early, Middle, and Late segments
* Analyze trajectory movement patterns across all three stages

---

## Findings

### Accuracy Trend

Both systems compute accuracy movement across a session.

The concepts are effectively equivalent.

Trajectory Dynamics provides a richer foundation because it is already connected to trajectory shape and trajectory state reasoning.

Assessment:

```text
Keep Trajectory Dynamics implementation.
```

---

### Latency vs Hesitation

Temporal Behavior V1 evaluates:

```text
response_time_s
```

Trajectory Dynamics evaluates:

```text
hesitation
```

These signals are related but represent different phenomena.

Response time measures total elapsed task duration.

Hesitation attempts to measure uncertainty or decision friction.

Assessment:

```text
Retain both signals.
```

---

### Confidence Trend

Temporal Behavior V1 evaluates retry variance to determine whether behavior is stabilizing or fluctuating.

Trajectory Dynamics currently has no equivalent signal.

Assessment:

```text
Retain Confidence Trend.
```

---

### Fatigue Risk

Temporal Behavior V1 derives fatigue risk from combinations of:

* accuracy trend
* latency trend
* confidence trend

Trajectory Dynamics currently has no fatigue model.

Assessment:

```text
Retain Fatigue Risk.
```

---

### Recovery Detection

Trajectory Dynamics introduces:

```text
trajectory_shape = recovery
trajectory_state = recovering
```

These concepts do not exist in Temporal Behavior V1.

Assessment:

```text
Major improvement.
```

---

### Peak-Then-Fall Detection

Trajectory Dynamics introduces:

```text
trajectory_shape = peak_then_fall
```

This behavior cannot be detected using the existing Early/Late segmentation model.

Assessment:

```text
Major improvement.
```

---

### Accuracy Range

Trajectory Dynamics introduces:

```text
accuracy_range
```

This provides a direct measure of session variability.

Temporal Behavior V1 currently lacks an equivalent metric.

Assessment:

```text
Useful additional signal.
```

---

## Architectural Conclusion

Trajectory Dynamics should not replace Temporal Behavior.

Instead:

```text
Temporal Behavior V2
=
Temporal Behavior V1
+
Trajectory Dynamics V3
```

The systems are complementary.

Temporal Behavior contributes:

* latency trend
* confidence trend
* fatigue risk

Trajectory Dynamics contributes:

* trajectory shape
* trajectory state
* recovery detection
* peak-then-fall detection
* accuracy range

Together they provide a substantially richer description of session-level behavioral movement.

---

## Recommended Integration Path

Phase 1

Keep Trajectory Dynamics independent.

No production integration changes.

---

Phase 2

Integrate Trajectory Dynamics into:

```text
project/app/services/analytics.py
```

through:

```python
_analyze_temporal_behavior(...)
```

---

Phase 3

Expose trajectory outputs through participant summaries and evaluator-facing artifacts.

---

Integration Risks
Accuracy Trend Duplication

Both Temporal Behavior V1 and Trajectory Dynamics V3 currently compute:

accuracy_trend

Running multiple implementations of the same signal may create inconsistent outputs and maintenance overhead.

Proposed Resolution:

Trajectory Dynamics becomes the authoritative owner of
accuracy_trend.

Temporal Behavior V2 consumes the Trajectory Dynamics
result rather than maintaining a separate implementation.
Signal Interpretation Risk

Latency and hesitation represent different behavioral observations and should not be presented as interchangeable measures.

Definitions:

Latency Trend
=
Change in total task completion time.
Hesitation Trend
=
Change in observed decision friction or uncertainty.

Evaluator-facing artifacts should clearly distinguish between these concepts to reduce interpretation errors.

Future Scalability Consideration

Trajectory Dynamics is expected to expand beyond:

trajectory_shape
trajectory_state
recovery detection

Future additions may include:

adaptation analysis
challenge progression
fatigue indicators
difficulty movement analysis

For this reason:

Trajectory Dynamics should remain an independent module.

Temporal Behavior V2 should orchestrate outputs from
Trajectory Dynamics rather than absorb its internal logic

Signal Ownership Principle

HumanOS should maintain a single authoritative implementation for each behavioral signal.

Guideline:

One Signal
One Owner
One Implementation

Examples:

accuracy_trend
→ Trajectory Dynamics
latency_trend
→ Temporal Behavior
confidence_trend
→ Temporal Behavior

This principle reduces duplication, simplifies testing, and improves auditability.


## Status

Current Status:

```text
Comparison Complete
Integration Design Approved
```

Next Step:

```text
Design Temporal Behavior V2 integration.
```

