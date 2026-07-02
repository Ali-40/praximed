# Sprint 7 / Module 65 — Wire JWT Auth to Notification Routes

Status: pending Module 64 review.

## Context

Modules 61–64 wired `get_current_user` (JWT Bearer) into `/patients`, `/consultations`,
`/clinical-workflows`, and `/appointment-requests`. Notification routes (`/notifications`)
still use `get_auth_context` (header-based). The wiring pattern is proven; Module 65
repeats it.

Note: `/notifications` may remain machine-only long-term (triggered by n8n/Vapi). The
AUTH_WIRING_PLAN.md notes this as Phase 3 requiring evaluation of whether human JWT is
ever needed. For now, wire the same way as other PHI routes.

## Scope

- Replace `Depends(get_auth_context)` with `Depends(get_current_user)` in
  `backend/app/api/routes/notifications.py`.
- Update the existing notification route test file to override
  `get_current_user` in fixtures and add JWT auth enforcement tests.
- Update `docs/security/AUTH_WIRING_PLAN.md` — mark `/notifications` wired.
- Update `docs/claude/CURRENT_STATE.md` and `docs/claude/NEXT_MODULE.md`.

## What not to do

- Do not modify machine routes, Vapi, n8n, or availability routes.
- Do not use real DB in tests.

## Acceptance

- All notification routes require Bearer JWT; header auth rejected.
- Tenant/role checks preserved.
- Other PHI routes unchanged.
- Full suite passes.
- Commit: `Sprint 7 / Module 65 — Wire JWT auth to notification routes`
