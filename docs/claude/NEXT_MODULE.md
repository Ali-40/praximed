# Sprint 16 / Module 112 — Railway Backend Service Creation Evidence

Status: pending Railway backend redeploy after Module 111 fix.

## Context

Module 111 complete:
- `requirements.txt` (repo root) — direct pinned dependencies; no nested `-r` include
- `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` updated
- `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` updated
- 22 contract tests; full suite: 2304/2304 passed
- Commit: (see git log)

Railway deploy history:
- First attempt (Module 110): failed — `ModuleNotFoundError: No module named 'backend'` (root dir set to `backend/`)
- Second attempt (Module 111): failed — Railway/Railpack could not resolve `-r backend/requirements.txt` during build cache
- Fix applied: root `requirements.txt` now lists all 7 dependencies directly

**The developer must:**
1. Push the Module 111 commit to `master`
2. Confirm Railway root directory is blank (repo root) — not `backend/`
3. Trigger Railway redeploy
4. Confirm `GET https://<railway-url>/health` → HTTP 200

## Scope

Evidence doc only. No code changes. No deployment by Claude.
No real secrets. No production data.

### If real Railway backend `/health` → 200 evidence is provided:

1. Create `docs/runtime/RAILWAY_BACKEND_SERVICE_CREATION_EVIDENCE.md`
   - Set result: PASS
   - Record Railway service name, URL, branch, commit SHA, build status
   - Record Nixpacks Python version detected
   - Record start command detected (full Procfile command)
   - Record root directory confirmed as blank/repo root
   - Record `requirements.txt` at repo root: direct deps confirmed
   - Record env var names set (not values): `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`, `APP_ENV`
   - Record `DATABASE_URL` status: absent (expected — Module 113 next)
   - Record `FRONTEND_CORS_ORIGINS` status: absent (expected)
   - Record `GET /health` → 200 and exact response body
   - Record `GET /health/ready` → 503 (expected; no DB yet)
   - Record sanitized build log snippet (no secrets)
2. Add contract tests for evidence doc
3. Update CURRENT_STATE.md
4. Update NEXT_MODULE.md → Module 113: Railway PostgreSQL Provisioning Evidence

### If redeploy still fails:

1. Create `docs/runtime/RAILWAY_BACKEND_SERVICE_CREATION_EVIDENCE.md`
   - Set result: FAIL / BLOCKED — document exact Railway error from logs
   - List exact fix steps
2. Add contract tests
3. Update CURRENT_STATE.md and NEXT_MODULE.md

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
- Full test suite passes (2304/2304 minimum)
- Commit: `Sprint 16 / Module 112 — Railway backend service creation evidence`
