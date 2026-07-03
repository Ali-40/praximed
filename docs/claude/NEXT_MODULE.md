# Sprint 15 / Module 108 — Staging Environment Wiring Evidence

Status: pending Module 107 review.

## Context

Module 107 complete:
- `docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` created (14 sections)
- `docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md` created (BLOCKED/PENDING — no Vercel project yet)
- 28 contract tests; full suite: 2188/2188 passed

Sprint 15 sequence so far:
- Module 105 — Railway backend service creation runbook (READY)
- Module 106 — Railway PostgreSQL provisioning/migration runbook + evidence (BLOCKED/PENDING)
- Module 107 — Vercel frontend project creation runbook + evidence (BLOCKED/PENDING)
- Module 108 — Staging environment wiring evidence ← NEXT

Module 108 creates the evidence document for staging environment wiring:
setting `FRONTEND_CORS_ORIGINS` on Railway after the Vercel URL is known,
confirming CORS preflight passes, and confirming the frontend and backend are
fully connected for fake-data staging smoke.

No actual deployment inside Claude. No real secrets. No runtime code changes.

## Scope

Docs/static tests only. No deployment. No real secrets. No runtime changes.

### 1. Read and audit current state

Read:
- docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md — Module 107
- docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md — Module 105
- docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md — Module 106
- docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md — Module 96
- docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md — blocker list
- docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md — Module 107 evidence
- docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md — Module 106 evidence
- backend/app/main.py — _cors_origins() implementation

### 2. Create `docs/deployment/STAGING_ENVIRONMENT_WIRING_RUNBOOK.md`

Sections:
1. **Purpose** — human-executable guide for wiring Railway backend and Vercel frontend together; CORS finalization; no Claude deployment
2. **Prerequisites** — Module 105 Railway backend URL known; Module 106 PostgreSQL + migration complete; Module 107 Vercel URL known; all env var secrets already set on Railway
3. **CORS bootstrap sequence recap** — 3-step sequence from Module 102/107; why FRONTEND_CORS_ORIGINS cannot be set until Vercel URL is assigned
4. **Step 1: Confirm Railway backend URL** — from Module 105 evidence; HTTPS; no trailing slash
5. **Step 2: Confirm Vercel frontend URL** — from Module 107 evidence; exact `*.vercel.app` URL; no trailing slash
6. **Step 3: Set FRONTEND_CORS_ORIGINS on Railway** — exact env var name; exact Vercel URL value; no wildcard; no trailing slash; Railway dashboard steps; redeploy required
7. **Step 4: Redeploy Railway backend** — trigger redeploy after env var change; wait for healthy status
8. **Step 5: Confirm NEXT_PUBLIC_API_BASE_URL on Vercel** — confirm it points to Railway backend HTTPS URL; redeploy Vercel if changed
9. **Step 6: CORS preflight verification** — browser DevTools; OPTIONS request to Railway backend; expected Access-Control-Allow-Origin header; expected status 200/204
10. **Step 7: Login smoke** — open Vercel URL in browser; navigate to /login; submit fake credentials; expect JWT stored (sessionStorage); dashboard loads
11. **Evidence to capture** — Railway backend URL; Vercel frontend URL; FRONTEND_CORS_ORIGINS value confirmed (no wildcard); CORS preflight screenshot description; login attempt result; no secret values
12. **Failure triage** — CORS error persists (wildcard forbidden; trailing slash in origin; Railway not redeployed; wrong env var name); login fails (NEXT_PUBLIC_API_BASE_URL wrong; API unreachable); preflight 403 (FRONTEND_CORS_ORIGINS not yet set or wrong)
13. **Stop rules** — wildcard CORS; production secrets; real patient data; ngrok URLs; secrets in evidence
14. **Result states** — PASS / BLOCKED/PENDING / FAIL
15. **What this runbook does not cover** — full Vapi smoke (Module 109); n8n calendar sync; production launch
16. **Recommended next** — Module 109: Staging Smoke Execution (full end-to-end)

### 3. Create `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md`

Evidence doc with BLOCKED/PENDING:
- Purpose (accuracy policy; no fabricated evidence)
- Current result (BLOCKED/PENDING — Vercel URL and Railway backend URL not yet confirmed wired)
- Preconditions available/missing
- Evidence table (Railway URL; Vercel URL; FRONTEND_CORS_ORIGINS confirmed; CORS preflight result; login result; no secrets)
- Blockers if pending
- Next evidence needed

### 4. Static contract tests

Create `backend/tests/test_staging_environment_wiring_runbook_contract.py`:
- Runbook doc exists
- Evidence doc exists
- Mentions staging environment wiring
- Mentions fake/non-PHI staging
- Mentions no Claude deployment
- Mentions FRONTEND_CORS_ORIGINS
- Mentions no wildcard CORS
- Mentions Railway backend HTTPS URL
- Mentions Vercel frontend URL
- Mentions NEXT_PUBLIC_API_BASE_URL
- Mentions CORS preflight
- Mentions Railway redeploy after env var change
- Mentions login smoke
- Mentions no real patient data
- Mentions no production secrets
- Mentions evidence capture
- Mentions no secret values in evidence
- Mentions stop rules
- Mentions PASS/BLOCKED/PENDING states
- Mentions Module 109
- Evidence doc mentions BLOCKED/PENDING
- No obvious real secrets in either doc

### 5. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 107 (already done) and Module 108
- `docs/claude/NEXT_MODULE.md` — Sprint 15 / Module 109: Staging Smoke Execution Evidence

## What not to do

- Do not deploy to Railway or Vercel
- Do not set real FRONTEND_CORS_ORIGINS (no real Vercel URL yet)
- Do not add real secrets
- Do not implement httpOnly cookie auth
- Do not change CORS implementation in backend code
- Do not start Fabel 5/UX sprint
- Do not change DB schema or migration files
- Do not fabricate PASS evidence

## Acceptance

- `docs/deployment/STAGING_ENVIRONMENT_WIRING_RUNBOOK.md` created
- `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` created (BLOCKED/PENDING)
- Contract tests pass
- Full test suite passes (2188/2188 minimum)
- Commit: `Sprint 15 / Module 108 — Staging environment wiring evidence`
