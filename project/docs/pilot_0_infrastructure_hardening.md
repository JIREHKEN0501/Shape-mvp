# HumanOS Pilot 0 — Infrastructure Hardening Specification

**Status:** PLANNED — pre-provisioning  
**Environment:** Pilot 0  
**Hosting:** Hetzner Cloud  
**Target:** CAX11 ARM64, Falkenstein, Germany  
**OS:** Ubuntu 24.04 LTS  
**Purpose:** Controlled infrastructure preparation before collection of real Pilot 0 participant data

---

## 1. Scope

This document defines the infrastructure hardening and deployment controls required before HumanOS Pilot 0 is exposed to real participants.

It supplements, and does not replace:

- `security_hardening.md`
- `deployment_security_strict.md`
- `deployment_policy_strict.md`
- `backup_recovery.md`
- `DPIA.md`
- `processors.md`

No participant data may be collected until the required controls in this document are verified.

---

## 2. Status Convention

- `PLANNED` — design decision made; not yet implemented
- `TO CONFIGURE` — requires server/account access
- `VERIFIED` — implemented and tested
- `BLOCKED` — cannot proceed until dependency is resolved
- `NOT APPLICABLE` — formally determined not to apply to Pilot 0

---

## 3. Deployment Target

| Control | Pilot 0 value | Status |
|---|---|---|
| Provider | Hetzner Cloud | PLANNED |
| Region | Falkenstein, Germany | PLANNED |
| Server | CAX11 | PLANNED |
| Architecture | ARM64 | PLANNED |
| Operating system | Ubuntu 24.04 LTS | PLANNED |
| Public IPv4 | Required for Pilot 0 | PLANNED |
| Additional volume | Not required initially | PLANNED |
| HumanOS application data | Protected participant data | PLANNED |

---

## 4. Network Firewall

### Required inbound policy

| Port | Protocol | Purpose | Status |
|---|---|---|---|
| 22 | TCP | SSH administration | TO CONFIGURE |
| 80 | TCP | TLS certificate provisioning / HTTP handling if required | TO CONFIGURE |
| 443 | TCP | HumanOS HTTPS | TO CONFIGURE |
| All other inbound | Any | Block | TO CONFIGURE |

Outbound traffic may remain unrestricted initially.

SSH source restriction will be evaluated after the server is provisioned and administrative access has been verified.

---

## 5. SSH Hardening

Required controls:

- Passphrase-protected SSH key.
- Key-based authentication.
- Password authentication disabled.
- Root SSH login disabled.
- Administrative access limited to authorized personnel.
- SSH configuration validated before terminating the initial administrative session.

Status: `TO CONFIGURE`

---

## 6. Host Security

Required controls:

- Ubuntu security updates enabled.
- Automatic security updates configured.
- Time synchronization enabled.
- Unnecessary services disabled.
- Least-privilege administrative access.
- Sensitive configuration files restricted with appropriate filesystem permissions.
- Host security state verified after configuration.

Status: `TO CONFIGURE`

---

## 7. Docker Runtime

Required controls:

- Docker Engine installed from an appropriate trusted source.
- HumanOS image built from the validated repository state.
- Container not run with unnecessary privileges.
- Only required filesystem mounts exposed.
- Participant logs protected from unnecessary host/container access.
- Runtime secrets supplied through environment/runtime configuration.
- Secrets excluded from Git and container images.
- Container restart behavior defined.

Status: `TO CONFIGURE`

---

## 8. TLS / HTTPS

Required controls:

- Public HTTPS endpoint.
- Valid TLS certificate.
- HTTP behavior explicitly configured.
- HTTPS enforced for participant traffic.
- HSTS enabled after HTTPS is verified.
- Required security headers verified.
- TLS configuration tested before participant access.

Status: `TO CONFIGURE`

---

## 9. Secret Management

Required runtime secrets include, as applicable:

- `SECRET_KEY`
- `ADMIN_TOKEN`
- Pilot 0 encryption/backup keys, where applicable.

Requirements:

- Secrets must not be committed to Git.
- Secrets must not be embedded in Docker images.
- Secrets must be supplied at runtime.
- Sensitive secret files, where used, must be restricted with `chmod 600`.
- Secret values must never appear in logs.
- Rotation procedures must be documented.

Status: `TO CONFIGURE`

---

## 10. Application and Participant Data Storage

HumanOS Pilot 0 storage includes participant-linked pseudonymous experimental data.

Required controls:

- Application/log directories owned by the appropriate service account.
- Participant logs not publicly accessible.
- No direct log exposure through the web server.
- Pseudonymous participant identifiers.
- No unnecessary PII.
- Existing participant erasure mechanism preserved.
- At-rest protection implemented before participant data collection.
- Storage permissions verified after deployment.

Status: `TO CONFIGURE`

---

## 11. Backup Strategy

Pilot 0 backups must:

- Be encrypted at rest.
- Include required application and participant-data recovery material.
- Exclude unnecessary caches and virtual environments.
- Have defined retention.
- Have an off-site recovery path.
- Be independently restorable.
- Never contain backup encryption keys inside the backup itself.

Backup automation will not be enabled until the final backup destination and retention configuration have been selected.

Status: `PLANNED`

---

## 12. Recovery and Rollback

Before participant access:

- Exact deployed Git commit recorded.
- Release/version identifier recorded.
- Known-good container image identified.
- Rollback procedure documented.
- Backup restoration procedure available.
- Application health check available.
- Incident recording path available.

Status: `TO CONFIGURE`

---

## 13. Pre-Participant Security Gate

Pilot 0 must not begin until all applicable items below are `VERIFIED`:

- [ ] Hetzner account/DPA governance gate completed
- [ ] Hetzner server billing/account verification completed
- [ ] Server provisioned in intended EU location
- [ ] Firewall configured
- [ ] SSH hardened
- [ ] Automatic security updates enabled
- [ ] Docker installed and validated
- [ ] HumanOS deployed from exact validated commit
- [ ] Runtime secrets configured
- [ ] TLS/HTTPS operational
- [ ] Security headers verified
- [ ] Participant storage permissions verified
- [ ] At-rest protection verified
- [ ] Backup destination selected
- [ ] Encrypted backup tested
- [ ] Restore procedure tested
- [ ] Application smoke tests passed
- [ ] Participant catalog gate passed
- [ ] Admin authentication verified
- [ ] Erasure path verified
- [ ] Pilot 0 operator checklist ready

---

## 14. Deployment Rule

No real participant data may enter the Pilot 0 environment while a mandatory pre-participant security gate remains `PLANNED`, `TO CONFIGURE`, or `BLOCKED`.

---

## 15. Change Control

Infrastructure changes affecting:

- participant data protection
- network exposure
- authentication
- secrets
- storage
- backups
- TLS
- deployment version

must be reviewed and recorded before participant use.

---

## 16. Current State

**Provider account:** Pending payment/verification

**Server:** Not provisioned

**Participant data:** Not present

**Firewall:** Not configured

**SSH hardening:** Not configured

**Automatic security updates:** Not configured on server

**Docker:** Not configured on server

**TLS:** Not configured

**Runtime secrets:** Not configured on server

**Participant storage:** Not configured

**Backups:** Not configured

**Pilot 0 infrastructure status:** PRE-PROVISIONING
