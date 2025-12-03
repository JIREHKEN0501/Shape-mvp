# HumanOS Tech — Consent Flow Specification  
_For adult users + school deployments (children/young people)_

Version: 1.0  
Status: Approved for MVP  
Last updated: <update date>

---

# 1. Purpose

This document defines the **user consent workflow** for the HumanOS cognitive & behavioral analytics system.  
It ensures:

- Legal compliance (GDPR / NDPR / school policies)
- Clear, age-appropriate explanations
- Proper capture of audit logs
- Support for both adult and child/parent consent paths

This consent flow must be implemented before any data collection begins.

---

# 2. Consent Entry Points

Depending on deployment structure:

### **A. Standalone / direct users (adults)**  
User signs up → sees consent modal → accepts or exits.

### **B. Organization-managed (schools, companies)**  
Organization sends a link or embeds the system.  
Two possible flows:

### **B1: Adult participants (e.g. staff, trainees, university students)**  
Same as (A), but controller notices must mention the organization.

### **B2: Children / minors in school settings**  
Consent must be obtained from:

- **Parent/guardian** (preferred and safest)  
- OR the **school**, depending on local laws & contract  
- Child must also receive age-appropriate explanation

The system must support:

✔ Parent link  
✔ School admin “pre-consent list”  
✔ Light student assent message at start

---

# 3. Flow Overview (all deployments)

Landing page / Pre-screen →
Consent Modal (role-specific) →
User accepts or declines →
If accepted → participant_id generated + logged
If declined → exit page

markdown
Copy code

---

# 4. Consent Modal — Structure

All consent screens must contain:

1. **Plain-language explanation of the system**
2. **What data we collect**
3. **How results will be used**
4. **Who can see the results**
5. **Rights to withdraw**
6. **Link to Privacy Notice**
7. **Two buttons: “I agree” and “I do not agree”**

Audit logs stored via:

action: "consent"
participant_id: generated or placeholder
status: "accepted" or "declined"
consent_version: "v1"
role: "adult" | "student" | "parent"
timestamp: <unix>

yaml
Copy code

---

# 5. CONSENT TEXTS  
### (You will use these *exactly* in the future UI)

---

## 5A. **ADULT CONSENT TEXT**

**Title:**  
**Consent to Participate in HumanOS Cognitive & Behavioral Tasks**

**Body:**  
By continuing, you voluntarily agree to participate in short cognitive and behavioral tasks provided by **HumanOS Tech**.

The system will process:

- Your task responses (answers, timings, number of attempts)  
- Behavioral patterns (such as speed, accuracy, difficulty progression)  
- Basic technical data (IP address, device type) for security

Your results will be used to help improve your learning experience, training support, or skill development.  
Only authorized staff from your organization and HumanOS Tech (for support and security purposes) may access your data.

You may withdraw at any time by stopping use or contacting your organization.  
For more details, see the **Privacy Notice**.

**Buttons:**  
[ I Agree ]  [ I Do Not Agree ]

---

## 5B. **PARENT / GUARDIAN CONSENT TEXT**

**Title:**  
**Parental Consent for Student Use of HumanOS**

**Body:**  
Your child’s school is using the HumanOS cognitive and behavioral learning tool to better understand learning patterns and support students.

HumanOS will process:

- Your child's responses to short puzzles and scenarios  
- Timing and interaction accuracy  
- Basic technical data (IP address, device type)

The goal is to provide teachers with better insights into strengths, support needs, and engagement.  
No decisions about your child will be made automatically.  
Only school staff and authorized HumanOS Tech personnel (support/security only) can access this data.

**You may withdraw consent at any time** by contacting the school.

By agreeing, you confirm you are the parent or legal guardian and consent to your child's participation.

**Buttons:**  
[ I Give Consent ]  [ I Do Not Consent ]

---

## 5C. **STUDENT ASSENT (AGE-APPROPRIATE)**

**Title:**  
**Before we start…**

**Body:**  
Your school is using a tool called HumanOS to understand how students learn.  
You’ll see short puzzles and questions.  
Your teacher can see your progress.  
If you don’t want to continue, tell your teacher.

**Button:**  
[ Continue ]

---

# 6. Data Collected & Purpose (to display in consent modal)

A standardized expandable section:

• Task responses and answers
• Time spent on each task
• Attempts, retries, hints
• Device/IP for security and rate-limits
• Aggregated analytics to help educators understand strengths and support needs

yaml
Copy code

---

# 7. Withdrawal Path

Users must be shown a clear message:

“**If you withdraw, your future data will stop being collected.  
You may request deletion of your previous data using the export/erase endpoints or by contacting the controller.**”

Students must be told:  
“Please inform your teacher if you want to stop.”

---

# 8. UI Flow Diagram (text version)

Start →
├─ Adult user →
│ Display Adult Consent → Accept → Generate participant_id → Start session
│ → Decline → Exit screen
│
├─ Parent / Guardian →
│ Display Parent Consent → Accept → Add child to approved list → Student login
│ → Decline → Do not allow child to proceed
│
└─ Student →
If parent consented or school uploaded pre-consent list:
Show Student Assent → Continue → Start session
Else:
Block access and show: “Consent required from parent/guardian.”

yaml
Copy code

---

# 9. API Interaction (Mapped to Your Current MVP)

### Entry:  
Before calling `/start_session`, UI must require:  

- `consent_version`  
- `role` (adult, parent, student)  
- `source` (“web”, “demo”, “school_portal”, etc.)  

### Storage:  
Consent events log to:

`logs/audit_log.jsonl`

With:

{
"ts": <timestamp>,
"action": "consent",
"participant_id": "<id or null>",
"role": "adult | parent | student",
"status": "accepted | declined",
"consent_version": "v1",
"extra": {}
}

yaml
Copy code

---

# 10. Responsibilities Split

### HumanOS Tech  
- Processes data securely  
- Provides dashboards  
- Maintains export/erase features  
- Assists with rights requests  
- Ensures technical compliance  

### School / Employer (Controller)  
- Decides legal basis  
- Obtains parent/guardian consent where required  
- Manages participant lists  
- Handles complaints and deletions first  

---

# 11. Versioning

- `v1` → MVP version  
- Future versions must be logged with semantic versioning:
  - `v1.1` (text edits)
  - `v2` (new data types / eye tracking)
  - `v3` (emotion detection or webcam modules)

---

# 12. Attachments

- Link to `privacy_notice.md`  
- Link to strict DPIA  
- Link to summary DPIA  
- Link to incident runbook  

---

# End of Document
