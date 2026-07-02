# Sprint 7 / Module 60 — Login Endpoint and Auth Wiring Plan

Status: pending Module 59 review.

## Goal

Add the login endpoint (`POST /auth/login`) and define where `get_current_user` will be wired into existing PHI routes.

## Scope

### Login endpoint
- Accept `email` and `password` in the request body (JSON, not form).
- Look up the user by `(clinic_id, email)` — clinic_id from a request body field or a machine header.
- Verify the password using `verify_password`.
- Issue a JWT access token using `create_access_token`.
- Return `{"access_token": "...", "token_type": "bearer", "expires_in": <seconds>}`.
- Return HTTP 401 for wrong credentials.
- Return HTTP 401 for inactive users.
- No refresh token yet — keep it minimal.

### Auth wiring plan
- Define which existing PHI routes will require `get_current_user` in addition to (or instead of) the current header-based `get_auth_context`.
- Do not wire yet — just document the plan as a comment or small doc section.

## What not to do

- Do not refactor or remove existing `get_auth_context` — PHI routes still use it.
- Do not add refresh tokens, OAuth, or RBAC in this module.
- Do not build frontend.
- Do not add email verification.

## Acceptance

- `POST /auth/login` with correct credentials → 200 + JWT token.
- `POST /auth/login` with wrong password → 401.
- `POST /auth/login` with inactive user → 401.
- No plaintext passwords logged or returned.
- All new tests pass. Full suite passes.
