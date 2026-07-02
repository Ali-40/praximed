# Sprint 7 / Module 62 — Wire JWT Auth to Consultation Routes

Status: pending Module 61 review.

## Context

Module 61 wired `get_current_user` (JWT Bearer) into `/patients` routes. Consultation routes
(`/consultations`) still use `get_auth_context` (header-based auth). The wiring pattern is
now proven; Module 62 repeats it for consultations.

## Scope

- Replace `Depends(get_auth_context)` with `Depends(get_current_user)` in
  `backend/app/api/routes/consultations.py`.
- Update `backend/tests/test_consultation_routes.py` (or equivalent) to override
  `get_current_user` in fixtures and add JWT auth enforcement tests.
- Update `docs/security/AUTH_WIRING_PLAN.md` — mark `/consultations` wired.
- Update `docs/claude/CURRENT_STATE.md` and `docs/claude/NEXT_MODULE.md`.

## What not to do

- Do not wire clinical-workflows, appointment-requests, or notifications yet.
- Do not modify machine routes or Vapi/n8n auth.
- Do not use real DB in tests.

## Acceptance

- All consultation routes require Bearer JWT; header auth rejected.
- Tenant/role checks preserved.
- Other PHI routes unchanged.
- Full suite passes.
- Commit: `Sprint 7 / Module 62 — Wire JWT auth to consultation routes`
