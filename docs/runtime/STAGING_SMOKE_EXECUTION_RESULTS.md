# Staging Smoke Execution Results — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 14 / Module 104
**Status:** BLOCKED/PENDING — staging services not yet created

---

## 1. Purpose

This document records the staging smoke execution status for PraxisMed.

**What this document is:**
- The authoritative record of whether staging smoke has been executed
- An accurate list of preconditions checked and blockers found
- A checklist of what the repo has ready vs. what requires external service creation
- The reference for Architecture Checkpoint 14 (staging deployment review)

**What this document is not:**
- A fabricated smoke pass — no evidence has been invented
- A deployment execution record — no deployment is run in this module
- A production launch plan — production PHI launch remains NO-GO
- A document containing real secrets, real patient data, or real staging URLs

**Accuracy policy:** This document reflects only what has been verified to exist.
No smoke step is marked PASS without real evidence from a real staging service.
Fabricating evidence would introduce false confidence into the deployment readiness record.

Staging uses fake/non-PHI data only. No production PHI launch. No real patient data.

---

## 2. Current Result

**Overall result: BLOCKED/PENDING**

Staging smoke cannot be executed because no staging services have been created.
The Railway backend service, Railway PostgreSQL add-on, and Vercel frontend project
do not exist at the time of this module's execution.

This result is **not a failure** — it is an accurate status. The repo is ready for
staging deployment per Modules 100–103. The missing items are external service creation
steps that require manual developer action outside this Claude Code session.

This document will be updated to PASS when:
1. Railway backend service is deployed and responding
2. Railway PostgreSQL is provisioned, migrated, and contains staging fake tenant/user
3. Vercel frontend is deployed with correct `NEXT_PUBLIC_API_BASE_URL`
4. All smoke steps listed in Section 4 are verified against real service responses

---

## 3. Preconditions Checked

| Precondition | Status | Notes |
|---|---|---|
| Railway backend service created | **MISSING** | No Railway service exists; no Railway project URL available |
| Railway PostgreSQL staging DB provisioned | **MISSING** | No Railway PostgreSQL add-on created; `DATABASE_URL` not yet available |
| Vercel frontend project created | **MISSING** | No Vercel project exists; no Vercel staging URL available |
| Staging API HTTPS URL | **UNKNOWN** | Assigned only after Railway service creation |
| Staging frontend HTTPS URL | **UNKNOWN** | Assigned only after first Vercel deployment |
| `JWT_SECRET_KEY` set in Railway dashboard | **MISSING** | Must be set before first Railway deploy |
| `VAPI_WEBHOOK_SECRET` set in Railway dashboard | **MISSING** | Must be set before Vapi smoke |
| `N8N_WEBHOOK_SECRET` set in Railway dashboard | **MISSING** | Required for n8n smoke; can be deferred if n8n is NOT ENABLED |
| `INTERNAL_WEBHOOK_SECRET` set in Railway dashboard | **MISSING** | Required for internal webhook routes |
| `FRONTEND_CORS_ORIGINS` set in Railway dashboard | **MISSING** | Cannot be set until Vercel URL is known |
| `NEXT_PUBLIC_API_BASE_URL` set in Vercel | **MISSING** | Cannot be set until Railway URL is known |
| Staging fake clinic UUID generated | **MISSING** | Placeholder `<staging-fake-clinic-id>` in Module 103 doc; not yet generated |
| Staging fake user created (`doctor.staging@praximed.test`) | **MISSING** | Not yet provisioned; staging DB does not exist |
| Staging bcrypt password hash generated | **MISSING** | Staging password not yet created |
| Migrations run against staging DB | **MISSING** | No Railway DB exists to run them against |
| Vapi test assistant staging tool URL configured | **MISSING** | Vapi assistant must point to Railway staging HTTPS URL |
| n8n staging workflow configured | **NOT ENABLED** | n8n staging smoke is optional; deferred until core smoke passes |
| Migration evidence captured | **NOT AVAILABLE YET** | No migration run; no sanitized output |
| Smoke evidence logs/screenshots | **NOT AVAILABLE YET** | No staging services; no evidence possible |

**Repo-side readiness (no external services required):**

| Item | Status |
|---|---|
| `backend/requirements.txt` | READY — 7 pinned runtime deps |
| `Procfile` | READY — `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
| `runtime.txt` | READY — `python-3.11` |
| `backend/.env.example` | READY — placeholder values; not committed |
| `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` | READY |
| `docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md` | READY |
| `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md` | READY |
| `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` | READY |
| `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` | READY |
| `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` | READY |
| `backend/scripts/run_migrations.py` | READY |
| `backend/scripts/db_smoke_test.py` | READY |
| All backend tests | READY — 2077/2077 passed locally |
| `frontend/package.json` build/start scripts | READY — `npm run build`, `npm start` |

---

## 4. Smoke Checklist

Each step below reflects the expected check during a real staging smoke execution.
Current status is PENDING for all steps because no staging services exist.

| # | Smoke Check | Expected Result | Current Status | Notes |
|---|---|---|---|---|
| 1 | `GET <staging-api-url>/health` | `{"status": "ok"}` — 200 | **PENDING** | Railway backend not deployed |
| 2 | `GET <staging-api-url>/health/ready` | `{"status": "ready"}` — 200 | **PENDING** | Requires DB connection |
| 3 | Database connection | `health/ready` returns 200; pool not None | **PENDING** | No Railway PostgreSQL |
| 4 | Migrations applied | `alembic_version` = `0002_password_hash`; all 11 tables exist | **PENDING** | Not yet run |
| 5 | Staging fake tenant exists | `clinics` row for staging clinic UUID | **PENDING** | Not yet provisioned |
| 6 | Staging fake user exists | `clinic_users` row for `doctor.staging@praximed.test` | **PENDING** | Not yet provisioned |
| 7 | Frontend loads at Vercel URL | 200; Next.js HTML returned | **PENDING** | Vercel project not created |
| 8 | `/login` renders | Login form visible in browser | **PENDING** | Vercel not deployed |
| 9 | CORS preflight from Vercel origin | `OPTIONS /auth/login` → correct `Access-Control-Allow-Origin` header | **PENDING** | `FRONTEND_CORS_ORIGINS` not set |
| 10 | Login with fake staging user | `POST /auth/login` → JWT returned | **PENDING** | No DB; no user row |
| 11 | JWT stored; `/dashboard` loads | 302→200; dashboard visible | **PENDING** | Requires login |
| 12 | Appointments section renders | Empty list or Vapi-created row | **PENDING** | Requires dashboard |
| 13 | Vapi test assistant fake call | `POST /vapi/tools/capture-appointment-request` → `status=new`, `action_required=true` | **PENDING** | Vapi assistant not configured for staging |
| 14 | Vapi-created row appears in dashboard | `appointment_requests` row visible | **PENDING** | Requires Vapi call to pass |
| 15 | Staff Confirm button works | `PATCH /appointment-requests/{id}/status` → `status=confirmed` | **PENDING** | Requires Vapi row |
| 16 | No auto-confirmation observed | No row starts with `status=confirmed` | **PENDING** | Verified only once rows exist |
| 17 | n8n fake calendar sync | `POST /webhooks/n8n/calendar-sync` → 200 | **NOT ENABLED** | Deferred; not required for first smoke |
| 18 | Logs sanitized | No `DATABASE_URL`, secrets, or PII in Railway log stream | **PENDING** | No logs available yet |
| 19 | Rollback path verified | Previous Vercel deployment can be promoted; Railway restartable | **PENDING** | No deployment to roll back |

---

## 5. Evidence Table

| Check | Evidence Required | Evidence Available? | Current Status | Notes |
|---|---|---|---|---|
| Backend health | HTTP 200 + `{"status":"ok"}` response body | **Not available yet** | PENDING | No Railway service |
| Database ready | HTTP 200 from `/health/ready` | **Not available yet** | PENDING | No Railway PostgreSQL |
| Migrations applied | Sanitized `alembic upgrade head` output; final revision `0002_password_hash` | **Not available yet** | PENDING | Not yet run |
| DB smoke test | `db_smoke_test.py` output showing all tables present | **Not available yet** | PENDING | Not yet run |
| Fake clinic in DB | `SELECT id FROM clinics WHERE slug='staging-fake-clinic'` → 1 row | **Not available yet** | PENDING | Not yet provisioned |
| Fake user in DB | `SELECT id FROM clinic_users WHERE email='doctor.staging@praximed.test'` → 1 row | **Not available yet** | PENDING | Not yet provisioned |
| Frontend loads | Browser screenshot or curl 200 from Vercel URL | **Not available yet** | PENDING | No Vercel project |
| CORS success | Browser network tab: no CORS error on login; correct headers | **Not available yet** | PENDING | `FRONTEND_CORS_ORIGINS` not set |
| Login smoke | JWT returned; `sessionStorage.praximed_access_token` populated | **Not available yet** | PENDING | No staging services |
| Vapi intake | `appointment_requests` row with `status=new`, `action_required=true` | **Not available yet** | PENDING | Vapi not configured for staging |
| Staff Confirm | `appointment_requests` row updated to `status=confirmed` after PATCH | **Not available yet** | PENDING | Requires Vapi row |
| No auto-confirm | No row with `status=confirmed` before staff action | **Not available yet** | PENDING | Verified once rows exist |
| Sanitized logs | Railway log screenshot with no secrets or PII visible | **Not available yet** | PENDING | No Railway service |

---

## 6. Blockers Preventing Staging Smoke

The following external actions must be completed before any smoke step can be attempted.
These require manual developer action and cannot be performed inside this Claude Code session.

| # | Blocker | Level |
|---|---|---|
| 1 | Railway backend service not created | **HIGH** |
| 2 | Railway PostgreSQL add-on not provisioned | **HIGH** |
| 3 | Vercel frontend project not created | **HIGH** |
| 4 | Staging API HTTPS URL not known (assigned by Railway after service creation) | **HIGH** |
| 5 | Staging frontend HTTPS URL not known (assigned by Vercel after first deploy) | **HIGH** |
| 6 | `JWT_SECRET_KEY` not set in Railway dashboard | **HIGH** |
| 7 | `VAPI_WEBHOOK_SECRET` not set in Railway dashboard | **HIGH** |
| 8 | `FRONTEND_CORS_ORIGINS` not set (depends on Vercel URL — unknown until Vercel deployed) | **HIGH** |
| 9 | `NEXT_PUBLIC_API_BASE_URL` not set in Vercel (depends on Railway URL — unknown until Railway deployed) | **HIGH** |
| 10 | Staging fake clinic UUID not generated; staging DB row not inserted | **HIGH** |
| 11 | Staging fake user (`doctor.staging@praximed.test`) not provisioned | **HIGH** |
| 12 | Staging bcrypt password not generated | **HIGH** |
| 13 | Migrations not run against staging DB | **HIGH** |
| 14 | Vapi test assistant staging tool URL not configured | **HIGH** |
| 15 | n8n staging workflow not configured (deferred; NOT ENABLED for first smoke) | MEDIUM |

---

## 7. What Is Ready (Repo-Side)

The following items are complete in the repository and do not block staging deployment:

| Item | Status | Source Module |
|---|---|---|
| `backend/requirements.txt` — 7 pinned runtime deps | READY | Module 101 |
| `Procfile` — uvicorn with `--host 0.0.0.0 --port $PORT` | READY | Module 101 |
| `runtime.txt` — `python-3.11` | READY | Module 101 |
| `.gitignore` coverage — `backend/.env`, `frontend/.env.local`, `frontend/.next/`, `frontend/node_modules/` | READY | Module 101 |
| `backend/scripts/run_migrations.py` — reads `DATABASE_URL`; runs `alembic upgrade head`; exits non-zero on failure | READY | Module 45 / verified Module 103 |
| `backend/scripts/db_smoke_test.py` — verifies 4 core tables after migrations | READY | Module 45 / verified Module 103 |
| `backend/migrations/versions/0001_initial_schema.py` — full 11-table schema | READY | Module 45 |
| `backend/migrations/versions/0002_add_password_hash_to_clinic_users.py` — adds `password_hash` column | READY | Module 59 |
| `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` — env vars, migration strategy, CORS rules | READY | Module 101 |
| `docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md` — project settings, env vars, CORS bootstrap | READY | Module 102 |
| `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md` — migration command, fake tenant strategy, seed rules | READY | Module 103 |
| `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` — step-by-step pre-deploy checklist | READY | Module 97 |
| `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` — smoke steps and failure triage | READY | Module 94 |
| `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` — per-variable spec for all staging components | READY | Module 96 |
| Frontend `npm run build` — verified locally (Module 77); no `output: standalone`; no `vercel.json` needed | READY | Module 77 |
| All backend tests — 2077/2077 passed locally | READY | Module 103 |
| `frontend/lib/api.ts` — reads `NEXT_PUBLIC_API_BASE_URL`; falls back to `http://127.0.0.1:8000` | READY | Verified Module 102 |
| `frontend/lib/auth.ts` — `sessionStorage` JWT; acceptable for fake-data staging only | READY | Verified Module 102 |

**No runtime code changes are required before staging deployment.** The repo is ready
to deploy. All blockers are external service creation steps.

---

## 8. What Must Happen Before Real Smoke

Ordered checklist — complete in this sequence:

| Step | Action | Depends On |
|---|---|---|
| 1 | Create Railway backend service (link to GitHub repo; set root to repo root) | Railway account |
| 2 | Create Railway PostgreSQL add-on and link to backend service | Step 1 |
| 3 | Wait for Railway PostgreSQL to show "Running" status | Step 2 |
| 4 | Set Railway backend env vars: `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`, `APP_ENV=staging` (use `openssl rand -hex 32` for each secret) | Step 1 |
| 5 | Deploy Railway backend; confirm Railway HTTPS URL assigned | Step 4 |
| 6 | Run `python backend/scripts/run_migrations.py` via Railway "Run Command" | Step 3 + Step 5 |
| 7 | Verify migrations: run `python backend/scripts/db_smoke_test.py` via Railway "Run Command" | Step 6 |
| 8 | Provision staging fake clinic and user via reviewed SQL (see Module 103 Section 8) | Step 6 |
| 9 | Create Vercel frontend project (root directory = `frontend`; Next.js auto-detect) | Vercel account |
| 10 | Set `NEXT_PUBLIC_API_BASE_URL` in Vercel to the Railway HTTPS URL from Step 5 | Step 5 + Step 9 |
| 11 | Deploy Vercel frontend; confirm Vercel HTTPS URL assigned | Step 10 |
| 12 | Set `FRONTEND_CORS_ORIGINS` in Railway dashboard to the exact Vercel URL from Step 11 | Step 11 |
| 13 | Restart or redeploy Railway backend (picks up new `FRONTEND_CORS_ORIGINS`) | Step 12 |
| 14 | Verify CORS preflight: `OPTIONS /auth/login` from Vercel origin returns correct headers | Step 13 |
| 15 | Configure Vapi test assistant staging tool URL to Railway HTTPS URL + `/vapi/tools/capture-appointment-request`; set `X-Clinic-Ref` to staging clinic UUID | Step 8 |
| 16 | Execute smoke checklist from Section 4 in order; stop on first failure | Steps 7–15 |
| 17 | Capture sanitized evidence for each smoke step (no secrets, no PII) | Step 16 |
| 18 | Update this document with PASS/FAIL result and real evidence | Step 17 |

---

## 9. Safety Constraints

All of the following must hold throughout staging smoke execution:

| Constraint | Detail |
|---|---|
| Fake/non-PHI data only | No real patient names, phone numbers, DOBs, or medical records in any staging row, log, or Vapi test call |
| No real patients | All appointment requests created during staging smoke use synthetic fake caller data |
| No production secrets | Staging secrets (`JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, etc.) must be freshly generated for staging; they must not match local-dev placeholders or future production secrets |
| No production DB | Staging Railway PostgreSQL is isolated from any future production DB; `DATABASE_URL` on staging must never point to a production database |
| No local-dev password in staging | The staging bcrypt hash must not be the hash of `local-dev-password` |
| No ngrok in staging | Vapi test assistant and `FRONTEND_CORS_ORIGINS` must use Railway/Vercel HTTPS URLs, not ngrok |
| No wildcard CORS | `FRONTEND_CORS_ORIGINS` must be the exact Vercel staging URL; `_cors_origins()` in `main.py` never returns `*` |
| No auto-confirmation | `appointment_requests` rows are always created with `status='new'`, `action_required=True`; no code path auto-confirms; stop if any row observed with `status='confirmed'` before staff action |
| Staff Confirm required | `PATCH /appointment-requests/{id}/status` requires a valid JWT and explicit staff action; cannot be bypassed by AI or automation |
| `sessionStorage` JWT acceptable for staging | The current frontend auth uses `sessionStorage`; this is acceptable for fake-data staging only; not PHI-safe for production |
| Stop on any stop rule | Any failure in the blockers listed in Module 103 Section 14 halts staging smoke immediately |

---

## 10. Recommended Next Step — Architecture Checkpoint 14

**Architecture Checkpoint 14 — Staging Deployment Review**

With Sprint 14 Modules 100–104 complete (prep documentation and accurate blocker status
recorded), Architecture Checkpoint 14 should:

- Review Sprint 14 deliverables (Modules 100–103 complete; Module 104 BLOCKED/PENDING)
- Decide whether to proceed from prep documents to actual Railway/Vercel staging service
  creation as the next developer action
- Confirm that Module 104 remains PENDING until real staging services exist, at which
  point it should be rerun to record actual PASS evidence
- Keep production PHI launch NO-GO (all 12 production blockers remain open)
- Keep auth/session hardening (httpOnly cookie) scheduled for Sprint 14 post-smoke
  evidence — implement only after M1/M2 evidence confirms staging is stable
- Keep Fabel 5/UX sprint deferred until staging topology confirmed and auth hardened
- Keep appointment workflow expansion deferred

The checkpoint does not authorize production launch. It reviews staging prep readiness
and decides the sequencing for actual service creation.
