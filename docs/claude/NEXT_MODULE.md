# Sprint 7 / Module 59 — Production Auth and User Session Foundation

Status: pending Architecture Checkpoint 05 review.

## Goal

Add human authentication as a parallel trust model alongside the existing machine auth layer. Doctors and admins must have production-grade login before the frontend can be built and before real patient data handling can begin.

## Scope

- Add a `users` table to `schema.sql` and a corresponding Alembic migration.
- Add `backend/app/db/repositories/user_repo.py` for user lookup and creation.
- Add secure password hashing (bcrypt or argon2).
- Add JWT access and refresh token issuance and validation.
- Add a `get_current_user` FastAPI dependency that protects PHI routes.
- Add tests covering login, token refresh, and unauthorized access rejection.

## What not to do

- Do not build the frontend.
- Do not implement OAuth (Google, Apple) yet — basic email/password first.
- Do not add role-based access control (RBAC) beyond doctor/admin distinction — keep it minimal.
- Do not touch machine auth, HMAC, or existing webhook routes.
- Do not modify existing completed modules unless the import chain requires it.

## Acceptance

- All new tests pass.
- Full backend tests pass (no regression).
- No existing machine auth or webhook behavior changed.
