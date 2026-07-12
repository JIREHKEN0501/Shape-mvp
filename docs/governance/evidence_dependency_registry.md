# Evidence Dependency Registry

Version: 1.0

Status: Active

Last Updated: 2026-07-12

Related

- ADR-008 — Evidence Governance
- Evidence Governance Sprint
- Routing Governance Sprint

# Purpose

This registry provides a governed inventory of HumanOS evidence objects, documenting their lineage, dependencies, downstream consumers, runtime eligibility, and validation status.

The registry operationalizes ADR-008 by ensuring every governed evidence object remains traceable to its originating observations while preserving transparency across downstream evidence transformations.

This registry is a living governance artifact and shall be updated whenever evidence objects are introduced, modified, deprecated, or reclassified.

---

# Registry Principles

Every governed evidence object shall:

1. Have documented lineage back to its originating observations.

2. Explicitly record any dependencies on other governed evidence objects.

3. Identify all known downstream consumers.

4. Distinguish between runtime, descriptive, and predictive evidence.

5. Record its current validation status.

6. Be reviewed whenever upstream evidence dependencies change.

---

---

# Evidence Layers

HumanOS currently organizes governed evidence into the following layers.

| Layer | Purpose |
|-------|---------|
| Observation | Directly measured participant behaviour. |
| Interpretation | Semantic interpretation derived from observations. |
| Prediction | Conditional forward-looking behavioural inference. |
| Descriptive Interpretation | Explains observed behaviour without influencing runtime adaptation. |

# Evidence Inventory

| Evidence Object            | Layer          | Evidence Type              | evidence Producer             | Depends On                                 | Downstream Consumers                                                        | Runtime Consumer | Validation Status | Notes                                  |
| -------------------------- | -------------- | -------------------------- | ---------------------- | ------------------------------------------ | --------------------------------------------------------------------------- | ---------------- | ----------------- | -------------------------------------- |
| latency_trend              | Observation    | Observation                | analytics.py           | Ordered response latency                   | fatigue_risk, tasks.py, routing                                             | Yes              | Audited           | Independent temporal observation       |
| accuracy_trend             | Observation    | Observation                | analytics.py           | Ordered task accuracy                      | fatigue_risk, tasks.py, routing                                             | Yes              | Audited           | Independent temporal observation       |
| retry_trend                | Observation    | Observation                | analytics.py           | Retry counts                               | fatigue_risk                                                                | Yes              | Audited           | Independent temporal observation       |
| hesitation_trend           | Observation    | Observation                | trajectory_dynamics.py | Hesitation events                          | Participant summary                                                         | No               | Audited           | Descriptive observation                |
| accuracy_range             | Observation    | Observation                | trajectory_dynamics.py | Segmented accuracy                         | trajectory_state                                                            | No               | Audited           | Descriptive observation                |
| fatigue_risk               | Interpretation | Runtime Interpretation     | analytics.py           | latency_trend, accuracy_trend, retry_trend | tasks.py, routing                                                           | Yes              | Audited           | Multi-evidence interpretation          |
| confidence_trend           | Interpretation | Runtime Interpretation     | analytics.py           | Retry variance                             | tasks.py, routing                                                           | Yes              | Audited           | Operationalizes retry consistency as behavioral confidence         |
| category_patterns          | Interpretation | Evidence Producer          | analytics.py           | Category behaviour statistics              | resolved_behavior_patterns, likely_response_style, risk_under_time_pressure | Yes              | Audited           | First-order interpretation             |
| resolved_behavior_patterns | Interpretation | Evidence Resolver          | analytics.py           | category_patterns, insight_patterns        | Future reporting / interpretation resolution layer                                           | Not currently    | Audited           | Preserves supporting evidence          |
| likely_response_style      | Prediction     | Prediction                 | analytics.py           | category_patterns                          | tasks.py, routing                                                           | Yes              | Audited           | Majority-pattern prediction            |
| risk_under_time_pressure   | Prediction     | Prediction                 | analytics.py           | category_patterns ("fast but inaccurate")  | tasks.py, routing                                                           | Yes              | Audited           | Conditional behavioural prediction     |
| trajectory_shape           | Interpretation | Descriptive Interpretation | trajectory_dynamics.py | Segmented accuracy                         | Participant summary                                                         | No               | Audited           | Session progression descriptor         |
| trajectory_state           | Interpretation | Descriptive Interpretation | trajectory_dynamics.py | trajectory_shape, accuracy_range           | Participant summary                                                         | No               | Audited           | Higher-order trajectory interpretation |

---

---

# Registry Maintenance

This registry shall be updated whenever:

- a new evidence object is introduced,
- evidence lineage changes,
- downstream consumers change,
- runtime eligibility changes,
- validation status changes,
- evidence is deprecated or removed.
