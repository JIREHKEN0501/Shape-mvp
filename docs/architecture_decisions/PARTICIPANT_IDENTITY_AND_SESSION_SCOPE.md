# HumanOS Participant Identity and Session Scope
## Architectural Decision Brief

### Status
Superseded by ADR-010

This decision brief is retained as historical architectural context.
The participant identity and session-scope decision is established by
ADR-010: Participant Session Scope and Governed Continuity.

## Question

What does participant identity mean within HumanOS, and under what conditions, if any, may participant history influence future HumanOS interactions?

## Why This Decision Is Required

The repository currently contains two architectural lines:

1. A session-scoped participant model in which sessions are contextual,
   time-bounded, non-diagnostic, and not intended to create internal
   longitudinal participant profiles.

2. An adaptive runtime in which a pseudonymous participant identifier
   is used to access participant history for adaptive task selection.

Both have substantial supporting implementation and documentation.

No existing ADR explicitly defines the relationship between these models.

## Established Principles

- Sessions are contextual and time-bounded.
- Sessions are not themselves personal traits.
- Core architecture and aviation materials prohibit internal longitudinal linkage.
- Adaptive routing was intentionally developed around participant history.
- Adaptive routing is intended to consume governed participant summaries
  and governed evidence.
- The Experience Layer may communicate governed session-state and
  experience continuity but must not perform behavioral reasoning.

## Decision Questions

### A. Participant Identity

Does `participant_id` represent:

1. only the current consent/session context;
2. a pseudonymous identity that may persist across sessions; or
3. a deployment-dependent identity whose permitted scope is explicitly governed?

### B. Session Scope

Is every HumanOS interaction:

1. strictly independent;
2. part of a governed adaptive session; or
3. dependent on the deployment mode?

### C. Adaptive History

May prior participant interaction influence future task selection?

If yes:

- under what consent condition?
- under what deployment condition?
- what evidence may be used?
- what history may be retained?
- what governance constraints apply?

### D. Deployment Boundaries

Are the aviation/pilot restrictions:

1. global HumanOS invariants; or
2. deployment-specific constraints?

### E. Experience Continuity

May HumanOS preserve participant-facing continuity such as:

- accessibility preferences;
- language;
- navigation state;
- experience preferences;

without using prior behavioral evidence for adaptive routing?

### F. Product Boundary

Are the session-scoped and adaptive systems:

1. two implementations of one HumanOS runtime;
2. two explicitly governed HumanOS operating modes; or
3. one HumanOS runtime plus externally managed longitudinal analysis?

## Evidence Gaps

The repository does not currently define:

- participant-ID persistence policy;
- consent-to-adaptive-history mapping;
- deployment-specific routing permissions;
- a formal operating-mode matrix;
- a canonical participant runtime;
- the handoff between Experience Layer consent and the selected runtime.

## Required Outcome

Before backend consolidation or Experience Layer integration,
HumanOS must establish:

- participant identity scope;
- session scope;
- adaptive-history permission;
- consent requirements;
- deployment boundaries;
- experience-continuity boundaries; and
- the relationship between session-scoped and adaptive runtime models.
