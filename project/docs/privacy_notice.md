# HumanOS Tech – Privacy Notice  
_for the Shape Cognitive & Behavioral Analytics MVP_

_Last updated: v1.0_

HumanOS Tech (“we”, “us”, “our”) provides a cognitive and behavioral analytics tool
(the “Service”) that helps organizations understand learning patterns, decision-making
styles, and areas for support. This Privacy Notice explains how we handle personal data
when the Service is used in pilots with schools, training organizations, or companies.

This notice is written to be understandable by non-lawyers and can be shared with
participants, parents/guardians, and client organizations.

---

## 1. Who is responsible for your data?

The organization that invites you to use the Service (for example, a **school** or
**employer**) normally acts as the **Data Controller**. HumanOS Tech acts as a
**Data Processor**, providing the technology and analytics on their behalf.

In some cases (for example, if you sign up directly with HumanOS Tech), we may act
as the Data Controller. In those cases, we will make that very clear at the point
of signup.

If you are unsure who the controller is in your case, please contact the organization
that invited you to use the tool, or email us using the contact details below.

---

## 2. What does the Service do?

The Service presents short tasks, puzzles, or scenarios and records:

- How you respond (answers, choices, reaction patterns)
- Basic timing (when you started, when you finished)
- Basic technical information (for example, IP address and browser type)

From this, we generate **aggregated metrics** such as:

- Accuracy, error rates, and number of attempts  
- Time taken on tasks  
- Patterns across categories (e.g. pattern recognition, reasoning, emotional judgment)

The goal is to help educators, trainers, or managers understand **how to support you**,
not to punish or label you.

---

## 3. What data do we collect?

We follow a strict **data minimization** approach.

We may process the following types of data, depending on how the Service is configured
by the controller (e.g. the school):

### 3.1 Identification data (kept as light as possible)

- A generated participant ID (e.g. `hp_xxxxxxxx`)  
- Optional mapping to a school or internal ID (usually kept by the school, not by us)  
- Role or group information (e.g. “Class 5B”, “math pilot group A”, “sales trainees 2025”)

We strongly encourage controllers **not** to send full names, home addresses,
or other direct identifiers into the analytics system.

### 3.2 Behavioral & cognitive task data

- Task responses (answers chosen, typed responses where applicable)
- Timestamps and duration (how long you spent on each task)
- Number of attempts, hints used, and completion status
- In some modules: responses to dilemmas or scenario-based questions

### 3.3 Technical and safety data

- IP address, browser type, device type (used for security and rate-limiting)
- Internal logs for performance, error tracking, and security events
- Honeypot / bot-detection events (e.g. automated scanners hitting decoy forms)

### 3.4 Sensitive data

The Service is **not** designed to collect medical diagnoses, clinical mental-health
information, or detailed biometric identifiers. We ask all controllers to avoid
entering such data. If you think such information has been entered by mistake,
please contact the controller or us so we can help remove or anonymize it.

---

## 4. Children and young people

The Service can be used with:

1. **Adult participants** (e.g. employees, university students, adult learners), and  
2. **Children or young people** in a school setting.

When the Service is used with **children**, we expect:

- The **school** (or educational organization) to act as Data Controller.
- The school to obtain a valid legal basis for processing:
  - For example: consent from a **parent or legal guardian** where required, and/or
    another appropriate basis under applicable data protection law.
- The school to provide parents/guardians with:
  - A clear explanation of what the tool does  
  - This Privacy Notice or an equivalent summary  
  - Contact details for questions or opt-out requests.

We design the system so that:

- Student data is kept to the **minimum necessary** for analytics.
- Sensitive decisions (e.g. exclusion, grading, discipline) should **not** be made
  solely on the basis of this tool’s outputs, and must always involve human judgment.

If you are a parent or guardian and have questions or wish to exercise your rights,
please contact your child’s school first. You may also contact us directly using
the details below.

---

## 5. Why do we process your data? (Legal basis)

The legal basis for processing depends on how the Service is being used:

- **Legitimate interests** – for example, a school or employer may use the Service
  to understand learning needs and improve support, while taking steps to protect
  your privacy and rights.
- **Consent** – for some pilots or optional research features, the controller
  may rely on your explicit consent (or a parent/guardian’s consent for a child).
  In such cases, you will be clearly informed and can withdraw consent at any time.
- **Contract** – if you sign up directly with us, basic processing may be necessary
  to provide the Service you requested.

The specific basis in your context should be described by the organization that
invited you to use the tool.

---

## 6. How do we use your data?

We use personal data to:

- Deliver tasks and exercises
- Compute metrics and dashboards for authorized staff
- Help instructors or managers personalize support
- Maintain security, rate limiting, and abuse prevention
- Improve the Service (in an aggregated or anonymized way where possible)

We **do not**:

- Sell your personal data
- Use your data for general advertising or unrelated marketing
- Use your data to make fully automated, high-impact decisions about you

---

## 7. How long do we keep your data?

Retention periods can vary by deployment, but we generally recommend:

- **Raw identifiers / direct mappings**: kept as short as possible (e.g. 30–90 days),
  or stored only by the controller (e.g. the school) and not by us.
- **Session logs & task results**: retained for the duration of the pilot or course
  and for a limited period afterwards (for example, up to 2 years) to allow follow-up
  analysis and auditing.
- **Aggregated, anonymized statistics**: may be kept for longer, as they no longer
  identify individuals.

Precise retention periods should be documented in the Data Protection Impact Assessment
(DPIA) for the specific deployment.

---

## 8. Who can see your data?

Access is restricted to:

- Authorized staff at the controller organization (e.g. teachers, school leadership,
  approved researchers, or HR/training leads)
- HumanOS Tech staff who need access to maintain, support, or secure the Service

We may share data with carefully selected third-party providers (for example,
cloud hosting or email delivery services) acting as **sub-processors**. These parties
must follow our instructions, protect your data, and cannot use it for their own
purposes.

We do **not** share personal data with unrelated third parties for their own marketing.

---

## 9. International transfers

Where data is hosted or accessed from outside your country, we use appropriate
safeguards such as:

- Data processing agreements with standard contractual clauses, and  
- Technical and organizational measures (encryption, access controls, logging).

Details of hosting locations and transfer safeguards can be provided on request.

---

## 10. Your rights

Depending on applicable data protection law, you may have the right to:

- Access a copy of your personal data
- Request correction of inaccurate data
- Request deletion or anonymization of your data (where legally possible)
- Object to certain types of processing
- Withdraw consent at any time, where consent is the legal basis
- Receive your data in a machine-readable format (data portability), in some cases

If you wish to exercise these rights:

1. First contact the organization that invited you to use the tool (e.g. your school
   or employer), as they are usually the Data Controller.
2. You may also contact HumanOS Tech using the details below, and we will cooperate
   with the controller to handle your request.

We support these rights through technical features such as:

- Export endpoints (`/export/<participant_id>`)
- Erasure / anonymization endpoints (`/erase/<participant_id>` or equivalent)
- Audit logs for access, export, and deletion events

---

## 11. Security

We take reasonable technical and organizational measures to protect your data, such as:

- TLS encryption in transit (HTTPS)
- Access controls and authentication for administrative tools
- Rate limiting and bot detection
- Logging and monitoring for suspicious activity
- Regular backups and recovery testing

No system is perfectly secure, but we design the Service to limit the impact
of any incident and to support timely detection and response.

For more details, see our internal **Incident Response Runbook** and **DPIA** documents,
which can be shared with client organizations under appropriate conditions.

---

## 12. Contact and complaints

If you have questions about this Privacy Notice or how your data is processed,
you can contact:

**HumanOS Tech – Data Protection Contact**  
Email: `privacy@humanos.tech` (placeholder, update with real address)  
Phone: `+234-XXX-XXX-XXXX` (placeholder, update with real number)

You also have the right to lodge a complaint with the relevant data protection
authority in your country. We always encourage you to contact us or the controller
first so we can try to resolve any concerns directly.

