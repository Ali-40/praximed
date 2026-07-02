# Sprint 9 / Module 73 — Run Frontend Browser Smoke and Fix Runtime Issues

Status: pending Module 72 review.

## Context

Module 72 prepared the local runtime smoke:
- `seed_local_data.py` now creates a login-capable user with a bcrypt password_hash.
- `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` documents the full 9-step runbook.
- Local login credentials: `doctor.local@praximed.test` / `local-dev-password`.

The frontend code has never been run in a real browser. Module 73 executes the runbook
and fixes any TypeScript compilation errors or Next.js runtime errors discovered.

## Scope

1. Run `npm install` in `frontend/` — resolve any dependency issues.
2. Run `npx tsc --noEmit` — fix all TypeScript compilation errors found.
3. Run `npm run dev` — verify the dev server starts without errors.
4. Start the local stack (PostgreSQL + backend) and seed the login user.
5. Open `http://localhost:3000`, log in, verify dashboard data loads, log out.
6. Fix any frontend runtime errors discovered; add a static contract test for each fix.
7. Document results in `docs/integrations/FRONTEND_LOCAL_SMOKE_RESULTS.md`.
8. Update `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` with actual test results.

## What not to do

- Do not add new dashboard sections or features.
- Do not implement token refresh or cookie-based auth.
- Do not modify backend routes.
- Do not deploy or build for production.

## Acceptance

- `npm run dev` starts without error.
- `npx tsc --noEmit` reports no errors.
- Full login → dashboard (all four sections) → logout flow confirmed in browser.
- Results documented in `docs/integrations/FRONTEND_LOCAL_SMOKE_RESULTS.md`.
- Full backend tests pass.
- Commit: `Sprint 9 / Module 73 — Frontend browser smoke results`
