# ADR-010: Participant Session Scope and Governed Continuity

## Status

Accepted

## Date

2026-08-09

## Authors

- Jireh Kenneth-Usen
- HumanOS Architecture

## Related

- ADR-008 — Evidence Governance and Conservation
- ADR-009 — Dependency-Aware Evidence Consumption
- HumanOS Participant Identity and Session Scope
- Experience Layer Architectural Brief

---

# Context

HumanOS currently contains both session-scoped participant experiences and an adaptive runtime that can consume governed participant history.

The session-scoped model treats each interaction as contextual and time-bounded and does not, by default, establish an internal longitudinal participant profile.

The adaptive runtime, however, uses a pseudonymous participant identifier to access governed participant history for adaptive task selection.

The repository previously documented these as unresolved architectural lines without defining their relationship.

Investigation of the existing runtime confirms that adaptive routing already operates through governed task-attempt history, participant summaries, evidence, routing decisions, and routing traces.

The investigation also confirms that HumanOS does not currently contain a formal portable state mechanism that permits a bounded representation of one experience to be transmitted into a later experience.

Accordingly, HumanOS must distinguish between:

1. experience continuity;
2. governed adaptive continuity; and
3. raw behavioral longitudinal history.

These are not equivalent architectural concepts.

---

# Decision

HumanOS adopts a **session-scoped-by-default architecture with explicitly governed adaptive continuity**.

## 1. Session Scope by Default

A HumanOS participant interaction is session-scoped by default.

A session provides the immediate context required to conduct and communicate an experience.

Session context shall not, by default, create an unrestricted internal longitudinal participant profile.

Raw behavioral history shall not silently cross session boundaries for adaptive use.

---

## 2. Canonical Adaptive History

Where governed adaptive continuity is authorized, the canonical runtime history format shall be the `task_attempt` representation consumed by the existing adaptive routing architecture.

The participant runtime shall therefore produce evidence in a form compatible with the governed adaptive pipeline rather than maintaining a parallel submission representation that cannot participate in that pipeline.

This decision does not require reimplementation of the existing routing system.

Existing evidence production, dependency-aware evidence consumption, signal extraction, arbitration, governed adaptation, and routing trace mechanisms remain authoritative.

---

## 3. Governed Adaptive Continuity

HumanOS may use accumulated, governed participant evidence to influence a subsequent experience where the deployment mode, consent scope, and applicable governance rules permit such continuity.

Such continuity shall operate through governed evidence and bounded representations rather than unrestricted raw behavioral history.

Adaptive continuity must preserve evidence provenance, dependency relationships, and traceability in accordance with ADR-008 and ADR-009.

No derived representation may acquire greater runtime influence merely because multiple dependent representations describe the same underlying observation.

---

## 4. Experience Continuity Is Distinct From Behavioral Continuity

HumanOS may preserve participant-facing experience continuity without treating that continuity as behavioral longitudinal history.

Experience continuity may include information such as:

- accessibility preferences;
- language preferences;
- navigation state;
- experience preferences; and
- other explicitly permitted participant-facing configuration.

Experience continuity does not, by itself, constitute behavioral inference.

The Experience Layer may communicate governed session state and experience continuity but shall not determine behavioral interpretation, routing decisions, or adaptive difficulty.

---

## 5. Participant Identity

`participant_id` shall not be treated as unrestricted personal identity.

Its meaning and permitted persistence shall be determined by the applicable HumanOS operating mode, consent scope, deployment constraints, and governance requirements.

Participant identity shall provide only the linkage necessary for an authorized runtime function.

Possession of a participant identifier shall not, by itself, authorize unrestricted access to behavioral history.

---

## 6. Raw History Versus Governed Evidence

HumanOS carries governed evidence forward only within an authorized history boundary.

HumanOS does not silently carry raw behavioral history forward across experiences for inference or adaptive use.

Where adaptive continuity is authorized, the runtime shall consume the governed representations permitted by the applicable architecture and governance rules.

---

# Constitutional Rule

**HumanOS carries governed evidence forward. It does not carry raw behavioral history forward silently.**

---

# Future Portable State

HumanOS acknowledges a future architectural requirement for a bounded portable state mechanism through which one experience may produce a governed representation that can be consumed by a later experience.

That mechanism is not defined by this ADR.

Before implementation, it shall require a separate architectural decision defining at minimum:

- the permitted representation;
- provenance requirements;
- consent scope;
- retention rules;
- participant identity requirements;
- deployment permissions;
- evidence dependencies;
- permitted inference;
- transmission boundaries;
- invalidation and expiry;
- participant visibility and control; and
- governance authority.

Until that architecture is explicitly defined and authorized, existing governed participant history remains the authoritative mechanism for adaptive continuity.

---

# Operating Model

HumanOS therefore supports the following architectural distinction:

### Session-scoped mode

- Immediate experience context is available.
- No unrestricted behavioral history is carried forward.
- Participant experience remains contextual and time-bounded.

### Governed adaptive mode

- Participant history may influence subsequent task selection.
- History must use the canonical governed representation.
- Evidence dependencies and provenance remain preserved.
- Runtime influence remains bounded by independent observations.
- Applicable consent and deployment constraints must authorize continuity.

### Experience continuity

- May exist independently of behavioral adaptation.
- May preserve participant-facing preferences and context.
- Must not be used as a hidden mechanism for behavioral inference.

---

# Non-Goals

This ADR does not:

- define the implementation of a portable cross-experience state object;
- define a new routing algorithm;
- redefine the SignalArbitrator;
- redefine evidence production;
- redefine evidence dependency semantics established by ADR-009;
- authorize unrestricted longitudinal behavioral profiling;
- make the Experience Layer responsible for behavioral reasoning;
- define deployment-specific consent mechanisms;
- replace the existing adaptive routing architecture.

---

# Architectural Consequences

The following consequences are accepted:

1. HumanOS has a session-scoped default rather than unrestricted longitudinal continuity.

2. Adaptive continuity remains possible where explicitly governed.

3. `task_attempt` becomes the canonical adaptive history representation.

4. Participant submission paths that cannot produce the canonical adaptive representation are not considered complete adaptive runtime paths.

5. Experience continuity and behavioral longitudinal history are treated as separate architectural concerns.

6. Future cross-experience state requires a separate architectural decision rather than being introduced implicitly through participant identifiers, hashes, summaries, or other derived representations.

7. The existing governed routing pipeline remains the authoritative mechanism for adaptive decision-making.

---

# Compliance Requirements

A compliant implementation shall ensure that:

1. Raw behavioral history is not silently used across session boundaries for adaptive purposes.

2. Adaptive continuity uses only representations authorized by the applicable operating mode and consent scope.

3. Governed evidence retains sufficient provenance and dependency information for runtime interpretation.

4. Participant identity does not automatically imply unrestricted access to historical behavioral evidence.

5. Experience continuity mechanisms cannot independently initiate behavioral inference or routing decisions.

6. Any future portable state mechanism is separately authorized before implementation.

---

# Relationship to Previous Architecture

ADR-008 governs evidence production and traceability.

ADR-009 governs dependency-aware consumption of governed evidence during adaptive runtime decision-making.

ADR-010 establishes the participant/session boundary within which those governed mechanisms may operate.

The existing `PARTICIPANT_IDENTITY_AND_SESSION_SCOPE.md` decision brief is therefore resolved by this ADR.

---

# Decision Summary

HumanOS is session-scoped by default.

Governed adaptive continuity is permitted where explicitly authorized.

Experience continuity is distinct from behavioral longitudinal history.

HumanOS carries governed evidence forward; it does not silently carry raw behavioral history forward.

A portable cross-experience state mechanism remains future architectural work and requires its own governance decision before implementation.
