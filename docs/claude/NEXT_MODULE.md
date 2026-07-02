# Sprint 9 / Module 75 — Run Frontend Browser Smoke Evidence

Status: pending Module 74 review.

## Context

The three runtime blockers from the initial smoke (Module 72–73) have been fixed:
1. Alembic revision ID shortened to `0002_password_hash`.
2. Seed script `sys.path` safety added.
3. Port-conflict guidance added to the runbook.

And the browser login blocker has been fixed (Module 74):
4. `CORSMiddleware` added to `backend/app/main.py` — OPTIONS preflight now returns 200.

The stack should now support a complete browser login → dashboard → logout flow.
Module 75 executes the full smoke and records evidence.

## Scope

1. Follow `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` Steps 1–9.
2. Capture the result of each step (command, expected output, actual output, pass/fail).
3. Fix any remaining runtime issues; add a test for each fix.
4. Create `docs/integrations/FRONTEND_LOCAL_SMOKE_RESULTS.md`:
   - Date of smoke run
   - Stack versions (Python, Node, Next.js, FastAPI)
   - Each step result
   - Any issues found and fixes applied
   - Final verdict: PASS or FAIL
5. Update `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` with any step corrections.

## What not to do

- Do not add new dashboard sections or features.
- Do not implement token refresh or cookie-based auth.
- Do not modify backend auth routes.
- Do not deploy or build for production.

## Acceptance

- All 9 runbook steps complete without error.
- `docs/integrations/FRONTEND_LOCAL_SMOKE_RESULTS.md` created with PASS verdict.
- Full backend tests pass.
- Commit: `Sprint 9 / Module 75 — Frontend browser smoke evidence`
