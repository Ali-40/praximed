# Sprint 13 / Module 96 — Staging Environment Variable Matrix

Status: pending Module 95 commit.

## Context

Module 95 chose the staging topology: **Railway (Backend + PostgreSQL) + Vercel (Frontend)**.

Key decisions from Module 95:
- Staging backend: `https://staging-api.up.railway.app`
- Staging frontend: `https://staging-app.vercel.app`
- `FRONTEND_CORS_ORIGINS`: `https://staging-app.vercel.app` (exact; no wildcard)
- `NEXT_PUBLIC_API_BASE_URL`: `https://staging-api.up.railway.app`
- `DATABASE_URL`: auto-injected by Railway PostgreSQL add-on
- All other staging secrets: set via Railway and Vercel dashboard env var UI
- No deployment executed in Module 95; no runtime code changed

Module 96 maps every env var the stack consumes to its staging value,
injection method, secret classification, and rotation policy for the Railway+Vercel platform.
This is docs-first. No deployment execution. No production secrets.

## Scope

### 1. Read and audit current state

Read:
- `docs/deployment/STAGING_DEPLOYMENT_TOPOLOGY_PLAN.md` — chosen topology
- `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` — canonical env var definitions
- `docs/deployment/PRODUCTION_READINESS_INVENTORY.md` — env var list from inventory
- `backend/.env.example` — backend env var template
- `frontend/.env.example` — frontend env var template
- `backend/app/main.py` — confirms which env vars are consumed at startup
- `frontend/lib/api.ts` — confirms NEXT_PUBLIC_API_BASE_URL usage

### 2. Create `docs/deployment/STAGING_ENV_VAR_MATRIX.md`

Sections:
1. **Purpose** — staging only; fake data; no PHI; no production values in this document
2. **Platform summary** — Railway (backend + PostgreSQL) + Vercel (frontend) per Module 95
3. **Backend env var matrix** — table with: var name, staging value or placeholder, injection platform (Railway), injection method (dashboard / CLI / auto), secret classification (secret / non-secret), rotation policy for staging
4. **Frontend env var matrix** — table with: var name, staging value, injection platform (Vercel), injection method, secret classification
5. **DATABASE_URL** — special section: auto-injected by Railway PostgreSQL add-on; format `postgresql://user:pass@host:port/db`; never hardcoded; Railway sets this automatically when PostgreSQL add-on is attached
6. **Secret generation instructions** — how to generate each secret value for staging (openssl rand -hex 32); which vars get unique per-environment values; which are platform-auto-injected
7. **Injection walkthrough** — step-by-step instructions for setting env vars in the Railway dashboard and the Vercel dashboard; no actual secrets shown
8. **CORS constraint** — `FRONTEND_CORS_ORIGINS` must be set to `https://staging-app.vercel.app` exactly; no wildcard; no localhost; enforced by `_cors_origins()` in `main.py`
9. **Vapi staging env var** — which env var the Vapi test assistant uses (the Railway URL); set on Vapi dashboard, not in Railway/Vercel
10. **n8n staging env var** — `N8N_WEBHOOK_SECRET` staging value; n8n workflow points to Railway URL
11. **Env var validation at startup** — what happens if a required var is missing (FastAPI startup failure; Alembic migration error); how to verify all vars are set before deploying
12. **Staging isolation guarantee** — staging vars are distinct from local and production; no value overlap; no production secret used in staging
13. **What NOT to put in env vars** — no real patient data; no production JWT secrets; no production database password
14. **Next step** — Module 97: Staging Deployment Dry-Run Checklist

### 3. Static contract tests

Create `backend/tests/test_staging_env_var_matrix_contract.py`:
- Matrix doc exists
- Mentions Railway as injection platform for backend vars
- Mentions Vercel as injection platform for frontend vars
- Mentions DATABASE_URL auto-injection by Railway PostgreSQL add-on
- Mentions JWT_SECRET_KEY
- Mentions VAPI_WEBHOOK_SECRET
- Mentions N8N_WEBHOOK_SECRET
- Mentions INTERNAL_WEBHOOK_SECRET
- Mentions FRONTEND_CORS_ORIGINS with staging value
- Mentions NEXT_PUBLIC_API_BASE_URL with staging value
- Mentions openssl rand or equivalent secret generation
- Mentions Railway dashboard (injection walkthrough)
- Mentions Vercel dashboard (injection walkthrough)
- No wildcard in CORS
- Mentions staging isolation (distinct from local and production)
- Mentions what happens if a required var is missing
- Mentions fake/non-PHI data only
- Mentions no deployment in this module
- Mentions Module 97 as next step
- No obvious real secrets in the document

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 96
- `docs/claude/NEXT_MODULE.md` — Module 97: Staging Deployment Dry-Run Checklist

## What not to do

- Do not execute any deployment
- Do not provision real infrastructure
- Do not add real production secrets or real domain names
- Do not change backend/frontend code
- Do not start the Fabel 5/UX sprint
- Do not implement httpOnly cookie auth yet

## Acceptance

- `docs/deployment/STAGING_ENV_VAR_MATRIX.md` created
- Contract tests pass
- Full test suite passes (1798/1798 minimum)
- Commit: `Sprint 13 / Module 96 — Staging environment variable matrix`
