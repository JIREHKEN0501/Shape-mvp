# Governance & Safety Docs (HumanOS Tech MVP)

This folder contains the core governance, safety, and compliance docs for the Shape / HumanOS MVP.

## Data Protection & Privacy

- `DPIA.md` – External-facing DPIA summary for clients and partners.
- `DPIA_summary.md` – Short, human-readable DPIA overview.
- `DPIA_strict.md` – Full internal DPIA with detailed risks and mitigations.

## Model & Analytics Governance

- `model_card.md` – Model Card for the cognitive / behavioral analytics engine.
- `TODO.md` – Compliance and engineering backlog items (privacy, safety, infra).

## Security & Incident Handling

- `incident_runbook.md` – Incident Response Runbook (strict internal version).
- `backup_logs.sh` – Helper script for rotating and backing up logs (ops tool).

## How this is used

- For pilots with **schools** or **companies**, share:
  - `DPIA.md` and `DPIA_summary.md` as part of the onboarding pack.
- Keep `DPIA_strict.md`, `incident_runbook.md`, and `model_card.md`
  as **internal** docs that you can show under NDA if needed.

Future additions:
- `privacy_notice.md` – public-facing privacy / consent notice.
- `consent_flow.md` – UX flow for informed consent (adults + parents/guardians).

