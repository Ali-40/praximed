# Sprint 15 / Module 105 — Railway Backend Service Creation Runbook

Status: pending Architecture Checkpoint 14 review.

## Context

Architecture Checkpoint 14 decisions:
- Actual fake-data staging service creation: GO
- Production PHI launch: NO-GO
- Auth/session hardening: after staging smoke evidence
- Fabel 5/UX: deferred
- Appointment workflow expansion: deferred

Sprint 14 complete (Modules 100–104). Repo-side staging prep is fully READY.
External blockers are the only remaining items before staging smoke.

The immediate next external blocker is Railway backend service creation.

Module 105 creates a human-executable runbook for the Railway backend service creation step.
It does not execute any Railway commands. It does not create a Railway service.
It does not claim any service was created. It provides exact steps the developer can follow.

## Scope

Docs/static tests only. No deployment. No real secrets. No runtime changes.

### 1. Read and audit current state

Read:
- docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md — Module 101 prep doc
- docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md — Module 97 checklist
- docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md — Module 96 env matrix
- docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md — Module 104 blocker list
- Procfile — confirm start command
- runtime.txt — confirm Python version
- backend/requirements.txt — confirm deps
- backend/.env.example — confirm env var names

### 2. Create `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md`

Sections:
1. **Purpose** — human-executable runbook for Railway backend service creation; no actual deployment in this module
2. **Prerequisites** — Railway account; GitHub repo access; secrets generated with `openssl rand -hex 32`
3. **Step 1: Create Railway project and backend service** — exact Railway dashboard UI steps; GitHub repo connection; service settings
4. **Step 2: Configure Railway service settings** — root directory (repo root, not `backend/`); start command confirmation (reads from Procfile); Python version (from runtime.txt)
5. **Step 3: Set environment variables** — exact variable names and generation commands for all 6 Railway env vars (`DATABASE_URL` auto-injected; `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET` via `openssl rand -hex 32`; `FRONTEND_CORS_ORIGINS` placeholder until Vercel URL known; `APP_ENV=staging`)
6. **Step 4: Configure health check** — set health check path to `/health` in Railway service settings
7. **Step 5: Trigger initial deploy** — Railway auto-deploys on push or manual trigger; what Nixpacks does (installs Python 3.11; runs `pip install -r backend/requirements.txt`; starts with Procfile `web:` command)
8. **Step 6: Verify deploy** — Railway build logs to check; expected success indicators; common failure modes
9. **Step 7: Capture evidence** — Railway service URL; deploy log screenshot; `GET /health` curl result; sanitized output only (no DATABASE_URL value in evidence)
10. **Start command reference** — exact Procfile line: `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`; why `--host 0.0.0.0` (not 127.0.0.1); why `$PORT` (Railway injects it)
11. **Common failure modes and triage** — missing `requirements.txt` (should not happen); wrong root directory; `$PORT` not used; 503 on `/health` before DB is ready (health is DB-independent); wrong import path
12. **Safety constraints** — no real patient data; no production secrets; no local-dev placeholders; no ngrok; staging-only secrets
13. **Evidence checklist** — items to capture before proceeding to Module 106
14. **What Module 106 covers** — Railway PostgreSQL provisioning and migration evidence (next step after this runbook)

### 3. Static contract tests

Create `backend/tests/test_railway_backend_service_creation_runbook_contract.py`:
- Runbook doc exists
- Mentions Railway backend service
- Mentions GitHub repo connection
- Mentions Procfile or start command
- Mentions `--host 0.0.0.0`
- Mentions `$PORT`
- Mentions `python -m uvicorn backend.app.main:app`
- Mentions runtime.txt or Python 3.11
- Mentions backend/requirements.txt
- Mentions JWT_SECRET_KEY
- Mentions VAPI_WEBHOOK_SECRET
- Mentions `openssl rand -hex 32`
- Mentions FRONTEND_CORS_ORIGINS
- Mentions health check or `/health`
- Mentions DATABASE_URL auto-injected
- Mentions no deployment executed in this module
- Mentions fake/non-PHI staging
- Mentions no production secrets
- Mentions evidence capture
- Mentions Module 106
- No obvious real secrets

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Checkpoint 14 and Module 105
- `docs/claude/NEXT_MODULE.md` — Sprint 15 / Module 106: Railway PostgreSQL Provisioning and Migration Evidence

## What not to do

- Do not create a Railway service
- Do not add real production or staging secrets
- Do not implement httpOnly cookie auth
- Do not change backend/frontend runtime behavior
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint
- Do not change DB schema or migration files
- Do not run npm install

## Acceptance

- `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` created
- Contract tests pass
- Full test suite passes (2103/2103 minimum)
- Commit: `Sprint 15 / Module 105 — Railway backend service creation runbook`
