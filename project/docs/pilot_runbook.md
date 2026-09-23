# HumanOS Pilot Runbook

**System:** HumanOS / Shape-MVP
**Pilot freeze commit:** `b0d898b`, (Protect analytics and dashboard routes)
**Branch:** `restructure/app-package`
**Document purpose:** Operational guide for running the HumanOS pilot safely and consistently.

---

This runbook is the operational entry point for the HumanOS pilot.

The following documents provide the authoritative procedures for specific
operational, security, privacy, and governance domains:

- Pilot readiness: `pilot_readiness_checklist.md`
- Consent: `consent_flow.md`
- Monitoring: `monitoring_playbook.md`
- Incident response: `incident_runbook.md`
- Data subject rights: `data_subject_rights_sop.md`
- Data retention: `data_retention_policy_strict.md`
- Administrative access: `admin_access_control_strict.md`
- Backup and recovery: `backup_recovery.md`
- Deployment security: `deployment_security_strict.md`

## 1. Purpose

This runbook defines the operational procedure for conducting a HumanOS pilot using the frozen pilot build.

The pilot is intended to validate the behavior of the HumanOS adaptive experience under controlled real-world use, including:

* participant onboarding and consent;
* explicit authorization for adaptive routing;
* canonical task progression;
* governed adaptive task selection;
* evidence validation;
* progression integrity;
* participant and experience ownership isolation;
* routing auditability;
* rejection handling;
* administrative monitoring and analytics; and
* privacy and data-handling controls.

The pilot should generate evidence about system behavior without changing the production code during an active pilot session.

---

## 2. Pilot Freeze

The current pilot freeze is:

**Commit:** `b0d898b`
**Message:** `Protect analytics and dashboard routes`

This freeze incorporates the final pilot security hardening, including administrative authorization for:

* `/dashboard`
* `/metrics/summary/<participant_id>`
* `/metrics/global`
* `/metrics/report/<participant_id>`

The frozen build should be treated as the reference version for the pilot.

Any code change discovered after the freeze should follow the change-control procedure described in Section 17.

---

## 3. Pilot Readiness Status

Passing the automated validation gates establishes technical readiness; authorization to begin the pilot remains conditional on completing the operational readiness checklist and rehearsal.

The following pilot gates have been validated.

| Gate | Area                                   | Status                        |
| ---- | -------------------------------------- | ----------------------------- |
| G1   | Ownership                              | PASS                          |
| G2   | Explicit adaptive authorization        | PASS                          |
| G3   | Canonical progression                  | PASS                          |
| G4   | Out-of-order rejection                 | PASS                          |
| G5   | Duplicate-task rejection               | PASS                          |
| G6   | Malformed cognitive evidence rejection | PASS                          |
| G7   | Rejection audit and answer non-leakage | PASS                          |
| G8   | Experience-scoped exclusion            | PASS                          |
| G9   | Governance before scoring              | PASS                          |
| G10  | Transition revalidation                | PASS                          |
| G11  | Transition source integrity            | PASS                          |
| G12  | Transition → progression integrity     | PASS                          |
| G13  | Behavioral path                        | N/A for current pilot catalog |
| G14  | Session reuse/context conflict         | PASS                          |
| G15  | Routing reproducibility/auditability   | PASS                          |
| G16  | Legacy bypass prevention               | PASS                          |
| G17  | Catalog/execution consistency          | PASS                          |
| G18  | Positive adaptive E2E traversal        | PASS                          |
| G19  | Cross-participant ownership isolation  | PASS                          |

The automated test suite was also executed successfully at the pilot freeze.

---

## 4. Roles

### 4.1 Participant

The participant:

* completes the consent process;
* explicitly authorizes adaptive routing where applicable;
* completes assigned cognitive tasks;
* submits task evidence;
* may withdraw according to the participant-facing procedure.

The participant should not have access to administrative analytics, routing traces, internal scoring metadata, or system secrets.

### 4.2 Pilot Operator / Administrator

The operator is responsible for:

* preparing the pilot environment;
* establishing participant experiences;
* monitoring pilot execution;
* reviewing authorized analytics;
* inspecting audit events when required;
* handling operational failures;
* initiating participant erasure where required; and
* preserving pilot records.

Administrative endpoints require administrator authorization.

### 4.3 Developer / Maintainer

The developer is responsible for:

* resolving confirmed defects;
* maintaining the frozen branch;
* rerunning the required validation suite after changes;
* producing a new freeze commit when a pilot-blocking defect requires code modification.

---

### 4.4 Pilot Start Gate

Do not begin a real participant session until:

- [ ] `pilot_readiness_checklist.md` has been completed.
- [ ] The frozen pilot commit has been verified.
- [ ] The environment smoke test has passed.
- [ ] Administrative access has been verified.
- [ ] Participant-facing access has been verified.
- [ ] Required privacy and consent procedures are available.
- [ ] The pilot operator has reviewed this runbook.

### 4.5 Pilot Operating Constraints

During an active pilot:

- Do not modify production code casually.
- Do not bypass consent or adaptive authorization.
- Do not manually alter progression state.
- Do not manually edit audit records.
- Do not expose administrative analytics to participants.
- Do not copy participant evidence into informal notes unnecessarily.
- Do not introduce new adaptive-routing rules without change control.
- Do not treat pilot observations as evidence of individual diagnosis or prediction.

# 5. Pre-Pilot Environment Checklist

Before admitting a participant, the operator must verify:

* [ ] Correct HumanOS repository and branch are being used.
* [ ] Frozen commit is `b0d898b` or an explicitly approved successor.
* [ ] Working tree contains no unintended modifications.
* [ ] Python virtual environment is active.
* [ ] Required dependencies are installed.
* [ ] Required environment variables are configured.
* [ ] Administrative credentials are configured securely.
* [ ] No administrative secrets are committed to Git.
* [ ] Log directories exist and are writable.
* [ ] Required application services are running.
* [ ] Participant-facing routes are reachable.
* [ ] Administrative routes require authorization.
* [ ] Audit logging is functioning.
* [ ] The pilot operator knows the participant withdrawal/erasure procedure.

Administrative credentials must not be entered into participant-facing workflows or committed to the repository.

---

# 6. Participant Onboarding

Each pilot participant should begin with a fresh participant context.

The onboarding sequence is:

1. Create or establish the participant.
2. Create the participant's bounded experience.
3. Present the consent process.
4. Record explicit consent.
5. Present adaptive-routing authorization where applicable.
6. Record the participant's adaptive authorization decision.
7. Begin canonical task progression.

Adaptive execution must not begin before the required authorization boundary has been satisfied.

---

# 7. Expected Experience Flow

The expected pilot progression is:

```text
Participant
    │
    ▼
Consent
    │
    ▼
Experience Created
    │
    ▼
Adaptive Authorization
    │
    ▼
Canonical Task
    │
    ▼
Validated Submission
    │
    ▼
Governed Adaptive Routing
    │
    ▼
Adaptive Task
    │
    ▼
Validated Submission
    │
    ▼
Progression / Routing Decision
    │
    ▼
Next Eligible Task
```

The system must maintain experience and participant ownership throughout the flow.

A participant must not be able to substitute another participant's experience context.

---

# 8. Participant-Facing Task Rules

Participant-facing task responses must expose only the information required to perform the task.

The participant-facing task payload must not expose:

* correct answers;
* internal correctness mappings;
* hidden decision codes;
* internal scoring information;
* routing candidate pools;
* routing-selection reasons that reveal protected system information;
* participant evidence belonging to another context; or
* administrative analytics.

Adaptive task selection is governed internally. The participant receives the resulting task rather than the internal candidate-selection process.

---

# 9. Valid Submission Procedure

For each task:

1. Participant receives the expected task.
2. Participant completes the task.
3. Participant submits the required evidence.
4. HumanOS validates the submission.
5. Only valid evidence proceeds to scoring/progression.
6. The appropriate completion/progression state is persisted.
7. The next task is determined according to the current governed routing state.

The canonical progression state is authoritative.

A participant should not manually select an arbitrary task in order to bypass progression.

---

# 10. Rejected Submission Handling

HumanOS is expected to reject invalid task submissions.

Examples include:

* out-of-order tasks;
* duplicate task submissions;
* malformed cognitive evidence;
* invalid experience context;
* mismatched participant/session context.

A rejection is not equivalent to a successful task completion.

Where appropriate, the rejection must generate an audit event.

### Evidence privacy

Rejected cognitive evidence must not be unnecessarily copied into the audit record.

The pilot specifically validates that malformed cognitive evidence can be audited without storing the submitted answer in the rejection audit record.

The operator should therefore avoid manually copying participant answers into external notes or logs when investigating a rejection.

---

# 11. Ownership and Session Integrity

HumanOS must preserve the relationship between:

* participant;
* experience;
* task;
* session; and
* progression state.

A participant must not be able to operate on another participant's experience by substituting an experience identifier.

Session reuse is permitted only when the persisted session context matches the current experience/participant/task context.

A context mismatch must fail closed.

---

# 12. Adaptive Routing

Adaptive routing is governed by the available evidence and eligibility rules.

The routing pipeline should be treated conceptually as:

```text
Observed evidence
      │
      ▼
Signal extraction
      │
      ▼
Signal normalization
      │
      ▼
Signal arbitration
      │
      ▼
Governance / eligibility
      │
      ▼
Candidate scoring
      │
      ▼
Bounded candidate selection
      │
      ▼
Routing trace
      │
      ▼
Selected task
```

Governance occurs before adaptive selection.

The pilot build records bounded routing-selection metadata sufficient to audit the candidate set used for the final selection without exposing task content or participant evidence.

The current implementation intentionally retains bounded randomness in final candidate selection.

---

# 13. Administrative Monitoring

Administrative analytics are restricted to authorized administrators.

The following areas require administrative authorization:

* dashboard;
* global metrics;
* participant summaries;
* participant reports; and
* administrative exports.

If an unauthorized request receives access to administrative analytics, the pilot must be treated as having encountered a security incident and the affected pilot activity should be paused pending investigation.

---

# 14. Audit Monitoring

Important audit events include, where applicable:

* consent events;
* authorization events;
* task evidence rejection;
* ownership/membership rejection;
* progression-related events;
* routing-related events;
* administrative activity.

Audit records should be used to establish what occurred without unnecessarily duplicating participant evidence.

When investigating an incident, use the minimum information required.

---

# 15. Participant Withdrawal and Erasure

If a participant requests withdrawal or erasure:

1. Stop further participant activity.
2. Record the operational event according to the approved procedure.
3. Execute the approved erasure/anonymization workflow.
4. Verify that applicable participant-linked records have been handled.
5. Preserve only records that are legitimately required for system/security/audit purposes according to the approved retention policy.
6. Document completion of the request.

The operator should not manually delete individual log lines unless the approved data-handling procedure specifically requires it.

---

# 16. Incident Handling

### Minor operational issue

Examples:

* temporary UI issue;
* participant confusion;
* recoverable request failure.

Action:

1. Record the issue.
2. Determine whether the participant can safely continue.
3. If continuation is safe, continue.
4. Otherwise pause the session.

### Integrity or security issue

Examples:

* participant accesses another participant's experience;
* unauthorized administrative analytics access;
* answer/correctness metadata exposed;
* progression bypass;
* unexpected participant data leakage.

Action:

1. Stop the affected pilot activity.
2. Preserve relevant audit information.
3. Record the incident.
4. Do not modify evidence or logs manually.
5. Escalate to the developer/maintainer.
6. Determine whether the frozen build must be reopened.

---

# 17. Change-Control Procedure

The pilot build should remain frozen while the pilot is running.

If a defect requires a code change:

1. Stop affected pilot activity.
2. Record the defect.
3. Identify the affected gate.
4. Implement the smallest appropriate fix.
5. Run targeted tests.
6. Run the full test suite.
7. Rerun affected pilot harnesses.
8. Run `git diff --check`.
9. Review the final diff.
10. Create a new freeze commit.
11. Update this runbook's freeze reference.
12. Repeat the pilot readiness verification before resuming.

Do not patch the running pilot informally.

---

# 18. Pilot Rehearsal

Before the first real participant, perform one complete dry run using a fresh test participant.

The rehearsal should cover:

* [ ] participant creation;
* [ ] experience creation;
* [ ] consent;
* [ ] adaptive authorization;
* [ ] canonical task;
* [ ] valid submission;
* [ ] adaptive task;
* [ ] adaptive submission;
* [ ] progression;
* [ ] audit inspection;
* [ ] administrative monitoring;
* [ ] participant-facing access restrictions;
* [ ] withdrawal/erasure procedure.

The rehearsal should be performed through the actual application flow rather than solely through unit tests.

---

# 19. Pilot Entry Criteria

The pilot may proceed when:

* [ ] frozen build is verified;
* [ ] environment is verified;
* [ ] participant flow is operational;
* [ ] consent is operational;
* [ ] adaptive authorization is operational;
* [ ] participant-facing exposure is acceptable;
* [ ] administrative authorization is verified;
* [ ] audit logging is functioning;
* [ ] data/privacy checks are complete;
* [ ] fresh-environment smoke test passes;
* [ ] full pilot rehearsal passes;
* [ ] no unresolved pilot-blocking security or integrity issue exists.

---

# 20. Pilot Exit

At the end of the pilot:

1. Stop new participant enrollment.
2. Complete outstanding sessions where appropriate.
3. Preserve required pilot records.
4. Review audit events.
5. Review routing behavior.
6. Review rejected submissions.
7. Review participant experience.
8. Record incidents and anomalies.
9. Perform the approved data-retention/erasure actions.
10. Produce a pilot findings report.

The pilot should produce evidence for the next HumanOS development phase rather than immediately triggering uncontrolled feature expansion.

---

# 21. Post-Pilot Review Questions

The post-pilot review should answer:

### System behavior

* Did canonical progression behave as expected?
* Did adaptive routing remain within governance boundaries?
* Were task transitions coherent?
* Were rejection paths understandable and safe?

### Routing

* What routing signals were observed?
* Were routing decisions stable and explainable from the recorded evidence?
* Were there unexpected oscillations or intervention patterns?
* Did the candidate-selection audit records provide sufficient information?

### Data and privacy

* Was only required information collected?
* Did logs contain unexpected participant information?
* Were rejection records appropriately minimized?
* Did participant withdrawal/erasure behave as intended?

### Operations

* Could an operator run the system without developer intervention?
* Were administrative tools sufficient?
* Were errors understandable?
* What operational procedures need improvement?

### Product/research

* What did the pilot demonstrate?
* What remains unvalidated?
* Which observations justify architectural changes?
* Which observations are merely operational issues?

---

# 22. Freeze Principle

During the pilot, **evidence takes priority over feature expansion**.

The purpose of the pilot is to observe HumanOS operating under controlled real-world conditions.

New capabilities should be considered only after the pilot evidence has been reviewed and the next development phase has been defined.

## Pilot Record

For each pilot deployment, record:

- Pilot identifier:
- Build/freeze commit:
- Operator:
- Start date:
- End date:
- Number of participants:
- Number of completed experiences:
- Incidents:
- Participant withdrawals:
- Data-erasure requests:
- Material anomalies:
- Final disposition:
