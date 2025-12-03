✅ Security Hardening Checklist

HumanOS Tech — MVP Security Controls
Version: 1.0
Updated: <set today’s date>

1. Overview

This document defines the minimum security controls required for the HumanOS cognitive & behavioral analytics system before pilot deployment in schools, training organizations, or companies.

It covers:

Application-level security

API rate limiting

Authentication & authorization

Logging & monitoring

Infrastructure

Data protection

School/child-specific risk safeguards

Incident readiness

Every item must be validated and checked before onboarding a customer.

2. Application Security
✔ 2.1 Input Validation

Validate every POST body (you already have validators for sessions).

Reject:

malformed JSON

non-dict payloads

missing required fields

events with invalid structure

Limit maximum JSON size: 1MB (Flask config).

✔ 2.2 XSS / Template Safety

Only use server-side rendered templates (demo.html, dashboard.html).

Escape all user-controlled strings in templates (Jinja does this by default).

Never allow HTML in answers/options.

✔ 2.3 CSRF (for browser flows)

Add CSRF token to forms if future admin UI uses POST/PUT/DELETE.

Demo mode is safe because it only reads public APIs.

✔ 2.4 Directory Traversal Protection

Never accept user-provided filenames.

Never read from user paths for export (you already loop through logs folder safely).

✔ 2.5 Secure Error Handling

API errors must never leak stack traces.

Return only: { "ok": false, "error": "internal_error" }.

3. Authentication & Authorization
✔ 3.1 Admin Token

Enforce ADMIN_TOKEN for all admin-like endpoints.

Rotate admin token every 30–90 days.

Store it in environment variables only.

✔ 3.2 Access Segmentation

Public endpoints (tasks, start_session, submit_result)

Semi-protected endpoints (export anonymized data; safe for participants)

Admin-only endpoints (export everything, delete logs, view metrics across all participants)

✔ 3.3 No Credentials in Code

Do not hardcode secrets.

Use .env or server environment variables only.

4. Rate Limiting & Abuse Prevention

You already have Flask-Limiter configured—now ensure:

✔ 4.1 Route-Based Limits

/start_session → 10/min per IP

/submit_result → 20/min per IP

/tasks/* → 30/min

/metrics/* → 5/sec

/export → 5/min

✔ 4.2 Global Limits

Add in extensions/limiter.py:

limiter.limit("200 per day, 50 per hour")


(You already have this.)

✔ 4.3 Honeypot Traps

Bot tripwire already exists in decoy_submit.
Must run an audit record when triggered.

5. Logging, Monitoring & Audit
✔ 5.1 Log Separation

Maintain separate logs:

audit_log.jsonl → security events

data_log.jsonl → user task data

incident_log.jsonl (optional)

✔ 5.2 Log Integrity

Append-only JSON lines

No retroactive rewrite

Checksums in future versions (v2)

✔ 5.3 Audit Mandatory Events

The following must always be logged:

consent accepted/declined

session_start

submit_result

admin actions

data export

errors that affect user data

✔ 5.4 Monitoring

Add cron job or lightweight script:

Detect >20 failed submit attempts

Detect repeated 400 errors

Detect spike in new participant IDs

Detect repeated honeypot hits

6. Data Protection & Storage
✔ 6.1 Encryption

At-rest: OS-level or full-disk encryption

In-transit: HTTPS only (enforced by reverse proxy)

✔ 6.2 Data Minimization

Collect only required metadata

No unnecessary PII

Participant IDs pseudonymous

✔ 6.3 Retention Policy

(From your retention doc)

Raw identifiers: 30 days

Behavioral metrics: 2 years

Logs: 6–12 months

School deployments may require custom retention windows

✔ 6.4 Deletion Mechanisms

Ensure:

/erase/<id> works

admin delete endpoint works

Logs can remove or anonymize participant IDs

7. Infrastructure & Deployment
✔ 7.1 Reverse Proxy (Nginx recommended)

Enforce HTTPS

Block HTTP entirely

Add security headers:

Strict-Transport-Security

X-Content-Type-Options: nosniff

X-Frame-Options: DENY

Content-Security-Policy (restrict inline scripts)

✔ 7.2 Gunicorn Configuration

Minimum:

gunicorn app:app -w 4 --timeout 30 --bind 0.0.0.0:5000

✔ 7.3 Firewall Rules

Allow only:

HTTPS

SSH (for maintenance)

Everything else blocked.

✔ 7.4 Backups

Daily encrypted backup of logs

Weekly off-site backup

Monthly restore test (mandatory)

8. School / Child-Specific Protections
✔ 8.1 Role-Based Access

Teacher/admin can only see their students

No cross-school or cross-organization access

Each school = isolated namespace (future v2 feature)

✔ 8.2 Parental Consent Verification

Parent must sign

Or school must provide Pre-Consent CSV list

Student blocked until consent verified

✔ 8.3 No Webcam / No Emotion Analysis (yet)

This MUST be disabled until DPIA + parental consent v2.

✔ 8.4 Sensitive Content Review

All tasks must be reviewed before deployment:

No political content

No harmful moral dilemmas

No triggering psychological questions

Age-appropriate difficulty settings

9. Secure Development Practices
✔ 9.1 Repository Safety

No credentials committed

/logs excluded from version control

Use .gitignore properly

✔ 9.2 Code Reviews

All changes involving:

helpers.py

validators.py

metrics.py

sessions.py

must be reviewed by at least one other contributor once team expands.

✔ 9.3 Dependency Updates

Monthly:

pip list --outdated
pip install --upgrade <package>

✔ 9.4 Static Analysis (Optional)

Use:

flake8
bandit -r project/

10. Release Checklist Before Any Deployment

This MUST be completed before onboarding ANY school or company:

🔒 Technical

HTTPS enabled

Admin token set

All logs working

Export & erase endpoints tested

No PII stored

Firewall configured

Backup policy active

📑 Compliance

DPIA_strict.md complete

DPIA_summary for external use

Privacy Notice visible in consent modal

Consent Flow implemented

Incident Runbook prepared

🧪 Testing

Load test /submit_result (100 req/s burst)

Validate rate limits

Validate adaptive engine for harmful loops

Validate tasks for age-appropriateness

END OF DOCUMENT
