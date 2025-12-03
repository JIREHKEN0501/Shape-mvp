Data Subject Rights Standard Operating Procedure (SOP)

HumanOS Tech – Data Participant Rights & Requests Handling
Version: 1.0
Last updated: <today’s date>

1. Purpose of this SOP

This SOP explains how HumanOS Tech and any Data Controllers (schools, companies, training centers) must process and respond to participant data rights requests, including:

Right of access

Right to rectification

Right to deletion / erasure

Right to withdraw consent

Right to data portability

Right to restrict or object to processing

This policy ensures compliance with NDPR, GDPR, FERPA (for schools), and global privacy standards.

2. Definitions

Data Controller – The organization deploying HumanOS (school/employer).

Data Processor – HumanOS Tech, processing data on behalf of the controller.

Participant – User of the system (student, employee, trainee).

Parent/Guardian – For minors, the legally authorized representative.

3. Request Channels

A rights request may come from:

A participant

A parent or legal guardian

A school administrator

A company HR representative

A regulatory authority

Valid channels include:

Email

Secure school/organization portal

In-person request at the controller’s office

Future in-app account settings

Data Subject Request (DSR) form

For security, HumanOS Tech never accepts requests via:

social media

SMS/WhatsApp

anonymous messages

unverifiable accounts

4. Verification Requirements
4.1 Adults

Verify identity using:

email match with organization records

confirmation from the Data Controller

matching participant_id token (if system allows it)

4.2 Students / Children

Requests must be verified through:

school administrator confirmation or

parent/guardian signature + ID verification

No direct student-only request may trigger deletion without adult authorization (required by law).

5. Types of Requests and Exact Procedures
5.1 Right of Access (Data Export)

Goal: Allow participants to view their stored data.

HumanOS Process (MVP):

Receive verified request.

Controller confirms participant identity.

HumanOS runs:

GET /export/<participant_id>


System returns JSON with all matching log entries:

session_start

submit_result

metrics

events

HumanOS sends the export securely (encrypted attachment or secure portal upload).

Log entry created:

action: "export_performed"
actor: <admin/system>
participant_id: <id>
status: "ok"

Expected Response Time

Within 7 days (max 30 days for complex cases).

5.2 Right to Rectification (Correcting Data)

Since HumanOS does not store names or personal PII, rectification refers to:

incorrect session metadata

task IDs

corrupted log entries

Procedure:

Controller identifies incorrect records.

HumanOS supports correction only by:

anonymizing old data

re-running or re-submitting corrected tasks

Never directly rewrite logs (immutability).

Document which entries were repaired.

5.3 Right to Deletion / Erasure
Endpoints used:

Public:

DELETE /erase/<participant_id>


Admin deep-clean:

POST /admin/erase/<participant_id>

Procedure:

Verify request (adult or parent/school admin).

Confirm that no legal or contractual retention requirements block deletion.

Run public or admin erase API.

The system:

replaces participant_id → anonymized:<timestamp>

removes identifying trace

keeps analytical value of anonymized data

Confirm deletion to requester.

Log action:

action: "erase_performed"
actor: admin/system
participant_id: <id>
changed_lines: <count>

5.4 Right to Withdraw Consent
If participant withdraws:

Stop collecting any further data

Block start_session for that participant

Run erase request if they want past data removed

Inform controller immediately

Add participant_id to denied list (future release)

Future endpoint:
POST /withdraw

MVP Process:

Controller emails withdrawal

System admin marks participant ID as blocked

Future sessions → rejected

Past data → erased if requested

5.5 Right to Restrict Processing

If restriction is requested:

Pause all analytics

Block submit_result

Allow export

Keep session data but label it “restricted”

Restriction lifted only on written approval from controller

5.6 Right to Object

Participants may object to:

automated profiling

analytics usage

decision-making without human review

Response procedure:

Inform the controller immediately.

Continue to collect data only if legally justified.

If objection valid → restrict processing or delete data.

6. Timeframes for Responses
Standard:

7 days for most requests.

Maximum Allowed:

30 days (extendable by another 30 for very complex cases).

High Priority:

Security-related deletion must be immediate.

7. Logging Requirements

Every rights request MUST be logged in audit_log.jsonl:

{
  "ts": <timestamp>,
  "action": "dsr_request",
  "participant_id": "<id>",
  "type": "<export|erase|withdraw|restrict|object>",
  "status": "<pending|completed>",
  "actor": "<controller/admin/system>",
  "extra": <metadata>
}

8. Responsibilities Breakdown
HumanOS Tech (Processor)

Execute delete/export requests

Maintain API reliability

Support controller via email/ticket

Maintain audit logs

Provide secure transfer

Data Controller (School/Employer)

Verify identity

Determine legal basis

Communicate with participants

Handle complaints

Document lawful retention exemptions

9. Special Notes for Minors & Students

Parent/guardian OR school approval is mandatory for any DSR.

Students alone cannot trigger deletion.

Exports for minors must be delivered only to school or guardian.

10. Versioning & Change Management

All changes must be:

reviewed by the Lead Architect

versioned in Git

communicated to deployment organizations

reflected in training materials

END OF DOCUMENT
