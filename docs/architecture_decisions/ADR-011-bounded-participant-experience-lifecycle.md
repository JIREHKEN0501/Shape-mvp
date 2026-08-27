# ADR-011: Bounded Participant Experience Lifecycle and Experience-Scoped Summaries

**Status:** Accepted

---

## 1. Context

HumanOS currently represents an individual task interaction as an independent session.

A participant-facing experience may contain multiple tasks executed sequentially. The current task registry defines task ordering through `TASK_SEQUENCE`, but the active participant architecture does not contain an explicit abstraction representing the bounded experience that contains those task sessions.

As a result, the current implementation conflates task completion with experience completion.

The current completion logic is effectively:

```python
is_complete = get_next_task(task_id) is None

This determines whether the current task is the final task in the registered sequence, but does not establish whether the bounded participant experience has completed as a whole.

This creates several architectural ambiguities:

session_id identifies an individual task interaction but does not identify the bounded participant experience containing it.
participant_id provides participant context but must not become an unrestricted historical aggregation key.
task ordering exists independently of experience lifecycle.
task-level summaries exist independently of experience-level completion.
the participant-facing final summary currently operates on the final task session rather than on the completed bounded experience.

ADR-010 establishes that HumanOS is session-scoped by default and that experience continuity is distinct from behavioral continuity.

ADR-010 also establishes that participant identity may provide only the linkage necessary for an authorized runtime function and that raw behavioral history must not silently cross experience boundaries.

This ADR defines the bounded participant experience required to support a multi-task participant flow without introducing unrestricted longitudinal behavioral profiling or portable cross-experience state.

2. Decision

HumanOS will introduce a bounded participant experience as the lifecycle and aggregation boundary for one finite participant-facing task sequence.

A bounded participant experience:

begins following successful participant consent;
receives a new opaque experience_id;
contains zero or more task sessions during its lifecycle;
associates each task session with exactly one bounded experience;
progresses according to the registered task sequence;
becomes completed only when all required tasks have successfully completed;
may become abandoned through an explicit application-level abandonment action;
may produce an experience-scoped participant summary only after successful completion.

The bounded experience is not a permanent representation of the participant.

It does not establish unrestricted longitudinal continuity between separate experiences.

3. Identity and Scope

HumanOS will maintain three distinct identity boundaries:

participant_id
      |
      | authorized participant context
      v
experience_id
      |
      | bounded experience membership
      v
session_id
      |
      | individual task interaction
      v
task_id
3.1 participant_id

participant_id identifies the participant context required by the authorized runtime function.

It may be stored on an experience where required for ownership and authorization.

participant_id must not be used as the aggregation key for participant-facing experience summaries.

Possession of participant_id does not authorize unrestricted retrieval or aggregation of historical behavioral sessions.

3.2 experience_id

experience_id identifies exactly one bounded participant experience.

Every new bounded experience receives a new opaque identifier.

An experience_id is an experience-scoped identifier and must not be reused across separate participant experiences.

The existence of an experience_id does not authorize cross-experience behavioral inference or historical aggregation.

3.3 session_id

session_id continues to identify one individual task interaction.

Task sessions remain independently persisted, contextual, and immutable once saved.

An individual task session belongs to one bounded experience.

4. Experience Lifecycle

The bounded experience lifecycle is:

             ┌──────────────┐
             │    ACTIVE    │
             └──────┬───────┘
                    │
          ┌─────────┴─────────┐
          v                   v
   ┌─────────────┐     ┌─────────────┐
   │  COMPLETED  │     │  ABANDONED  │
   └─────────────┘     └─────────────┘
ACTIVE

The experience is available for the participant's current bounded task flow.

Creation and activation occur as part of successful consent processing.

COMPLETED

The experience has successfully completed all required tasks in its registered sequence and all required task sessions have been successfully persisted and validated.

ABANDONED

The experience has been explicitly abandoned through an authorized application-level action.

Browser closure, network interruption, and inactivity do not automatically mark an experience as abandoned in this phase.

Automatic expiry and timeout-based abandonment are deferred.

5. Experience Creation Boundary

The bounded experience is created following successful consent.

The intended lifecycle is:

POST /consent
      |
      v
consent accepted
      |
      v
create bounded experience
      |
      v
issue experience_id
      |
      v
make experience context available
      |
      v
load first task

Creating the experience at successful consent ensures that every participant task session has an established bounded experience to which it can belong.

An experience may therefore exist without any task session if the participant provides consent but does not begin the first task.

Such an experience remains ACTIVE until an explicit abandonment or future authorized expiry mechanism occurs.

This ADR does not define automatic expiry.

6. Task Session Membership

Each task submission must contain or otherwise resolve the current bounded experience_id through an authorized participant context.

When a task session is persisted:

session_id
experience_id
participant_id
task_id
...

The task session remains independently identifiable and retrievable by session_id.

The experience_id establishes containment only.

It does not change the meaning of the task session or convert the session into a longitudinal participant record.

A task session must not be attached to an experience belonging to another participant context.

A task session must not be silently reassigned between experiences.

7. Completion Semantics

HumanOS will distinguish three separate completion concepts.

7.1 Task session completion

A task session is complete when the submitted task interaction passes the applicable validation and is successfully persisted.

Task completion is independent of whether another task follows.

7.2 Experience completion

An experience is complete only when every required task in the experience's registered task sequence has successfully produced a valid persisted task session.

The fact that:

get_next_task(task_id) is None

must not, by itself, be treated as the complete semantic definition of the participant experience.

Task ordering remains the responsibility of the task registry.

Experience lifecycle state remains the responsibility of the experience layer.

7.3 Adaptive-catalog completion

Existing adaptive task selection, routing, arbitration, and orchestration semantics remain separate from participant experience completion.

This ADR does not redefine:

adaptive task selection;
SignalArbitrator behavior;
routing decisions;
evidence production;
task-attempt history;
adaptive difficulty;
governed continuity.
8. Experience-Scoped Summary

Existing task/session summary generation remains session-scoped.

In particular:

build_cognitive_session_summary(session)

continues to summarize one cognitive task session according to the existing summary contract.

The existing summary contract is not replaced by this ADR.

A separate experience-level summary may aggregate task/session summaries belonging to the current bounded experience.

The aggregation boundary is:

current experience_id
       |
       +---- task session 1
       |
       +---- task session 2
       |
       +---- task session N
       |
       v
experience summary

The aggregation boundary is not:

participant_id
       |
       +---- historical experience 1
       +---- historical experience 2
       +---- historical experience N
       |
       v
longitudinal participant profile

An experience summary may only be presented as a completed participant-facing summary when:

the experience is COMPLETED;
all required task sessions exist;
all required task sessions are valid;
all required task-level summaries required by the experience summary contract are valid.

If any required component is missing or invalid:

experience_summary = null

No partial result is presented as a completed experience summary.

This preserves the existing fail-closed summary validation approach.

9. Storage and Retrieval Constraints

The bounded experience will be persisted using the existing application storage architecture rather than introducing an unrelated storage system solely for experience lifecycle state.

The experience record shall contain, at minimum:

experience_id
participant_id
status
sequence_version
created_ts
completed_ts

completed_ts may remain null while the experience is active or abandoned without completion.

The experience record may contain the participant identifier necessary for authorized ownership and access.

However:

participant_id must not be used as the experience-summary aggregation key;
participant-facing experience retrieval must be scoped to an authorized current experience;
the existence of an experience record must not expose unrestricted historical task sessions;
separate experiences must remain independently bounded.

Any future requirement for cross-experience portable state is outside the scope of this ADR.

10. Privacy and Governance Invariants

The following invariants apply:

Task sessions remain independent, contextual interactions.
Every bounded experience receives a new opaque experience_id.
An experience_id scopes exactly one bounded participant run.
A session_id scopes exactly one task interaction.
participant_id establishes authorized participant context but does not define the experience aggregation boundary.
Participant-facing summaries aggregate only sessions belonging to the current bounded experience.
Separate experiences are not silently combined.
Raw behavioral history is not silently carried across experience boundaries.
Experience continuity does not constitute behavioral inference.
Experience lifecycle logic does not determine behavioral interpretation, routing, or adaptive difficulty.
Existing task/session summary contracts remain valid.
Experience summaries must fail closed when required task-level evidence is missing or invalid.
The bounded experience mechanism is not a substitute for governed adaptive history.
The bounded experience mechanism is not portable state.

These invariants preserve the constitutional rule established by ADR-010:

HumanOS carries governed evidence forward. It does not carry raw behavioral history forward silently.

11. Abandonment Semantics

In this phase, abandonment is an explicit application-level state transition.

An experience may be marked ABANDONED when the participant or authorized application flow explicitly terminates the bounded experience.

The following do not automatically constitute abandonment:

browser closure;
tab closure;
network interruption;
failed navigation;
temporary server interruption;
inactivity.

Automatic timeout and expiry semantics are deferred until separately specified and tested.

An abandoned experience cannot subsequently be treated as a completed experience without an explicitly defined lifecycle transition authorized by a future architectural decision.

12. Non-Goals

This ADR does not:

define portable cross-experience state;
define longitudinal participant profiling;
authorize unrestricted historical behavioral aggregation;
redefine participant identity;
redefine adaptive task_attempt history;
convert participant task sessions into adaptive history;
redefine routing algorithms;
redefine the SignalArbitrator;
redefine evidence production;
redefine evidence dependency semantics established by ADR-009;
replace the existing cognitive session summary contract;
redesign participant task UI;
redesign the task registry;
modify the adaptive demo protocol;
introduce automatic inactivity timeout or expiry;
define deployment-specific consent mechanisms beyond the existing consent boundary.

Any future portable state mechanism must be defined by a separate architectural decision consistent with ADR-010.

13. Architectural Consequences
Positive consequences
Task completion and experience completion become explicit and independently testable concepts.
Multiple task sessions can belong to one bounded participant experience without changing the meaning of an individual session.
Participant-facing summaries can aggregate a bounded experience without creating an unrestricted longitudinal participant profile.
Existing task-level summary contracts remain reusable.
Task sequence management remains separated from experience lifecycle management.
Future expansion of the task sequence does not require redefining participant identity or session semantics.
The architecture preserves a clear boundary between experience continuity and governed adaptive continuity.
Trade-offs
HumanOS introduces an additional lifecycle object and identifier.
Task submission must carry or resolve bounded experience context.
Experience persistence and retrieval require additional validation and lifecycle handling.
Experience-level summaries require an aggregation layer distinct from existing task/session summaries.
Additional contract and regression tests are required.

These costs are accepted because they provide explicit boundaries that the current task-based completion logic does not provide.

14. Implementation Sequence

Implementation shall proceed through independently verifiable checkpoints.

Checkpoint 1A — Architecture
Add and review ADR-011.
Do not modify participant runtime behavior.
Checkpoint 1B — Contract tests

Add tests covering:

experience identity creation;
unique experience identifiers;
lifecycle states;
task-session membership;
experience/task separation;
completion semantics;
incomplete experience handling;
experience-scoped summary isolation;
cross-experience isolation.

No participant runtime implementation should be considered complete until these contracts exist.

Checkpoint 2 — Experience persistence

Implement:

bounded experience creation after successful consent;
experience persistence;
authorized current-experience access;
lifecycle state storage.
Checkpoint 3 — Task session membership

Update task-session creation/persistence so each task session belongs to the current bounded experience.

Verify:

ownership;
membership;
missing experience handling;
cross-experience isolation.
Checkpoint 4 — Completion semantics

Separate:

task session completion;
experience completion;
adaptive-catalog completion.

Remove the current assumption that the absence of a next task is sufficient to represent all completion semantics.

Checkpoint 5 — Experience summary

Implement an experience-level summary layer that:

retrieves only sessions belonging to the current experience;
reuses existing task/session summary contracts;
validates required summaries;
fails closed when required data is missing or invalid.
Checkpoint 6 — Participant experience integration

Connect:

consent
  ↓
experience
  ↓
task sequence
  ↓
task sessions
  ↓
experience completion
  ↓
experience summary

Only after the backend contract is stable should the participant-facing UI be updated.

Checkpoint 7 — Regression and release checkpoint

Run:

existing test suite;
new experience contract tests;
participant flow integration tests;
summary validation tests;
cross-experience isolation tests;
task sequence regression tests.

Review the resulting diff and repository status before committing.

## 14A. Implementation and Verification Status

ADR-011 has been implemented and verified through the participant experience flow.

The implementation verifies:

- bounded experience creation and lifecycle state;
- experience-scoped task progression;
- rejection of tasks outside the current progression state;
- task-session membership within the active experience;
- separation of task completion from experience completion;
- experience-scoped analytics and summary generation;
- objective performance and decision-observation separation;
- fail-closed summary behavior;
- participant-facing completion and experience reflection;
- final-task experience completion;
- cross-experience and ownership boundaries.

Verification includes the full participant progression integration test and the existing application test suite.

The implementation is considered complete for the scope defined by this ADR. Automatic expiry, portable cross-experience state, longitudinal participant profiling, and adaptive continuity remain outside the scope of ADR-011.

15. Relationship to ADR-010

ADR-011 implements a bounded form of experience continuity while preserving the architectural constraints established by ADR-010.

Specifically, this ADR does not establish portable state between separate experiences and does not authorize unrestricted behavioral continuity.

Experience continuity remains distinct from adaptive continuity and behavioral inference.

Where future requirements require information to move from one completed experience into a later experience, a separate architectural decision is required.


---

