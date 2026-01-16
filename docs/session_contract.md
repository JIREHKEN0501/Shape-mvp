Session Contract

Version: 1.0
Last updated: 2026-01-11

1. Purpose

This document defines what a session represents in this system, what participants and administrators can access, and the guarantees the system makes regarding interpretation, privacy, and use of data.

This contract exists to ensure:

Clarity for participants

Responsible system design

Ethical and statistical correctness

Long-term trust and defensibility


2. What a Session Is

A session represents a single, time-bounded interaction with a task.

A session is defined by:

One participant

One task (and task version)

One continuous attempt

A unique session identifier (session_id)

A session captures how a task was approached during that attempt, not who the participant is.

Sessions are contextual, temporary, and non-diagnostic by design.


3. What a Session Is Not

A session is not:

A measure of intelligence

A personality profile

A permanent label

A prediction of future performance

A diagnosis or psychological assessment

No session, on its own or combined with others, defines an individual.


4. Data Stored in a Session

Depending on task type, a session may include:

Timing information

Aggregated task outcomes (e.g., accuracy)

Interaction patterns (e.g., pauses, retries)

A generated session summary (if the session is complete)

The system avoids storing:

Raw personal identifiers

Interpretive labels

Cross-session traits

Inferred psychological attributes

### Session Summary Adapter

All session summaries returned to participants MUST:
- Be generated via `build_session_summary`
- Be session-scoped only
- Never assign traits, labels, or diagnoses
- Follow a stable output structure


5. Participant Access (Summary-First)

Participants may retrieve only their own sessions.

Participant access is:

Session-scoped

Ownership-verified

Summary-first

Participants receive:

Aggregated metrics

A descriptive session summary (if the session is complete)

Participants do not receive:

Raw internal logs

Cross-participant comparisons

Hidden inferences

Administrative analytics


6. Interpretation Boundaries

All metrics and summaries describe patterns observed within a single session.

Key principles:

Patterns describe behavior in context, not identity

Averages are not guarantees

Trends do not eliminate individual variation

Exceptions do not invalidate distributions

The system intentionally avoids converting statistical patterns into personal claims.


7. Population Patterns vs Individuals

This system distinguishes clearly between:

Population-level patterns (used for research and system design)

Individual sessions (used for reflection and feedback)

Population statistics:

Describe trends

Inform system behavior

Do not apply deterministically to individuals

Individual sessions:

Are not compared against population norms

Are not used to assign traits

Are not treated as predictive


8. Administrative Access

Administrative access, where present, is:

Purpose-limited

Audited

Aggregated by default

Administrative tools are designed to:

Monitor system health

Improve task design

Ensure ethical compliance

They are not designed for surveillance, profiling, or participant ranking.


9. Schema Versioning & Compatibility

Each session includes a schema version.

The system:

Supports known schema versions explicitly

Treats unknown or unsupported versions as invalid

Avoids silent reinterpretation of legacy data

This ensures long-term correctness and interpretability.


10. Guarantees

This system guarantees that it will:

Treat sessions as contextual and non-permanent

Separate population patterns from individuals

Avoid diagnostic or inferential claims

Preserve participant privacy by default

Provide transparency about what is measured and why


11. Non-Goals

This system is not intended to:

Predict personal outcomes

Replace professional assessment

Rank or score individuals in isolation

Produce definitive conclusions about people


12. Closing Principle

Patterns describe populations, not people.
Sessions describe moments, not identities.


This principle governs system design, interpretation, and communication.


## Stability Guarantee (v1)

The session summary contract is considered **stable** under version `1.x`.

- Keys may be added, but existing keys MUST NOT change meaning
- Any breaking change requires a new major version (v2)
- Summaries describe **session-level patterns only**
- Summaries MUST NOT:
  - assign traits
  - predict future behavior
  - label individuals
  - persist across sessions as identity

Incomplete sessions MUST return:
```json
{
  "session_summary": null
}
