# Production Hardening Gap Review — PraxisMed

**Date:** 2026-07-05
**Sprint:** Sprint 17 / Module 119
**Result:** PRODUCTION PHI NO-GO — hardening gaps block production use

---

## 1. Purpose

This document inventories every production hardening gap that blocks real clinic/PHI
production use, ranks gaps by severity, and defines the safest implementation order.

**Based on:**
- Architecture Checkpoint 16 (fake-data staging core PASS — Module 118B)
- Code inspection: `backend/app/api/routes/auth.py`, `frontend/lib/auth.ts`, `frontend/lib/api.ts`
- Existing planning docs: `PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md`, `ENVIRONMENT_AND_SECRETS_CONTRACT.md`, `AUTH_SESSION_HARDENING_IMPLEMENTATION_PLAN.md`

**What this document is:**
- A ranked gap inventory with severity, current state, risk, and recommended module
- An ordered implementation plan for closing gaps before production PHI use
- An explicit production NO-GO statement with conditions

**What this document is not:**
- An implementation guide — no code is changed in this module
- A production deployment plan
- A fabricated readiness claim — no gap is closed until evidence exists

Staging uses fake/non-PHI data only. No production secrets recorded. No real patient data.

---

## 2. Current Result

**PRODUCTION PHI NO-GO**

The fake-data staging core loop is PASS (Architecture Checkpoint 16). The system is
architecturally sound and deployable with fake data. Production PHI use is blocked until
the critical gaps in Section 4 are closed.

### What is already proven in fake-data staging

| Item | Status |
|---|---|
| Railway backend (HTTPS; health endpoints; machine auth; DB write) | **PASS** |
| Railway PostgreSQL (migrated schema; asyncpg pool; 4 tables; stable) | **PASS** |
| Vercel frontend (Next.js build; HTTPS; login page; protected dashboard) | **PASS** |
| browser login (POST /auth/login → JWT; CORS; sessionStorage; dashboard renders) | **PASS** |
| Vapi appointment capture (tool call → DB row; status=new; action_required=True) | **PASS** |
| staff Confirm (dashboard Confirm button → status=confirmed; no auto-confirm) | **PASS** |

These prove the system architecture is correct. They do not prove production readiness.

---

## 3. What Remains Unproven for Production

The following are confirmed NOT PROVEN against real production conditions:

- httpOnly Secure cookie session (auth/session hardening not implemented)
- token storage security (sessionStorage is XSS-accessible; explicitly flagged in code)
- production secrets rotation (staging secrets must never be used in production)
- PHI logging and redaction policy (raw_payload columns may capture PHI; no policy enforced)
- tenant isolation assurance (code review of multi-tenant data access not completed)
- audit log completeness and access controls for production
- backups and restore strategy for production PostgreSQL
- incident response and rollback plan for production
- monitoring, alerting, and uptime visibility
- rate limiting and abuse protection on auth and API endpoints
- CORS/domain finalization (custom production domain not registered)
- error handling and user-safe failures (no production error boundaries)
- n8n staging workflow (n8n staging is PENDING/DEFERRED)
- real clinic onboarding flow and admin controls

---

## 4. Production Blockers — Ranked by Severity

### Critical (BLOCKS production PHI use — must be resolved first)

---

#### C1 — Auth/session hardening (httpOnly Secure SameSite cookie)

**Why it matters:** `sessionStorage` is readable by any JavaScript on the same origin.
A successful XSS attack can steal the JWT and impersonate clinic staff for up to 60
minutes. The code already flags this: `frontend/lib/auth.ts` comment (lines 3–5):
*"Token storage uses sessionStorage (local development only). For production: replace
with httpOnly cookies set by the backend /auth/session endpoint."*

**Current status:** `sessionStorage` only. No httpOnly cookie. No CSP. No `/auth/logout`
route. No `/auth/refresh` route. Token expiry is 60 minutes with no auto-renewal.

**Risk if ignored:** JWT theft via XSS → attacker impersonates clinic staff → accesses
PHI for up to 60 minutes per stolen token. Unacceptable for any PHI-bearing system.

**Recommended module:** Module 120 — Auth/session hardening implementation

---

#### C2 — Token storage / session model

**Why it matters:** The current token storage model (`sessionStorage`, Bearer header,
client-side auth guard) is documented as local-dev only. No server-side session
invalidation exists. Logout only clears `sessionStorage`; the JWT remains valid until
expiry. There is no `POST /auth/logout` endpoint to invalidate server-side state.

**Current status:** Client-side only. No logout endpoint. No token revocation. No session
table. No `/auth/refresh`. 60-minute token lifetime with no renewal path.

**Risk if ignored:** Staff "logout" does not invalidate the JWT. A token intercepted after
logout remains usable. Long-lived credentials with no server-side revocation path.

**Recommended module:** Module 120 — Auth/session hardening implementation

---

#### C3 — Production secrets rotation and review

**Why it matters:** Staging uses freshly generated secrets scoped to the staging
environment. Production must use separate, independently generated secrets. Using staging
secrets in production creates cross-environment credential risk.

**Current status:** Staging secrets exist on Railway. Production env var values for
`JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`,
`DATABASE_URL` are not generated or stored. No rotation policy defined. No secrets
manager in use.

**Risk if ignored:** Staging secret exposure or rotation invalidates production auth.
Cross-environment credential reuse. No rotation path for compromised secrets.

**Recommended module:** Module 121 — Secrets and environment hardening review

---

#### C4 — PHI logging and redaction policy

**Why it matters:** The `appointment_requests` table has a `raw_payload` column that
stores the raw Vapi tool call body. In production, this payload may contain patient names,
phone numbers, or health-related call transcripts — all potentially PHI. No log redaction
policy or structured audit access control exists.

**Current status:** `raw_payload` stored without redaction. Railway log stream may capture
request/response bodies containing PHI. No PHI logging policy. No field-level encryption.
No structured access log for PHI fields.

**Risk if ignored:** Patient data (names, phone numbers, health context) logged in Railway
log stream or stored in `raw_payload` without access control. GDPR/HIPAA violation risk.

**Recommended module:** Module 122 — PHI logging/redaction and audit hardening

---

#### C5 — Tenant isolation assurance

**Why it matters:** PraxisMed is multi-tenant: each clinic's data must be strictly
isolated. Every data access path must be audited to confirm that `clinic_id` scoping is
enforced at the DB query level, not only at the route level.

**Current status:** `clinic_id` is present in all tables and included in most queries.
No formal tenant isolation audit has been performed. No automated test verifies that
cross-tenant data access is blocked.

**Risk if ignored:** A bug in any query could return data from the wrong clinic. In a
PHI context, this is a serious breach. Multi-tenant isolation must be verified, not
assumed.

**Recommended module:** Module 123 — Tenant isolation and access-control verification

---

#### C6 — Audit log completeness and compliance review

**Why it matters:** The `audit_log` table exists but no formal audit policy defines what
events must be logged, retention periods, or who can access audit records. GDPR Article
30 (records of processing) and similar compliance frameworks require documented audit
capability.

**Current status:** `audit_log` table in schema. No defined audit events. No access
control for audit read. No retention policy. No compliance framework review completed.

**Risk if ignored:** Inability to demonstrate audit capability to regulators or clinic
operators. Non-compliance with GDPR/HIPAA audit requirements.

**Recommended module:** Module 122 — PHI logging/redaction and audit hardening

---

#### C7 — Backups and restore strategy

**Why it matters:** Production PostgreSQL (patient data, appointment records) must have
automated backups and a tested restore path. A DB failure without a restore strategy
means permanent data loss.

**Current status:** Railway PostgreSQL offers managed backups (configuration not
verified). No backup schedule confirmed. No restore runbook. No recovery time objective
(RTO) or recovery point objective (RPO) defined.

**Risk if ignored:** Permanent data loss on DB failure or accidental deletion. No path
to recover patient appointment records.

**Recommended module:** Module 124 — Backup/restore and rollback runbook

---

#### C8 — Incident response and rollback plan

**Why it matters:** A production deployment needs a documented rollback path: how to
revert to the previous Railway deployment, roll back a migration (`alembic downgrade`),
and restore from backup. Without this, an incident cannot be resolved systematically.

**Current status:** `alembic downgrade -1` command known. Railway service restart known.
No documented incident response runbook. No on-call definition. No escalation path.

**Risk if ignored:** An incident (bad deploy, data corruption, outage) cannot be resolved
methodically. Extended downtime for a clinic disrupts patient care.

**Recommended module:** Module 124 — Backup/restore and rollback runbook

---

### High (blocks production quality — must be resolved before clinic launch)

---

#### H1 — Monitoring, alerts, and uptime visibility

**Why it matters:** No production uptime monitoring. No error alerting. No Railway log
stream sanitization verified. A backend crash or DB outage is invisible until a clinic
staff member reports it.

**Current status:** Railway health endpoint exists (`/health`, `/health/ready`). No
external monitoring configured. No alert routing. No log-based error detection.

**Recommended module:** Module 125 — Monitoring/alerts/rate-limit plan

---

#### H2 — Rate limiting and abuse protection

**Why it matters:** `POST /auth/login` has no rate limiting. An attacker can run
credential-stuffing attacks against the login endpoint. API endpoints have no request
rate caps.

**Current status:** No rate limiting middleware. No IP-based or email-based throttle on
`/auth/login`. FastAPI default — unlimited concurrent requests.

**Recommended module:** Module 125 — Monitoring/alerts/rate-limit plan

---

#### H3 — CORS/domain finalization

**Why it matters:** Staging uses `https://praximed.vercel.app` and
`https://web-production-fd91d.up.railway.app` — provider default URLs. Production
requires a registered custom domain with HTTPS, stable `FRONTEND_CORS_ORIGINS`,
and `NEXT_PUBLIC_API_BASE_URL` set to the production backend URL.

**Current status:** No production domain registered. Vercel/Railway default URLs only.
`FRONTEND_CORS_ORIGINS` is not set to a production domain.

**Recommended module:** Module 125 — Monitoring/alerts/rate-limit plan (domain
finalization can be included or split into its own module)

---

#### H4 — Error handling and user-safe failures

**Why it matters:** Production users (clinic staff) must see safe, actionable error
messages — not stack traces or internal error details. Currently, some FastAPI exception
handlers return raw detail strings.

**Current status:** FastAPI default exception handlers. No structured error response
format for the frontend. No production error boundaries in Next.js frontend.

**Recommended module:** Module 125 or a dedicated error-handling module

---

### Medium (important for launch quality — address after critical/high)

---

#### M1 — n8n staging workflow

**Why it matters:** n8n is the calendar sync integration. It was PENDING/DEFERRED at
Architecture Checkpoint 16. If clinic calendar sync is in the demo scope, n8n staging
must be configured and tested.

**Current status:** n8n staging is PENDING/DEFERRED. n8n production is NOT PROVEN.

**Recommended module:** Module 126 — n8n staging workflow, if still needed

---

#### M2 — Custom domain and email branding

**Why it matters:** Production clinic use requires a stable, branded domain. Provider
default URLs are not acceptable for patient-facing or clinic-facing communications.

**Current status:** No production domain registered. Vercel/Railway default URLs.

**Recommended module:** Infrastructure task — coordinate with domain registration

---

#### M3 — Clinic onboarding documentation and admin controls

**Why it matters:** Real clinic onboarding requires a reproducible provisioning process
for new clinics and users. The current provisioning process (Railway console SQL) is
manual and fragile.

**Current status:** Manual Railway console SQL for clinic/user provisioning. No admin
UI. No onboarding runbook for new clinics.

**Recommended module:** Module 127+ or separate admin sprint

---

#### M4 — UI/UX polish

**Why it matters:** The current dashboard is functional but minimal. A premium
doctor-facing UI (Fabel 5 or equivalent) is deferred pending production hardening.

**Current status:** Deferred. Not in scope until critical/high gaps are closed.

**Recommended module:** Separate UX sprint (post-hardening)

---

## 5. Recommended Implementation Order

| Module | Title | Resolves | Priority |
|---|---|---|---|
| **Module 120** | Auth/session hardening implementation | C1, C2 | CRITICAL |
| **Module 121** | Secrets and environment hardening review | C3 | CRITICAL |
| **Module 122** | PHI logging/redaction and audit hardening | C4, C6 | CRITICAL |
| **Module 123** | Tenant isolation and access-control verification | C5 | CRITICAL |
| **Module 124** | Backup/restore and rollback runbook | C7, C8 | CRITICAL |
| **Module 125** | Monitoring/alerts/rate-limit plan | H1, H2, H3, H4 | HIGH |
| **Module 126** | n8n staging workflow, if still needed | M1 | MEDIUM |

Modules 120–124 must all be complete before any real clinic or PHI use. Modules 125–126
can overlap with Module 120–124 work but must be complete before public production launch.

---

## 6. Explicit Production NO-GO Conditions

The following must be true before **any** real clinic use, PHI access, or public launch:

| Condition | Status |
|---|---|
| No real patient data in any staging environment row, log, or Vapi call | **CONFIRMED for staging** |
| No real clinic calls routed through staging backend | **CONFIRMED — staging is fake data only** |
| No PHI accessible through the current sessionStorage auth | **CONFIRMED — no real PHI in staging** |
| No public production launch until critical blockers C1–C8 are closed | **ENFORCED** |

**Production PHI readiness is NO-GO until all critical blockers (C1–C8) are resolved.**

---

## 7. Recommended Next Module

**Sprint 17 / Module 120 — Auth/session hardening implementation**

Module 120 should:
- Inspect the current auth/session model in full detail (`frontend/lib/auth.ts`,
  `frontend/lib/api.ts`, `backend/app/api/routes/auth.py`,
  `backend/app/api/dependencies/current_user.py`)
- Identify token storage risks and the concrete changes required
- Propose and implement the httpOnly Secure SameSite cookie strategy (Option B from
  `PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md` Section 6)
- Add `POST /auth/logout` route
- Update frontend to use `credentials: "include"` instead of `Authorization` Bearer header injection
- Full test suite must pass after implementation

---

## 8. Safety Constraints

All of the following hold throughout this review:

| Constraint | Status |
|---|---|
| No secrets recorded (JWT_SECRET_KEY, VAPI_WEBHOOK_SECRET, DATABASE_URL, bcrypt hashes, tokens) | **CONFIRMED — no secrets recorded** |
| No passwords recorded | **CONFIRMED** |
| No tokens recorded | **CONFIRMED** |
| No DATABASE_URL recorded | **CONFIRMED — variable name only** |
| No real patient data | **CONFIRMED — fake/non-PHI staging only** |
| No production PHI | **CONFIRMED — production PHI NO-GO** |
| Fake/non-PHI staging remains the only allowed environment | **CONFIRMED** |
