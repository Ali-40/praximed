# Sprint 7 / Architecture Checkpoint 06 — Human Auth Wiring Review

Status: pending Module 65 review.

## Context

Modules 61–65 wired `get_current_user` (JWT Bearer) into all five PHI human-facing
route groups:
- `/patients` ✓ Module 61
- `/consultations` ✓ Module 62
- `/clinical-workflows` ✓ Module 63
- `/appointment-requests` ✓ Module 64
- `/notifications` ✓ Module 65

Machine routes (Vapi, n8n, availability, webhooks) continue using machine auth
(`get_auth_context` with `X-Service-*` headers) and are unchanged.

## Scope

Create Architecture Checkpoint 06 document covering:
- Summary of what was wired (all 5 PHI route groups, which modules, which commits)
- The wiring pattern used and why it's consistent
- Current auth boundary: human routes JWT, machine routes header-based
- Remaining risks: `get_auth_context` still present in codebase for machine callers;
  no frontend yet consuming the JWT; session expiry/refresh not yet handled
- Sprint 8 candidates

Update `docs/security/AUTH_WIRING_PLAN.md` — note Sprint 7 JWT wiring complete.
Update `docs/claude/CURRENT_STATE.md` and `docs/claude/NEXT_MODULE.md`.

## What not to do

- Do not modify any route files.
- Do not modify test files.
- Do not remove `get_auth_context` — still used by machine auth stack.

## Acceptance

- Architecture Checkpoint 06 document created.
- CURRENT_STATE.md updated.
- NEXT_MODULE.md updated to Sprint 8 first module.
- Full suite still passes.
- Commit: `Sprint 7 / Architecture Checkpoint 06 — Human auth wiring review`
