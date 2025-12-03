PIA_strict.md — HumanOS Tech
Full Data Protection Impact Assessment (Strict, Legal Grade)

Version: 1.0
Prepared by: Jireh Kenneth-Usen (Lead Architect, HumanOS Tech)
Last Updated: <today’s date>

1. PROJECT OVERVIEW

HumanOS Tech is a cognitive and behavioral analytics platform designed to measure pattern recognition, reasoning, emotional intelligence, decision-making, and cognitive performance using interactive tasks and structured activities.

HumanOS will operate across:

Primary & secondary schools (minors under 18)

Universities & corporate training programs (adults)

Specialized fields (aviation, security, clinical psychology)

Due to the dual nature of the target audience, this DPIA provides compliance models for:

Adult participants providing their own consent, and

Children/minors where consent may come from parents or authorized educational institutions, according to national policies.

This DPIA fulfills the requirements of:

GDPR Articles 35–36 (Data Protection Impact Assessment)

GDPR Articles 5–6 (Lawfulness, fairness, transparency)

GDPR Article 8 (Children’s data)

NDPR Nigeria (Data Protection Regulation)

Data Minimization & Purpose Limitation Principles

2. DESCRIPTION OF PROCESSING
2.1 Nature of processing

Participants interact with cognitive tasks (pattern recognition, logic, emotional scenarios) and behavioral tasks (timing, response selection). The system logs:

pseudonymous session IDs

task answers & metadata

timestamps

performance results

analytics summaries

adaptive difficulty suggestions

audit trail events

system usage metadata (IP hash, rate limiting triggers, bot-tripwire events)

2.2 Scope

Processing occurs on HumanOS servers deployed by the organization using the system (school, company, or research body).

No biometric, facial, or body movement data is collected in the MVP.

Eye-tracking (Phase 5) will require an additional DPIA addendum.

2.3 Processing actors
Role	Description
Data Controller	The school, company, or organization using HumanOS
Data Processor	HumanOS Tech (software platform)
Data Subject	Students (minors), employees, trainees, or adults
Third Parties	None at this stage
3. PURPOSE & NECESSITY OF PROCESSING
Primary Purposes

Cognitive assessment

Behavioral pattern tracking

Learning progression insights

Adaptive task sequencing

Educator dashboards

HR/training performance insights

Secondary Purposes

Model improvement

Aggregate analytics

System performance, audit, security

Non-Purposes (explicitly excluded)

The system does not:

make automated decisions with legal/employment consequences

create psychological diagnoses

gather personal identifiers (name, email, etc.)

collect minors’ identifiable data without authorization

4. DATA CATEGORIES
4.1 Data collected

Pseudonymous participant IDs (e.g., hp_fa23b1ea)

Task answers

Reaction time (if enabled)

Session metadata (consent version, source)

Audit trail events

Adaptive difficulty selections

Behavioral task events (non-biometric)

4.2 Sensitive data

The system does not intentionally collect sensitive personal data under GDPR Article 9.

However, cognitive and behavioral data can be inferred to be:

“Psychological profiling,” which may carry elevated risk.
Thus, we treat it with the same safeguards as special category data.

5. DATA SUBJECTS & CONSENT MODELS
5.1 Adults (18+)

Consent is obtained directly via:

on-screen consent form

affirmative “Start” action

explicit notice about data processing & rights

5.2 Minors (under 18)

Two supported models:

A. Parent/Legal Guardian Consent

Required for home/supplementary use

Required if the school mandates it

B. School Consent (acting as data controller)

Allowed where:

national policy grants schools authority

parent notices are given

data is used for educational assessment

HumanOS stores the consent version, timestamp, and controller name, not parent names.

6. LAWFUL BASIS
Processing Activity	Basis (Adults)	Basis (Minors)
Task performance recording	Consent (Art. 6(1)(a))	Consent OR school’s legitimate interest
Analytics & reports	Legitimate Interest (Art. 6(1)(f))	Legitimate Interest balanced test
Security logging	Legitimate interest	Legitimate interest
User rights operations	Legal obligation	Legal obligation

Legitimate Interest Balancing Test (LIBT) is included below.

7. LEGITIMATE INTEREST BALANCING TEST (LIBT)
Purpose test

The platform aims to improve learning and performance. This is legitimate and beneficial.

Necessity test

Cognitive and behavioral data are required to generate insights. No less intrusive method exists.

Balancing test

Mitigations include:

pseudonymized IDs

no sensitive personal identifiers

minimal data retention

strong security controls

transparent consent process

ability to delete/export data

Outcome: processing passes the LIBT.

8. RISK ASSESSMENT (NUMERICAL)

Scale:
Likelihood (L) & Impact (I) rated 1–5
Risk Score = L × I
(1–5 Low, 6–12 Moderate, 13–25 High)

Risk	L	I	Score	Severity
Unauthorized access to logs	3	4	12	Moderate
Misuse of analytics	2	4	8	Moderate
Re-identification (behavioral uniqueness)	1	4	4	Low
Admin token compromise	2	5	10	Moderate
Inference of psychological traits	3	4	12	Moderate
Minors’ data mishandling	2	5	10	Moderate
Biometric misunderstanding (users think biometrics collected)	2	3	6	Moderate
9. MITIGATIONS
9.1 Technical Controls

Pseudonymization

IP hashing

Rate limiting

HMAC log integrity

Strict admin token rotation

TLS encryption

Minimal data collection

Local-only storage

No third-party tracking

No cloud analytics

9.2 Organizational Controls

Staff access limitation

In-house data governance policy

Mandatory DPIA review every 6 months

Ethics Board for minors and moral/emotion tasks

9.3 User Rights Workflow

Supports:

Access

Export

Erasure

Withdraw consent

Objection

All through /export, /erase, and consent controls.

10. RETENTION & DELETION POLICY
Data Type	Retention	Deletion Method
Logs (data_log.jsonl)	30–90 days	overwrite + rotate
Analytics summaries	12–24 months	aggregation & anonymization
Audit logs	12 months	secure wipe
Backups	30 days	encrypted at rest

Organizations may configure retention according to law.

11. SECURITY CONTROLS CHECKLIST

 Rate limiting

 HMAC log integrity

 Bot detection

 Pseudonymization

 IP hashing

 Audit logging

 Admin token with rotation

 No plaintext secrets

 HTTPS (deployment requirement)

 Local-only processing

 Server patching workflow

12. DATA BREACH RESPONSE PLAN
Trigger events:

Unauthorized access

Suspicious admin activity

Log corruption

Server compromise

Data leak indication

Response steps (within 72 hours):

Contain the issue

Disable admin tokens

Preserve forensic logs

Notify controller (school/company)

Assess impacted subjects

Provide remedial recommendations

Regenerate keys/admin credentials

Submit regulatory notifications (if required)

13. ETHICS OVERSIGHT

Required for modules involving:

emotion recognition tasks

moral dilemma tasks

adaptive difficulty for minors

reaction-time stress indicators

Reviewer group includes:

psychologist

pedagogy expert

software lead

data protection officer

14. CONCLUSION & RESIDUAL RISK

With all mitigation measures applied:

Residual risk: Low to Moderate

Acceptable for an MVP

Requires periodic review as features expand

Suitable for minors only under consent-based or institutional control frameworks

15. SIGN-OFF
Role	Name	Signature	Date
System Architect	Jireh Kenneth-Usen	—	—
Data Protection Lead	To be assigned	—	—
Ethics Reviewer	To be assigned	—	—
Executive/Controller	Org-specific	—	—
