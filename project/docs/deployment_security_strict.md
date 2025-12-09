# HumanOS Tech — Deployment Security Policy (STRICT INTERNAL VERSION)
Owner: Lead Architect (Jireh Kenneth-Usen)
Audience: Engineering, Security, Compliance
Classification: INTERNAL — CONFIDENTIAL
Last Updated: {{auto-fill on commit}}

---

## 1. Purpose

This policy defines strict security requirements for all HumanOS deployments across:
- development
- staging
- production
- hotfix environments

It ensures confidentiality, integrity, and availability of systems used by minors and institutions.

---

## 2. Scope

This policy covers:

- deployment pipelines
- Gunicorn / Flask app configuration
- environment variables & secrets
- admin token management
- access control for deployers
- rollback & recovery
- monitoring requirements
- security checks before each release

---

## 3. Deployment Roles & Permissions

### 3.1 Authorized Deployers
Only the following may deploy to production:

- Lead Architect (Jireh Kenneth-Usen)
- Approved future DevOps engineer
- Approved security lead (future role)

No one else can trigger a production deployment.

### 3.2 Required Tools
- SSH key with passphrase
- MFA-enabled GitHub account
- Production encryption keys (restricted)

---

## 4. Deployment Preconditions (Mandatory)

Before ANY deployment:

1. **Run full test suite**
   - All API endpoints must pass
   - Behavioral tasks tested
   - No regressions in consent or retention flows

2. **Security checks**
   - No debug mode
   - No exposed secrets
   - TLS required (production)
   - Rate limits enabled
   - Honeypot routes enabled

3. **Compliance checks**
   - No new data category added
   - No change affecting minors without DPIA review
   - Data retention windows unchanged unless approved

4. **Admin Token Rotation (Mandatory Every 30 Days)**
   - New token generated
   - Stored securely as environment variable
   - Logged to audit system (token value redacted)

5. **Version Tagging**
   - Git tag vX.Y.Z created
   - CHANGELOG updated

---

## 5. Deployment Process

### 5.1 Standard Deployment
1. Merge approved PR to `main` (future process)
2. Create release tag
3. SSH into server / or CI pipeline triggers deploy
4. Pull latest code
5. Restart Gunicorn safely
6. Run smoke tests:
   - `/status`
   - `/start_session`
   - `/submit_result`
   - admin routes (with token)

### 5.2 No Downtime Rule
Deployments must:
- restart workers gradually
- ensure at least one worker remains active
- never reset participant sessions

---

## 6. Secret Management

- Environment variables stored ONLY in `.env` (never committed)
- Admin tokens stored in env only
- Server secrets rotated every 90 days
- Use `chmod 600` for sensitive files
- SSH keys must have passphrases

---

## 7. Rollback Policy

Rollback must happen IMMEDIATELY if:

- fairness issues detected
- wrong difficulty progression
- tasks serve incorrect data
- any privacy issue occurs
- server is unstable

Rollback window:
**10 minutes from detection**.

Rollback steps:
1. Checkout previous stable tag
2. Restart Gunicorn
3. Log event to `/audit_logs/deployment_events.jsonl`
4. Open a Post-Incident Review within 24 hours

---

## 8. Post-Deployment Monitoring

Within first 24 hours:
- Monitor logs for anomalies
- Watch rate-limit spikes
- Review honeypot triggers
- Confirm correct retention behavior

---

## 9. Enforcement

Violations may result in:
- immediate rollback
- temporary loss of deployment privileges
- additional reviews
- internal investigation

---

**End of STRICT VERSION**

