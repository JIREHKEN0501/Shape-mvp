HumanOS Tech — Access Control & Admin Rights Policy

Version: 1.0
Last updated: <today’s date>

1. Purpose of This Policy

This Access Control & Admin Rights Policy defines:

who can access what

how administrative permissions are assigned

how authentication is controlled

how authorization is enforced

how misuse is detected, monitored, and responded to

The policy applies to all instances of the HumanOS Cognitive & Behavioral Analytics Platform, including pilot deployments, demos, training environments, and production.

2. Access Control Principles

HumanOS follows these core principles:

2.1 Least Privilege

Users only receive the minimum access required for their role.

2.2 Separation of Duties

No single individual can perform all high-risk administrative actions.

2.3 Role-Based Access Control (RBAC)

Permissions are granted based on logical roles (e.g., Admin, Teacher, Researcher).

2.4 Zero Trust by Default

All requests must be authenticated or validated.
Anonymous access is only allowed for public task access endpoints (i.e., loading tasks for a session), but never for analytics or participant data.

3. User Roles & Permissions
3.1 Participant / Student

Permissions:

Start a session

Complete a task

Submit results

No access to:

analytics

other participants

exports

system configuration

3.2 Teacher / Facilitator Access

(Enabled only in school deployments — not active in the MVP yet)

Can:

View reports for participants under their class/school

Download participant summaries

See strengths/gaps

Trigger task sessions during supervised evaluations

Cannot:

Access global metrics

Delete logs

Export raw system data

See participants from other schools

Teacher access always requires school-issued accounts or OAuth SSO.

3.3 Organization Admin (School Admin / HR Admin / Training Center Admin)

Can:

Access reports for users within their organization

Export anonymized participant results

Manage class/department groupings

Trigger access revocations

Review performance analytics limited to their organization

Cannot:

Access global cross-organization data

Change system-level configurations

Access audit logs

3.4 System Administrator (HumanOS Tech Internal)

Full internal access but still bound by separation-of-duties.

Can:

View full logs

Run data corrections

Perform internal debugging

Manage internal tokens, caching, and rate limits

Execute secure deletion requests

Cannot:

Make architectural changes without CTO approval

Access production systems outside approved maintenance windows

3.5 Super Admin (CTO / Lead Architect)

Highest level of authorization.

Can:

Change system-level configurations

Manage deployment credentials

Approve or revoke System Administrator rights

Approve incident response escalations

Approve security policy changes

4. Authentication Requirements
4.1 Admin Token Authentication (MVP)

For the MVP (what you currently built), the admin API uses a rotating bearer token stored in environment variables:

ADMIN_TOKEN=xxxxxxxxxxxx


Requirements:

Minimum 32 characters

Store only in environment variables

Rotate every 30–90 days

Never commit to GitHub

Auto-logout behavior on token rotation

4.2 Strong Authentication for Teacher/Admin Portals (V2)

When school dashboards come online:

OAuth2 / SSO (Google Workspace for Education, Microsoft 365, etc.)

Optional MFA

Passwords never stored by HumanOS

JWT-based session tokens with 15–30 min expiry

4.3 Device/IP Monitoring

Admin requests must log:

IP address

timestamp

endpoint accessed

actor ID (or token-derived label)

Repeated access from unexpected networks → flagged.

5. Authorization Enforcement
5.1 Endpoint-Level Authorization
Endpoint	Public	Teacher	Org Admin	System Admin	Super Admin
/tasks	✔	✔	✔	✔	✔
/start_session	✔	✔	✔	✔	✔
/submit_result	✔	✔	✔	✔	✔
/metrics/summary/<id>	✖	✔ (their students only)	✔ (their users only)	✔	✔
/metrics/global	✖	✖	✖	✔	✔
/metrics/report/<id>	✖	✔ (their students only)	✔	✔	✔
/export/<id>	✖	✔ (their users only)	✔	✔	✔
/admin/*	✖	✖	✖	✔	✔

In the MVP:

Only system admin token access is implemented.

Teacher/org admin roles will be implemented in Phase 5 (RBAC upgrade).

6. Session Security
6.1 Session Expiry

Admin sessions expire after 30–60 minutes (in V2 dashboard).

API token access lasts until token rotation only.

6.2 Replay Protection

All endpoints should validate:

Timestamps

Participant IDs

Duplicates in rapid submission windows

6.3 Rate limiting

Applied per-IP, per-endpoint (already implemented in your MVP).

7. Log Access Control

Only the following roles may read raw logs:

System Admin

Super Admin

Teachers/Org Admins can never access raw log files because they include:

error details

potentially sensitive metadata

system health information

A compromised school account should never lead to system-wide data exposure.

8. Data Export Controls
8.1 Participant-level exports

Allowed for:

Teacher (their students only)

Org Admin (their users only)

System Admin

Super Admin

8.2 Full-system data exports

Only:

System Admin

Super Admin

8.3 Export Logging

Every export writes to audit_log.jsonl:

who exported

what they exported

the time

IP address

9. Admin Rights Assignment & Review
9.1 Onboarding

New admins require:

identity verification

authorization from CTO

least-privilege assignment

logging of role creation in audit log

9.2 Quarterly Review (Mandatory)

Every 3 months:

Remove inactive admins

Rotate all admin tokens

Review logs for unusual patterns

Validate that no former employee retains access

9.3 Emergency Revocation

Any admin access can be disabled immediately by:

CTO

System Admin (if CTO unavailable)

Token invalidation is instant.

10. Misuse & Abuse Detection
Triggers include:

10 export attempts within 1 minute

20 failed admin token validations

unusual time-of-day admin activity

rapid browsing of multiple participant reports

deletion or modification of logs (should be impossible)

access from new geographic locations

Automated actions (MVP or V2):

temporary IP ban

alert to CTO

flag written to audit log

11. Enforcement

Violation of this policy may result in:

access revocation

account deactivation

incident response activation

legal and contractual consequences (for enterprise clients)

12. Versioning & Change Control

All changes to this policy must be:

reviewed by CTO

logged

versioned in Git

communicated to all system administrators

END OF DOCUMENT
