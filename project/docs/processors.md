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
