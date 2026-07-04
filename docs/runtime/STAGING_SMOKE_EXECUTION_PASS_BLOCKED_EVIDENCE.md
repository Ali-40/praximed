# Staging Smoke Execution PASS/BLOCKED Evidence — PraxisMed

**Date:** 2026-07-04
**Sprint:** Sprint 16 / Module 116
**Status:** BLOCKED/PENDING — backend/PostgreSQL/migrations/fake clinic+user/direct login PASS; Vercel/CORS/browser dashboard/Vapi/n8n PENDING

---

## 1. Purpose

This document is the final Sprint 15 staging smoke evidence record for PraxisMed.
It captures whether the full staging smoke — Railway backend, Railway PostgreSQL,
Vercel frontend, Vapi test assistant, and optional n8n — has been executed and passed.

**What this document is:**
- The authoritative PASS/BLOCKED record for Sprint 15 staging smoke
- A precise checklist of every smoke step and its current status
- The trigger document for Architecture Checkpoint 15 once PASS is recorded

**What this document is not:**
- A document containing fabricated evidence — no step is marked PASS without real proof
- A deployment executed by Claude — no Railway or Vercel actions are taken here
- A production launch plan — production PHI launch remains NO-GO
- A document containing real secrets, real staging URLs, or real patient data

**Accuracy policy:** No smoke step is marked PASS without real evidence from a real
staging service. Fabricating evidence would introduce false confidence into the
deployment readiness record. If a step has not been executed against a real service,
its status is PENDING or BLOCKED.

Staging uses fake/non-PHI data only. No production PHI launch. No real patient data.
No production secrets. No fabricated success.

---

## 2. Current Result

**Overall result: BLOCKED/PENDING**

Railway backend service (Module 112 PASS), Railway PostgreSQL, and migrations
(Module 114 PASS) are confirmed. Staging fake clinic/user, Vercel frontend, CORS
wiring, Vapi, and n8n remain PENDING. Overall staging smoke cannot be marked PASS
until all smoke checklist steps in Section 4 are confirmed with real evidence.

Sprint 15/16 runbooks confirmed READY:
- Module 105: Railway backend service creation runbook (READY)
- Module 106: Railway PostgreSQL provisioning and migration runbook (READY)
- Module 107: Vercel frontend project creation runbook (READY)
- Module 108: Staging environment wiring runbook (READY)

This document becomes PASS when all smoke steps in Section 4 are executed against real
services and evidence is provided by the developer.

---

## 3. Evidence Status Summary

| Component | Evidence Required | Evidence Available? | Current Status | Notes |
|---|---|---|---|---|
| Railway backend service | Service URL; `/health` → 200 | `https://web-production-fd91d.up.railway.app` — commit `081121b` | **PASS** |
| Railway backend `/health` | HTTP 200; `{"status": "ok", "service": "PraxisMed API"}` | `{"status":"ok","service":"PraxisMed API"}` — HTTP 200 | **PASS** |
| Railway PostgreSQL | `DATABASE_URL` auto-injected; PostgreSQL "Running" | Online; DATABASE_URL wired — Module 114 | **PASS** |
| Migrations | `run_migrations.py` exit 0; `0002_password_hash (head)` | Exit 0; both revisions applied; 4 tables confirmed — Module 114 | **PASS** |
| Fake staging clinic/user | SELECT confirms rows; clinic UUID recorded; email `doctor.staging@praximed.test` | `clinic_id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056`; `user_id=5b63b514-7624-4e8e-9af0-71c153ba7b83`; both `active` — Module 115 | **PASS** |
| Vercel frontend | Project URL; build success | Not available yet | PENDING | Module 107 runbook READY |
| Vercel `/login` | Page renders in browser; no 404 | Not available yet | PENDING | Requires Vercel deploy |
| CORS browser call | OPTIONS → `Access-Control-Allow-Origin` matches Vercel URL; no wildcard | Not available yet | PENDING | Requires `FRONTEND_CORS_ORIGINS` set |
| Dashboard login | JWT in sessionStorage; redirect to `/dashboard` | Not available yet | PENDING | Requires fake user + CORS |
| Dashboard protected route | `/dashboard` renders; appointment list visible | Not available yet | PENDING | Requires login |
| Appointment Confirm | `PATCH /appointment-requests/{id}/status` → `status=confirmed`; staff action only | Not available yet | PENDING | Requires existing row |
| Vapi test assistant call | POST to `/vapi/tools/capture-appointment-request` → 200 | Not available yet | PENDING | Requires Vapi config |
| Vapi-created appointment row | Row in DB: `status=new`, `action_required=True` | Not available yet | PENDING | Requires Vapi call |
| Staff Confirm Vapi row | Row updated to `status=confirmed` after staff action; no auto-confirmation | Not available yet | PENDING | Requires Vapi row |
| n8n staging fake sync | POST to n8n endpoint → 200; no production calendar write | Not available yet | NOT ENABLED / DEFERRED | Optional for initial smoke |
| Logs sanitized | No `DATABASE_URL`, secrets, or PII in Railway log stream | Not available yet | PENDING | Confirmed from Railway log view |
| Rollback path | Previous Railway/Vercel deployment can be restored | Not available yet | PENDING | Documented in runbooks |

---

## 4. Smoke Checklist Status

Each check below reflects the expected verification during real staging smoke execution.
All are PENDING because no staging services exist at this time.

| # | Smoke Check | Expected Pass Signal | Current Status | Blocker |
|---|---|---|---|---|
| 1 | Backend `/health` | HTTP 200; `{"status": "ok", "service": "PraxisMed API"}` | **PASS** — `https://web-production-fd91d.up.railway.app/health` → `{"status":"ok","service":"PraxisMed API"}` (commit `081121b`) | — |
| 2 | Database connection `/health/ready` | HTTP 200; `{"status": "ready", "checks": {"app": "ok"}}` | **PASS** — `https://web-production-fd91d.up.railway.app/health/ready` → 200 (Module 116) | — |
| 3 | Migrations applied | `alembic current` → `0002_password_hash (head)`; `run_migrations.py` exit 0 | **PASS** — exit 0; `0001_initial_schema` + `0002_password_hash` applied; 4 tables confirmed (Module 114) | — |
| 4 | Frontend `/login` | Page renders in browser; login form visible; no 404 or blank page | **PENDING** | Vercel project not created |
| 5 | CORS frontend to API | OPTIONS preflight → `Access-Control-Allow-Origin: <vercel-url>`; HTTP 200/204; no wildcard | **PENDING** | `FRONTEND_CORS_ORIGINS` not set; wiring incomplete |
| 6 | Fake login (direct backend) | `POST /auth/login` with `doctor.staging@praximed.test` → JWT returned | **PASS** — HTTP 200; `access_token` present (REDACTED); `token_type=bearer` (Module 116) | — |
| 7 | Protected dashboard | `/dashboard` returns 200; appointment list renders (may be empty) | **PENDING** | Requires login |
| 8 | Dashboard sections render | Appointment cards / empty state visible; no 500 errors in browser console | **PENDING** | Requires dashboard load |
| 9 | Staff Confirm existing appointment | `PATCH /appointment-requests/{id}/status` → `status=confirmed`; staff-initiated only | **PENDING** | No existing rows; no DB |
| 10 | Vapi test assistant fake call | Vapi initiates POST to `/vapi/tools/capture-appointment-request` → HTTP 200; tool returns appointment data | **PENDING** | Vapi test assistant not configured for staging |
| 11 | Vapi-created row in dashboard | New `appointment_requests` row visible with `status=new` | **PENDING** | Requires Vapi call |
| 12 | Staff Confirm Vapi row | Row status updates to `confirmed` after staff PATCH; `action_required` becomes `False` | **PENDING** | Requires Vapi row |
| 13 | n8n fake calendar sync | POST to n8n endpoint → 200; no production calendar write | **NOT ENABLED** | Deferred; not required for initial smoke PASS |
| 14 | Logs sanitized | Railway log stream visible; no `DATABASE_URL`, secrets, or PII visible in log output | **PENDING** | No Railway service |
| 15 | Rollback path known | Previous Vercel deployment can be promoted; Railway service restartable; `alembic downgrade -1` known | **PENDING** | No deployments exist to roll back |

---

## 5. Repo-Side Readiness

The following repo-side items are confirmed ready. No code changes are required before
staging deployment.

| Item | Path | Status |
|---|---|---|
| Start command | `Procfile` — `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | READY |
| Python version | `runtime.txt` — `python-3.11` | READY |
| Runtime dependencies | `backend/requirements.txt` — 7 pinned deps | READY |
| Migration runner | `backend/scripts/run_migrations.py` | READY |
| DB smoke test | `backend/scripts/db_smoke_test.py` — 4 tables | READY |
| Migration files | `0001_initial_schema.py` + `0002_add_password_hash_to_clinic_users.py` | READY |
| Frontend build | `frontend/package.json` — `"build": "next build"` | READY |
| Next.js config | `frontend/next.config.js` — no `output: 'standalone'`; no `vercel.json` needed | READY |
| Frontend env example | `frontend/.env.example` — `NEXT_PUBLIC_API_BASE_URL` documented | READY |
| CORS implementation | `backend/app/main.py` — `_cors_origins()` never returns `*` | READY |
| Railway backend runbook | `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` | READY |
| Railway PostgreSQL runbook | `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` | READY |
| Vercel frontend runbook | `docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` | READY |
| Wiring runbook | `docs/deployment/STAGING_ENVIRONMENT_WIRING_RUNBOOK.md` | READY |
| DB migration/seed strategy | `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md` | READY |
| Smoke runbook | `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` | READY |
| All backend tests | `backend/tests/` | READY — 2237/2237 passed |

---

## 6. External Blockers

All of the following require manual developer action before any smoke step can be marked PASS.

| # | Blocker | Level |
|---|---|---|
| 1 | Railway backend service not created (Module 105 runbook READY) | **HIGH** |
| 2 | Railway backend HTTPS URL not known | **HIGH** |
| 3 | Railway PostgreSQL not provisioned (Module 106 runbook READY) | **HIGH** |
| 4 | `DATABASE_URL` not auto-injected into Railway backend | **HIGH** |
| 5 | Migrations not run against Railway PostgreSQL | **HIGH** |
| 6 | Staging fake clinic not provisioned | **HIGH** |
| 7 | Staging fake user (`doctor.staging@praximed.test`) not provisioned | **HIGH** |
| 8 | Vercel frontend project not created (Module 107 runbook READY) | **HIGH** |
| 9 | Vercel frontend URL not known | **HIGH** |
| 10 | `NEXT_PUBLIC_API_BASE_URL` not set in Vercel | **HIGH** |
| 11 | `FRONTEND_CORS_ORIGINS` not set in Railway (Module 108 runbook READY) | **HIGH** |
| 12 | Vapi test assistant not pointed to staging Railway URL | **HIGH** |
| 13 | Rollback path not confirmed (no deployments exist yet) | MEDIUM |
| 14 | n8n staging workflow not configured | LOW (optional for initial smoke) |

---

## 7. PASS Criteria for Future Rerun

This document transitions from BLOCKED/PENDING to PASS only when **all** of the
following are confirmed with real evidence:

| PASS Requirement | Evidence Required |
|---|---|
| Railway backend `/health` returns 200 | `curl` output or browser; exact JSON; HTTP status code |
| Railway backend `/health/ready` returns 200 | Confirms DB pool connected; migrations applied |
| Migrations run successfully against Railway PostgreSQL | `run_migrations.py` exit code 0; sanitized output; `alembic current` = `0002_password_hash (head)` |
| Staging fake clinic row exists in DB | `SELECT` output showing clinic UUID with `slug='staging-fake-clinic'`; no secrets |
| Staging fake user row exists in DB | `SELECT` showing `doctor.staging@praximed.test`; no password hash in evidence |
| Vercel `/login` loads | Browser confirmation; no 404; login form visible |
| CORS preflight passes | OPTIONS → `Access-Control-Allow-Origin` = exact Vercel URL; no wildcard; HTTP 200/204 |
| Fake login succeeds | `POST /auth/login` → JWT; sessionStorage populated; `/dashboard` loads |
| Protected dashboard renders | Appointment list visible (may be empty); no 500 errors |
| Vapi test call creates row | POST to `/vapi/tools/capture-appointment-request` → 200; row in DB |
| Vapi row has `status=new`, `action_required=True` | DB query or dashboard confirmation |
| Staff Confirm works | `PATCH /appointment-requests/{id}/status` → `status=confirmed`; staff-initiated only |
| No auto-confirmation observed | No row shows `status=confirmed` before staff action |
| n8n staging passes OR is explicitly NOT ENABLED | PASS result or explicit "NOT ENABLED — deferred" notation |
| Railway logs contain no secrets or PII | Log screenshot or excerpt; no `DATABASE_URL` value; no passwords |
| Rollback path documented | Previous Railway/Vercel deployment identified; `alembic downgrade -1` command noted |

---

## 8. Safety Constraints

All of the following must hold throughout staging smoke execution:

| Constraint | Detail |
|---|---|
| Fake/non-PHI data only | No real patient names, phone numbers, DOBs, or medical records in any staging row, log, or Vapi test call |
| No production secrets | Staging secrets (`JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, etc.) are freshly generated; no overlap with local-dev or production |
| No production DB | Staging `DATABASE_URL` points to Railway-provisioned staging PostgreSQL only |
| No real patients | All Vapi test calls use synthetic fake caller data |
| No local-dev password | Staging bcrypt hash must not be the hash of `local-dev-password` |
| No ngrok in staging | Vapi and CORS must use Railway/Vercel HTTPS URLs; no ngrok tunnel |
| No wildcard CORS | `FRONTEND_CORS_ORIGINS` must be the exact Vercel HTTPS URL; `*` is forbidden |
| HTTPS staging URLs only | All Railway and Vercel URLs use HTTPS; no HTTP |
| Vapi test assistant only | Use a Vapi test assistant, not the production Vapi assistant |
| No auto-confirmation | `appointment_requests` rows always created with `status='new'` and `action_required=True`; stop if auto-confirmed |
| Staff Confirm required | Status change to `confirmed` requires explicit staff action via `PATCH /appointment-requests/{id}/status` |
| sessionStorage JWT is fake-data-only | JWT stored in `sessionStorage` is XSS-accessible; acceptable for fake-data staging; must be replaced with httpOnly cookie auth before production PHI access |

---

## 9. Next Human Actions

Complete these steps in order to rerun and pass staging smoke:

| Step | Action | Runbook |
|---|---|---|
| 1 | Create Railway backend service; confirm `/health` → 200 | `RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` |
| 2 | Create Railway PostgreSQL; confirm `DATABASE_URL` auto-injected; `/health/ready` → 200 | `RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` |
| 3 | Run `python backend/scripts/run_migrations.py` via Railway "Run Command"; confirm exit 0 | `RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` |
| 4 | Provision staging fake clinic and user via SQL; confirm `SELECT` returns rows | `RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` |
| 5 | Create Vercel frontend project; root dir = `frontend`; confirm build succeeds | `VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` |
| 6 | Set `NEXT_PUBLIC_API_BASE_URL` in Vercel to Railway backend HTTPS URL; confirm Vercel redeploy | `VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` |
| 7 | Set `FRONTEND_CORS_ORIGINS` on Railway to exact Vercel URL; redeploy Railway backend | `STAGING_ENVIRONMENT_WIRING_RUNBOOK.md` |
| 8 | Configure Vapi test assistant: server URL, `X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes: vapi:tool` | `STAGING_ENVIRONMENT_WIRING_RUNBOOK.md` |
| 9 | Configure n8n staging workflow (if enabled); confirm HMAC secret matches `N8N_WEBHOOK_SECRET` | `STAGING_ENVIRONMENT_WIRING_RUNBOOK.md` |
| 10 | Run all smoke checks in Section 4 in order; stop on first failure | `DEPLOYMENT_SMOKE_RUNBOOK.md` |
| 11 | Capture sanitized evidence for each PASS step; update this document | This document |
| 12 | Proceed to Architecture Checkpoint 15 | `docs/claude/NEXT_MODULE.md` |

---

## 10. Recommended Next Step — Architecture Checkpoint 15

**Architecture Checkpoint 15 — Staging Deployment Evidence Review**

With Sprint 15 Modules 105–109 complete (all human-executable runbooks created;
staging smoke evidence BLOCKED/PENDING), Architecture Checkpoint 15 should:

- Review Sprint 15 deliverables (Modules 105–109 all complete; all runbooks READY)
- Decide that further documentation is not needed — the next action is manual service
  creation by the developer using the Sprint 15 runbooks
- Identify the exact first manual action: follow `RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md`
- Confirm production PHI launch remains NO-GO until staging smoke evidence is PASS
- Confirm auth/session hardening (httpOnly cookie) is scheduled after fake-data staging smoke PASS
- Confirm Fabel 5/UX sprint remains deferred
- Confirm appointment workflow expansion remains deferred
- Confirm no further runbook or evidence template docs are needed before manual work begins
