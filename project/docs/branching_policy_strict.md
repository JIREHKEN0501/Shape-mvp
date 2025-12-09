# HumanOS Tech — Branching & Deployment Policy (STRICT INTERNAL VERSION)

Last Updated: {{auto-fill on commit}}
Owner: Lead Architect (Jireh Kenneth-Usen)
Audience: Engineering, DevOps, Security
Classification: INTERNAL — CONFIDENTIAL

---

## 1. Purpose

This policy defines how HumanOS Tech:

- uses git branches for safe development
- merges and tags releases
- promotes code from local → staging → production
- keeps auditability for incidents and regressions

---

## 2. Key Branches

- **main** (or **restructure/app-package** while in MVP phase)
  - Always deployable.
  - Only contains code that has passed tests and basic manual verification.
  - Protected: no direct force-push, no history rewrite.

- **feature/** branches
  - New functionality, refactors, or modules.
  - Examples:
    - `feature/adaptive-task-flow`
    - `feature/admin-dashboard`
    - `feature/ml-metrics-v1`

- **fix/** branches
  - Bug fixes, patches, hotfixes.
  - Examples:
    - `fix/rate-limit-metrics`
    - `fix/token-rotation-bug`

- **chore/** branches
  - Non-functional changes (docs, formatting, tooling).
  - Examples:
    - `chore/update-dpia`
    - `chore/cleanup-legacy-routes`

---

## 3. Standard Workflow

1. **Create a branch**

   ```bash
   git checkout -b feature/<short-description>
Commit frequently

Use clear, small commits.

Example messages:

feat: add /metrics/report endpoint

fix: correct pattern_001 scoring

docs: add data retention policy

Run tests before merge

Run at least:

bash
Copy code
pytest
For changes touching routes, also run quick curl or browser sanity checks.

Merge back to main / release branch

Prefer merge via PR (when using GitHub UI).

If working solo:

ensure tests pass

ensure CHANGELOG and version are updated when behavior changes

git checkout main (or restructure/app-package)

git merge <branch-name>

git push

Tag releases

After a meaningful release:

bash
Copy code
git tag -a vX.Y.Z -m "HumanOS X.Y.Z — short description"
git push origin vX.Y.Z
4. Deployment Rules
Local dev

Use flask run or python app.py for quick checks.

Use ./run_gunicorn.sh to mirror production behavior locally.

Staging / Demo

Must be based on the latest main (or release) branch.

Only deploy after:

tests pass

DPIA / privacy impact is considered for major changes

CHANGELOG is updated

Production (future)

Only tagged commits are eligible (e.g., v0.3.0).

Deployment logs must record:

version

time

operator

environment

5. Breaking Changes & Migrations
Any change that:

breaks an API

changes scoring logic in a non-backwards-compatible way

alters log formats or data schema

MUST:

Bump MAJOR or MINOR version (see versioning policy).

Add a clear section in the CHANGELOG.

Include migration notes and (if possible) rollback steps.

Be tested on staging before production.

6. Hotfix Procedure
For urgent fixes in production:

Branch from the deployed tag or release branch:

bash
Copy code
git checkout -b fix/hotfix-<issue> vX.Y.Z
Implement and test minimal changes.

Merge back into main/release.

Tag as PATCH version (e.g., vX.Y.(Z+1)).

Update CHANGELOG with a ### Security or ### Hotfix section.

7. Enforcement
No code should be deployed directly from untracked local changes.

Force-push to shared branches (main/release) is forbidden except under documented emergency and with approval.

Violations of this policy may result in restricted deployment rights.

END OF STRICT VERSION
