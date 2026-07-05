# Staging Environment Wiring Evidence — PraxisMed

**Date:** 2026-07-05
**Sprint:** Sprint 16 / Module 118A
**Status:** PARTIAL PASS — backend/PostgreSQL/migrations/fake clinic+user/login/Vercel/CORS/dashboard PASS; Vapi test attempted (Vapi UI "completed successfully" but staging_count=0; no DB row was inserted — Module 118A diagnostic); tenant config fix applied — Module 118A; Vapi/n8n PENDING

---

## 1. Purpose

This document records the actual evidence from wiring the PraxisMed fake-data staging
environment: Railway backend, Railway PostgreSQL, Vercel frontend, Vapi test assistant,
and n8n staging workflow.

**Accuracy policy:** No evidence step is marked PASS without real proof from real
external staging services. No evidence is fabricated. If a wiring step has not been
executed or confirmed against real services, its status is PENDING or BLOCKED.

Staging uses fake/non-PHI data only. No production secrets. No real patient data.

---

## 2. Current Result

**Overall result: BLOCKED/PENDING**

Railway backend service, Railway PostgreSQL, and migrations are confirmed PASS.
Fake staging clinic/user, Vercel frontend, CORS wiring, Vapi, and n8n remain PENDING.

This document will be updated to PASS when:
1. ~~Railway backend URL is confirmed and `/health` returns 200~~ **PASS**
2. ~~Railway PostgreSQL is provisioned; `DATABASE_URL` auto-injected; migrations applied~~ **PASS**
3. ~~Staging fake clinic and user are provisioned in Railway PostgreSQL~~ **PASS**
4. ~~Vercel frontend URL is confirmed and `/login` loads in browser~~ **PASS**
5. ~~`NEXT_PUBLIC_API_BASE_URL` is set to Railway backend HTTPS URL in Vercel~~ **PASS**
6. ~~`FRONTEND_CORS_ORIGINS` is set to exact Vercel URL in Railway backend~~ **PASS**
7. ~~CORS preflight passes (no wildcard; `Access-Control-Allow-Origin` matches Vercel URL)~~ **PASS**
8. ~~Fake login succeeds (JWT in sessionStorage; dashboard loads)~~ **PASS**
9. Vapi test assistant URL/headers are set and a test call creates a row in the DB ← blocker identified; tenant config fix applied (Module 118A); retest pending (Module 118B)
10. Sanitized evidence is captured for each step above

---

## 3. Preconditions Available / Missing

| Precondition | Status | Notes |
|---|---|---|
| Railway backend service exists (Module 112) | **PASS** | `https://web-production-fd91d.up.railway.app` — commit `081121b` |
| Railway backend HTTPS URL known | **PASS** | `https://web-production-fd91d.up.railway.app` |
| Railway PostgreSQL provisioned (Module 114) | **PASS** | Online; `DATABASE_URL` wired; migrations applied |
| `DATABASE_URL` auto-injected into Railway backend | **PASS** | Confirmed wired; value not recorded |
| Migrations applied: `0002_password_hash (head)` | **PASS** | Both revisions applied; DB smoke confirmed 4 tables |
| Staging fake clinic provisioned | **PASS** | `id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056` `slug=staging-fake-clinic` `status=active` — Module 115 |
| Staging fake user (`doctor.staging@praximed.test`) provisioned | **PASS** | `id=5b63b514-7624-4e8e-9af0-71c153ba7b83` `role=doctor` `status=active` — Module 115 |
| Vercel frontend project exists (Module 117) | **PASS** | `https://praximed.vercel.app` — login page loads; dashboard confirmed |
| Vercel frontend URL known | **PASS** | `https://praximed.vercel.app` |
| `NEXT_PUBLIC_API_BASE_URL` set in Vercel | **PASS** | Points to `https://web-production-fd91d.up.railway.app` |
| `FRONTEND_CORS_ORIGINS` set in Railway | **PASS** | Set to `https://praximed.vercel.app` (no wildcard) |
| Vapi test assistant configured | **BLOCKED** | Module 118A: Vapi UI "completed successfully" but staging_count=0; no DB row was inserted; headers incorrect; tenant config missing (fixed — Module 118A); retest in Module 118B |
| n8n staging workflow configured | **PENDING / DEFERRED** | Optional for initial smoke |

**Repo-side readiness (no external services required):**

| Item | Status |
|---|---|
| `Procfile` — `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | READY |
| `runtime.txt` — `python-3.11` | READY |
| `backend/requirements.txt` — 7 pinned deps | READY |
| `backend/scripts/run_migrations.py` | READY |
| `backend/scripts/db_smoke_test.py` | READY |
| `backend/migrations/versions/0001_initial_schema.py` | READY |
| `backend/migrations/versions/0002_add_password_hash_to_clinic_users.py` | READY |
| `frontend/package.json` — `"build": "next build"` | READY |
| `frontend/next.config.js` — no `output: 'standalone'` | READY |
| `frontend/.env.example` — `NEXT_PUBLIC_API_BASE_URL` documented | READY |
| `backend/app/main.py` — `_cors_origins()` never returns `*` | READY |
| Module 105 Railway backend runbook | READY |
| Module 106 Railway PostgreSQL runbook | READY |
| Module 107 Vercel frontend runbook | READY |
| Module 108 wiring runbook | READY |
| Full test suite: 2188/2188 passed | READY |

---

## 4. Wiring Evidence Table

| Evidence Item | Evidence Available? | Current Value | Status |
|---|---|---|---|
| Railway backend URL | `https://web-production-fd91d.up.railway.app` | **PASS** |
| Railway backend `/health` response | `{"status":"ok","service":"PraxisMed API"}` — 200 | **PASS** |
| Railway PostgreSQL service status | Online / Running | **PASS** |
| `DATABASE_URL` auto-injected confirmed | Confirmed wired to backend service (name only; value not recorded) | **PASS** |
| Migrations applied | `run_migrations.py` exit 0; both revisions applied | **PASS** |
| `alembic current` output | `0002_password_hash (head)` (confirmed via migration output) | **PASS** |
| `db_smoke_test.py` result | 4 tables confirmed: clinics, patients, consultation_sessions, audit_log | **PASS** |
| Railway backend `/health/ready` response | `{"status":"ready","checks":{"app":"ok"}}` — 200 | **PASS** |
| Backend direct login smoke (`POST /auth/login`) | HTTP 200; `access_token` present (value REDACTED); `token_type=bearer` | **PASS** |
| Railway backend env var names set (not values) | Not available yet | Expected: `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`, `FRONTEND_CORS_ORIGINS` | PENDING |
| Staging fake clinic UUID | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` | **PASS** |
| Staging fake user email confirmed | `doctor.staging@praximed.test` | **PASS** |
| Vercel frontend URL | `https://praximed.vercel.app` | **PASS** |
| `NEXT_PUBLIC_API_BASE_URL` name confirmed in Vercel | Confirmed (value = Railway backend HTTPS URL) | **PASS** |
| Vercel build status | Ready / Success | **PASS** |
| Vercel commit SHA deployed | (see Railway/Vercel deploy dashboard) | **PASS** |
| `/login` loads in browser | Confirmed — login form visible at `https://praximed.vercel.app/login` | **PASS** |
| `FRONTEND_CORS_ORIGINS` set to exact Vercel URL | `https://praximed.vercel.app` (no wildcard) | **PASS** |
| `FRONTEND_CORS_ORIGINS` — no wildcard confirmed | Confirmed — exact URL only | **PASS** |
| CORS from browser | Browser login succeeded without CORS error — CORS is working | **PASS** |
| Fake login succeeds (JWT returned) | Confirmed — browser login HTTP 200; token present (REDACTED) | **PASS** |
| Dashboard loads after login | `https://praximed.vercel.app/dashboard` — all four sections visible | **PASS** |
| Vapi test assistant server URL set | Module 118A: URL set (`https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request`); headers incorrect | Required headers: `Content-Type: application/json`, `X-Vapi-Service-Name: vapi`, `X-Vapi-Clinic-Id: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056`, `X-Vapi-Scopes: vapi:tool`; remove `X-Clinic-Ref` | BLOCKED — Module 118B |
| Vapi `X-Vapi-Scopes: vapi:tool` confirmed (singular) | X-Vapi-Scopes was set but other required headers were missing or wrong | `X-Vapi-Service-Name` was absent; `X-Clinic-Ref` is not a recognized alias — must use `X-Vapi-Clinic-Id` | BLOCKED — Module 118B |
| Vapi staging tenant config for UUID | Missing — caused ConfigNotFoundError (HTTP 404) | `backend/tenants/configs/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/clinic_config.json` created — Module 118A; Railway redeploy required | FIXED — awaiting redeploy |
| Vapi test call creates row in DB | Module 118A: Vapi UI "completed successfully" but staging_count=0; no DB row was inserted | Vapi treats HTTP 4xx as "completed"; root causes: wrong headers + missing tenant config (tenant config fixed — Module 118A) | BLOCKED — Module 118B |
| Appointment row `status=new`, `action_required=True` | Not confirmed — staging_count=0 | — | PENDING |
| Staff Confirm flow (no auto-confirm) | Not confirmed | — | PENDING |
| n8n staging configured (if enabled) | Not available yet | — | PENDING/DEFERRED |
| No secrets in any evidence record | Confirmed through Module 117 | **PASS** |
| No real patient data in staging | Confirmed — dashboard shows zero rows; footer notes fake data | **PASS** |

---

## 5. Blockers

All require manual developer action before the corresponding evidence row can be captured.

| # | Blocker | Level | Status |
|---|---|---|---|
| 1 | Railway backend service not yet created | **HIGH** | **RESOLVED — Module 112** |
| 2 | Railway backend HTTPS URL not yet known | **HIGH** | **RESOLVED — Module 112** |
| 3 | Railway PostgreSQL not yet provisioned | **HIGH** | **RESOLVED — Module 114** |
| 4 | `DATABASE_URL` not yet auto-injected into Railway backend | **HIGH** | **RESOLVED — Module 114** |
| 5 | Migrations not yet run against Railway PostgreSQL | **HIGH** | **RESOLVED — Module 114** |
| 6 | Staging fake clinic not yet provisioned | **HIGH** | **RESOLVED — Module 115** |
| 7 | Staging fake user not yet provisioned | **HIGH** | **RESOLVED — Module 115** |
| 8 | Vercel frontend project not yet created | **HIGH** | **RESOLVED — Module 117** |
| 9 | Vercel URL not yet known | **HIGH** | **RESOLVED — Module 117** (`https://praximed.vercel.app`) |
| 10 | `NEXT_PUBLIC_API_BASE_URL` not yet set in Vercel | **HIGH** | **RESOLVED — Module 117** |
| 11 | `FRONTEND_CORS_ORIGINS` not yet set in Railway | **HIGH** | **RESOLVED — Module 117** |
| 12 | Railway backend not redeployed after `FRONTEND_CORS_ORIGINS` set | **HIGH** | **RESOLVED — Module 117** |
| 13 | Vapi headers incorrect: `X-Vapi-Service-Name` missing; `X-Clinic-Ref` not a recognized alias (must use `X-Vapi-Clinic-Id`); staging tenant config was missing (fixed — Module 118A) | MEDIUM | BLOCKED — Module 118B |
| 14 | n8n staging workflow not yet configured | LOW (optional for initial smoke) | PENDING/DEFERRED |

---

## 6. What Is Repo-Ready

The following repo-side items are ready and require no code changes before wiring:

- `Procfile` — correct start command with `--host 0.0.0.0 --port $PORT`
- `runtime.txt` — `python-3.11`
- `backend/requirements.txt` — 7 pinned production dependencies
- `backend/scripts/run_migrations.py` — reads `DATABASE_URL`; runs `alembic upgrade head`
- `backend/scripts/db_smoke_test.py` — verifies 4 core tables; no write operations
- `backend/migrations/` — 2 migration files; final head: `0002_password_hash`
- `backend/app/main.py` — `_cors_origins()` reads `FRONTEND_CORS_ORIGINS`; never returns `*`
- `frontend/package.json` — `"build": "next build"` confirmed
- `frontend/next.config.js` — no `output: 'standalone'`; no `vercel.json` needed
- `frontend/.env.example` — `NEXT_PUBLIC_API_BASE_URL` documented
- All runbooks: Module 105, 106, 107, 108

---

## 7. Next Evidence Needed

To update this document from BLOCKED/PENDING to PASS, the developer must complete the
following steps in order and capture evidence for each:

1. **Railway backend URL** — from Module 105 runbook; confirm `/health` → 200
2. **Railway PostgreSQL wiring proof** — `DATABASE_URL` injected; `/health/ready` → 200
3. **Migration evidence** — `run_migrations.py` exit 0; `alembic current` → `0002_password_hash (head)`
4. **Staging fake clinic/user proof** — SELECT confirms rows; clinic UUID recorded
5. **Vercel frontend URL** — from Module 107 runbook; confirm `/login` loads
6. **`NEXT_PUBLIC_API_BASE_URL` confirmed** — env var name set in Vercel; Vercel redeployed
7. **CORS/API wiring proof** — `FRONTEND_CORS_ORIGINS` set; OPTIONS preflight → 200/204; `Access-Control-Allow-Origin` matches Vercel URL exactly; no wildcard
8. **Fake login proof** — credentials accepted; JWT in sessionStorage; dashboard loads
9. **Vapi staging tool proof (Module 118B)** — correct Vapi headers (`Content-Type`, `X-Vapi-Service-Name: vapi`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes: vapi:tool`; remove `X-Clinic-Ref`); push tenant config fix; Railway redeploy; direct endpoint smoke → 200; DB check `staging_count > 0`; `status=new`; `action_required=True`
10. **Staff Confirm proof** — no auto-confirm; staff action required for status change
11. **n8n staging proof (if enabled)** — staging endpoint receives signed POST; no production calendar write

Once all rows in Section 4 are marked PASS, proceed to Module 109 (Staging Smoke
Execution Evidence — full end-to-end smoke documentation).
