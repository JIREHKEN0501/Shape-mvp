# Operational Boundaries & Escalation Policy

## Purpose
This document defines conditions under which the system must:
- Limit output
- Reduce confidence
- Escalate to human review
- Halt interpretation entirely

These rules exist to prevent misuse, overreach, and harm.

---

## Automatic Limitation Conditions

The system MUST limit or soften outputs when:

- Total task attempts < 5
- Only one category is represented
- Sessions are clustered within a short time window
- Confidence score < 0.4
- Data sufficiency = false

In these cases:
- Confidence level must be "low" or "unknown"
- Industry lenses must include cautionary language
- No strengths/weaknesses framing should be definitive

---

## Human Escalation Triggers

The system MUST recommend human review when:

- Accuracy drops >30% between sessions
- Latency increases sharply across attempts
- Behavioral volatility exceeds baseline thresholds
- Outputs are requested for hiring, diagnosis, or risk prediction

---

## Explicit Non-Use Cases

This system MUST NOT be used for:

- Medical diagnosis
- Mental health assessment
- Hiring/firing decisions
- Security risk prediction
- Legal judgments
- Predicting intent, character, or future behavior

---

## Kill Switch Conditions

The system should be paused or disabled if:

- Logs show repeated misuse patterns
- Outputs are being used without human oversight
- Regulatory requirements change
- Model drift is detected without mitigation

---

## Responsibility Statement

This system supports decision-making.
It does not replace human judgment.

