# Routing Signal Inventory

Date: 2026-06-19

Status: Investigation

Area: Routing / Signal Governance

Related:

* Finding 09
* Finding 14
* Finding 15

---

# Purpose

This inventory documents every signal entering the HumanOS routing pipeline.

The objective is to identify:

* signal origin
* whether the signal is primary or derived
* whether the signal's source also enters routing
* potential dependency relationships

This document does not recommend implementation changes.

Its purpose is to establish an accurate inventory before remediation design.

---

# Classification Rules

## Primary Signal

A signal generated directly from observable participant data.

Examples:

* latency trend
* accuracy trend

Primary signals have no upstream HumanOS signal dependencies.

---

## Derived Signal

A signal computed from one or more existing observations or signals.

Derived signals may summarize or interpret lower-level evidence.

---

## Unknown

Insufficient inspection has been completed to determine origin.

---

# Inventory

| Routing Signal           | Source Module | Primary / Derived | Immediate Inputs                                | Parent Signal Also Routed? | Notes                          |
| ------------------------ | ------------- | ----------------- | ----------------------------------------------- | -------------------------- | ------------------------------ |
| fatigue_risk             | analytics.py  | Derived           | latency_trend, accuracy_trend, confidence_trend | Yes                        | dependency identifieed            |
| latency_trend            | analytics.py  | Primary           | response latency observations                   | No                         | Direct behavioral observation  |
| confidence_trend         | analytics.py  | primary           | retry observations                                         | TBD                        | computed directly from raw telemetry |            |
| accuracy_trend           | analytics.py  | Primary           | task outcomes                                   | No                         | Direct performance observation |
| likely_response_style    | analytics.py  | TBD               | TBD                                             | TBD                        | Requires inspection            |
| risk_under_time_pressure | analytics.py  | TBD               | TBD                                             | TBD                        | Requires inspection            |
| behavior_pattern         | analytics.py  | TBD               | TBD                                             | TBD                        | Requires inspection            |

---

# Current Observations

Confirmed:

* fatigue_risk is derived.
* latency_trend is routed independently.
* Both currently enter the routing pipeline.

Further inspection is required before determining whether additional derived signals share similar dependency relationships.

---

# Scope

Only routing signals are included.

This inventory does not evaluate:

* dashboards
* summaries
* participant reports
* validation artifacts

Only signals influencing adaptive routing decisions are considered.

