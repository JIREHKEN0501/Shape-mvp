A — MAINTENANCE & UPDATE SOP (STRICT INTERNAL VERSION)

Filename: project/docs/maintenance_sop_strict.md
Confidentiality: INTERNAL — DO NOT SHARE
Owner: Lead Architect (Jireh Kenneth-Usen)

HumanOS Tech — Maintenance & Update Standard Operating Procedure (STRICT VERSION)

Last Updated: {{auto-fill on commit}}
Audience: Engineering, Security, Compliance
Classification: INTERNAL — CONFIDENTIAL

1. Purpose

This SOP defines the required procedures for:

updating task logic

modifying difficulty progression

adding new task types

updating backend routes

changing model or scoring logic

performing maintenance on the API, dashboard, logs, or database

ensuring safety for minors and adult users

preventing regressions or downtime

2. Scope

Applies to:

Flask API backend

task engine

scoring logic

admin dashboard

data stores (session logs, analytics, backups)

documentation updates

release versioning

deployment scripts (gunicorn/systemd)

Does not apply to public-facing materials — this is internal engineering only.

3. Maintenance Categories
3.1 Routine Maintenance

Performed weekly or bi-weekly:

log rotation

clearing expired PII

verifying deletion jobs

backup status checks

rate-limit health checks

reviewing error logs for spikes

dependency inventory

token rotation planning

3.2 Scheduled Updates

Includes:

new tasks (pattern, reasoning, moral conflict, conflict scenarios, etc.)

new scoring logic

new cognitive metrics

UI/dashboard updates

library upgrades

config changes

schema adjustments

All scheduled updates require:

staging validation

version bump

updated CHANGELOG

updated documentation

3.3 Emergency Maintenance

Triggered by:

API downtime

worker crashes

incorrect scoring / logic failure

security breach

data misrouting

minors’ data exposure

production instability

Requires:

immediate rollback

IC (Incident Commander) activation

audit log entry

post-mortem report

4. Update Workflow (Strict Process)
4.1 Step 1 — Create a Branch
git checkout -b maintenance/<description>

4.2 Step 2 — Make Update

Changes must be isolated and documented.

4.3 Step 3 — Run Tests

unit tests

task execution tests

scoring verification

manual endpoint tests

4.4 Step 4 — Push to Staging

Must validate:

session_start

submit_result

metrics relationships

deletion flows

admin dashboard

4.5 Step 5 — Review and Approval

Requires both:

Engineering approval

Compliance validation (if minors involved)

4.6 Step 6 — Version Bump

A version increment is mandatory for:

scoring updates

task difficulty changes

new task categories

any change affecting data output

4.7 Step 7 — Production Deployment

Only after:

confirmation that staging is stable

backups taken

rollback defined

5. Rollback Procedure (Strict)

Rollback must occur if:

scoring is incorrect

task engine crashes

users report unexpected behavior

logs show exceptions repeating

system health drops below threshold

Rollback Steps:

Stop gunicorn workers

Restore previous version backup

Redeploy previous tag

Verify health

Document rollback in CHANGELOG

File an incident log

6. Access Control

Only approved roles may perform maintenance:

Action	Allowed Roles
Task/scoring updates	Lead Architect, Senior Engineer
API code changes	Engineering
Deployment	Engineering + Compliance
Schema changes	Lead Architect only
Rollback	IC + Lead Architect
7. Weekly Review Requirements

Engineering must run a weekly checklist:

error logs reviewed

new warnings analyzed

deletion jobs verified

rate limits stable

no orphan sessions

disk usage healthy

backup integrity validated

8. Enforcement

Failure to follow this SOP can result in:

removal of deployment or edit permissions

internal review

compliance escalation

audit documentation

END OF STRICT VERSION
