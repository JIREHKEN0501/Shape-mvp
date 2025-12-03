HumanOS Tech — Incident Response RUNBOOK
Operational Cheat Sheet
Version 1.0 • Internal Only
0. Purpose

This runbook is a quick-action guide for engineers and admins responding to urgent incidents.
It summarizes the exact steps and commands needed for:

System outages

Security breaches

Suspicious activity

Data integrity issues

Admin token compromise

Log corruption

Child-related data escalation

Use the full IRP for policy-level details.
Use this runbook for fast, practical action.

1. When an Incident is Reported

Do these immediately:

1. Pause all deployments & admin operations
export INCIDENT_MODE=1

2. Notify internal responders

Lead Architect (Incident Commander)

Security Lead

Engineering Lead

3. Collect snapshot evidence
tail -n 200 logs/audit_log.jsonl > incident/audit_tail.log
tail -n 200 logs/data_log.jsonl > incident/data_tail.log
cp -r logs incident/logs_backup_$(date +%s)

4. Check server/system health
ps aux | grep python
df -h
free -m
sudo systemctl status <your-service-name>

2. Initial Checks
Check suspicious traffic
grep "submit_result" logs/audit_log.jsonl | tail
grep "session_start" logs/audit_log.jsonl | tail

Check for honeypot hits
grep "decoy_hit" logs/audit_log.jsonl | tail

Check admin access anomalies
grep "admin" logs/audit_log.jsonl | tail

3. Severity Quick Classification

Use this cheat list:

Severity 1 — Critical

Admin token leak

Unauthorized access confirmed

Children’s data exposed

Large-scale automation attack

Logs tampered or wiped

Server breach

Severity 2 — High

Repeated suspicious requests

Bot patterns

Attempted endpoint misuse

Severity 3 — Medium

Isolated anomalies

Temporary performance issues

Metric calculation errors

Severity 4 — Low

Incorrect UI behavior

Minor warnings

Log classification:

echo '{"ts":'$(date +%s)',"event_type":"incident_classification","severity":1}' \
>> logs/audit_log.jsonl

4. Containment Actions
A. Rotate admin token immediately

Open:

project/app/helpers.py


Regenerate:

export ADMIN_TOKEN=$(openssl rand -hex 32)


Restart the app.

B. Block malicious IPs
sudo ufw deny from <ip-address>

C. Temporarily disable sensitive routes

Comment out:

/admin/*

/erase/<id>

/export/*

Restart the app.

D. Increase rate limits

In limiter.py:

default_limits=["20 per minute"]


Restart app.

5. Eradication
Fix the root cause

Apply code patch

Patch dependencies

Rebuild pseudonymization pipeline if needed

Replace corrupted logs with backup copies

Verify no traces remain
grep -R "error" logs/*
grep -R "unauthorized" logs/*

6. Recovery
Re-enable disabled routes

Uncomment admin and export/erase routes.

Reset rate limits to production

Restore 120 per minute (or config value).

Restart and validate
systemctl restart <service>
pytest
curl http://localhost:5000/status

Test critical endpoints
/start_session
/tasks
/tasks/<task>
/submit_result
/metrics/*
/admin/dashboard

7. Communication Requirements

If minors are involved or it is Severity 1:

Notify the school within 48 hours

Provide summary of incident

Provide list of affected participant IDs

Provide measures taken and next steps

Offer a follow-up call

Never disclose internal system details.

8. Postmortem
Within 72 hours:

Create:

project/docs/postmortems/incident_<timestamp>.md


Include:

Timeline

Root cause

Fix

Lessons learned

Recommendations

Required DPIA update

✔️ RUNBOOK COMPLETE
