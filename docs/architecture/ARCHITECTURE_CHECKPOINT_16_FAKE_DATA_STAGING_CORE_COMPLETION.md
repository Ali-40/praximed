# Architecture Checkpoint 16 — Fake-Data Staging Core Completion Review

**Date:** 2026-07-05
**Sprint:** Sprint 16 / Modules 110–118B
**Result:** FAKE-DATA STAGING CORE PASS
**Full test suite:** 2468/2468 passed

---

## 1. Purpose

This checkpoint freezes Sprint 16 fake-data staging core as PASS, maps every
confirmed staging smoke check to its evidence module, states clearly what is and
is not production-ready, and recommends the next module path.

**Accuracy policy:** No item is marked PASS without real evidence from real deployed
staging services. No evidence is fabricated.

Staging uses fake/non-PHI data only. No production secrets. No real patient data.
No secrets recorded in any evidence document.

---

## 2. Checkpoint Result

**FAKE-DATA STAGING CORE PASS**

The full fake-data staging loop — from Vapi tool call through Railway backend,
Railway PostgreSQL, Vercel frontend, browser login, dashboard row visibility, and
staff Confirm — is confirmed working against live deployed staging services.

Production PHI readiness remains NO-GO. n8n staging workflow remains PENDING/DEFERRED.

---

## 3. Proven Deployed Loop

The following end-to-end path has been exercised with real deployed services and
fake/non-PHI data:

```
Vapi test assistant
  → POST /vapi/tools/capture-appointment-request (Railway backend HTTPS)
  → Railway backend authenticates machine tool call (X-Vapi-Service-Name / X-Vapi-Clinic-Id / X-Vapi-Scopes)
  → Railway PostgreSQL inserts appointment_requests row (status=new, action_required=True)
  → Vercel frontend fetches and displays row in dashboard
  → Staff clicks Confirm in browser dashboard
  → Railway backend updates row to status=confirmed
  → No auto-confirmation observed at any step
```

All components confirmed live:
- Vapi test assistant / tool call
- Railway backend (HTTPS; machine auth; DB write)
- Railway PostgreSQL (migrated schema; asyncpg pool; row visible in DB)
- Vercel frontend (HTTPS; login; protected dashboard; row display; Confirm UI)
- browser login (JWT; sessionStorage; no CORS error)
- dashboard row visibility (Appointments count reached 2 then 3; Test Patient rows; status: new)
- staff Confirm (two rows updated to status: confirmed; one row remained status: new; no auto-confirm)

---

## 4. Evidence Map by Module

| Module | Deliverable | Status |
|---|---|---|
| Module 112 | Railway backend service creation — `https://web-production-fd91d.up.railway.app`; `/health` → 200 | **PASS** |
| Module 114 | Railway PostgreSQL migration — `run_migrations.py` exit 0; `0002_password_hash (head)`; 4 tables confirmed | **PASS** |
| Module 115 | Fake staging clinic/user provisioned — `clinic_id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056`; `doctor.staging@praximed.test`; both `active` | **PASS** |
| Module 116 | Backend login smoke — `GET /health/ready` → 200; `POST /auth/login` → 200; bearer token issued (REDACTED) | **PASS** |
| Module 117 | Vercel frontend deployment / API wiring / CORS / browser login / dashboard — `https://praximed.vercel.app`; all four sections visible | **PASS** |
| Module 118A | Tenant config blocker fix — `backend/tenants/configs/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/clinic_config.json` created | **PASS** |
| Module 118B | Vapi staging dashboard loop — correct headers; Vapi call created rows; dashboard showed rows; staff Confirm confirmed | **PASS** |

Evidence documents:

| Document | Module | Status |
|---|---|---|
| `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` | Module 114 | PASS |
| `docs/runtime/FAKE_STAGING_CLINIC_USER_PROVISIONING_EVIDENCE.md` | Module 115 | PASS |
| `docs/runtime/BACKEND_STAGING_LOGIN_SMOKE_EVIDENCE.md` | Module 116 | PASS |
| `docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_AND_API_WIRING_EVIDENCE.md` | Module 117 | PASS |
| `docs/runtime/VAPI_STAGING_DASHBOARD_LOOP_EVIDENCE.md` | Module 118B | PASS |
| `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` | Modules 112–118B | CORE PASS |
| `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` | Modules 112–118B | CORE PASS |

---

## 5. What Is PASS

| Item | Confirmed |
|---|---|
| Fake-data staging backend (Railway backend service; HTTPS; health endpoints) | **PASS** |
| Fake-data staging database (Railway PostgreSQL; migrations applied; 4 tables; asyncpg pool) | **PASS** |
| Fake-data staging frontend (Vercel deployment; Next.js build; HTTPS; login page) | **PASS** |
| Fake-data staging auth/login (fake clinic/user provisioned; `POST /auth/login` → JWT; CORS; browser login) | **PASS** |
| Fake-data Vapi appointment capture (Vapi tool call → Railway → DB row inserted; `status=new`, `action_required=True`) | **PASS** |
| Fake-data dashboard row visibility (dashboard fetches and renders appointment rows from Railway PostgreSQL) | **PASS** |
| Fake-data dashboard Confirm (staff Confirm button updates row to `status=confirmed`; no auto-confirm) | **PASS** |

---

## 6. What Remains PENDING

The following are explicitly not proven and must be addressed before any production
or PHI-bearing use:

| Item | Status | Priority |
|---|---|---|
| n8n staging workflow (n8n receives signed POST from backend; no production calendar write) | **PENDING / DEFERRED** | LOW — optional for initial smoke |
| Production auth/session hardening (httpOnly cookie; replace sessionStorage JWT) | **PENDING** | HIGH — required before production PHI access |
| Production secrets review (rotate JWT_SECRET_KEY, VAPI_WEBHOOK_SECRET, etc. for production) | **PENDING** | HIGH |
| PHI/compliance review (GDPR/HIPAA applicability; data residency; audit log completeness) | **PENDING** | HIGH |
| Custom domain (Railway/Vercel default URLs used in staging) | **PENDING** | MEDIUM |
| Monitoring / logging / alerting (Railway log stream sanitization; error alerting; uptime monitoring) | **PENDING** | MEDIUM |
| Rollback path confirmed against live deployments | **PENDING** | MEDIUM |
| Real clinic onboarding flow (real clinic/user provisioning; admin workflow) | **PENDING** | MEDIUM |
| UI/UX polish (Fabel 5 or equivalent premium doctor-facing UI sprint) | **PENDING / DEFERRED** | LOW |

---

## 7. Explicit NO-GO

| Constraint | Status |
|---|---|
| No real patient data in any staging row, log, or Vapi test call | **CONFIRMED** |
| No production PHI access | **NO-GO** — production PHI launch requires items in Section 6 first |
| Not production-ready | **CONFIRMED** — fake-data staging only; production checklist incomplete |
| No wildcard CORS (`FRONTEND_CORS_ORIGINS` is exact Vercel URL; `*` is forbidden) | **CONFIRMED** |
| Staff Confirm required (no auto-confirmation; `status=confirmed` requires explicit staff action) | **CONFIRMED** |

---

## 8. Recommended Next Path

### Primary Recommendation

**Sprint 17 / Module 119 — Production Hardening Gap Review**

Reason: The fake-data staging core loop is proven. Before production use, clinic demos,
or onboarding real patients, the project needs a structured review of the production
hardening gaps listed in Section 6 — particularly auth/session hardening (httpOnly
cookie), secrets rotation, and PHI/compliance review. A dedicated gap review module
produces an actionable checklist and module plan for those gaps.

n8n can be added in a later sprint once the production hardening path is clear.
Deferring n8n now avoids entangling the hardening track with an optional integration.

### Alternative

**Sprint 16 / Module 119 — n8n Staging Workflow Wiring Evidence**

Choose this path only if n8n is immediately needed for a demo scope or integration
milestone. n8n as an alternative does not block the production hardening track — both
paths can be pursued, but the primary recommendation is to address production hardening
first.

---

## 9. Safety Constraints

All of the following are confirmed for every Sprint 16 evidence document:

| Constraint | Status |
|---|---|
| No secrets recorded (JWT_SECRET_KEY, VAPI_WEBHOOK_SECRET, N8N_WEBHOOK_SECRET, DATABASE_URL, bcrypt hashes, tokens) | **CONFIRMED** — no secrets recorded |
| No real patient data | **CONFIRMED** — fake data only; patient name "Test Patient" |
| No passwords recorded | **CONFIRMED** — staging user password not recorded |
| No tokens recorded | **CONFIRMED** — JWT access_token value not recorded; REDACTED in all docs |
| No DATABASE_URL recorded | **CONFIRMED** — variable name only; value not recorded |
| Fake/non-PHI staging only | **CONFIRMED** — all staging rows use fake synthesized data |
| Production PHI readiness NO-GO | **CONFIRMED** — no production use until Section 6 items are addressed |
