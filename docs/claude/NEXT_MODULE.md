# Sprint 7 / Module 64 — Wire JWT Auth to Appointment Routes

Status: pending Module 63 review.

## Context

Modules 61–63 wired `get_current_user` (JWT Bearer) into `/patients`, `/consultations`,
and `/clinical-workflows`. Appointment request routes (`/appointment-requests`) still use
`get_auth_context` (header-based). The wiring pattern is proven; Module 64 repeats it.

## Scope

- Replace `Depends(get_auth_context)` with `Depends(get_current_user)` in
  `backend/app/api/routes/appointment_requests.py`.
- Update the existing appointment request route test file to override
  `get_current_user` in fixtures and add JWT auth enforcement tests.
- Update `docs/security/AUTH_WIRING_PLAN.md` — mark `/appointment-requests` wired.
- Update `docs/claude/CURRENT_STATE.md` and `docs/claude/NEXT_MODULE.md`.

## What not to do

- Do not wire `/notifications` yet.
- Do not modify machine routes, Vapi, n8n, or availability routes.
- Do not use real DB in tests.

## Acceptance

- All appointment request routes require Bearer JWT; header auth rejected.
- Tenant/role checks preserved.
- Other PHI routes unchanged.
- Full suite passes.
- Commit: `Sprint 7 / Module 64 — Wire JWT auth to appointment routes`
