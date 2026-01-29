# Education Demo Script — HumanOS

This demo illustrates how HumanOS can be used in an educational setting
to support instructional insight without profiling, diagnosis, ranking,
or surveillance of learners.

The walkthrough is intentionally simple and constrained.

---

## 1. Context

An educator is reviewing a learning activity designed to test
pattern completion skills.

The educator’s goal is not to evaluate a learner as a person,
but to understand whether the task itself is:
- appropriately difficult
- clearly structured
- reasonably paced

No learner identity is entered into the system.

---

## 2. Task Selection

The educator selects a predefined task:

- **Task ID:** `pattern_completion_v1`
- **Domain:** Education
- **Scope:** Single session only

Tasks are selected from a fixed task catalog.
Unregistered or custom task IDs are rejected by the system.

---

## 3. Session Execution

A learner completes the task in one session.

During the session, the system records only:
- task interactions
- response timing
- task-specific outcomes

The system does not store:
- names
- participant IDs
- prior session references
- demographic or personal information

Each session is handled independently.

---

## 4. System Output

After completion, the system produces a **session summary**.

The summary contains:
- observable performance metrics (e.g. accuracy, timing)
- task-level interaction statistics

The summary does **not** contain:
- traits or character descriptions
- predictions about future performance
- comparisons to other learners
- recommendations or judgments

The system output is descriptive, not evaluative.

---

## 5. Human Interpretation

The educator reviews the session summary.

Using their professional judgment and contextual knowledge,
the educator may consider questions such as:
- Was the task too time-pressured?
- Were instructions unclear?
- Did many learners struggle at the same step?

The system does not answer these questions.
It provides only the task-level evidence.

All interpretation remains human-led.

---

## 6. What the System Explicitly Refuses to Do

The system cannot:
- link this session to previous sessions internally
- label the learner with traits or abilities
- rank learners against each other
- predict future learning outcomes
- automate instructional decisions

These are structural constraints, not configuration options.

---

## 7. Why This Is Safe for Education

Safety is achieved through design:

- identity-agnostic handling
- session-scoped summaries
- strict task registry enforcement
- schema-validated outputs
- language and inference boundaries

Even if misused intentionally,
the system does not provide mechanisms
for profiling or surveillance.

---

## 8. Demo Outcome

At the end of the demo:
- the educator understands the task better
- the learner has not been labeled or judged
- no persistent learner record exists in the system

The demo shows that useful educational insight
can exist without turning learners into data profiles.
