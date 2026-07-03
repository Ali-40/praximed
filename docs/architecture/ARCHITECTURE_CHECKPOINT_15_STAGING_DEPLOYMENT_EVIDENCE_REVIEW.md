# Architecture Checkpoint 15 — Staging Deployment Evidence Review

**Date:** 2026-07-03
**Sprint:** Sprint 15 complete (Modules 105–109)
**Backend tests:** 2266/2266 passed
**Status:** Sprint 15 reviewed. Planning phase complete. Manual Railway backend service creation: GO. Production PHI launch: NO-GO.

---

## 1. Current Status

Sprint 15 delivered the complete set of human-executable staging deployment runbooks.
No deployment was executed. No external Railway or Vercel services were created. No real
patient data was used. No runtime code was changed. No production secrets were added.

| Deliverable | Module | Commit | Status |
|---|---|---|---|
| Railway backend service creation runbook | 105 | d48a84c | Complete |
| Railway PostgreSQL provisioning/migration runbook + evidence doc | 106 | 6705c1c | Complete — evidence BLOCKED/PENDING |
| Vercel frontend project creation runbook + evidence doc | 107 | a861d32 | Complete — evidence BLOCKED/PENDING |
| Staging environment wiring runbook + evidence doc | 108 | 9e5b457 | Complete — evidence BLOCKED/PENDING |
| Staging smoke execution PASS/BLOCKED evidence doc | 109 | 0405836 | Complete — evidence BLOCKED/PENDING |

**Test suite:** 2266/2266 passed (78 new tests added across Sprint 15)

**No deployment executed.** No external services created. No real patient data used.
No production secrets. No runtime code changes. No auth refactor. Production PHI launch
remains NO-GO.

**All evidence documents are correctly BLOCKED/PENDING.** This is accurate — no staging
service exists yet. No evidence has been fabricated.

---

## 2. Sprint 15 Review

### 2.1 Module 105 — Railway Backend Service Creation Runbook

A 15-section human-executable guide for creating the Railway backend service. No deployment was run.

**Key content documented:**
- Exact Procfile start command: `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Why `--host 0.0.0.0` is required (Railway network routing; `127.0.0.1` times out)
- Why `$PORT` is required (Railway auto-injects; hard-coded `8000` fails health checks)
- Why `backend.app.main:app` is the correct import path (service root = repo root)
- All 6 required Railway env var names (with `openssl rand -hex 32` for secrets)
- First deploy expectations: `/health` → 200; `/health/ready` → 503 until DB
- 12-row failure triage; 6 stop rules

### 2.2 Module 106 — Railway PostgreSQL Provisioning and Migration Runbook

A 15-section guide for provisioning Railway PostgreSQL and running migrations. Evidence doc: BLOCKED/PENDING.

**Key content documented:**
- Railway PostgreSQL add-on creation via dashboard
- `DATABASE_URL` auto-injection via Railway variable reference (never pasted manually)
- Migration command: `python backend/scripts/run_migrations.py` via Railway "Run Command"
- Expected final revision: `0002_password_hash (head)` (11 tables)
- `db_smoke_test.py` verification (4 core tables)
- Staging fake clinic/user SQL provisioning with ON CONFLICT
- Safety: no local Docker `DATABASE_URL`; no production `DATABASE_URL`
- 11-row failure triage; 8 stop rules

### 2.3 Module 107 — Vercel Frontend Project Creation Runbook

A 14-section guide for creating the Vercel frontend project. Evidence doc: BLOCKED/PENDING.

**Key content documented:**
- Root directory must be `frontend` — critical; without it Vercel fails to find `package.json`
- `NEXT_PUBLIC_API_BASE_URL` is the only required Vercel env var
- `NEXT_PUBLIC_API_BASE_URL` is a public build-time variable baked into the browser bundle; not a secret
- Forbidden backend secrets in Vercel: `DATABASE_URL`, `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`, `POSTGRES_PASSWORD`
- `FRONTEND_CORS_ORIGINS` on Railway cannot be finalized until Vercel URL is assigned
- CORS errors at this stage are expected and acceptable
- 10-row failure triage; 7 stop rules

### 2.4 Module 108 — Staging Environment Wiring Runbook

A 13-section guide for wiring all staging components together. Evidence doc: BLOCKED/PENDING.

**Key content documented:**
- Full 5-component wiring map (Railway PostgreSQL → backend → Vercel; Vapi → backend; n8n → backend)
- 15-step wiring order (Railway first → PostgreSQL → migrations → fake data → Vercel → CORS → Vapi → n8n → smoke)
- `FRONTEND_CORS_ORIGINS` must be exact Vercel URL; no wildcard; no trailing slash; no ngrok
- `X-Vapi-Scopes: vapi:tool` (singular — plural returns HTTP 403)
- Vapi test assistant must match `VAPI_WEBHOOK_SECRET` in Railway
- 11 common wiring failures; 8 stop rules

### 2.5 Module 109 — Staging Smoke Execution PASS/BLOCKED Evidence

A 10-section smoke evidence document. Current result: BLOCKED/PENDING.

**Key content documented:**
- 15-step smoke checklist (all PENDING; no fabricated evidence)
- 16 explicit PASS criteria for when smoke evidence can be marked PASS
- 17-row evidence summary (all "Not available yet")
- 14 external blockers
- 12 safety constraints including no auto-confirmation, staff Confirm required, no real patients
- 12-step ordered next human action plan
- sessionStorage JWT acceptable for fake-data staging only

---

## 3. What Is Ready (Repo-Side)

All of the following are confirmed ready. No further code changes, runbooks, or planning
documents are required before manual external service creation begins.

| Item | Path | Status |
|---|---|---|
| Start command | `Procfile` — `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | READY |
| Python version | `runtime.txt` — `python-3.11` | READY |
| Runtime dependencies | `backend/requirements.txt` — 7 pinned deps (fastapi, uvicorn, asyncpg, alembic, pydantic, PyJWT, bcrypt) | READY |
| Application entry point | `backend/app/main.py` — `backend.app.main:app` | READY |
| Health endpoints | `/health` (no DB) and `/health/ready` (DB required) | READY |
| Migration runner | `backend/scripts/run_migrations.py` | READY |
| DB smoke test | `backend/scripts/db_smoke_test.py` | READY |
| Migration files | `0001_initial_schema.py` (11 tables) + `0002_add_password_hash_to_clinic_users.py` | READY |
| Frontend build | `frontend/package.json` — `"build": "next build"` (Next.js 14.2.3) | READY |
| Frontend config | `frontend/next.config.js` — no `output: 'standalone'`; no `vercel.json` needed | READY |
| Frontend env example | `frontend/.env.example` — `NEXT_PUBLIC_API_BASE_URL` documented | READY |
| CORS implementation | `backend/app/main.py` — `_cors_origins()` reads `FRONTEND_CORS_ORIGINS`; never returns `*` | READY |
| Railway backend runbook | `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` | READY |
| Railway PostgreSQL runbook | `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` | READY |
| Vercel frontend runbook | `docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` | READY |
| Wiring runbook | `docs/deployment/STAGING_ENVIRONMENT_WIRING_RUNBOOK.md` | READY |
| DB migration/seed strategy | `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md` | READY |
| Smoke runbook | `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` | READY |
| All backend tests | `backend/tests/` | READY — 2266/2266 passed |
| No further planning docs needed | — | CONFIRMED |

---

## 4. What Is Still Blocked

All blocked items require manual developer action outside this Claude Code session.
None can be resolved by creating additional planning documents.

| # | Blocker | Resolution |
|---|---|---|
| 1 | Railway backend service not created | Follow `RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` |
| 2 | Railway backend HTTPS URL not known | Assigned by Railway after service creation |
| 3 | Railway PostgreSQL not created | Follow `RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` |
| 4 | Staging API URLs unknown | Assigned after Railway service creation |
| 5 | Backend env vars not set (`JWT_SECRET_KEY`, etc.) | Set in Railway Variables panel before first deploy |
| 6 | `DATABASE_URL` not wired | Auto-injected after Railway PostgreSQL add-on is linked |
| 7 | Migrations not run against staging DB | Run via Railway "Run Command" after PostgreSQL creation |
| 8 | Staging fake clinic/user not provisioned | SQL insert via Railway shell after migrations |
| 9 | Vercel project not created | Follow `VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` |
| 10 | `NEXT_PUBLIC_API_BASE_URL` not set | Set in Vercel after Railway URL is known |
| 11 | `FRONTEND_CORS_ORIGINS` not set | Set in Railway after Vercel URL is known |
| 12 | Vapi test assistant not pointed to staging | Configure in Vapi dashboard after Railway URL is known |
| 13 | n8n staging workflow not configured | Configure in n8n after Railway URL is known (optional for initial smoke) |
| 14 | Staging smoke not run | Run after all wiring is complete |
| 15 | Rollback path not confirmed | No deployments exist yet; rollback documented in runbooks |

---

## 5. Decisions

| Decision | Outcome | Rationale |
|---|---|---|
| More planning documents before manual setup | **NO** | Sprint 15 produced the complete runbook set. No further planning is needed before the first manual action. |
| Manual Railway backend service creation | **GO** | Repo is fully ready. Runbook is complete. This is the exact next step. |
| Railway PostgreSQL creation | **GO** — after Railway backend creation | Follow Module 106 runbook after Module 105 backend creation succeeds. |
| Vercel frontend creation | **GO** — after Railway URL is known | Follow Module 107 runbook after Railway backend URL is assigned. |
| Staging environment wiring | **GO** — after Railway + Vercel URLs are known | Follow Module 108 runbook after both URLs are assigned. |
| Staging smoke execution | **GO** — after wiring is complete | Follow `DEPLOYMENT_SMOKE_RUNBOOK.md` after all wiring validated. |
| Production PHI launch | **NO-GO** | Staging smoke evidence has not been captured. 12 production blockers remain open. Auth/session hardening not yet implemented. |
| Auth/session hardening (httpOnly cookie) | **GO — after fake-data staging smoke evidence** | Module 98 plan is complete. Implement only after staging smoke is marked PASS. SameSite=None required for Railway+Vercel cross-domain staging. |
| Fabel 5 / frontend UX sprint | **DEFER** | Wait until staging topology confirmed and auth hardened. |
| Appointment workflow expansion | **DEFER** | No new appointment workflow features until staging smoke is stable. |

---

## 6. Exact Next Human Action

**The planning phase is complete. The next action is manual.**

Follow **`docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md`** to create the
PraxisMed Railway backend service for fake-data staging.

**First manual steps:**

1. Open https://railway.app and log in
2. Create a new Railway project: **New Project → Deploy from GitHub repo**
3. Select the PraxisMed repository
4. Verify Nixpacks detects Python 3.11 from `runtime.txt`
5. Verify start command: `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
6. Set health check path to `/health`
7. Set source branch to `master`
8. Generate four secrets with `openssl rand -hex 32` and set in Railway Variables:
   - `JWT_SECRET_KEY`
   - `VAPI_WEBHOOK_SECRET`
   - `N8N_WEBHOOK_SECRET`
   - `INTERNAL_WEBHOOK_SECRET`
9. Set `APP_ENV=staging`
10. Trigger first deploy
11. Confirm `GET https://<railway-url>/health` → `{"status": "ok", ...}` — HTTP 200
12. Confirm `GET https://<railway-url>/health/ready` → HTTP 503 (expected; no DB yet)

**Do NOT set `DATABASE_URL` manually** — it will be auto-injected by the Railway
PostgreSQL add-on in Module 106.

**Do NOT run migrations yet** — wait for Railway PostgreSQL in Module 106.

**Refer to the complete runbook for full steps, failure triage, and stop rules.**

---

## 7. Evidence the Developer Must Capture

After Railway backend service creation, record the following. No secret values.

| Evidence Item | What to Record |
|---|---|
| Railway project name | e.g., `praxismed-staging` |
| Railway service name | e.g., `praxismed-backend-staging` |
| Railway service URL | `https://<service>.up.railway.app` |
| Source branch deployed | `master` |
| Commit SHA deployed | Full SHA from Railway deployment log |
| Build status | Success or Failure |
| Nixpacks Python version detected | `3.11` |
| Start command detected | Full Procfile command |
| Env var names set (not values) | `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`, `APP_ENV` |
| `DATABASE_URL` status | Absent (expected at this stage) |
| `FRONTEND_CORS_ORIGINS` status | Absent (expected at this stage) |
| `GET /health` HTTP status | `200` |
| `GET /health` response body | `{"status": "ok", "service": "PraxisMed API"}` |
| `GET /health/ready` HTTP status | `503` (expected — no DB yet) |
| Sanitized build log snippet | First 10–15 lines; no secret values |
| Any errors or warnings | Description only; no secret values |

This evidence will be recorded in Module 110.

---

## 8. Safety Rules for Manual Setup

These rules apply throughout all manual staging service creation steps:

| Rule | Detail |
|---|---|
| Fake/non-PHI data only | No real patient names, phone numbers, DOBs, or medical records in any staging component |
| No real patients | All Vapi test calls use synthetic fake caller data |
| No production secrets | All Railway secrets are staging-only values from `openssl rand -hex 32`; never reused from local-dev or production |
| No production DB | Staging `DATABASE_URL` points to Railway-provisioned staging PostgreSQL only |
| No local-dev password | Staging bcrypt hash must not be the hash of `local-dev-password` |
| No secrets pasted into docs or chat | Never paste `JWT_SECRET_KEY`, `DATABASE_URL`, or any generated secret into any document or this session |
| No ngrok for staging | Railway URL is stable; ngrok creates an unauditable tunnel |
| No wildcard CORS | `FRONTEND_CORS_ORIGINS` must be the exact Vercel HTTPS URL; `*` is forbidden |
| Stop if Railway asks for production secrets | Staging and production must be fully isolated |
| Stop if secrets appear in logs | Any secret visible in Railway logs is a stop condition |
| Stop if real patient data appears | Any real name, phone, DOB, or medical record in any component is a stop condition |

---

## 9. Go/No-Go Table

| Action | Decision | First Step |
|---|---|---|
| Manual Railway backend service creation | **GO** | `RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` |
| Railway PostgreSQL creation | **GO** — after Railway backend URL confirmed | `RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` |
| Vercel frontend creation | **GO** — after Railway backend URL confirmed | `VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` |
| Staging smoke execution | **GO** — after wiring complete | `DEPLOYMENT_SMOKE_RUNBOOK.md` |
| Production PHI launch | **NO-GO** | Staging smoke evidence required; auth hardening required; 12 production blockers open |
| Auth/session hardening (httpOnly cookie) | **GO — after staging smoke PASS** | Module 98 plan complete; implement after smoke evidence |
| Fabel 5 / frontend UX sprint | **DEFER** | After staging confirmed and auth hardened |
| Appointment workflow expansion | **DEFER** | After staging smoke stable |

---

## 10. Recommended Next Module — Module 110

**Sprint 16 / Module 110 — Railway Backend Service Creation Evidence**

When the developer completes the Railway backend service creation steps:

1. Provide the Railway service URL, build status, commit SHA, and evidence items from Section 7
2. Module 110 records this evidence
3. If `/health` → 200: evidence marked PASS; proceed to Module 111 (Railway PostgreSQL)
4. If blocked: evidence remains BLOCKED/PENDING with exact blocker documented

Module 110 accepts only real evidence. No fabricated PASS. No real secrets in evidence.
No production data.
