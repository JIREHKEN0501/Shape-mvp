A — Public-Facing Data Processing Addendum (DPA)

Filename: project/docs/DPA.md
Audience: Schools, companies, organizations
Classification: PUBLIC
Legally safe. “Client-facing.” Simple.

HumanOS Tech — Data Processing Addendum (DPA)

Version: v1.0
Effective Date: {{auto-fill on commit}}

This Data Processing Addendum (“DPA”) forms part of the service agreement between HumanOS Tech (“Processor”) and the subscribing organization (“Controller”).

1. Purpose of This DPA

This DPA ensures HumanOS processes personal data in compliance with:

NDPR (Nigeria Data Protection Regulation)

GDPR (where applicable)

COPPA (for child users)

FERPA (for school deployments)

2. Roles

Controller: The school or organization choosing to use HumanOS.

Processor: HumanOS Tech, acting only on instructions of the Controller.

HumanOS does not sell or transfer data to third parties.

3. Categories of Data Processed

HumanOS processes:

Participant identifiers (pseudonymized)

Task performance (answers, timing, progression)

Behavioral metrics (difficulty adaptation, scoring)

Diagnostic logs (crash logs, system events)

Consent records (parent/school authorization)

HumanOS never requires:

Biometric identifiers

Facial recognition data

Financial information

Government-issued ID numbers

4. Lawful Basis & Consent

For adults: direct consent during onboarding.

For minors: parental or school authorization.

Controller is responsible for obtaining lawful consent when required.

5. Security Measures

HumanOS implements:

Encryption in transit (TLS 1.2+)

Encryption at rest (AES-256)

Role-based access control

Strict admin token rotation

Audit logging

Rate limiting + abuse detection

6. Subprocessors

HumanOS may use approved subprocessors (hosting, email services, analytics).
A full list is available in processors.md.

No subprocessor receives identifiable student information beyond what is strictly necessary.

7. Data Retention & Deletion

Participant identifiers stored 30 days.

Behavioral metrics stored 12 months.

Aggregated analytics stored 24 months.

Backups stored 30 days (encrypted).
Deletion endpoints: /erase/<participant_id>.

Full policy: retention_policy.md.

8. Data Subject Rights

HumanOS supports:

Export (/export/<id>)

Correction

Deletion

Withdrawal (stop future collection)

Objection to processing

Requests are handled within 72 hours.

9. International Transfers

If HumanOS transfers data across borders, transfers will follow:

Standard Contractual Clauses (SCCs)

NDPR cross-border transfer rules

10. Breach Notification

HumanOS will notify affected Controllers:

Within 48 hours of confirming a data breach

With details, impact assessment, and remediation steps

Controllers must notify parents/students as required by law.

11. Termination

Upon termination:

All identifiers are deleted within 30 days

All behavioral data anonymized

Backups rotated out on their normal schedule

12. Liability

HumanOS is liable for violations caused by:

Negligence

Unauthorized data sharing

Security failures within HumanOS systems

Controller is liable for:

Improper consent

Unauthorized uploads

Misuse of exports

END OF PUBLIC VERSION
