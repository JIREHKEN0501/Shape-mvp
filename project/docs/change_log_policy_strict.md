A — INTERNAL CHANGE-LOG & VERSIONING POLICY (STRICT)

Filename: project/docs/change_log_policy_strict.md
Confidentiality: INTERNAL — DO NOT SHARE

Paste this in:
# HumanOS Tech — Change-log & Versioning Policy (STRICT INTERNAL VERSION)

Last Updated: {{auto-fill on commit}}
Owner: Lead Architect (Jireh Kenneth-Usen)
Audience: Engineering, Compliance, Security
Classification: INTERNAL — CONFIDENTIAL

---

## 1. Purpose

This policy defines how HumanOS:

- tracks changes to code, tasks, scoring logic, and infrastructure
- communicates changes internally and (where appropriate) to clients
- versions releases in a predictable, auditable way
- ensures we can correlate bugs, incidents or regressions to a specific release

---

## 2. Scope

Applies to:

- Backend API (Flask app, routes, services)
- Task catalog and task metadata (difficulty, category, scoring)
- Scoring logic and metrics computation
- Admin dashboard & analytics views
- Infrastructure & deployment changes (e.g., gunicorn config)
- Compliance docs (DPIA, IR runbook, policies) when they affect behavior

Does NOT cover personal notes, scratch branches, or purely internal experiments that never reach staging or prod.

---

## 3. Versioning Scheme

We use **semantic versioning**:

`MAJOR.MINOR.PATCH` (e.g., `1.3.2`)

- **MAJOR** — breaking changes:
  - API contracts change
  - Scoring logic changes in a way that invalidates historical comparisons
  - Data schema changes that require migration
- **MINOR** — new features, backwards compatible:
  - new tasks or categories
  - new metrics or dashboards
  - new endpoints that don’t break existing ones
- **PATCH** — bug fixes and small improvements:
  - fix in scoring logic
  - UI bug fixes
  - performance tuning
  - documentation corrections tied to releases

The current version is stored in:

- `project/__init__.py` (e.g., `__version__ = "0.2.0"`)
- `project/docs/CHANGELOG.md`

---

## 4. CHANGELOG Rules

All user-facing or behavioral changes **MUST** be recorded in `project/docs/CHANGELOG.md`.

Each release entry MUST include:

- version number
- date (UTC)
- type of changes:
  - Added
  - Changed
  - Fixed
  - Security
- note if minors are impacted or if there are privacy implications
- migration/rollback notes (if applicable)

Example entry:

```markdown
## [0.3.0] — 2025-12-10

### Added
- New “conflict_resolution_001” task for moral reasoning.
- /metrics/report/<participant_id> endpoint for teacher reports.

### Changed
- Updated difficulty scaling for pattern_001 to align with new benchmarks.

### Fixed
- Corrected handling of missing consent_version in /start_session.

### Security
- Rotated admin token and hardened rate limits on /admin routes.
5. Workflow Integration
5.1 Before Merging to Main/Release
Every PR or merge that changes behavior MUST:

Update project/docs/CHANGELOG.md

Bump version in project/__init__.py if needed

Reference the change in the commit message, e.g.:

feat: add adaptive task suggestion engine

fix: correct metrics aggregation for logical_reasoning

chore: update docs and DPIA

5.2 After Deployment
Tag the commit in git, e.g.:

bash
Copy code
git tag -a v0.3.0 -m "HumanOS 0.3.0 — Adaptive tasks + metrics report"
git push origin v0.3.0
Confirm CHANGELOG entry is present and accurate.

Link incidents (if any) to the deployed version.

6. Special Handling: Children & Sensitive Environments
If a change affects:

consent flows

data retention

anything specific to minors (e.g., school dashboards, youth programs)

Then:

The CHANGELOG entry MUST explicitly mention it.

Compliance docs (DPIA, consent flow, privacy notice) MUST be reviewed and, if needed, updated.

A record MUST be added to the compliance log noting the version.

7. Emergency Fixes
If an emergency bug fix is deployed:

Use a PATCH bump (e.g., 0.3.1 → 0.3.2).

Add a clear ### Security or ### Hotfix section to the CHANGELOG.

Document the incident in the incident runbook + IR logs.

Rollback events MUST also be reflected in the CHANGELOG (e.g., “0.3.0 rolled back to 0.2.4 due to scoring regression”).

8. Enforcement
Failure to maintain accurate versioning and CHANGELOG entries may lead to:

inability to trace user impact

compliance risk

internal review and restricted deployment rights

This policy is binding for all engineers and contributors with merge or deployment permissions.

END OF STRICT INTERNAL VERSION
