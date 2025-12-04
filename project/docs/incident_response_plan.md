HumanOS Tech — Incident Response Plan (IRP)
Version 1.0 • Last Updated: 2025-12-03

(Internal document — may be shared with clients under NDA)

1. Purpose

This Incident Response Plan defines the required procedures for detecting, responding to, mitigating, and recovering from incidents involving:

Personal data

Behavioral/cognitive session data

Security events

System compromise

Unauthorized access

Misuse by administrators, schools, or organizations

This plan ensures compliance with:

NDPR (Nigeria)

GDPR principles (where applicable)

Basic ISO 27001 incident management standards

Best practices for EdTech, HRTech, and behavioral analytics systems

2. Scope

This IRP covers the entire HumanOS MVP environment, including:

Flask application & API endpoints

Behavioral/cognitive session data (logs/data_log.jsonl, audit logs, consent logs)

Admin dashboard

Rate limiting and bot-tripwire protections

Data exports (JSON)

Any deployment used in pilot schools or companies

Any cloud or on-prem hosting instance

3. Incident Categories

HumanOS defines incidents under four severity tiers:

Severity 1 — Critical

Unauthorized access to participant data

Compromise of admin token or security keys

Server breach or active intrusion

Exposure of children’s personal data

Large-scale log/data exfiltration

Ransomware or data corruption

Severity 2 — High

Unusual API activity bypassing rate limits

Automated scraping / bot activity at scale

Suspicious behavioral patterns from internal admins

Partial unavailability of the system

Severity 3 — Medium

Minor data integrity issues

Failure in pseudonymization pipeline

Isolated suspicious access attempts

Temporary performance degradation

Severity 4 — Low

Logging anomalies

Admin UI malfunction

Incorrect metrics summary

Task catalog inconsistencies

4. Incident Response Team (IRT) Roles
1. Incident Commander (IC)

Oversees the response. Makes all final decisions.
Default: Lead Architect (Jireh Kenneth-Usen).

2. Security Lead

Analyzes logs, verifies scope, coordinates containment.

3. Engineering Lead

Fixes code or server configuration.

4. Data Protection Officer (DPO)

(Not yet assigned — role must exist before public deployment.)
Reviews legal implications, especially for minors.

5. Communications Lead

Communicates approved messages to schools, parents, or companies.

5. IRP Workflow Overview

Every incident follows six mandatory phases:

Detect

Classify

Contain

Eradicate

Recover

Learn

6. Phase 1 — Detection

Triggered by any of the following:

Automated triggers

Spike in /submit_result or /start_session traffic

Rate-limit violations

Decoy/honeypot trigger hits

Excessive admin dashboard access attempts

Unexpected deletion/export attempts

Tampered log files

Missing logs or corrupted log entries

Manual triggers

Complaint from school, parent, or company

Suspicious admin behavior

Backend crash or unexpected restart

CI/CD anomaly

Evidence to collect immediately

Last 500 lines of audit_log

Last 500 lines of data_log

Admin access history

Server access logs

Screenshots where applicable

7. Phase 2 — Classification

The IRT assigns a severity level (1–4):

If children’s data is involved → automatic Severity 1.

If admin token leak is suspected → Severity 1.

If logs show targeted automation → Severity 2.

Record classification in audit_log:

{
  "ts": <timestamp>,
  "event_type": "incident_classification",
  "severity": 1 | 2 | 3 | 4,
  "details": "<summary>"
}

8. Phase 3 — Containment

Depending on severity:

Critical (Severity 1)

Immediately rotate admin token and system keys

Temporarily disable /export, /erase, and admin endpoints

Block offending IPs

Pull system offline if necessary

Lock access to logs (read-only mount)

Create a full snapshot of the system

High (Severity 2)

Increase rate limits dynamically

Suspend the compromised session or user

Enable extra logging

Medium (Severity 3)

Patch affected modules

Restart limited services

Low (Severity 4)

Mark anomaly and continue monitoring

9. Phase 4 — Eradication

Remove the root cause:

Fix vulnerabilities (XSS, CSRF, rate-limit bypass, logic flaws)

Patch Python/Flask dependencies

Repair corrupted log entries

Remove malicious files or scripts

Improve tripwire rules

Redeploy container/app with clean state

10. Phase 5 — Recovery

Once the system is safe:

Restore functionality step-by-step

Re-enable admin routes

Lower rate limits to normal mode

Verify logs and data integrity

Run automated tests (pytest)

Validate all endpoints manually:

/tasks

/submit_result

/metrics/*

/admin/*

Post-incident communication

Depending on impact:

Notify affected schools/parents

Provide data breach summary (if required by NDPR/GDPR)

Provide recommendations

Schedule follow-up meeting

11. Phase 6 — Lessons Learned

Within 72 hours of closing the incident:

Conduct an internal postmortem

Document root cause and timeline

Update:

DPIA

Model Card

Incident Runbook

System architecture design

Monitoring rules

Security checklist

Store postmortem as:

project/docs/postmortems/<incident_id>.md

12. Storage, Retention & Evidence Handling

Incident evidence must be stored for 2 years

Access restricted to IC + Security Lead

Must include:

Logs

Server traces

Screenshots

Emails/notices

Patched code diffs

Evidence must never include direct identifiers of minors

13. Parent & School Safeguard Requirements

HumanOS must support incidents involving minors:

Schools act as data controllers

Parents can request:

Export

Erasure

Explanation of processing

Schools must be notified within 48 hours of any Severity 1 incident

Incidents involving classroom tasks require:

Confirmation of student roster

Verification that affected IDs match pseudonymized IDs

14. Final Verification Checklist

Before closing the incident, verify:

 All affected components restored

 All vulnerabilities patched

 DPIA updated if risk classification changed

 Stakeholder notifications completed

 Internal postmortem stored

 Monitoring rules updated

 Admin token rotated (if applicable)
