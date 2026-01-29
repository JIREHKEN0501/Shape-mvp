HumanOS — ML Observation Contract

Phase 13 | Pre-ML Safety & Scope Lock

This document defines the only data that machine learning components within the HumanOS ecosystem may observe, process, and emit.

Its purpose is to:

prevent scope creep

preserve HumanOS design invariants

ensure ML improves the instrument, not the subject

provide a clear enforcement reference for builders and reviewers

This contract applies to all ML systems consuming HumanOS outputs.

1. Contract Scope

This contract governs:

ML models used for task analysis, calibration, and structure

batch or offline ML processes

any analytics labeled “ML” within the HumanOS ecosystem

This contract does not authorize:

changes to the HumanOS Core

inline or real-time inference during task execution

any ML that operates on individuals

2. Permitted ML Inputs

ML systems may observe only the following categories of data.

2.1 Session Summaries (Validated Only)

Allowed fields (examples):

summary_version

summary_type

task-level metrics (e.g. accuracy, timing, variance)

step-level error counts (if present)

aggregate flags produced by the summary adapter

Constraints:

summaries must be session-scoped

summaries must pass schema validation

summaries must contain no identity fields

2.2 Task Metadata

Allowed fields:

task_id

declared difficulty

domain

task structure (steps, constraints)

prerequisite tags

version metadata

Task metadata is considered non-sensitive and safe for ML use.

2.3 Aggregation Rules

ML may only operate on:

aggregated summaries grouped by task_id

population-level statistics

cohort-level distributions (where cohorts are non-identifying)

Disallowed:

per-participant aggregation

cross-session linkage

reconstruction of individual trajectories

3. Explicitly Forbidden Inputs

ML systems must never observe, infer, or reconstruct:

participant identifiers

session identifiers used for linkage

identity hashes or proxies

free-text responses tied to individuals

labels such as “ability,” “skill,” “readiness,” or “aptitude”

externally inferred traits injected back into the system

Any ML system requiring these inputs is out of scope.

4. Permitted ML Outputs

ML systems may emit task-centric outputs only.

Allowed outputs include:

empirical difficulty scores

confidence intervals

task calibration flags

step-level breakdown reports

task-to-task dependency graphs

ambiguity or noise indicators

All outputs must be:

non-personal

descriptive

advisory

5. Forbidden ML Outputs

ML systems must not emit:

predictions about individuals

rankings or scores of participants

personalized recommendations

automated progression decisions

language implying traits or future performance

Any such output constitutes a contract violation.

6. Output Destinations

ML outputs may be sent only to:

task registry updates

human review interfaces

offline reports

external systems clearly labeled as non-HumanOS inference

ML outputs must not:

re-enter the HumanOS Core as decision logic

influence task execution in real time

bypass human review

7. Enforcement & Review

Compliance with this contract is enforced through:

schema validation

code review

test coverage

architectural separation

Any proposed ML capability must be reviewed against this contract before implementation.

Violations are grounds for rejection, not refactoring.

8. Stability Guarantee

This contract is considered stable for Phase 13.

Changes require:

explicit review

justification

confirmation that HumanOS design invariants remain intact

This contract exists to protect long-term trust, not to slow development.

End of Contract
