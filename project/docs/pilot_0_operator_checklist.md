---

# HumanOS Pilot 0 — Operator Checklist

**Protocol:** Pilot 0 — Controlled Pilot
**Application freeze:** `eaa6fe7`
**Validation evidence:** `8333802`
**Operator:** __________________
**Pilot date:** __________________
**Participant code:** __________________

---

## 1. Before the Participant Arrives

### Environment

* [ ] Confirm the application is running.
* [ ] Confirm `/status` returns HTTP 200.
* [ ] Confirm the expected application version is running.
* [ ] Confirm no unplanned application changes have been made since the frozen build.
* [ ] Confirm the participant-facing task catalog is available.
* [ ] Confirm the operator has access to the required administrative/monitoring surface.
* [ ] Confirm the observation log is ready.
* [ ] Assign a non-identifying pilot code.

**Pilot code:** __________________

### Operator readiness

* [ ] Do not provide answers or reasoning for cognitive tasks.
* [ ] Be prepared to record unexpected behaviour rather than immediately fixing it.
* [ ] Know the withdrawal/erasure procedure.
* [ ] Know how to record a P0, P1, P2, or Observation.
* [ ] Keep participant contact information separate from analytical evidence.

---

## 2. Participant Briefing

Before beginning:

* [ ] Explain the purpose of the pilot in appropriate participant-facing language.
* [ ] Explain what the participant will be asked to do.
* [ ] Explain that participation is voluntary.
* [ ] Explain the relevant data collection/privacy information.
* [ ] Explain that adaptive routing may change task sequence or difficulty.
* [ ] Explain how to report technical problems.
* [ ] Explain how withdrawal works.
* [ ] Confirm the participant has an opportunity to ask questions about the pilot itself.

Do **not**:

* [ ] reveal answers;
* [ ] explain how a cognitive task should be solved;
* [ ] suggest which response is expected;
* [ ] influence the participant's task strategy.

---

## 3. Consent

* [ ] Participant completes the consent flow.
* [ ] Confirm consent was successfully recorded.
* [ ] Do not proceed if consent has not been established.
* [ ] Record any consent-related problem in the observation log.

**Consent:**

* [ ] Confirmed
* [ ] Issue

---

## 4. Experience Creation

* [ ] Create the participant's experience using the documented flow.
* [ ] Confirm the experience is associated with the correct participant/session context.
* [ ] Do not manually alter participant state to bypass normal progression.
* [ ] Record any unexpected creation or session behaviour.

---

## 5. Adaptive Authorization

* [ ] Participant is presented with the adaptive authorization flow.
* [ ] Participant explicitly authorizes adaptive participation.
* [ ] Confirm authorization was successfully recorded.
* [ ] Do not silently enable adaptive routing.
* [ ] Do not proceed with adaptive participation if required authorization is absent.

**Adaptive authorization:**

* [ ] Confirmed
* [ ] Issue

---

## 6. During the Experience

### Participant behaviour

Observe without coaching.

Record:

* [ ] instruction confusion;
* [ ] navigation confusion;
* [ ] repeated requests for clarification;
* [ ] unexpected difficulty;
* [ ] frustration or disengagement;
* [ ] unexpected task interpretation;
* [ ] other notable participant feedback.

These are observations about the experience, not diagnoses of the participant.

### System behaviour

Watch for:

* [ ] expected task presented;
* [ ] canonical progression maintained;
* [ ] adaptive routing activated as expected;
* [ ] correct task difficulty/sequence behaviour;
* [ ] rejected submissions handled correctly;
* [ ] unexpected HTTP/application errors;
* [ ] session or ownership problems;
* [ ] unexpected latency;
* [ ] unexpected task content;
* [ ] other anomalies.

---

## 7. If Something Goes Wrong

**Do not immediately modify the application.**

First:

1. [ ] Observe what happened.
2. [ ] Record the participant code.
3. [ ] Record the task/session context.
4. [ ] Record the visible error or behaviour.
5. [ ] Determine whether the participant can safely continue.
6. [ ] Classify the issue.

### P0 — Pilot blocker

Examples:

* participant/data isolation failure;
* consent bypass;
* serious authorization failure;
* material data leakage;
* unrecoverable session integrity problem.

Action:

* [ ] Stop affected pilot activity.
* [ ] Preserve evidence.
* [ ] Record the incident.
* [ ] Do not continue as though the problem did not occur.

### P1 — Significant issue

Action:

* [ ] Record the issue.
* [ ] Determine whether the current session can safely continue.
* [ ] Flag for review before cohort expansion.

### P2 — Improvement

Action:

* [ ] Record the issue.
* [ ] Continue if the participant experience remains valid.
* [ ] Add to post-pilot improvement list.

### Observation

Action:

* [ ] Record without immediately treating it as a defect.
* [ ] Continue if appropriate.
* [ ] Review after the pilot.

---

## 8. Operator Intervention

If technical assistance is required:

* [ ] Record what happened.
* [ ] Record why intervention was necessary.
* [ ] Record what assistance was provided.
* [ ] Do not provide cognitive/task assistance.
* [ ] Note whether the intervention may have affected the session.

**Intervention required:**

* [ ] No
* [ ] Yes

**Description:**

---

---

---

## 9. Participant Withdrawal

If the participant chooses to withdraw:

* [ ] Stop further participant activity.
* [ ] Record the withdrawal event.
* [ ] Follow the documented withdrawal/erasure procedure.
* [ ] Verify that participant-linked records were handled appropriately.
* [ ] Record completion of the procedure.
* [ ] Do not manually delete individual log lines unless the approved procedure requires it.

**Withdrawal:**

* [ ] No
* [ ] Yes

---

## 10. Session Completion

When the participant completes the experience:

* [ ] Confirm the expected completion state.
* [ ] Record whether all intended tasks were completed.
* [ ] Record any rejected submissions.
* [ ] Record notable adaptive-routing events.
* [ ] Record technical incidents.
* [ ] Confirm there is no unresolved pilot-blocking issue.
* [ ] Obtain participant feedback.

---

## 11. Participant Feedback

Ask the participant for practical feedback about the experience.

Suggested questions:

1. What was clear?
2. What was confusing?
3. Was anything unexpectedly difficult?
4. Did anything feel repetitive or unclear?
5. Did the instructions make sense?
6. Did the experience behave differently from what you expected?
7. Did you encounter any technical problems?
8. Is there anything you would change?

Record the participant's feedback without turning it into a psychological interpretation.

---

## 12. Post-Session Record

Complete the participant record:

| Field                         | Result |
| ----------------------------- | ------ |
| Pilot code                    |        |
| Consent                       |        |
| Adaptive authorization        |        |
| Session completed             |        |
| Tasks completed               |        |
| Rejections                    |        |
| Routing anomalies             |        |
| Technical incidents           |        |
| Participant feedback captured |        |
| Operator intervention         |        |
| Withdrawal                    |        |
| P0/P1/P2 findings             |        |
| Follow-up required            |        |

---

## 13. End-of-Day Operator Review

After all participants scheduled for the day:

* [ ] Count participants recruited.
* [ ] Count participants who started.
* [ ] Count participants who completed.
* [ ] Count withdrawals.
* [ ] Review technical incidents.
* [ ] Review P0/P1/P2 findings.
* [ ] Review recurring participant confusion.
* [ ] Review adaptive-routing observations.
* [ ] Review evidence-quality problems.
* [ ] Review operator documentation gaps.
* [ ] Do not make application changes solely because an observation was interesting.
* [ ] Preserve the pilot evidence.

### End-of-day disposition

**Pilot status:**

* [ ] Continue Pilot 0
* [ ] Pause for review
* [ ] Repeat controlled testing
* [ ] Prepare for expansion
* [ ] Escalate P0/P1 issue

**Operator notes:**

---

---

---

---

## 14. Core Operator Rule

> **Observe first. Record second. Classify third. Change the system only after review.**

The purpose of Pilot 0 is not to demonstrate that nothing unexpected happens.

The purpose is to discover what happens when real people interact with the frozen system.

---

**Checklist version:** 0.1
**Status:** Draft for Pilot 0 use.
