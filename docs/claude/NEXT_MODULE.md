# Sprint 16 / Module 111 — Railway Backend Service Creation Evidence

Status: pending Railway backend redeploy with root directory fix.

## Context

Module 110 complete:
- `requirements.txt` created at repo root (Nixpacks bridge: `-r backend/requirements.txt`)
- `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` updated: root directory must be blank (repo root); Section 5.4 added documenting `ModuleNotFoundError: No module named 'backend'` when root=`backend`
- `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` updated: Section 3.0 added for root requirements bridge
- 16 contract tests; full suite: 2282/2282 passed
- Commit: (see git log)

Real deployment failure confirmed:
- Initial Railway deploy with `root=backend` caused `ModuleNotFoundError: No module named 'backend'`
- Root cause: Python resolves `backend.app.main:app` relative to the working directory;
  when root is `backend/`, the `backend` package cannot be found inside itself
- Fix applied: root `requirements.txt` + root directory must be blank

**The developer must:**
1. Push the `requirements.txt` commit to the Railway-tracked branch
2. In Railway service settings → Root Directory: **clear/blank** (repo root)
3. Redeploy the Railway backend service
4. Confirm `GET /health` → 200

## Scope

Evidence doc only. No code changes. No deployment by Claude.
No real secrets. No production data.

### If real Railway backend `/health` → 200 evidence is provided:

1. Create `docs/runtime/RAILWAY_BACKEND_SERVICE_CREATION_EVIDENCE.md`
   - Set result: PASS
   - Record Railway service name, URL, branch, commit SHA, build status
   - Record Nixpacks Python version detected
   - Record start command detected (from Procfile)
   - Record root directory confirmed as blank/repo root
   - Record `requirements.txt` bridge confirmed
   - Record env var names set (not values): `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`, `APP_ENV`
   - Record `DATABASE_URL` status: absent (expected)
   - Record `FRONTEND_CORS_ORIGINS` status: absent (expected)
   - Record `GET /health` → 200 and response body
   - Record `GET /health/ready` → 503 (expected; no DB yet)
   - Record sanitized build log snippet (no secrets)
2. Add contract tests for the evidence doc
3. Update CURRENT_STATE.md
4. Update NEXT_MODULE.md → Module 112: Railway PostgreSQL Provisioning Evidence

### If no evidence or if redeploy still fails:

1. Create `docs/runtime/RAILWAY_BACKEND_SERVICE_CREATION_EVIDENCE.md`
   - Set result: BLOCKED/PENDING (or FAIL with exact error)
   - Document the exact error from Railway logs
   - List exact fix steps
2. Add contract tests
3. Update CURRENT_STATE.md
4. Update NEXT_MODULE.md accordingly

## What not to do

- Do not deploy to Railway
- Do not add real secrets
- Do not fabricate PASS evidence
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint
- Do not change DB schema or migration files

## Acceptance

- `docs/runtime/RAILWAY_BACKEND_SERVICE_CREATION_EVIDENCE.md` created (PASS or BLOCKED/PENDING)
- PASS only with real `/health` → 200 evidence
- Contract tests pass
- Full test suite passes (2282/2282 minimum)
- Commit: `Sprint 16 / Module 111 — Railway backend service creation evidence`
