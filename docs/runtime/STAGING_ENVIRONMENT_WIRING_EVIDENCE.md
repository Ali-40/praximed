# Staging Environment Wiring Evidence — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 15 / Module 108
**Status:** BLOCKED/PENDING — staging environment wiring evidence not yet provided

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

External staging services have not been confirmed created and no wiring evidence has
been provided. This result is accurate — it is not a failure. The runbook
(`STAGING_ENVIRONMENT_WIRING_RUNBOOK.md`) defines all steps required to move this
document to PASS.

This document will be updated to PASS when:
1. Railway backend URL is confirmed and `/health` returns 200
2. Railway PostgreSQL is provisioned; `DATABASE_URL` auto-injected; migrations applied
3. Staging fake clinic and user are provisioned in Railway PostgreSQL
4. Vercel frontend URL is confirmed and `/login` loads in browser
5. `NEXT_PUBLIC_API_BASE_URL` is set to Railway backend HTTPS URL in Vercel
6. `FRONTEND_CORS_ORIGINS` is set to exact Vercel URL in Railway backend
7. CORS preflight passes (no wildcard; `Access-Control-Allow-Origin` matches Vercel URL)
8. Fake login succeeds (JWT in sessionStorage; dashboard loads)
9. Vapi test assistant URL/headers are set and a test call creates a row in the DB
10. Sanitized evidence is captured for each step above

---

## 3. Preconditions Available / Missing

| Precondition | Status | Notes |
|---|---|---|
| Railway backend service exists (Module 105) | **PENDING** | Runbook published; service not yet confirmed created |
| Railway backend HTTPS URL known | **PENDING** | Required for `NEXT_PUBLIC_API_BASE_URL` and Vapi tool URL |
| Railway PostgreSQL provisioned (Module 106) | **PENDING** | Runbook published; DB not yet confirmed provisioned |
| `DATABASE_URL` auto-injected into Railway backend | **PENDING** | Follows Module 106 completion |
| Migrations applied: `0002_password_hash (head)` | **PENDING** | Follows `DATABASE_URL` injection |
| Staging fake clinic provisioned | **PENDING** | Follows migrations |
| Staging fake user (`doctor.staging@praximed.test`) provisioned | **PENDING** | Follows migrations |
| Vercel frontend project exists (Module 107) | **PENDING** | Runbook published; project not yet confirmed created |
| Vercel frontend URL known | **PENDING** | Required for `FRONTEND_CORS_ORIGINS` |
| `NEXT_PUBLIC_API_BASE_URL` set in Vercel | **PENDING** | Requires Railway backend URL |
| `FRONTEND_CORS_ORIGINS` set in Railway | **PENDING** | Requires Vercel URL |
| Vapi test assistant configured | **PENDING** | Requires Railway backend URL and staging clinic UUID |
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
| Railway backend URL | Not available yet | — | PENDING |
| Railway backend `/health` response | Not available yet | Expected: `{"status": "ok", ...}` — 200 | PENDING |
| Railway backend `/health/ready` response | Not available yet | Expected: `{"status": "ready", ...}` — 200 | PENDING |
| Railway backend env var names set (not values) | Not available yet | Expected: `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`, `FRONTEND_CORS_ORIGINS` | PENDING |
| `DATABASE_URL` auto-injected confirmed | Not available yet | — | PENDING |
| Migrations applied | Not available yet | Expected: exit code 0 | PENDING |
| `alembic current` output | Not available yet | Expected: `0002_password_hash (head)` | PENDING |
| `db_smoke_test.py` result | Not available yet | Expected: 4 tables confirmed | PENDING |
| Staging fake clinic UUID | Not available yet | — | PENDING |
| Staging fake user email confirmed | Not available yet | Expected: `doctor.staging@praximed.test` | PENDING |
| Vercel frontend URL | Not available yet | — | PENDING |
| `NEXT_PUBLIC_API_BASE_URL` name confirmed in Vercel | Not available yet | — | PENDING |
| Vercel build status | Not available yet | Expected: Success | PENDING |
| Vercel commit SHA deployed | Not available yet | — | PENDING |
| `/login` loads in browser | Not available yet | — | PENDING |
| `FRONTEND_CORS_ORIGINS` set to exact Vercel URL | Not available yet | — | PENDING |
| `FRONTEND_CORS_ORIGINS` — no wildcard confirmed | Not available yet | — | PENDING |
| CORS preflight OPTIONS → 200/204 | Not available yet | Expected: `Access-Control-Allow-Origin: https://<vercel-url>` | PENDING |
| Fake login succeeds (JWT in sessionStorage) | Not available yet | — | PENDING |
| Dashboard loads after login | Not available yet | — | PENDING |
| Vapi test assistant server URL set | Not available yet | Expected: Railway URL + `/vapi/tools/capture-appointment-request` | PENDING |
| Vapi `X-Vapi-Scopes: vapi:tool` confirmed (singular) | Not available yet | — | PENDING |
| Vapi test call creates row in DB | Not available yet | — | PENDING |
| Appointment row `status=new`, `action_required=True` | Not available yet | — | PENDING |
| Staff Confirm flow (no auto-confirm) | Not available yet | — | PENDING |
| n8n staging configured (if enabled) | Not available yet | — | PENDING/DEFERRED |
| No secrets in any evidence record | Not available yet | — | PENDING |
| No real patient data in staging | Not available yet | — | PENDING |

---

## 5. Blockers

All require manual developer action before any evidence row can be captured.

| # | Blocker | Level |
|---|---|---|
| 1 | Railway backend service not yet created | **HIGH** |
| 2 | Railway backend HTTPS URL not yet known | **HIGH** |
| 3 | Railway PostgreSQL not yet provisioned | **HIGH** |
| 4 | `DATABASE_URL` not yet auto-injected into Railway backend | **HIGH** |
| 5 | Migrations not yet run against Railway PostgreSQL | **HIGH** |
| 6 | Staging fake clinic not yet provisioned | **HIGH** |
| 7 | Staging fake user not yet provisioned | **HIGH** |
| 8 | Vercel frontend project not yet created | **HIGH** |
| 9 | Vercel URL not yet known | **HIGH** |
| 10 | `NEXT_PUBLIC_API_BASE_URL` not yet set in Vercel | **HIGH** |
| 11 | `FRONTEND_CORS_ORIGINS` not yet set in Railway | **HIGH** |
| 12 | Railway backend not redeployed after `FRONTEND_CORS_ORIGINS` set | **HIGH** |
| 13 | Vapi test assistant not yet configured with Railway URL/headers | MEDIUM |
| 14 | n8n staging workflow not yet configured | LOW (optional for initial smoke) |

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
9. **Vapi staging tool proof** — Vapi test call → 200; row in DB; `status=new`; `action_required=True`
10. **Staff Confirm proof** — no auto-confirm; staff action required for status change
11. **n8n staging proof (if enabled)** — staging endpoint receives signed POST; no production calendar write

Once all rows in Section 4 are marked PASS, proceed to Module 109 (Staging Smoke
Execution Evidence — full end-to-end smoke documentation).
