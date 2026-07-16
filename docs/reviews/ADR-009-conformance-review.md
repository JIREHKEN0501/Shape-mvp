# ADR-009 Architectural Conformance Review

Status: In Progress

Purpose

To evaluate existing HumanOS runtime components for conformance with the governance requirements established by ADR-009 before implementation changes are introduced.

## Component

Signal Extractor

### ADR-009 Status

⚠️ Partially Compliant

### Observations

The Signal Extractor successfully converts governed evidence into normalized routing signals while preserving signal type, confidence, priority, and source.

However, dependency relationships between governed evidence objects are not preserved during signal extraction.

Signals do not distinguish evidence class, nor do they identify the independent observations supporting derived evidence.

### Findings

Finding 1

Dependency identity is not currently populated during signal extraction despite the RoutingSignal schema providing an extensible metadata field capable of preserving such information.
The Signal Arbitrator currently consumes routing signals as independent runtime observations.

Dependency relationships between governed evidence objects are not considered during arbitration, preventing dependency-aware runtime reasoning.

Finding 2

Evidence class is not currently represented within routing signal metadata despite the existing schema supporting extensible governance metadata.
Routing directives are determined without evaluating the dependency lineage of the evidence contributing to the decision.

Finding 3

Independent evidence provenance is not available during runtime signal consumption.
Existing governance metadata supported by the RoutingSignal schema is not consumed during runtime arbitration.

Finding 4

Routing decisions currently treat all signals as having equivalent runtime influence regardless of confidence, priority, or dependency structure.

### Recommendations

Extend routing signals to include governance metadata supporting:

- Dependency Identity
- Evidence Class
- Independent Evidence Set

This enhancement would satisfy ADR-009 without altering existing routing behaviour.

1.

Incorporate dependency metadata into arbitration.

2.

Evaluate runtime influence using dependency-aware evidence relationships.

3.

Consume evidence class during routing decisions.

4.

Incorporate confidence and priority into governed runtime influence.

5.

Preserve dependency-aware reasoning within routing explanations

Positive Finding

The RoutingSignal schema already provides an extensible metadata mechanism suitable for dependency-aware governance.

ADR-009 implementation can therefore extend existing routing metadata without requiring structural modification to the routing signal model.
The Signal Arbitrator already demonstrates several governance-aligned characteristics.

- Deterministic decision generation.
- Explicit conflict detection.
- Human-readable routing rationale.
- Session-scoped decision-making.

### Findings

Finding 1

tasks.py already preserves extensive runtime traceability through routing traces, governance envelopes, orchestration health evaluation, and task metadata.

Finding 2

No architectural changes to the routing pipeline structure are required for ADR-009 compliance.

Finding 3

Remaining ADR-009 implementation work depends upon upstream routing components exposing dependency-aware governance information.

Recommendations

No structural modifications to tasks.py are currently recommended.

Upon completion of dependency-aware routing within the Signal Extractor and Signal Arbitrator, tasks.py should preserve any additional governance metadata required for runtime traceability.

# Overall Assessment

ADR-009 implementation readiness is high.

The current routing architecture already provides:

- Modular routing orchestration
- Deterministic runtime decisions
- Routing trace preservation
- Governance-state synthesis
- Runtime explainability infrastructure

Remaining implementation work is concentrated within dependency-aware signal production and dependency-aware signal consumption.

No architectural redesign of the routing pipeline is required.


Component	         Status
RoutingSignal Schema	✅ Compliant
Signal Extractor	⚠️ Partially Compliant
Signal Arbitrator	⚠️ Partially Compliant
tasks.py        	✅ Mostly Compliant

And then:

ADR-009 Implementation Priorities
Populate governance metadata during signal extraction.
Interpret dependency-aware metadata during runtime arbitration.
Extend runtime traceability with dependency-aware information.
Validate ADR-009 compliance.


New Finding
Finding R-009-02: Routing Consumes a Legacy Participant Summary

Observation

The adaptive routing pipeline currently derives routing decisions from _summarise_history(events) rather than the governed participant summary produced by generate_participant_summary(participant_id).

Evidence

Runtime investigation demonstrated:

generate_participant_summary() produces:
temporal_behavior
behavior_prediction
patterns
resolved_behavior_patterns
governed interpretations
_summarise_history() produces only:
attempted_task_ids
attempts_by_category
correct_by_category
difficulties_by_category

Consequently:

extract_routing_signals() receives incomplete participant summaries during runtime.
Routing signals are not generated despite governed analytics existing.
Runtime routing traces contain empty signals_considered.

Architectural Impact

HumanOS currently maintains two independent participant summary pipelines.

This creates divergence between governed analytics and adaptive routing.

Recommendation

Adaptive routing shall consume the governed participant summary as its canonical evidence source.
