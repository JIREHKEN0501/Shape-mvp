audit_policy_strict.md (Internal Strict Version)

Filename: project/docs/audit_policy_strict.md
Audience: Engineering, Security, Compliance
Classification: INTERNAL — CONFIDENTIAL

# HumanOS Tech — Audit & Logging Policy (STRICT INTERNAL VERSION)

**Version:** 1.0  
**Owner:** Lead Architect (Jireh Kenneth-Usen)  
**Last Updated:** {{fill on commit}}  
**Classification:** INTERNAL — CONFIDENTIAL

---

## 1. Purpose

This policy defines how HumanOS Tech captures, stores, protects, and reviews audit logs.

Audit logging supports:

- security monitoring
- accountability for admin actions
- incident investigation
- regulatory compliance (NDPR, GDPR, COPPA, FERPA)
- protection of minors and vulnerable users

This policy is binding for all environments and systems where HumanOS is deployed.

---

## 2. Scope

This policy applies to:

- All environments: development, staging, production
- All services that handle:
  - participant sessions
  - cognitive/behavioral analytics
  - admin access
  - configuration changes
- All logs written to:
  - `logs/audit_log.jsonl`
  - `logs/data_log.jsonl`
  - `logs/consent_log.jsonl`
  - backup archives containing these files

---

## 3. What Must Be Logged

### 3.1 Core Events

The system MUST log:

- `session_start`
- `submit_result`
- `consent_given` / `consent_withdrawn`
- `admin_login` / `admin_logout` (future)
- `admin_access` (dashboard, exports, erasures)
- `decoy_hit` / honeypot triggers
- `erase_performed` / `erase_error`
- `export_generated`
- `security_incident` (e.g., suspected abuse)

### 3.2 Required Log Fields

Each audit entry should include at minimum:

```json
{
  "ts": <timestamp>,
  "event_type": "session_start|submit_result|admin_access|...",
  "actor": "participant:<id>|admin:<id>|system",
  "subject": "<route or resource>",
  "status": "ok|denied|error",
  "extra": {
    "...": "contextual data"
  }
}


Where possible, identifiers MUST be pseudonymized (e.g., participant_id) rather than real-world PII.

4. Log Storage & Protection

Logs must be stored under the logs/ directory by default.

Logs must be:

append-only (no in-place modification)

UTF-8 encoded

rotated according to LOG_MAX_BYTES and LOG_BACKUPS

Backups of logs must be encrypted (disk-level or application-level encryption).

4.1 Tamper Resistance

Where LOG_HMAC_KEY is configured:

each log entry should include a tamper-evident HMAC or checksum

verification tools may be added to validate integrity

Intentional modification or deletion of logs outside rotation is prohibited.

5. Retention & Deletion

Audit logs retention is governed by data_retention_policy_strict.md.

As a default:

audit logs: 24 months

security/system logs: 90 days

Deletion is performed via rotation or explicit retention job; manual deletion is not allowed except via authorized maintenance, which must also be logged.

6. Access Control

Only authorized roles may read audit logs:

Lead Architect

Security/Compliance roles

Designated engineers on-call

Access to logs must require:

server-level authentication

no direct public exposure

No one may:

share raw audit logs externally without redaction

store copies in personal devices or unsanctioned cloud drives

7. Use of Audit Logs

Audit logs may be used for:

investigating incidents

monitoring abuse or anomalous patterns

supporting compliance reports

verifying data subject rights handling (export/erase)

validating system behavior during upgrades

Audit logs MUST NOT be used for:

profiling individual students for punishment

discriminatory decisions

marketing or commercial targeting

8. Review & Monitoring

A lightweight review of key audit events should occur at least monthly.

After each security or privacy incident, a focused review of relevant logs must be performed.

Summary reports (e.g., number of admin accesses, erase requests) may be generated for internal oversight.

9. Incident Handling

If logs are:

missing,

corrupted,

tampered with, or

inaccessible during an incident,

this is itself a security incident and must be:

recorded in the incident runbook

escalated to the Lead Architect

investigated for root cause

10. Compliance Mapping

NDPR: integrity, accountability, audit trail

GDPR: Art. 5(2) accountability, Art. 30 records of processing

COPPA/FERPA: ability to demonstrate lawful and appropriate use of children’s/ students’ data

11. Enforcement

Violation of this policy, including unauthorized access or manipulation of logs, may result in:

removal of system access

internal investigation

contractual or legal consequences, especially where minors are involved

END OF AUDIT & LOGGING POLICY (STRICT VERSION)
