# HumanOS Effort Signal Design

Date: 2026-06-16

Status: Proposed

Area: Temporal Analysis

---

## Motivation

Validation Trial 01 revealed a distinction between:

* fatigue
* increasing effort

Current HumanOS fatigue logic may classify rising latency as moderate fatigue risk even when:

* accuracy remains stable
* retries remain stable
* hesitation remains stable

Independent evaluators reviewing participant artifacts interpreted such cases primarily as increasing effort rather than fatigue.

These observations suggest that effort and fatigue may represent distinct behavioral constructs and should not automatically be treated as equivalent.

---

## Proposal

Introduce a separate effort signal.

The effort signal is observational.

It does not imply:

* fatigue
* motivation
* strategy
* intent
* internal cognitive state

It only describes observable changes in effort-related indicators derived from available telemetry.

The objective is to capture effort-related observations without introducing unsupported explanations.

---

## States

### stable

Latency remains relatively consistent across the observation window.

Accuracy remains stable.

Interpretation:

No notable change in observed time investment.

---

### rising

Latency increases relative to earlier observations.

Accuracy remains stable.

Interpretation:

Increased time investment observed alongside maintained performance.

---

### declining

Latency decreases relative to earlier observations.

Accuracy remains stable.

Interpretation:

Reduced time investment observed alongside maintained performance.

No explanation regarding cause is implied.

---

### unknown

Signal combination is ambiguous.

Available evidence is insufficient to determine effort direction.

Examples may include:

* latency increasing while accuracy declines
* conflicting signals across indicators
* incomplete observation windows

Interpretation:

Insufficient evidence to classify effort direction.

---

## Examples

### Example A — effort_signal = rising

Observed:

* latency increasing
* accuracy stable

Output:

```text
effort_signal = rising
```

Interpretation:

Increased time investment observed alongside maintained performance.

This is not automatically a fatigue indicator.

---

### Example B — effort_signal = unknown

Observed:

* latency increasing
* accuracy declining

Output:

```text
effort_signal = unknown
```

Reason:

Latency increase accompanies declining performance.

Available evidence is insufficient to determine whether the pattern reflects effort, fatigue, task complexity, or another factor.

Fatigue-related assessment remains the responsibility of fatigue logic.

---

### Example C — effort_signal = stable

Observed:

* latency stable
* accuracy stable

Output:

```text
effort_signal = stable
```

Interpretation:

No meaningful change in observed time investment.

---

### Example D — effort_signal = declining

Observed:

* latency decreasing
* accuracy stable

Output:

```text
effort_signal = declining
```

Interpretation:

Reduced time investment observed alongside maintained performance.

No explanation regarding cause is implied.

---

## Boundaries

The effort signal operates independently from fatigue assessment.

### Effort Signal Owns

Cases where:

* latency changes
* accuracy remains stable

The effort signal describes observable effort-related patterns only.

---

### Fatigue Logic Owns

Cases where:

* accuracy declines
* performance degradation is observed

Fatigue assessment remains a separate concern.

---

### Overlap Cases

Example:

* latency increasing
* accuracy declining

Output:

```text
effort_signal = unknown
```

Fatigue logic may independently assess fatigue risk using its own criteria.

These outputs are not in conflict.

They describe different aspects of the same observation window.

---

## Validation Considerations

Before integration, the proposal should be evaluated through:

### Synthetic Testing

Verification that effort classifications behave consistently across representative signal combinations.

Particular attention should be paid to boundary conditions where effort and fatigue may appear similar.

---

### Evaluator Review

Independent evaluators should review sample participant artifacts to determine whether effort-related classifications remain distinguishable from fatigue-related interpretations.

---

### Regression Review

Introduction of an effort signal should not weaken existing fatigue detection logic.

Any future implementation should demonstrate that effort and fatigue remain separate observational constructs.

---

### Ambiguity Handling

The system should preserve an unknown state when evidence is insufficient.

HumanOS should avoid forcing effort classifications when available telemetry does not support them.

---

## Relationship To Finding 09

This proposal emerged from the Fatigue Risk Audit.

The audit identified that rising latency alone may reflect multiple phenomena, including:

* increasing effort
* deliberation
* adaptation
* fatigue

The effort signal is intended to capture one observable component of this pattern without assuming a specific explanation.

---

## Status

Not implemented.

Proposed for future validation and review.

No production integration is recommended until fatigue remediation work is completed and the relationship between effort and fatigue signals has been further evaluated.

