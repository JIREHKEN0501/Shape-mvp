HumanOS Tech — Third-Party Processor Inventory
1. Purpose

This document lists all external service providers (“processors”) that handle or may handle user data on behalf of HumanOS Tech.
It supports compliance with NDPR, GDPR, FERPA, and school-level data governance requirements.

2. Processor Inventory Table
Processor Name	Category	Data Shared	Purpose	Storage Location	Risk Level	Contract / DPA Status
Hosting Provider (TBD—e.g., DigitalOcean / AWS / Azure)	Cloud Infrastructure	Pseudonymized logs, task results	Host backend services and maintain uptime	EU/US region (configurable)	Medium	To draft
Email Provider (optional—Mailgun/SendGrid)	Transactional Email	Admin email, event alerts	Notify admins of incidents or system alerts	US/EU	Medium	To draft
Error Monitoring (Sentry / TBD)	Crash/Error Logging	Stack traces, anonymous context	Detect and debug backend issues	EU/US	Medium	To draft
Analytics (Optional)	System Analytics	Aggregated, anonymized metrics only	Usage insights, performance	EU/US	Low	To draft
Backup Storage (Cloud bucket)	Data Retention	Encrypted backups	Restores after outage/data loss	EU/US	Medium	To draft
3. Data Classification

HumanOS Tech classifies data into:

Tier 0 – Public: No restrictions (e.g., website content)

Tier 1 – Low Sensitivity: Pseudonymized task results

Tier 2 – Medium Sensitivity: Metadata, device info

Tier 3 – High Sensitivity: Raw identifiers (not stored long-term; if temporarily collected, immediately hashed or redacted)

Tier 4 – Restricted: Minor data (special protection required)

HumanOS mainly processes Tier 1–2 data.

4. Contracts & Safeguards Checklist (per processor)

Each third-party processor must meet the following:

DPA (Data Processing Agreement) signed

Clear retention limits

Encryption at rest and in transit

Sub-processor transparency

Right to audit clause

Breach notification within 72 hours

GDPR/NDPR-compliant security measures

Servers located in compliant jurisdictions

Annual security review

5. Risk Ratings Explained

Low: Minimal data, aggregated or anonymized

Medium: Pseudonymized behavioral data

High: Any processor with access to identifiers (HumanOS avoids this)

B. PROCESSOR RISK ASSESSMENT (embedded in same file)

Add this section below the table:

Risk Assessment Summary
Risk Category	Description	HumanOS Mitigation
Unauthorized Access	Processor staff misuse access	Strong encryption, DPA restrictions, logging
Data Residency Risk	Non-local storage laws	Only compliant regions (EU/US)
Minor Data Protection	Schools require extra safeguards	Parental consent workflows, strict DPIA
Vendor Breach	Processor is compromised	72-hour breach clause, incident runbook
Over-collection	Processor collects extra data	Data minimization clauses in contract
Sub-processor Chains	Hidden subcontractors	Require pre-approval before adding subs
Retention Risk	Data held longer than needed	Max 30–90 day retention rules
C. DATA PROCESSING AGREEMENT TEMPLATE (project/docs/dpa_template.md)

Full formal legal-style template:

Data Processing Agreement (DPA) — HumanOS Tech

Effective Date: ___
Parties:
HumanOS Tech (“Controller”)
and
________________________________ (“Processor”)

1. Subject Matter

Processor handles pseudonymized behavioral/cognitive assessment data for the purpose of hosting, delivering, or supporting HumanOS services.

2. Duration

Valid for the duration of the service contract unless terminated earlier.

3. Nature & Purpose of Processing

Processor may store, transmit, or process pseudonymized session data, logs, or analytics for:

hosting

uptime monitoring

backup storage

email delivery

performance analysis

4. Categories of Data

Participant ID (pseudonymized)

Task results

Timing metrics

Device metadata

Session events

No raw identifiers (names, emails, photos) are stored by HumanOS.

5. Data Subject Categories

Students (minors—with school/parental consent)

Adult users

Staff performing training tasks

6. Processor Obligations

Processor shall:

Process data only on documented instructions

Provide encryption in transit + at rest

Ensure confidentiality

Limit access to authorized personnel

Support HumanOS in fulfilling NDPR/GDPR obligations

Notify HumanOS within 72 hours of a breach

Delete/purge data upon contract termination

Not subcontract without written approval

7. Security Measures

Access logs

Role-based access control

Data minimization

Encrypted backups

Annual audits

8. Return or Erasure of Data

Upon termination, Processor shall return OR securely erase all data.

9. Audit Rights

HumanOS may request a security report or audit summary annually.

10. Liability

Processor is responsible for damages resulting from unauthorized processing, breaches, or non-compliance.
