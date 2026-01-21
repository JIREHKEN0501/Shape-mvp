# Session Summary Versioning & Deprecation Policy

## Purpose
This document defines how session summaries evolve over time without breaking
existing data, users, or analyses.

Summaries are immutable once written. New logic adapts to old data.

---

## Versioning Rules

- Every summary MUST declare a `summary_version`
- Versions are semantic and monotonic (e.g. 1.0 → 1.1 → 2.0)
- Older versions remain readable indefinitely

---

## Backward Compatibility

- New summary versions MUST be able to read older versions
- No destructive migrations of stored session summaries
- Interpretation logic branches by `summary_version`

---

## Deprecation Policy

A summary version may be marked as:
- **active** – fully supported
- **deprecated** – readable but not emitted for new sessions
- **retired** – readable only for audit/export, not UI rendering

Deprecated versions:
- Must remain readable
- Must not change semantics retroactively

---

## Breaking Changes

Breaking changes require:
1. New `summary_version`
2. Updated schema documentation
3. Explicit adapter routing
4. CI coverage

---

## Guarantees

- Summaries describe sessions, not people
- Summaries never imply permanent traits
- No version may introduce diagnostic or inferential claims

---

_Last updated: Phase 12A-3_

