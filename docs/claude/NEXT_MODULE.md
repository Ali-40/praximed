# Sprint 7 / Module 63 — Wire JWT Auth to Clinical Workflow Routes

Status: pending Module 62 review.

## Context

Modules 61–62 wired `get_current_user` (JWT Bearer) into `/patients` and `/consultations`.
Clinical workflow routes (`/clinical-workflows`) still use `get_auth_context` (header-based).
The wiring pattern is proven; Module 63 repeats it for clinical workflows.

## Scope

- Replace `Depends(get_auth_context)` with `Depends(get_current_user)` in
  `backend/app/api/routes/clinical_workflows.py`.
- Update `backend/tests/test_clinical_workflow_routes.py` to override
  `get_current_user` in fixtures and add JWT auth enforcement tests.
- Update `docs/security/AUTH_WIRING_PLAN.md` — mark `/clinical-workflows` wired.
- Update `docs/claude/CURRENT_STATE.md` and `docs/claude/NEXT_MODULE.md`.

## What not to do

- Do not wire appointment-requests or notifications yet.
- Do not modify machine routes or Vapi/n8n auth.
- Do not use real DB in tests.

## Acceptance

- All clinical workflow routes require Bearer JWT; header auth rejected.
- Tenant/role checks preserved.
- Other PHI routes unchanged.
- Full suite passes.
- Commit: `Sprint 7 / Module 63 — Wire JWT auth to clinical workflow routes`
