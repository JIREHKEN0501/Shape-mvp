HumanOS — ML Task-Structure Layer

Phase 13 | Instrument Intelligence, Not Human Inference

This document defines the role of machine learning within the HumanOS ecosystem.

The ML Task-Structure Layer exists to improve the quality of observation and task design, not to model or judge individuals.

It operates under the design invariants defined in:

humanos_design_invariants.md

external_longitudinal_model.md

1. Purpose

The ML Task-Structure Layer enhances HumanOS by learning about:

task difficulty

task structure

skill dependencies

common breakdown points

It explicitly does not learn about individuals.

The goal is to make HumanOS a better instrument, not a smarter judge.

2. Scope of Learning
2.1 Unit of Analysis

The ML layer operates on:

tasks

task components

task sequences

aggregate session summaries

It never operates on:

individual identities

persistent participant histories

inferred traits or abilities

2.2 Inputs

Permitted inputs include:

anonymized, session-scoped summaries

task event traces

error locations within tasks

timing distributions

task metadata (difficulty, prerequisites)

All inputs must:

be unlinkable to identity

lack cross-session identifiers

pass schema validation

3. Core Capabilities
3.1 Empirical Task Difficulty Calibration

The ML layer may learn:

whether a task is harder or easier than declared

which steps contribute most to failure

how time pressure affects outcomes

Outputs:

updated difficulty estimates

flags for task redesign

These outputs modify tasks, not learners.

3.2 Skill & Prerequisite Graph Discovery

The ML layer may infer:

which sub-skills predict task failure

hidden dependencies between task components

incorrect or missing prerequisite assumptions

This produces a task-centric skill graph, e.g.:

Task A → Task B → Task C


This graph:

represents structural knowledge

does not place individuals on the graph automatically

informs instructional scaffolding

3.3 Breakdown Pattern Detection

The ML layer may identify:

common failure points

ambiguous instructions

steps that produce high variance

Outputs support:

task refinement

instructional emphasis

safer sequencing

3.4 Remedial Task Set Recommendation

Given a task with observed breakdowns, the system may recommend:

“Tasks that exercise the prerequisite components of this task.”

This is not learner personalization.

It is structural scaffolding based on task relationships.

4. Architectural Placement

The ML Task-Structure Layer does not sit inside the HumanOS Core.

Its placement:

HumanOS Core
     ↓
Validated Session Summaries
     ↓
ML Task-Structure Layer
     ↓
Updated Task Metadata / Skill Graphs
     ↓
HumanOS Task Registry (revised tasks)


The HumanOS Core remains unchanged.

5. Explicit Prohibitions

The ML Task-Structure Layer must never:

infer individual ability

label participants

predict individual futures

personalize difficulty automatically

adapt task flow per participant

create learner profiles

Any capability that violates these rules must be rejected.

6. Human Role

Humans remain responsible for:

interpreting task insights

deciding instructional changes

applying scaffolding

approving curriculum adjustments

ML outputs are advisory, not authoritative.

7. Long-Term Value

As AI systems become more powerful, the value of HumanOS lies in:

disciplined placement of intelligence

refusal to automate judgment

clarity about responsibility

The ML Task-Structure Layer strengthens HumanOS without compromising trust.
