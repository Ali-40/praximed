# Sprint 16 / Module 117 — Vercel Frontend Deployment and API Wiring

Status: pending manual Vercel frontend project creation, deployment, and CORS wiring.

## Context

Module 116 complete:
- `GET /health` → 200
- `GET /health/ready` → 200 — DB pool healthy; JWT_SECRET_KEY confirmed set
- `POST /auth/login` → 200 — access_token present; token_type=bearer
- Full test suite: 2400/2400 passed
- Commit: (see git log)

Railway backend URL (confirmed): `https://web-production-fd91d.up.railway.app`
Fake staging clinic_id (confirmed): `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`
Fake staging email (confirmed): `doctor.staging@praximed.test`

## Scope

Evidence doc + static tests. No deployment by Claude.
No real secrets. No production data.

### The developer must:

Follow `docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md`:

1. Create a new Vercel project from this repository
   - Root directory: `frontend`
   - Framework: Next.js (auto-detected)
   - Build command: `next build` (Vercel default)
2. Set the environment variable in Vercel:
   - `NEXT_PUBLIC_API_BASE_URL` = `https://web-production-fd91d.up.railway.app`
3. Deploy and confirm build succeeds
4. Capture the Vercel frontend URL (e.g. `https://praximed-xxx.vercel.app`)
5. Confirm `GET <vercel-url>/login` → page renders (no 404, login form visible)
6. In Railway backend service, set:
   - `FRONTEND_CORS_ORIGINS` = exact Vercel HTTPS URL (no trailing slash; no wildcard)
7. Redeploy Railway backend after `FRONTEND_CORS_ORIGINS` is set
8. Confirm Railway backend still shows `/health` → 200 after redeploy

### Evidence to capture (no secrets):

- Vercel project name
- Vercel frontend URL (not a secret; used for CORS wiring)
- Vercel build status: Success
- Deployed git commit SHA
- `NEXT_PUBLIC_API_BASE_URL` variable name confirmed in Vercel (not the value)
- `GET <vercel-url>/login` → HTTP status + whether login form is visible
- `FRONTEND_CORS_ORIGINS` variable name set in Railway (not the value)
- Railway backend redeploy status after CORS env var set
- `GET /health` → 200 after Railway redeploy

### Module 117 will create/update:

1. `docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md` (new) — PASS or BLOCKED/PENDING
2. Contract tests for Vercel deployment evidence
3. Update `STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — mark Vercel URL, build, NEXT_PUBLIC_API_BASE_URL, FRONTEND_CORS_ORIGINS PASS if confirmed
4. Update `STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — mark check 4 (frontend /login) PASS if confirmed; check 5 (CORS) still needs browser verification
5. Update `CURRENT_STATE.md` and `NEXT_MODULE.md` → Module 118 (Browser CORS and Dashboard Smoke)

## What not to do

- Do not deploy Vercel from Claude
- Do not add real secrets to any document
- Do not use wildcard CORS (`*`) — `FRONTEND_CORS_ORIGINS` must be the exact Vercel URL
- Do not fabricate PASS evidence
- Do not implement httpOnly cookie auth
- Do not change backend CORS implementation
- Do not start Fabel 5/UX sprint

## CORS bootstrap sequence (must follow this order)

1. Deploy Vercel → get Vercel URL
2. Set `FRONTEND_CORS_ORIGINS=<vercel-url>` in Railway
3. Redeploy Railway backend
4. Only then can browser requests from the Vercel frontend reach the Railway API without CORS error

## Acceptance

- `docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md` created (PASS or BLOCKED/PENDING with real evidence)
- PASS only with real Vercel URL and confirmed build from real Vercel service
- Contract tests pass
- Full test suite passes (2400/2400 minimum)
- Commit: `Sprint 16 / Module 117 — Vercel frontend deployment and API wiring evidence`
