A — IAM Roles & Privilege Model (Public Version)

Filename: project/docs/iam_roles_public.md
Audience: Schools, parents/guardians, institutional clients
Confidentiality: PUBLIC
Tone: Clean, transparent, simple to understand

HumanOS Tech — IAM Roles & Access Model (Public Version)

Version: v1.0
Last Updated: {{auto-fill on commit}}
Applies To: School administrators, teachers, partner organizations
Purpose:
This document explains the access levels HumanOS uses to protect participant data, especially for children and young users.

1. Overview

HumanOS uses a strict Role-Based Access Control (RBAC) system.
Each role can access only what is necessary to perform its duties.

No single user or staff member has unrestricted access.

2. HumanOS Roles
2.1 Student / Participant

Completes cognitive + behavioral tasks

No access to dashboards

No visibility into internal analytics

No ability to export or delete data directly (handled via parent/school)

2.2 Teacher / School Administrator

Permissions:

View aggregated class or group dashboards

Request export/deletion for specific participants

Create new assessment sessions

Track progress and difficulty levels

Cannot:

Access raw logs

View audit logs

Modify tasks or metrics

See other schools’ data

2.3 Parent / Guardian (for minors)

Permissions:

Request export of their child's data

Request deletion/anonymization

Withdraw future data collection

Cannot:

Access dashboards

Modify tasks

View other participants

2.4 HumanOS Support

Permissions:

Assist with account or access recovery

Validate requests

Forward export/deletion requests to compliance

Cannot:

View raw student data

Access metrics

Run internal tools

3. What HumanOS Staff Cannot Access

To ensure privacy and safety:

No staff member can view participant answers

No staff member can view cognitive performance unless properly authorized

No one can re-identify anonymized participants

No staff member can directly modify logs

All internal activity is monitored and auditable.

4. External Integrations

Third-party vendors (if used) are strictly limited to:

hosting

security scanning

backups

None can view participant data.

5. Summary Table
Role	Data Access	Special Permissions
Student	None	Complete tasks only
Teacher/Admin	Aggregated dashboards	Request delete/export
Parent	Their child’s data only	Export/Delete/Withdraw
Support	Ticket handling only	Cannot view participant data
6. Commitment to Data Protection

HumanOS will never sell data, share it with advertisers, or allow unauthorized access.
All access is logged, monitored, and reviewable.

END OF PUBLIC VERSION
