# Railway Backend Service Creation Evidence — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 16 / Module 112
**Status:** PASS — Railway backend service is active and `/health` returns 200

---

## 1. Purpose

This document records the real evidence from creating the PraxisMed Railway backend
service for fake-data staging. Evidence reflects only what has been verified against
the real Railway service.

**Accuracy policy:** No step is marked PASS without real evidence from the real Railway
service. Staging uses fake/non-PHI data only. No production secrets recorded here.
No real patient data.

---

## 2. Current Result

**Overall result: PASS**

The Railway backend service is active and responding. The `/health` endpoint returns
the expected JSON response with HTTP 200. The root `requirements.txt` direct dependency
fix (Module 111) resolved the Railway/Railpack build failure.

---

## 3. Evidence

| Evidence Item | Value | Status |
|---|---|---|
| Railway service status | Active / Online | **PASS** |
| Railway service URL | `https://web-production-fd91d.up.railway.app` | **PASS** |
| Deployed commit SHA | `081121b` — Sprint 16 / Module 111 — Railway root requirements direct dependency fix | **PASS** |
| Health endpoint path | `/health` | **PASS** |
| `GET /health` HTTP status | `200` | **PASS** |
| `GET /health` response body | `{"status":"ok","service":"PraxisMed API"}` | **PASS** |
| Root `requirements.txt` (direct deps) | fastapi, uvicorn, asyncpg, alembic, pydantic, PyJWT, bcrypt — all listed directly; no `-r backend/requirements.txt` | **PASS** |
| Procfile start command | `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | **PASS** |
| Root directory setting | Repo root (blank) — not `backend/` | **PASS** |
| Python version | 3.11 (from `runtime.txt`) | **PASS** |
| Backend imports (`backend.app.main:app`) | Resolving correctly from repo root | **PASS** |
| `DATABASE_URL` status | Absent (expected — Railway PostgreSQL not yet provisioned) | PENDING |
| `FRONTEND_CORS_ORIGINS` status | Absent (expected — Vercel URL not yet known) | PENDING |
| `GET /health/ready` HTTP status | 503 (expected — no DB pool yet) | PENDING |

---

## 4. What This Proves

- **Railway can build and deploy the PraxisMed repo** — Nixpacks detects Python 3.11
  from `runtime.txt`; installs 7 packages from root `requirements.txt`
- **Root `requirements.txt` with direct dependencies works** — the `-r backend/requirements.txt`
  nested include that caused Module 111 build failure is resolved
- **Procfile start command works** — `backend.app.main:app` resolves from repo root;
  `--host 0.0.0.0` and `--port $PORT` are correct for Railway
- **Backend imports resolve from repo root** — no `ModuleNotFoundError: No module named 'backend'`
- **Public HTTPS Railway URL is serving the backend** — `https://web-production-fd91d.up.railway.app`
  is the staging backend URL for all subsequent wiring steps
- **`/health` endpoint confirms app startup** — FastAPI lifespan completed; app is responding

---

## 5. What This Does Not Prove

| Area | Status | Next Module |
|---|---|---|
| Railway PostgreSQL connected | NOT PROVEN | Module 113 |
| `DATABASE_URL` injected | NOT PROVEN | Module 113 |
| Migrations applied (`0002_password_hash` head) | NOT PROVEN | Module 113 |
| Staging fake clinic/user provisioned | NOT PROVEN | Module 113 |
| `/health/ready` returns 200 | NOT PROVEN | Module 113 |
| Vercel frontend deployed | NOT PROVEN | Module 114 |
| `NEXT_PUBLIC_API_BASE_URL` set to Railway URL | NOT PROVEN | Module 114 |
| CORS wired (`FRONTEND_CORS_ORIGINS` = Vercel URL) | NOT PROVEN | Module 115 |
| Browser login works | NOT PROVEN | Module 115 |
| Vapi test assistant pointed to staging | NOT PROVEN | Module 115 |
| n8n staging workflow configured | NOT PROVEN | Module 115 |
| Full staging smoke passed | NOT PROVEN | Module 116 |
| Production PHI readiness | NOT PROVEN | Production PHI launch remains NO-GO |

---

## 6. Safety Boundary

| Rule | Status |
|---|---|
| Staging uses fake/non-PHI data only | CONFIRMED — no real patient data in any staging component |
| Railway environment label | Railway may display "production" in URL (`web-production-fd91d`) — this is a Railway naming convention; PraxisMed's staging status is fake-data-only staging; not production PHI |
| No real patient data | CONFIRMED — no patient records in Railway backend at this stage |
| No production secrets | CONFIRMED — staging secrets are staging-only values; no production credentials |
| No production database | CONFIRMED — `DATABASE_URL` not yet wired; no DB connected |
| Production PHI launch | **NO-GO** — staging smoke not yet executed; auth hardening not implemented |

---

## 7. Remaining Blockers

The following must be completed before full staging smoke can be marked PASS.
All require manual developer action.

| # | Blocker | Level | Next Step |
|---|---|---|---|
| 1 | Railway PostgreSQL not provisioned | **HIGH** | Module 113 |
| 2 | `DATABASE_URL` not wired into Railway backend | **HIGH** | Module 113 |
| 3 | Migrations not run | **HIGH** | Module 113 |
| 4 | Staging fake clinic/user not provisioned | **HIGH** | Module 113 |
| 5 | Vercel frontend not deployed | **HIGH** | Module 114 |
| 6 | `NEXT_PUBLIC_API_BASE_URL` not set in Vercel | **HIGH** | Module 114 |
| 7 | `FRONTEND_CORS_ORIGINS` not set in Railway | **HIGH** | Module 115 |
| 8 | CORS preflight not verified | **HIGH** | Module 115 |
| 9 | Fake login not tested | **HIGH** | Module 115 |
| 10 | Vapi test assistant not pointed to staging URL | **HIGH** | Module 115 |
| 11 | n8n staging workflow not configured | LOW (optional for initial smoke) | Module 115 |
| 12 | Full staging smoke not executed | **HIGH** | Module 116 |

---

## 8. Recommended Next Step — Module 113

**Sprint 16 / Module 113 — Railway PostgreSQL Provisioning and Migration Execution Evidence**

Now that the Railway backend URL is confirmed (`https://web-production-fd91d.up.railway.app`),
the next step is:

1. Add the Railway PostgreSQL plugin to the same Railway project
2. Confirm `DATABASE_URL` is auto-injected into the backend service
3. Wait for Railway PostgreSQL to show "Running" status
4. Run `python backend/scripts/run_migrations.py` via Railway "Run Command"
5. Confirm exit code 0; capture sanitized output
6. Run `python backend/scripts/db_smoke_test.py` to verify 4 tables
7. Provision staging fake clinic and user via SQL
8. Confirm `GET /health/ready` → 200

Follow `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` for
exact steps and evidence to capture.
