# Session Summary Schema

**Version:** 1.0  
**Scope:** Per-session, task-scoped summaries  
**Purpose:** Describe observed patterns without inference or diagnosis

---

## Overview

A session summary represents **how a participant interacted with a single task**.  
It does **not** describe traits, abilities, or long-term characteristics.

Summaries are:
- Task-scoped
- Immutable after creation
- Non-diagnostic
- Non-identifying

---

## Top-Level Structure

```json
{
  "summary_version": "1.0",
  "summary_type": "cognitive | strategy | behavioral",
  "data": { }
}
Cognitive Summary
summary_type: "cognitive"

json
Copy code
{
  "total_questions": number,
  "accuracy_ratio": number | null,
  "avg_time_per_question": number | null,
  "median_time_per_question": number | null,
  "time_variance": number | null,
  "speed_accuracy_profile": "fast_accurate | slow_accurate | fast_inaccurate | slow_inaccurate | insufficient_data"
}
Field Notes
accuracy_ratio is bounded between 0.0 and 1.0

Timing values are expressed in seconds

Profiles are descriptive, not evaluative

Strategy Summary
summary_type: "strategy"

Strategy summaries are task-specific and may differ in structure.

json
Copy code
{
  "note": "strategy summary not yet implemented"
}
Guarantees
No participant identifiers are included

No raw answers are included

No cross-session aggregation

No predictive claims

Design Principle
Patterns describe sessions, not people
summaries support reflection, not judgement.
