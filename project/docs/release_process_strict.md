# HumanOS Tech — Release & Deployment Workflow (STRICT VERSION)

Owner: Lead Architect (Jireh Kenneth-Usen)  
Audience: Engineering, DevOps, Security, Compliance  
Classification: INTERNAL — CONFIDENTIAL  

---

## 1. Goals

This document defines how we:

- version the HumanOS platform  
- move changes from local development → staging → production  
- enforce pre-release checks (tests, lint, docs)  
- tag releases and record them in the CHANGELOG  
- handle hotfixes and rollbacks  

No code is deployed to a client-facing environment without following this workflow.

---

## 2. Versioning Scheme

We use **semantic versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR** — breaking changes, schema changes, incompatible API behavior  
- **MINOR** — new features, non-breaking changes, new endpoints, new tasks  
- **PATCH** — bug fixes, internal docs, small UI tweaks, non-functional changes  

Example:  
- `0.4.0` — new compliance layer + dashboards  
- `0.4.1` — bug fix to analytics summary  
- `1.0.0` — first stable public release

Git tags follow the format: `v0.4.0`, `v0.4.1`, etc.

---

## 3. Environments

Current phases (single machine, but logically separated):

- **Local Development**
  - Flask dev server (`flask run`) and `pytest`
  - Uses local logs in `logs/` and local JSONL data
- **Staging / Demo**
  - Gunicorn via `./run_gunicorn.sh` on port 8000
  - Used for demos, manual QA, and test data
- **Future Production**
  - Hosted environment (cloud VM / container)
  - Same app image as staging, but with real client traffic
  - Stricter network, monitoring, and backup policies

All production-like deployments MUST be reproducible from Git.

---

## 4. Standard Release Workflow

### 4.1 Prepare the Release

1. Ensure working directory is clean:

   ```bash
   git status
Run automated tests:

pytest


Update docs if relevant:

project/docs/CHANGELOG_internal.md

project/docs/CHANGELOG_public.md

Any policy or runbook affected

Bump version number:

In project/docs/CHANGELOG_internal.md

In any version metadata endpoint (e.g. /status route)

Commit changes:

git add ...
git commit -m "Bump version to 0.x.y and update docs"

4.2 Tag the Release

After commit:

git tag -a v0.x.y -m "HumanOS Tech v0.x.y"
git push origin restructure/app-package
git push origin v0.x.y


Tags are immutable; do NOT re-use version numbers.

5. Staging / Demo Deployment

Pull the latest release:

git pull origin restructure/app-package


Activate virtualenv and install dependencies if needed:

source venv/bin/activate
pip install -r requirements.txt


Run Gunicorn:

./run_gunicorn.sh


Smoke tests (manual):

curl http://localhost:8000/status

Run:

/start_session

/submit_result

/metrics/global

/metrics/report/<demo_id>

Open /dashboard or /demo in browser and verify UI loads.

If all checks pass, mark the version as “Staging Verified” in the internal CHANGELOG.

6. Production Deployment (Future)

When a real production environment exists:

Create a release branch (optional but recommended):

git checkout -b release/v0.x.y


Deploy same tagged version (v0.x.y) to production server.

Run production smoke tests using demo users or safe test accounts.

Log deployment in:

CHANGELOG_internal.md

Deployment log (future project/docs/deploy_log.md)

Notify stakeholders (schools / clients) only after successful verification.

7. Hotfix Workflow

Use for urgent fixes in production.

Branch from the production tag:

git checkout -b hotfix/v0.x.y+1 v0.x.y


Apply minimal necessary change, add tests.

Run pytest and local smoke tests.

Bump patch version:

e.g. from 0.4.0 → 0.4.1

Update CHANGELOG (“Fixed” + “Security” sections).

Tag and push:

git commit -m "Hotfix: <short summary>"
git tag -a v0.4.1 -m "Hotfix v0.4.1"
git push origin hotfix/v0.4.1
git push origin v0.4.1


Deploy to staging, then production.

8. Rollback Procedure

If a release causes critical issues:

Identify last stable tag, e.g. v0.3.2.

On server:

git fetch --all
git checkout v0.3.2
./run_gunicorn.sh  # or restart service


Document rollback in:

CHANGELOG_internal.md (under “Changed / Reverted”)

Incident Runbook log

Open a separate bug ticket to investigate root cause.

9. Release Approval

Before tagging any release that will be shown to a client:

✅ Tests pass (pytest)

✅ Security checks reviewed (rate limits, admin token, honeypot)

✅ Docs updated (CHANGELOG + any affected policy)

✅ No unresolved critical TODOs in code

✅ For minors: consent & retention rules still valid

Approvers:

Lead Architect (mandatory)

future Security/Compliance role for major versions

End of Strict Release Workflow
