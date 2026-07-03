# Sprint 15 / Module 107 — Vercel Frontend Project Creation Runbook

Status: pending Module 106 review.

## Context

Module 106 complete:
- `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` created (15 sections)
- `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` created (BLOCKED/PENDING — no Railway PostgreSQL yet)
- 25 contract tests; full suite: 2160/2160 passed

Sprint 15 sequence so far:
- Module 105 — Railway backend service creation runbook (READY)
- Module 106 — Railway PostgreSQL provisioning/migration runbook + evidence (BLOCKED/PENDING)
- Module 107 — Vercel frontend project creation runbook ← NEXT

Module 107 creates a human-executable runbook for creating the Vercel frontend project.
No actual Vercel deployment inside Claude. No real secrets. No frontend code changes.

## Scope

Docs/static tests only. No deployment. No real secrets. No runtime changes.

### 1. Read and audit current state

Read:
- docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md — Module 102 prep doc
- docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md — Module 105
- docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md — Module 106
- docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md — Module 96
- docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md — Module 97
- docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md — blocker list
- frontend/package.json — build/start commands
- frontend/.env.example
- frontend/next.config.js

### 2. Create `docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md`

Sections:
1. **Purpose** — human-executable Vercel frontend project creation guide; no Claude deployment
2. **Prerequisites** — Module 106 completion (Railway backend URL known); Vercel account; GitHub access; Railway backend `NEXT_PUBLIC_API_BASE_URL` source
3. **Step 1: Create Vercel project** — exact Vercel dashboard steps; import GitHub repo; framework auto-detect
4. **Step 2: Set root directory** — must be `frontend` (critical: without this Vercel fails to find `package.json`)
5. **Step 3: Configure build settings** — framework=Next.js (auto-detect); install=`npm install`; build=`npm run build`; output=`.next` (managed by Vercel); no `vercel.json` needed; no `output:standalone`
6. **Step 4: Set `NEXT_PUBLIC_API_BASE_URL`** — exact Railway backend HTTPS URL from Module 105; public var; baked into build; not a secret; must be set before first build
7. **Step 5: Trigger first deploy** — what Vercel does; expected build log; Next.js 14.2.3 build time
8. **Step 6: Capture Vercel URL** — the assigned `*.vercel.app` URL; needed for Module 108 CORS update
9. **CORS dependency note** — `FRONTEND_CORS_ORIGINS` on Railway cannot be finalized until this Vercel URL is known; document it before proceeding to Module 108
10. **No backend secrets in Vercel env** — `NEXT_PUBLIC_*` vars are public/baked into browser bundle; list what must never appear
11. **Evidence to capture** — Vercel project name; Vercel URL; `NEXT_PUBLIC_API_BASE_URL` name confirmed; build status; commit SHA; build log snippet; no secret values
12. **Failure triage** — build fails (root directory wrong; TypeScript error; env var missing); 404 on deploy; CORS error in browser (FRONTEND_CORS_ORIGINS not yet set; expected at this stage)
13. **Stop rules** — backend secrets in Vercel env; wrong `NEXT_PUBLIC_API_BASE_URL`; production data; build fails without obvious config fix
14. **Result states** — PASS / BLOCKED/PENDING / FAIL
15. **What this runbook does not cover** — CORS update on Railway (Module 108); Vapi config (Module 108); full smoke (Module 109)
16. **Recommended next** — Module 108: Staging Environment Wiring Evidence

### 3. Create `docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md`

Evidence doc with BLOCKED/PENDING if no Vercel project exists:
- Purpose (accuracy policy; no fabricated evidence)
- Current result (BLOCKED/PENDING if no Vercel URL available)
- Preconditions available/missing
- Evidence table (Vercel URL; build status; `NEXT_PUBLIC_API_BASE_URL` name; build log; commit SHA)
- Blockers if pending
- Next evidence needed

### 4. Static contract tests

Create `backend/tests/test_vercel_frontend_project_creation_runbook_contract.py`:
- Runbook doc exists
- Evidence doc exists
- Mentions Vercel frontend project
- Mentions fake/non-PHI staging
- Mentions no Claude deployment
- Mentions root directory `frontend`
- Mentions Next.js auto-detect
- Mentions `npm run build`
- Mentions `NEXT_PUBLIC_API_BASE_URL`
- Mentions Railway backend HTTPS URL
- Mentions public build-time variable (not a secret)
- Mentions no backend secrets in Vercel env
- Mentions `FRONTEND_CORS_ORIGINS` dependency on Vercel URL
- Mentions evidence capture
- Mentions stop rules
- Mentions PASS/BLOCKED/PENDING states
- Mentions Module 108
- Evidence doc mentions BLOCKED/PENDING
- No obvious real secrets in either doc

### 5. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 106 and Module 107
- `docs/claude/NEXT_MODULE.md` — Sprint 15 / Module 108: Staging Environment Wiring Evidence

## What not to do

- Do not create a Vercel project
- Do not run `npm install` or `npm run build`
- Do not add real secrets
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint
- Do not change DB schema or migration files

## Acceptance

- `docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` created
- `docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md` created (BLOCKED/PENDING if no Vercel project)
- Contract tests pass
- Full test suite passes (2160/2160 minimum)
- Commit: `Sprint 15 / Module 107 — Vercel frontend project creation runbook`
