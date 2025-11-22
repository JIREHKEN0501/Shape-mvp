# Data Protection Impact Assessment (DPIA)
**Project:** Cognitive & Behavioral Analytics System MVP  
**Version:** 1.0  
**Date:** 2025-10-30  
**Owner:** Jireh Kenneth-Usen  
**Repository:** shape-mvp  

---

## 1. Purpose and Description
This project is a cognitive-behavioral analytics web application designed to assess and improve user learning, problem-solving, and behavioral progression through structured mental exercises.  

The system captures limited interaction data (task responses, timestamps, pseudonymous identifiers) to infer cognitive and behavioral patterns while preserving user privacy.  

No biometric, personal identifying, or sensitive demographic data is collected.

---

## 2. Scope of Processing
| Data Category | Example Fields | Purpose | Retention |
|----------------|----------------|----------|------------|
| Consent Records | participant_id, timestamp, ip_hash | Record user agreement | 2 years |
| Behavioral Data | task_id, answer_hash, result, timestamps | Cognitive performance analysis | 2 years |
| Audit Logs | actor, action, timestamp | Compliance trail | 2 years |
| Backups | timestamped data_log.jsonl.bak | Disaster recovery | 30 days |

---

## 3. Data Flow Summary
1. Participant accesses system and provides informed consent.  
2. A pseudonymous ID is assigned (`UUID4`).  
3. User task interactions are logged (hashed answers, results).  
4. Data is stored locally under `logs/`.  
5. Participant may export or erase data at any time.  
6. Admin actions are logged in append-only `audit_log.jsonl`.

---

## 4. Lawful Basis for Processing
- **Consent:** Users must explicitly consent before data capture begins.  
- **Legitimate Interest:** Behavioral analytics for educational and cognitive development.  
- **Right to Withdraw:** Accessible `/erase` endpoint to anonymize data.  

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|-------|-------------|---------|-------------|
| Unauthorized access to logs | Medium | High | Role-based access, admin token, encryption-at-rest planned |
| Loss of data integrity | Low | Medium | Versioned backups and append-only logs |
| Model bias / unfair outcomes | Medium | Medium | Human-in-loop validation and testing dataset diversity |
| User re-identification | Low | High | Pseudonymization, hashed answers, no PII collected |

---

## 6. Residual Risk Evaluation
Residual risks are considered **low**, with active mitigations in place for access control, logging, and anonymization.

---

## 7. Data Subject Rights and Controls
- **Right to access:** `/export/<participant_id>`  
- **Right to erasure:** `/erase` (cookie or token-based)  
- **Right to withdraw consent:** `/erase` endpoint  
- **Transparency:** `model_card.md` and `/metadata` route (planned)

---

## 8. Review and Updates
- Reviewed before each new model version or dataset expansion  
- DPIA versioned in Git for traceability  
- Next review due: **January 2026**

---

## 9. Approvals
| Role | Name | Signature | Date |
|-------|------|------------|------|
| Data Controller | Jireh Kenneth-Usen | — | 2025-10-30 |
| Project Lead | Jireh Kenneth-Usen | — | 2025-10-30 |

