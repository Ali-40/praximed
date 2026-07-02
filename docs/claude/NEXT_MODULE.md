# Sprint 7 / Module 61 — TBD

Status: pending Module 60 review.

## Context

Module 60 completed the login endpoint (`POST /auth/login`). The `get_current_user` JWT
dependency exists but is not yet wired to any PHI routes. The auth wiring plan is documented
in `docs/security/AUTH_WIRING_PLAN.md`.

## Likely candidates for Module 61

1. **Wire `get_current_user` into `/patients` routes** — lowest-risk PHI route, read-heavy.
2. **User management routes** — `POST /auth/register` or admin user creation endpoint.
3. **Token refresh** — if a short-lived token strategy is needed before PHI wiring.

## Decision point

Confirm direction before starting Module 61.
