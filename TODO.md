# Very important TODOs for the cognitive-behavioral analytics project

- [ ] 1. Consent & Onboarding
  - [ ] Implement explicit consent flow before any data capture.
  - [ ] Record consent records (participant_id, timestamp, consent_version, ip_hash).
  - [ ] Provide clear privacy notice with retention, purpose, contact, and opt-out.

- [ ] 2. Data Minimization & Pseudonymization
  - [ ] Only collect necessary fields; avoid storing PII.
  - [ ] Replace identifiers with `participant_id` and store mapping in encrypted store.
  - [ ] Hash or redact sensitive free text entries.

- [ ] 3. DPIA & Risk Register
  - [ ] Create `DPIA.md` listing data types, purposes, risks, mitigations, residual risk, sign-off.
  - [ ] Update before major pilot or public testing.

- [ ] 4. Security Controls
  - [ ] TLS (HTTPS).
  - [ ] Encryption at rest for sensitive fields.
  - [ ] RBAC for admin/research roles; strong password policies.
  - [ ] Regular backups and secure key management.

- [ ] 5. Logging & Audit Trail
  - [ ] Append-only logs for consent, data exports, erasures, model changes.
  - [ ] Include who/when/what in logs; store logs in protected location.

- [ ] 6. Retention & Deletion Policy
  - [ ] Define retention windows (e.g., raw identifiers 30 days; anonymized metrics 2 years).
  - [ ] Implement automatic purge procedures and deletion endpoints.

- [ ] 7. Data Subject Rights Endpoints
  - [ ] /export to provide user data (JSON).
  - [ ] /erase to anonymize/purge identifiable data.
  - [ ] /withdraw to stop future collection.

- [ ] 8. Model Governance & Documentation
  - [ ] Maintain `model_card.md` per model version (purpose, data, metrics, limitations).
  - [ ] Version control for models and dataset snapshots.
  - [ ] CI check ensuring `model_card.md` exists before deploy.
- [ ] 9. Bias, Testing & Human-in-the-loop
  - [ ] Run bias/robustness tests; maintain test dataset and unit tests.
  - [ ] Add human review workflow for high-risk model outputs.

- [ ] 10. Monitoring & Incident Response
  - [ ] Monitoring for performance drift, anomalous predictions, data leaks.
  - [ ] IR plan with contact list, timeline, and notification templates.

- [ ] 11. Third-party Processors & Contracts
  - [ ] Inventory of external services and data they access.
  - [ ] Processor agreements and assessed risk levels.

- [ ] 12. UX & Consent Clarity
  - [ ] Make consent language simple and actionable.
  - [ ] Provide visible control for participants to pause or opt-out.
 [ ] 13. Privacy-preserving Analytics
  - [ ] Aggregate/anonymize metrics before analytics or export.
  - [ ] Consider differential privacy / k-anonymity for shared outputs.

- [ ] 14. CI/CD & Deployment Safety Checks
  - [ ] Pre-deploy checks: no PII in artifact, `model_card.md` present, security scan passed.
  - [ ] Staging environment with synthetic/test data.

- [ ] 15. Documentation & Training
  - [ ] Maintain README, `DPIA.md`, `model_card.md`, `incident_runbook.md` in repo.
  - [ ] Training for team on data handling and IR procedures.

- [ ] 16. Legal & Regulatory Review
  - [ ] Confirm applicability of NDPR and other regional laws; document legal basis.
  - [ ] Keep evidence of legal review and sign-offs.
- [ ] 17. Ethics Oversight
  - [ ] Setup small ethics review board or checklist for experiments with participants.
  - [ ] Pre-register studies where applicable.

- [ ] 18. Minimal Viable Compliance Tasks (first sprint)
  - [ ] Consent modal + consent_log writer.
  - [ ] Pseudonymize IDs on write.
  - [ ] Basic /erase and /export endpoints.
  - [ ] `DPIA.md` and `model_card.md` templates.

- [ ] 19. Backup & Recovery
  - [ ] Encrypted backups, tested restores, and documented RTO/RPO.

- [ ] 20. Budget & Resource Notes
  - [ ] Estimate cloud costs, encryption key management, and legal/ethical review time.

## PHASE 2 — Compliance & Transparency (COMPLETED)
**Completed:** 2025-10-30

Summary:
- Implemented explicit consent flow and recorded consent logs (consent_log.jsonl).
- Implemented pseudonymization (participant UUIDs) and hashed answer storage.
- Added append-only behavioral data logs (data_log.jsonl).
- Built audit trail (audit_log.jsonl) that records consent, submissions, exports, erasures, and admin deletes.
- Implemented participant data rights:
  - Export endpoint (/export/<participant_id>) — admin or participant via cookie.
  - Erase endpoint (/erase) — participant-initiated anonymization (erased_ token).
  - Admin permanent delete with backups (/admin/delete_participant/<participant_id>).
- Created DPIA.md and model_card.md and linked them to /metadata.
- Added /metadata endpoint (JSON + HTML dashboard) for transparency; it auto-reads DPIA.md and model_card.md and displays a live "Last Review" date.
- Backup and safety: logs are backed up before any destructive operation; admin actions require ADMIN_TOKEN.

Notes & next steps:
- Move logs to an encrypted DB (recommended for production).
- Replace ADMIN_TOKEN header auth with proper RBAC / admin login.
- Add automated retention purge for backups older than X days.
- Phase 3 (Analytics & Insight Dashboard) planned next.

Signed-off-by: Jireh Kenneth-Usen — 2025-10-30
