B — Strict Internal BCDR Plan

Filename: project/docs/bcdr_strict.md
Audience: Engineering, Security, Compliance
Classification: INTERNAL — DO NOT SHARE EXTERNALLY
Tone: specific, technical, binding**

HumanOS Tech — Business Continuity & Disaster Recovery Plan (STRICT VERSION)

Version: v1.0
Owner: Lead Architect (Jireh Kenneth-Usen)

1. Core Recovery Metrics

RTO: 2 hours max (internal target)

RPO: 12 hours max

MAO: 6 hours

These are stricter than client-facing numbers.

2. Critical Systems Priority Map
System	Priority	Notes
Authentication	1	Required for admin access
Consent system	1	Legal requirement
Task engine (submit/start)	1	Core service
Database	1	Must be restored first
Audit logs	2	Needed for post-incident
Analytics	3	Can stay offline up to 24 hrs
Dashboard	3	Non-critical during disaster
3. Required Redundancies (Internal)
3.1 Backups

Daily backups

30-day encrypted retention

Local + remote copy (future cloud)

Backup integrity script must run daily at 03:00

3.2 Failover

Fast rebuild script (deploy_from_scratch.sh)

Bootstrap script for keys, user roles, and secrets

Local environment snapshots stored weekly

3.3 Token & Key Management

Admin token rotated weekly

Database encryption key rotated yearly

Backup decryption keys stored offline

4. Disaster Recovery Procedures (Strict)
4.1 Database Loss

Stop all write operations

Validate most recent backup

Restore to isolated node

Run integrity_check.py

Switch traffic

Log event in audit trail

Trigger Incident Runbook (if breach)

4.2 Compromise of Production

Revoke admin tokens immediately

Rotate keys

Stand up clean environment

Restore backup

Audit logs for unauthorized activity

Write internal postmortem within 48 hours

4.3 Major Cloud Outage

Move to secondary environment (manual for MVP)

Rebuild application

Restore DB backup

Notify clients every 60 minutes

Maintain operations via lightweight mode (local tasks only)

5. Continuity of Operations

Engineering on-call rotation (future)

Daily health checks

Every commit must pass security tests

All emergency access must be logged & approved

6. Testing Requirements

Quarterly tabletop exercise

Annual full restore simulation

Post-incident evaluation mandatory

7. Violations & Enforcement

Any engineer skipping BCDR steps is subject to:

suspension of production access

retraining

internal disciplinary action

possible termination for severe negligence

END OF STRICT VERSION
