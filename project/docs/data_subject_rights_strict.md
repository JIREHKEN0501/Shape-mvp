HumanOS Tech — Data Subject Rights Request SOP (STRICT INTERNAL VERSION)

Filename: project/docs/data_subject_rights_strict.md
Classification: INTERNAL — CONFIDENTIAL
Audience: Engineering, Compliance, Security, Lead Architect (Jireh Kenneth-Usen)
Legal Basis: NDPR, GDPR, COPPA (for minors), FERPA (schools)

1. Purpose

This SOP defines the processes HumanOS Tech must follow when handling data subject rights requests, including:

Right of Access (data export)

Right to Deletion / Erasure

Right to Withdraw Consent

Right to Correction (future feature)

Parental Rights for Minors

School Administrator Rights (as data controllers)

The goal is ensuring timely, secure, transparent processing per legal and ethical requirements.

2. Scope

This SOP applies to:

All environments (dev, staging, production)

All participant types (adults, minors)

All involved teams (engineering, operations, compliance)

All request channels:

school administrator portal (future)

parent-authenticated email request (verified)

participant request (adults only)

direct API request via endpoints

3. Allowed Requestors
Request Type	Who Can Request	Verification Required
Adult Participant	Participant	ID of participant_id provided + signed confirmation
Minor Participant	Parent/Guardian	Proof of parental authority (school registry / written consent)
School Deployments	School Admin	Must match registered admin token for the school
Legal Requests	Legal authority	Must pass legal review

No request from an unauthorized third party should be processed.

4. Request Intake Procedure
4.1 Acceptable Intake Paths

API Endpoint
/export/<participant_id>
/erase/<participant_id>
/withdraw/<participant_id> (future)

School Admin Request
Authenticated via school-level admin token.

Parent/Guardian Email
Must match verified parent contact stored during onboarding.

Legal Notice
Processed only after compliance review.

4.2 Logging

Every request MUST be logged in:

logs/audit_log.jsonl

With fields:

{
  "ts": <timestamp>,
  "request_type": "export|erase|withdraw",
  "participant_id": "...",
  "initiated_by": "adult|parent|school_admin|legal",
  "verification_status": "pending|verified|rejected",
  "handler": <team member or system>,
  "status": "initiated"
}

5. Verification Workflow
5.1 Adult Participant

Confirm the participant_id exists.

Confirm a matching export or erase request via secure method.

Send “verification in progress” response.

5.2 Parent / Guardian (Minors)

Must satisfy at least one:

verification through school admin

matching parental email on file

signed authorization document uploaded (future feature)

5.3 School Admin

Admin token must be valid.

Must match assigned institution in config.

5.4 Legal

Only processed after internal legal counsel approves.

If verification fails:

reject

log

notify requester

no data processed

6. Fulfillment Workflows
6.1 Right of Access (Export Request)
Steps:

Fetch all records for participant_id from:

session logs

task results

consent logs

metadata

Package into JSON export
Format:
project/exports/<participant_id>/<timestamp>.json

Sanitize

remove system-only fields

ensure no admin tokens or internal identifiers leak

Deliver to Requestor

for schools/parents: send via secure email

for adults: provide secure download link (future)

Audit Log Update
status: completed

Deadline: 7 days (strict internal target)

6.2 Right to Erasure (Delete Request)
Steps:

Verify requestor identity.

Run anonymization job:

Replace participant_id with irreversible hash:

hp_<hash> → anon_<timestamp_random>


Delete PII from:

mapping tables

consent records older than retention limit

raw identifiers

Keep anonymized metrics intact (allowed under NDPR/GDPR).

Write deletion receipt to logs.

Deadline: 72 hours (COPPA requirement for minors)

6.3 Withdraw Consent

(If participant or parent asks to stop further data collection)

Steps:

Mark participant status as: consent_withdrawn = true

Block all future task submissions for them

Erase historical data (same as erasure workflow)

Log withdrawal event

7. Forbidden Actions

Deleting aggregated analytics

Deleting audit logs before retention window expires

Returning data via unverified channels

Processing requests without verification

Sharing internal logs or admin activity

8. Incident Handling

Any failure or delay more than 24 hours triggers:

escalation to Lead Architect

security review

temporary halt of deletion/export pipeline

entry added to incident_runbook.md

9. Responsibilities
Role	Responsibility
Lead Architect	Approves exceptions, oversees compliance
Engineering	Executes export/erase operations
Security	Verifies authenticity, monitors logs
School Admin	Verifies parents for minors
DPO (future)	Handles legal & compliance escalations
10. Enforcement

Violations of this SOP may result in:

access removal

internal disciplinary action

legal repercussions for mishandling minor data

This is a binding internal document.
