# Sprint 13 / Module 97 — Staging Deployment Dry-Run Checklist

Status: pending Module 96 review.

## Context

Module 96 defined the complete staging environment variable matrix for Railway
(Backend + PostgreSQL) + Vercel (Frontend).

Key decisions from Modules 95–96:
- Staging backend: `https://staging-api.up.railway.app`
- Staging frontend: `https://staging-app.vercel.app`
- `DATABASE_URL`: auto-injected by Railway PostgreSQL add-on
- `FRONTEND_CORS_ORIGINS`: `https://staging-app.vercel.app` (exact; no wildcard)
- `NEXT_PUBLIC_API_BASE_URL`: `https://staging-api.up.railway.app`
- All secrets: Railway dashboard; high-entropy per-staging values
- Staging fake clinic UUID: distinct from local `11111111-...`; assigned at DB provisioning
- `seed_local_data.py` must NOT run in staging
- Backend start command: `python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

Module 97 produces a step-by-step pre-deployment dry-run checklist for the Railway +
Vercel staging topology. This is docs-first. No deployment execution. No real secrets.
No runtime code changes.

## Scope

### 1. Read and audit current state

Read:
- `docs/deployment/STAGING_DEPLOYMENT_TOPOLOGY_PLAN.md` — chosen topology (Module 95)
- `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` — full env var matrix (Module 96)
- `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` — canonical env var definitions
- `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` — smoke runbook (Module 94)
- `backend/scripts/run_migrations.py` — migration execution details
- `backend/app/main.py` — startup requirements
- `frontend/next.config.js` — Next.js build config
- `docker-compose.postgres.yml` — local DB context (for contrast with staging)

### 2. Create `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md`

Sections:
1. **Purpose** — dry-run checklist only; no deployment execution; no real secrets; Railway + Vercel; fake data only
2. **Prerequisites** — what must be true before the checklist begins (GitHub repo, test suite pass, local smoke pass, no real data)
3. **Phase 1 — Railway project setup** — project creation, service creation, GitHub connection; checklist format
4. **Phase 2 — Railway PostgreSQL provisioning** — add PostgreSQL add-on; verify DATABASE_URL auto-injected; no manual connection string
5. **Phase 3 — Railway backend environment variables** — set each var from Module 96 matrix in Railway dashboard; secret classification; how to verify each without printing
6. **Phase 4 — Railway backend start command** — set `run_migrations.py && uvicorn $PORT`; migration gate explanation
7. **Phase 5 — Migration verification** — how to confirm migrations ran; Railway log stream; expected output; failure triage
8. **Phase 6 — Backend smoke checks** — `/health`, `/health/ready`, `/auth/login` with staging credentials; no real data
9. **Phase 7 — Vercel project setup** — project creation, GitHub connection, framework detection (Next.js), build command, output directory
10. **Phase 8 — Vercel environment variable injection** — `NEXT_PUBLIC_API_BASE_URL`; verify staging value; no secrets in Vercel
11. **Phase 9 — Vercel build and deploy** — trigger build; verify `npm run build` passes; check function logs
12. **Phase 10 — Frontend smoke checks** — `/login` loads; login with staging credentials; dashboard visible; no CORS errors
13. **Phase 11 — CORS verification** — browser devtools → OPTIONS preflight → `Access-Control-Allow-Origin` matches staging frontend origin; no wildcard
14. **Phase 12 — Vapi staging configuration** — update Vapi test assistant server URL to Railway URL; set machine auth headers; remove ngrok URL; verify `vapi:tool` singular
15. **Phase 13 — Vapi smoke check** — trigger fake Vapi test call; verify appointment row created; status=new; staff Confirm; no auto-confirmation; no calendar booking
16. **Phase 14 — n8n staging configuration (optional)** — update n8n workflow webhook URL; set HMAC secret; test signed request; mark NOT ENABLED if deferred
17. **Phase 15 — Staging isolation verification** — confirm no local UUIDs in staging DB; no local-dev secrets in Railway; no production values; sessionStorage JWT only for fake data
18. **Phase 16 — Go/No-Go decision** — pass/fail checklist; conditions that block deployment; staging approval != production approval
19. **Non-goals** — no production launch; no auth refactor; no Fabel 5; no appointment workflow expansion; no CI/CD pipeline in this module

### 3. Static contract tests

Create `backend/tests/test_staging_deployment_dry_run_checklist_contract.py`:
- Checklist doc exists
- Mentions Railway
- Mentions Vercel
- Mentions PostgreSQL
- Mentions DATABASE_URL auto-injection
- Mentions migration gate
- Mentions `/health` and `/health/ready`
- Mentions CORS verification (OPTIONS preflight or Access-Control-Allow-Origin)
- Mentions no wildcard CORS
- Mentions `FRONTEND_CORS_ORIGINS`
- Mentions `NEXT_PUBLIC_API_BASE_URL`
- Mentions Vapi test assistant
- Mentions `vapi:tool` singular
- Mentions no ngrok
- Mentions no auto-confirmation
- Mentions staging fake clinic (not local `11111111-...` UUID)
- Mentions n8n (or deferred/NOT ENABLED note)
- Mentions sessionStorage JWT acceptable for fake staging only
- Mentions staging approval is not production approval
- Mentions no deployment execution in this module
- Mentions no real secrets
- Mentions fake/non-PHI data only
- Confirms no obvious real secrets in doc

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 97
- `docs/claude/NEXT_MODULE.md` — Module 98: Auth/Session Hardening Implementation Plan

## What not to do

- Do not execute any deployment
- Do not provision real infrastructure
- Do not add real production secrets or real domain names
- Do not change backend/frontend code
- Do not start the Fabel 5/UX sprint
- Do not implement httpOnly cookie auth yet (plan in Module 98)

## Acceptance

- `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` created
- Contract tests pass
- Full test suite passes (1832/1832 minimum)
- Commit: `Sprint 13 / Module 97 — Staging deployment dry-run checklist`
