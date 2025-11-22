# Model Card: Cognitive-Behavioral Assessment Engine
**Version:** 1.0  
**Date:** 2025-10-30  
**Maintainer:** Jireh Kenneth-Usen  
**Repository:** shape-mvp  

---

## 1. Model Overview
This prototype evaluates behavioral and cognitive task performance through simple sequence and reasoning exercises. It is designed for research and educational purposes.

### Intended Use
- Cognitive training and assessment research  
- UX testing for learning feedback systems  
- Behavioral data simulation for future AI model development  

### Not Intended For
- Medical diagnosis  
- Employment or credit screening  
- Psychological or clinical evaluations  

---

## 2. Data and Features
| Data Input | Description | Processing |
|-------------|--------------|-------------|
| `answer_hash` | SHA256 hash of user response | Prevents raw data storage |
| `result` | Correct or incorrect | Used for behavioral scoring |
| `timestamp` | UTC ISO time | Used for time-to-response metrics |
| `participant_id` | UUID (pseudonymized) | Session linkage only |

No personal identifiers or biometric features are collected.

---

## 3. Model Architecture (Planned)
- Rules-based evaluation (current MVP)  
- Probabilistic learning model (planned phase 2)  
- Emotional and hesitation scoring (phase 3)  
- Federated analytics (long-term privacy design)

---

## 4. Metrics (Current)
| Metric | Description | Example Value |
|---------|--------------|----------------|
| Task Accuracy | Correct answers / total tasks | 80% |
| Response Time | Average completion time per task | 4.2 seconds |
| Retry Count | Number of attempts before correct | 1.3 avg |
| Consent Rate | % of users who accept consent | 100% (demo) |

---

## 5. Ethical Considerations
- User agency: explicit consent and opt-out available  
- Transparency: model purpose, data flow, and rights documented  
- Privacy: no raw answers or identities stored  
- Bias monitoring: qualitative checks on difficulty balance  

---

## 6. Limitations
- Limited dataset size (MVP demo)  
- No demographic normalization yet  
- No bias calibration model implemented  
- Local file storage (no encrypted DB yet)

---

## 7. Maintenance Plan
- Add automated model_card update check in CI/CD  
- Maintain version logs for each deployed model  
- Re-run validation after each new cognitive module added  

---

## 8. Contact
**Project Lead:** Jireh Kenneth-Usen  
**Email:** jirehkenneth2001@gmail.com  
**Location:** Lagos, Nigeria  
**License:** Research-only, internal prototype use.

