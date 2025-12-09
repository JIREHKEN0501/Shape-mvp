# HumanOS Tech — Admin Access Control & Token Rotation SOP (STRICT INTERNAL VERSION)

Last Updated: {{auto-fill on commit}}
Owner: Lead Architect (Jireh Kenneth-Usen)
Audience: Engineering, Security, DevOps
Classification: INTERNAL — CONFIDENTIAL — DO NOT DISTRIBUTE

---

## 1. Purpose

This SOP defines strict procedures for:

- admin dashboard access
- admin token creation, rotation, expiration
- secure handling of environment secrets
- emergency revocation
- monitoring and audit logging

This ensures compliance with NDPR/GDPR security-by-design and protects against unauthorized access.

---

## 2. Access Control Principles

### 2.1 Least Privilege
- Only the Lead Architect + authorized system maintainers may generate admin tokens.
- Admin privileges MUST NOT be granted to external testers, school staff, or operators.

### 2.2 No Shared Credentials
- Each admin must have an **individual token**.
- Shared or “team tokens” are forbidden.

### 2.3 Zero Trust Boundaries
- Every admin request must include the correct `ADMIN_TOKEN` header.
- Admin endpoints must remain rate-limited and logged.

---

## 3. Admin Token Lifecycle

### 3.1 Creation
Tokens are generated using:

openssl rand -hex 32

The token is then set in:

- `.env` file for local dev
- environment variables for staging/production

### 3.2 Storage Requirements
- Never stored in Git.
- Never logged in plaintext.
- Never shared via email, WhatsApp, SMS, screenshots.
- For production: stored only in secret managers (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault).

### 3.3 Rotation Frequency
- **Every 90 days** or immediately after:
  - staff departure
  - accidental exposure
  - suspicious admin activity
  - endpoint anomalies

### 3.4 Rotation Procedure

1. Generate new token
2. Update environment variables
3. Restart application (or Gunicorn service)
4. Test `/status` with new token
5. Revoke old token
6. Log the rotation event in `audit_log.jsonl`

### 3.5 Expiration Policy
Tokens older than 90 days must be auto-expired with a manual override field.

---

## 4. Admin Dashboard Access Rules

### 4.1 Valid Authentication Required
- Every admin request must include:

X-Admin-Token: <token>

### 4.2 Logging
Each access event logs:

- timestamp
- admin_id (mapped internally)
- endpoint accessed
- IP address (hashed)
- success/failure result

### 4.3 Allowed IP Zones (future hardening)
- Optional: restrict admin access to VPN or known IPs.

---

## 5. Emergency Revocation

Revocation triggers:

- suspected credential leak
- unusual rate-limited events
- brute force attempts
- mismatched token hashes
- admin misuse

Procedure:

1. Remove token from environment
2. Deploy restart
3. Add entry to `audit_log.jsonl`:

{"event":"token_revoked","by":"lead_architect","reason":"<reason>","ts":<timestamp>}

4. Notify all internal stakeholders

---

## 6. Monitoring & Alerting

- Admin access attempts (success/failure) MUST be logged.
- Repeated failed admin access attempts trigger an alert.
- Unusual admin routes or frequent metadata exports should raise warnings.
- Logs must be retained for **24 months** per audit policy.

---

## 7. Compliance Mapping

- **NDPR** — security controls, access restrictions, incident reporting
- **GDPR** — integrity & confidentiality (Art. 32)
- **COPPA/FERPA** — heightened security for minors’ data
- **Internal Governance** — enforce strict roles and traceability

---

## 8. Enforcement

Unauthorized access or mishandling of tokens may result in:

- immediate revocation
- internal investigation
- system lockout pending review
- legal consequences depending on data sensitivity

END OF STRICT VERSION
