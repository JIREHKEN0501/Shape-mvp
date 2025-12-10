B — Strict Internal Data Subject Rights SOP

Filename: project/docs/data_subject_rights_sop_strict.md
Audience: Engineering, Security, Compliance
Classification: INTERNAL — DO NOT SHARE**

HumanOS Tech — Data Subject Rights (STRICT SOP)

Owner: Lead Architect
Last Updated: {{auto-fill on commit}}

This SOP defines the mandatory internal procedures for handling DSR requests.

1. Authorization Requirements (Strict)
Adult Participants

Requires:

email verification OR

matching participant_id + recent session activity

Minors

Requires ONE of the following:

signed parental verification

request originating from school admin domain

school admin credentials in dashboard

uploaded authorization letter (rare case)

All minor requests must be stored in audit_log.jsonl with tag "minor_request": true.

2. Internal Timelines

These override public SLAs:

Action	Internal Target
Export	≤ 24 hours
Deletion	≤ 24 hours
Withdrawal	≤ 12 hours
3. Technical Procedures
3.1 Export Procedure

Lookup participant in DB

Pull:

sessions

metrics

saved answers

consent record

Ensure no admin tokens or internal metadata leak

Generate export JSON using internal script

Hash final export

Store a copy in /exports/ for 7 days

Send encrypted attachment to requester

3.2 Deletion Procedure (Erase Endpoint)

Deletion = anonymization + unlinking, not “removal”.

Steps:

Replace participant_id with anonymized ID

Overwrite:

identifiers

linkages

session metadata

Run verification query to ensure no remnants

Log deletion event in audit_log.jsonl

Generate confirmation report

3.3 Withdrawal Procedure

Mark participant record as "withdrawn": true

Prevent future logging

Automatically end active sessions

Log withdrawal event

Notify Client Success team

4. Fraud Detection

Requests flagged as suspicious must be escalated if:

requester cannot verify identity

request comes from unusual IP or mismatched school domain

multiple deletion attempts occur

Escalation goes to:
Lead Architect → Security → Legal (future role)

5. Logging Rules (Mandatory)

Every request MUST log:

requester identity

participant ID

request type

timestamps (request + fulfillment)

operations performed

whether request involved a minor

handler user ID (engineer/admin processing it)

6. Prohibited Actions

Never send raw DB dumps

Never share admin logs externally

Never delete audit logs

Never bypass guardian verification for minors

Violation = security incident.

7. Periodic Audits

Quarterly review of DSR process

Random sampling of past requests

Verification that anonymization is irreversible

END OF STRICT VERSION
