# Sprint 9 / Module 74 — Run Frontend Browser Smoke Evidence

Status: pending Module 73 review.

## Context

Module 72 prepared the local runtime smoke runbook and seed login user.
Module 73 fixed the three blockers found during the first manual run:
1. Alembic revision ID shortened to ≤32 chars (`0002_password_hash`).
2. Seed script `sys.path` safety added for direct execution.
3. Runtime doc updated with port-conflict resolution and JWT_SECRET_KEY requirement.

The stack should now run without blockers. Module 74 executes the full smoke and
records evidence.

## Scope

1. Follow `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` from Step 1 to Step 9.
2. Capture the result of each step (success / failure / output).
3. Fix any remaining runtime issues discovered; add a test for each fix.
4. Create `docs/integrations/FRONTEND_LOCAL_SMOKE_RESULTS.md` documenting:
   - Date of smoke run
   - Each step: command run, expected output, actual output, pass/fail
   - Any issues found and their fixes
   - Final verdict: PASS or FAIL
5. Update `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` with any step corrections.

## What not to do

- Do not add new dashboard sections or features.
- Do not implement token refresh or cookie-based auth.
- Do not modify backend routes.
- Do not deploy or build for production.

## Acceptance

- All 9 runbook steps complete without error.
- `docs/integrations/FRONTEND_LOCAL_SMOKE_RESULTS.md` created with PASS verdict.
- Full backend tests pass.
- Commit: `Sprint 9 / Module 74 — Frontend browser smoke evidence`
