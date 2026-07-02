# Sprint 9 / Module 72 — Frontend Local Runtime Smoke and Seed Login

Status: pending Architecture Checkpoint 07 review.

## Context

Sprint 8 produced a complete Next.js frontend (Modules 66–71) — login flow and four
live dashboard sections — but the frontend has never been run in a real browser.
Architecture Checkpoint 07 identified this as the highest-priority risk before building
additional features.

## Goal

Run the frontend in a real browser against the local backend. Prove that the code
written in Sprint 8 works end-to-end and document the result.

## Scope

1. Run `npm install` in `frontend/` and resolve any dependency issues.
2. Run `npx tsc --noEmit` to check for TypeScript compilation errors; fix any found.
3. Run `npm run dev` — verify the dev server starts without errors.
4. Start the backend (`uvicorn backend.app.main:app --reload`) and the local PostgreSQL
   container (`docker-compose -f docker-compose.postgres.yml up -d`).
5. Seed a local user via `backend/scripts/seed_local_data.py`.
6. Open `http://localhost:3000`:
   - Verify redirect to `/login`.
   - Log in with seeded Clinic ID, email, password.
   - Verify redirect to `/dashboard`.
   - Verify all four sections show loading → data (or empty if no records).
   - Log out and verify redirect back to `/login`.
7. Document the result in `docs/integrations/FRONTEND_LOCAL_SMOKE_RESULTS.md`.
8. Fix any frontend runtime errors discovered; add a static contract test for each fix.

## What not to do

- Do not add new dashboard features or forms.
- Do not implement token refresh or cookie-based auth.
- Do not modify backend routes.
- Do not run in production or deploy.

## Acceptance

- `npm run dev` starts without error.
- `npx tsc --noEmit` reports no errors (or all found errors are fixed).
- Full login → dashboard → logout flow completes in a real browser.
- Results documented in `docs/integrations/FRONTEND_LOCAL_SMOKE_RESULTS.md`.
- Full backend tests pass.
- Commit: `Sprint 9 / Module 72 — Frontend local runtime smoke and seed login`
