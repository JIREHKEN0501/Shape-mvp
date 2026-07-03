# Routing Signal Dependency Audit

**Date:** 2026-06-27

**Status:** Completed

**Area:** Routing Architecture / Signal Governance

**Related**

* Finding 09 — Fatigue Risk Trigger Was Over-Sensitive
* Finding 14 — Effort and Fatigue Represent Distinct Behavioral Constructs
* Finding 15 — Fatigue Routing Introduces Dependency Duplication

---

# Purpose

This audit was conducted to determine whether the HumanOS routing pipeline contains dependency relationships that allow the same underlying behavioral observation to influence routing decisions through multiple pathways.

The investigation was initiated following the redesign of the fatigue model (Finding 09), where concern arose that routing decisions might be unintentionally amplifying evidence by treating derived signals and their parent observations as independent inputs.

The objective was to establish an evidence-based inventory of routed signals before designing any architectural remediation.

---

# Scope

The audit examined the complete routing signal pathway:

```
analytics.py
        ↓
signal_extractor.py
        ↓
signal_arbitrator.py
```

Only signals participating in adaptive routing decisions were considered.

Participant summaries, dashboards, interpretation reports, and validation artifacts were outside the scope of this audit.

---

# Audit Method

For every routed signal, the following questions were answered:

1. Where is the signal created?
2. Is the signal computed directly from participant observations?
3. Is the signal derived from other HumanOS signals?
4. Does its parent signal also enter the routing pipeline?
5. Could the same underlying evidence influence routing more than once?

Signals were then classified as either:

* **Primary** — computed directly from observable participant data.
* **Derived** — computed from one or more existing HumanOS signals or higher-level interpretations.

---

# Routing Signal Inventory

| Routed Signal            | Classification | Immediate Inputs                                  | Parent Also Routed? | Observation                      |
| ------------------------ | -------------- | ------------------------------------------------- | ------------------- | -------------------------------- |
| accuracy_trend           | Primary        | Task correctness observations                     | No                  | Independent temporal signal      |
| latency_trend            | Primary        | Response latency observations                     | No                  | Independent temporal signal      |
| confidence_trend         | Primary        | Retry observations                                | No                  | Independent temporal signal      |
| fatigue_risk             | Derived        | accuracy_trend + latency_trend + confidence_trend | **Yes**             | Confirmed dependency duplication |
| likely_response_style    | Derived        | category_patterns                                 | No                  | Parent remains internal          |
| risk_under_time_pressure | Derived        | category_patterns                                 | No                  | Parent remains internal          |

---

# Findings

## Observation 1

The temporal behavior layer is architecturally well separated.

The three temporal routing primitives:

* accuracy_trend
* latency_trend
* confidence_trend

are each computed directly from independent participant observations.

No evidence was found that these signals are themselves derived from other HumanOS signals.

---

## Observation 2

The behavioral prediction layer follows a hierarchical design.

Signals such as:

* likely_response_style
* risk_under_time_pressure

are derived from higher-level behavioral abstractions (category_patterns).

However, those parent abstractions are not routed independently.

Consequently, no dependency duplication was identified within the behavioral prediction pathway.

---

## Observation 3

A single confirmed dependency duplication was identified.

fatigue_risk is derived from:

* accuracy_trend
* latency_trend
* confidence_trend

while those temporal signals are simultaneously routed as independent routing inputs.

This permits the same underlying participant observations to influence routing decisions through both:

1. direct temporal signals, and
2. the derived fatigue assessment.

---

# Architectural Assessment

The original hypothesis proposed that routing dependency duplication might be systemic.

The audit does not support that conclusion.

Instead, the evidence indicates that dependency duplication is currently localized to the fatigue routing pathway.

No comparable dependency relationships were identified among the remaining routed behavioral prediction signals.

---

# Implications

The audit supports a targeted remediation strategy rather than a general redesign of the routing architecture.

Future work should focus on:

* redesigning fatigue signal generation,
* clarifying the interaction between fatigue and temporal routing,
* preventing derived fatigue assessments from unintentionally reinforcing their own parent observations.

The remaining routing architecture does not currently require structural modification based on the evidence collected during this audit.

---

# Conclusion

This audit established a complete inventory of routed HumanOS signals and traced each signal to its originating observations.

Only one confirmed dependency duplication was identified.

The evidence indicates that the routing architecture is largely well structured, with the fatigue pathway representing a localized architectural issue rather than a system-wide signal governance failure.

This audit provides the evidential basis for subsequent fatigue remediation work and supports Finding 15.


## Next Steps

This audit supports the following subsequent work:

- Finding 15 — Fatigue Routing Introduces Dependency Duplication
- Fatigue Signal Remediation Sprint
- Routing Signal Governance Improvements

