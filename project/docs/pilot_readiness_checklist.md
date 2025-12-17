PHASE 8A — PILOT READINESS CHECKLIST
1. System Stability

 App boots cleanly with no traceback errors

 /status returns 200 OK

 /tasks, /tasks/next/<id>, /submit_result tested via curl

 Adaptive task selection returns valid tasks

 No hard crashes on malformed input

 Rate limits active and enforced

2. Data Safety & Compliance

 Consent required before session start

 Participant IDs are pseudonymous

 /export/<participant_id> works

 /erase/<participant_id> works

 Retention policy documented (public + strict)

 No raw PII stored in logs

3. Interpretability & Safety

 Insights are non-diagnostic

 Confidence scoring present

 Industry lenses respect confidence & data sufficiency

 Interpretation boundaries included in summaries

 No deterministic or predictive language in outputs

4. Scope Control

 Pilot users clearly defined (who / where / why)

 Explicit statement: pilot ≠ production

 No automated decisions affecting users

 Human-in-the-loop expectation documented

5. Operational Readiness

 Incident runbook exists

 Backup & recovery documented

 Monitoring checklist present

 Single maintainer (you) clearly defined

 Kill-switch plan exists (disable endpoints if needed)

Status: ⬜ Not Started / ⬜ In Progress / ⬜ Ready
Signed off by: Jireh Kenneth-Usen
Date: ___
