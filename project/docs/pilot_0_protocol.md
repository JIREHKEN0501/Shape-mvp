# HumanOS Pilot 0 — Controlled Pilot Protocol

Protocol version: 0.1
Pilot stage: Pilot 0 — Initial controlled cohort
Target cohort: 5–10 participants
Application freeze: eaa6fe7
Validation evidence: 8333802
Planned pilot window: 25 September 2026
Status: Draft for operator review

## 1. Purpose

Pilot 0 is the first controlled real-participant evaluation of the frozen HumanOS pilot build.

The purpose is to determine whether HumanOS can be operated consistently with real participants while collecting evidence about:

participant onboarding;
consent;
adaptive authorization;
canonical task progression;
adaptive task execution;
evidence validation;
rejection handling;
ownership and session integrity;
participant experience;
operator experience;
routing behaviour; and
quality and interpretability of captured operational evidence.

Pilot 0 is an operational and exploratory pilot.

It is not intended to establish:

scientific validity of HumanOS behavioural inference;
clinical or psychological diagnostic capability;
population-level conclusions;
predictive accuracy;
validated psychological measurement;
generalizable behavioural classifications.
## 2. Pilot Build

Pilot 0 will operate against the frozen application build documented in the validation evidence record.

Application freeze: eaa6fe7

No application behaviour should be changed during an active participant session.

If a pilot-blocking defect is discovered, the session should be stopped or safely concluded and the issue documented before any code change is introduced.

Changes should follow the documented change-control process rather than being made ad hoc during participant operation.

## 3. Participant Cohort

Pilot 0 will begin with approximately 5–10 participants.

Participants may be recruited from:

friends;
colleagues;
trusted contacts; and
other individuals who voluntarily agree to participate.

The initial cohort should prioritize participants who are willing to provide detailed feedback about confusing instructions, technical problems, unexpected behaviour, and their overall experience.

Broader online recruitment may be considered after Pilot 0 has been reviewed.

Participant principle

Each participant should complete one primary pilot experience during Pilot 0 unless an operational issue requires a controlled repeat or rehearsal.

## 4. Participant Identification

HumanOS should not use participant names as analytical identifiers.

The pilot operator should maintain a simple external pilot reference such as:

P001
P002
P003
...

The pilot reference is an operational coordination identifier.

It should not be inserted into HumanOS as a substitute for its existing participant/session controls unless explicitly required by the application.

Any contact information used for recruitment or follow-up should remain separate from analytical evidence.

## 5. Participant Briefing

Before beginning the experience, the participant should receive a concise explanation covering:

what HumanOS is being evaluated for;
what the participant will be asked to do;
that participation is voluntary;
what information is collected;
that adaptive routing may change the sequence or difficulty of tasks;
how withdrawal is handled;
how to report a technical or usability problem; and
who to contact regarding the pilot.

The briefing should not disclose answers, expected solutions, or task-specific reasoning that could influence participant responses.

## 6. Consent

A participant must complete the documented consent flow before the experience begins.

The operator should verify that consent has been successfully established before proceeding.

No participant should be manually advanced around the consent mechanism.

## 7. Adaptive Authorization

Where adaptive routing is used, the participant must explicitly authorize adaptive participation through the documented flow.

The operator should verify that adaptive authorization is recorded before proceeding into the adaptive experience.

Adaptive participation must not be silently enabled by the operator.

## 8. Participant Journey

The expected Pilot 0 journey is:

Participant recruitment
        ↓
Participant briefing
        ↓
Consent
        ↓
Experience creation
        ↓
Explicit adaptive authorization
        ↓
Canonical task progression
        ↓
Adaptive task execution
        ↓
Experience completion
        ↓
Participant feedback
        ↓
Operator review

The operator should follow the documented flow rather than manually manipulating participant state.

## 9. Participant Independence

The purpose of Pilot 0 is to observe the participant interacting with the system.

The operator should therefore avoid influencing task responses.

If a participant asks for help answering a cognitive task, the operator should not provide the answer or reasoning.

A suitable response is:

"Please answer based on your own understanding. I can't provide help with the task itself."

The operator may assist with genuine technical problems, such as navigation or an obviously broken interface, while recording the intervention.

## 10. What the Operator Observes

The operator should observe five categories.

10.1 Technical behaviour

Record:

application errors;
HTTP errors;
broken pages;
unexpected task transitions;
session problems;
unexpected latency;
service restarts;
any intervention required to continue.
10.2 Participant comprehension

Record instances where participants:

do not understand an instruction;
interpret an instruction differently than intended;
misunderstand progression;
are uncertain about what they are expected to do;
repeatedly request clarification.

The operator should record the observation without independently diagnosing the participant.

10.3 Participant experience

Record notable:

frustration;
confusion;
boredom;
excessive perceived difficulty;
repetition;
unexpected transitions;
willingness or unwillingness to continue.

These observations describe the experience and should not be interpreted as psychological conclusions.

10.4 System behaviour

Verify where observable:

expected tasks are presented;
canonical progression is maintained;
adaptive routing activates where expected;
invalid submissions are rejected;
ownership boundaries remain intact;
audit events are generated as expected.
10.5 Operator experience

After each session, the operator should ask:

Could another trained operator run this session using the documentation without needing access to the codebase?

If not, document what information was missing.

## 11. Evidence Recorded Per Participant

At minimum, record:

Field	Description
Pilot code	P001, P002, etc.
Cohort	Pilot 0
Consent	Confirmed / issue
Adaptive authorization	Confirmed / issue
Session completed	Yes / No
Tasks completed	Count or documented endpoint
Rejections	Count/type
Routing anomalies	Yes / No + description
Technical incidents	Yes / No + description
Participant feedback	Short summary
Operator notes	Operational observations
Follow-up required	Yes / No

The observation record should contain only the information necessary to operate and evaluate the pilot.

## 12. Incident Classification

Pilot findings should be classified rather than immediately converted into code changes.

P0 — Pilot blocker

An issue that prevents safe or valid continuation of the pilot.

Examples:

participant data isolation failure;
consent bypass;
serious authorization failure;
unrecoverable session integrity problem;
material data leakage.

A P0 should stop the affected pilot activity pending review.

P1 — Significant issue

An issue that does not necessarily stop the current session but should be addressed before expanding the pilot.

Examples:

recurring progression problem;
significant participant confusion;
repeated adaptive-routing anomaly;
important evidence-quality problem.
P2 — Improvement

A non-blocking problem or usability improvement.

Examples:

unclear wording;
minor interface friction;
operator documentation gap;
inconvenient workflow.
Observation

An interesting result that does not itself constitute a defect.

Examples:

unexpected task-selection pattern;
unusual participant strategy;
potentially useful routing behaviour;
question requiring later research.
## 13. Do Not Fix During Observation

The operator should not modify the application simply because an unexpected result occurs.

Instead:

observe;
record;
classify;
continue if safe and valid;
review after the session.

The purpose of Pilot 0 is partly to discover what deserves engineering attention.

Immediate intervention is appropriate only when necessary to protect participant integrity, data integrity, safety, or the validity of the session.

## 14. Withdrawal and Erasure

A participant may withdraw according to the documented withdrawal procedure.

If withdrawal occurs:

stop further participant activity;
record the operational event;
execute the approved withdrawal/erasure process;
verify that participant-linked records were handled;
preserve only records that are legitimately required;
document completion.

The operator should not manually delete individual log entries unless the approved procedure specifically requires it.

## 15. Pilot 0 Success Criteria

Pilot 0 does not require a completely problem-free system.

The pilot is considered operationally successful if:

System
participants can enter through the documented flow;
consent operates correctly;
adaptive authorization operates correctly;
canonical progression operates correctly;
adaptive routing executes where expected;
no unresolved P0 integrity/security issue occurs.
Participant experience
participants can understand the basic experience sufficiently to complete it;
recurring severe confusion is not observed;
participants can provide meaningful feedback.
Evidence
sessions can be associated with their pilot references;
significant events can be reconstructed;
unexpected behaviour is recorded;
incidents are classified.
Operator
the operator can execute the documented workflow;
operational gaps are identified and recorded;
another trained operator could reasonably reproduce the workflow after reviewing the documentation.
## 16. Pilot 0 Exit Review

After the initial cohort, findings should be grouped into:

Pilot blockers
Issues requiring resolution before expansion
Non-blocking improvements
Research/analytical observations
Documentation changes

The team should then decide whether to:

proceed to a larger cohort;
repeat Pilot 0 after targeted corrections; or
pause the pilot for further engineering/review.

The next cohort should not automatically begin merely because the initial participants completed their sessions.

## 17. Expansion Principle

If Pilot 0 completes successfully, expansion should occur progressively rather than immediately jumping to 100–200 participants.

A proposed progression is:

Stage	Approx. participants	Purpose
Pilot 0	5–10	Controlled operational validation
Pilot 1	20–30	Broader real-participant evaluation
Pilot 2	50–100	Expanded operational and exploratory evidence
Extended pilot	100–200+	Larger exploratory dataset if justified

Expansion decisions should be based on evidence from the preceding stage.

Participant count alone should not be treated as evidence of scientific validity.

## 18. Pilot 0 Final Record

At the end of Pilot 0, record:

number of participants recruited;
number who started;
number who completed;
number who withdrew;
number of technical incidents;
number of P0/P1/P2 findings;
major participant feedback themes;
operator observations;
adaptive-routing observations;
evidence-quality issues;
recommended application changes;
recommended documentation changes;
decision regarding expansion.

Status: Draft — pending final operator review before pilot use.
