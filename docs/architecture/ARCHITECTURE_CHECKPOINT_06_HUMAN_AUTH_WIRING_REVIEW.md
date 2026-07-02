# Architecture Checkpoint 06 — Human Auth Wiring Review

**Date:** Sprint 7 / Module 65 complete
**Scope:** Sprint 7 — Modules 59–65 (production auth foundation and PHI route JWT wiring)
**Type:** Human authentication security review

---

## 1. Current Status

Sprint 7 is complete. All five PHI human-facing route groups now require a valid JWT Bearer token. The backend has a working login endpoint, a `get_current_user` FastAPI dependency, and consistent tenant/role enforcement across all protected routes.

The backend is **local-only and test-ready**. It is not production-deployed. No frontend exists yet. All tests use mocked databases, injected auth contexts, and test-only JWT secrets — no real user credentials, no real patient data.

Full backend test suite: **1461/1461 passed**.

---

## 2. Completed Sprint 7 Work

### Module 59 — Auth and User Session Foundation

- `backend/app/core/password_hashing.py` — bcrypt hash and verify; no plaintext stored or logged
- `backend/app/core/jwt_tokens.py` — HS256 JWT create/decode; `MissingJWTSecretError` surfaces missing env var as 503
- `backend/app/db/repositories/user_repo.py` — `get_user_by_email`, `get_user_by_id`, `create_user`
- `backend/app/api/dependencies/current_user.py` — `get_current_user` FastAPI dependency; decodes Bearer JWT, loads user from DB, returns `AuthContext`; raises 401 for missing/invalid/expired token or inactive user; raises 503 for missing `JWT_SECRET_KEY`
- `backend/app/db/schema.sql` — `password_hash` column added to `clinic_users`
- `backend/migrations/versions/0002_add_password_hash_to_clinic_users.py` — migration for schema change
- Tests: 51/51 (hashing, JWT, user repo, dependency)

### Module 60 — Login Endpoint

- `backend/app/schemas/auth.py` — `LoginRequest`, `LoginResponse`, `LoginUserInfo`
- `backend/app/api/routes/auth.py` — `POST /auth/login`; issues JWT on valid credentials
- `backend/app/api/router.py` — auth router registered
- `docs/security/AUTH_WIRING_PLAN.md` — wiring order documented
- Tests: 10/10

**Login security behaviors:**
- Wrong password and unknown email both return 401 "Invalid credentials" — no user enumeration
- Inactive account returns 401 "Account is not active" (separate message only after password verified)
- Missing `password_hash` returns 401 — not a 500
- `password_hash` never returned in any response
- Missing `JWT_SECRET_KEY` returns 503 — not a silent failure
- Email normalized to lowercase before lookup

### Modules 61–65 — PHI Route JWT Wiring

All five PHI route groups wired from `get_auth_context` (header-based) to `get_current_user` (JWT Bearer):

| Module | Route group | Tests |
|---|---|---|
| 61 | `/patients` | 36/36 |
| 62 | `/consultations` | 38/38 |
| 63 | `/clinical-workflows` | 46/46 |
| 64 | `/appointment-requests` | 29/29 |
| 65 | `/notifications` | 30/30 |

Each module followed the same wiring pattern:
- `Depends(get_auth_context)` replaced with `Depends(get_current_user)` across all route handlers
- `require_staff_clinic_access` / `require_clinical_clinic_access` utilities unchanged
- Test fixtures updated to override `get_current_user` via `app.dependency_overrides`
- 8 JWT enforcement tests added per module (missing token, invalid token, wrong clinic, role denial, role allowed, valid JWT CRUD)
- Cross-route smoke tests in sibling test files already used `!= 404` assertions — no changes needed

---

## 3. What Is Proven

| Capability | Evidence |
|---|---|
| Login endpoint issues a valid JWT | `test_auth_login_route.py` — 10/10 |
| bcrypt password verification works | `test_password_hashing.py` — 12/12 |
| JWT encode/decode with expiry works | `test_jwt_tokens.py` — 12/12 |
| `get_current_user` rejects missing token with 401 | All 5 PHI route test files |
| `get_current_user` rejects invalid/expired token with 401 | All 5 PHI route test files |
| `get_current_user` rejects inactive user with 401 | `test_current_user_dependency.py` |
| `get_current_user` surfaces missing `JWT_SECRET_KEY` as 503 | `test_current_user_dependency.py` |
| Wrong-clinic token rejected with 403 | All 5 PHI route test files |
| Viewer role rejected on staff and clinical routes | All 5 PHI route test files |
| Staff role allowed on staff-level routes | Module 61, 64, 65 tests |
| Doctor role allowed on clinical routes | Module 62, 63 tests |
| Tenant isolation via `clinic_id` preserved end-to-end | All PHI route modules |
| User enumeration prevented (same 401 for bad user/bad password) | `test_auth_login_route.py` |
| `password_hash` never appears in any response | Login response schema verified |
| Machine routes (Vapi, n8n, webhooks) unchanged | Existing machine auth tests still pass |
| `get_auth_context` still available for machine callers | Not removed; machine routes untouched |
| Audit logging preserved after auth switch | All PHI route audit tests still pass |

---

## 4. What Is Not Proven

| Area | Status |
|---|---|
| Refresh token flow | Not implemented — access tokens only |
| Logout / token revocation | Not implemented — no token blacklist |
| Rate limiting on `POST /auth/login` | Not implemented — brute force possible |
| Password reset flow | Not implemented |
| Email verification on account creation | Not implemented |
| `JWT_SECRET_KEY` in a real secret manager | Not started — env var only |
| Frontend consumption of JWT | Not started — no frontend exists |
| Secure JWT storage on client (httpOnly cookie vs localStorage) | Not decided |
| Multi-device / concurrent session management | Not implemented |
| Token storage after server restart | Stateless — tokens remain valid until expiry |
| Real user creation outside seed scripts | No self-registration endpoint |
| Admin user management UI | Not started |
| GDPR/DSGVO subject access and deletion flows | Not started |
| Production deployment with real TLS | Not started |

---

## 5. Security Review

### JWT Authentication

- Algorithm: HS256 (symmetric). Secret loaded from `JWT_SECRET_KEY` env var at call time.
- Claims: `sub` (user_id), `clinic_id`, `role`, `iat`, `exp`.
- Default expiry: 60 minutes (`DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES`).
- Missing secret raises `MissingJWTSecretError` → 503, not a silent fallback to an empty key.
- Expired tokens raise `ExpiredJWTError` → 401 "Token has expired".
- Malformed tokens raise `InvalidJWTError` → 401.
- **Gap:** No refresh tokens. Users must re-login after 60 minutes or the token must be made long-lived (worse). Refresh token rotation should be added before production.

### Password Hashing

- bcrypt with `gensalt()` per hash — unique salts, no rainbow table attacks.
- `verify_password` returns `bool` — never raises on mismatch, preventing timing side-channels from propagating to the caller.
- Empty password and empty hash both return `False` — not an error.
- `hash_password` rejects empty input with `PasswordHashingError`.
- No plaintext passwords appear in logs, responses, or test fixtures.

### Inactive User Rejection

- `get_current_user` loads the user record from DB on every request and checks `status == "active"`.
- Deactivating a user takes effect on the next request — no need to wait for token expiry.
- **Note:** This adds one DB round-trip per request. In production, this lookup should be cached (e.g., Redis with short TTL) or replaced with a token version claim to avoid per-request DB load at scale.

### Tenant / Clinic Guards

- `require_staff_clinic_access` (STAFF_ROLES: owner, admin, doctor, staff) used on `/patients`, `/appointment-requests`, `/notifications`.
- `require_clinical_clinic_access` (CLINICAL_ROLES: owner, admin, doctor) used on `/consultations`, `/clinical-workflows`.
- Both helpers compare `auth.clinic_id` (from the verified JWT) against the `clinic_id` in the request body or query param. Mismatch → 403.
- `AuthContext.clinic_id` is populated from the DB user record (not the JWT claim) in `get_current_user`, so a JWT with a tampered `clinic_id` claim cannot bypass the tenant check.

### Role Guards

- Viewer role is rejected on all five PHI route groups.
- Staff is rejected on clinical routes (consultations, clinical-workflows).
- Doctor, owner, and admin are allowed across all PHI routes.
- Role check is enforced at the route level via the `require_*` helpers, not just at login.

### Machine Routes Separation

- `/vapi/tools/*`, `/vapi/webhooks/*`, `/webhooks/n8n/*`, `/calendar/*` all continue using `get_auth_context` (machine header auth + HMAC signature verification).
- `get_auth_context` has not been removed from the codebase — machine callers still need it.
- No JWT is required or accepted on machine routes. No machine route was modified in Sprint 7.
- The separation is clean: human routes use `get_current_user`, machine routes use `get_auth_context` + signature deps.

---

## 6. Main Risks Before Frontend / Production

| Risk | Severity | Notes |
|---|---|---|
| No refresh tokens | High | 60-min expiry forces frequent re-login or dangerously long-lived tokens; must be resolved before production |
| No logout / session revocation | High | Compromised access token is valid until expiry; no way to force sign-out |
| No rate limiting on `/auth/login` | High | Brute force attack possible with no throttle; must be added before public access |
| `JWT_SECRET_KEY` in env var only | High | No secret rotation, no secret manager; any server env dump exposes all sessions |
| No frontend auth storage plan | Medium | httpOnly cookie is safer than localStorage; decision deferred until frontend module |
| No password reset | Medium | Lost password = locked out; requires out-of-band email flow |
| No email verification | Medium | Any email address can be used; no ownership proof |
| No real user creation flow | Medium | Users must be seeded manually; no admin UI or self-registration |
| Machine auth still header-trust only | Medium | No cryptographic proof of Vapi/n8n identity; shared secret must stay confidential |
| No replay protection on webhooks | Medium | Captured valid HMAC signatures can be replayed within validity window |
| No GDPR/DSGVO compliance work | High | Real patient data cannot be processed until consent, access, and deletion flows exist |
| No production deployment | High | No hosted environment, no TLS, no CI/CD, no production secrets |

---

## 7. Recommended Next Sprint Options

### A. Frontend / Dashboard Foundation

Build the Next.js frontend skeleton: login page, session handling (httpOnly cookie or secure localStorage), clinic dashboard with appointment queue, and doctor review workflow stubs.

**Pros:** Makes the product visible to clinic staff; validates the full JWT round-trip (login → token → protected API → data) end to end; unblocks pilot user testing.
**Cons:** Requires careful decision on JWT storage and CORS configuration; does not close auth hardening gaps (no refresh tokens, no rate limiting).

### B. Auth Hardening

Add refresh token rotation, logout endpoint (token blacklist), rate limiting on `/auth/login`, and password reset via email.

**Pros:** Closes the highest-severity auth gaps before production; reduces risk of session hijacking and brute force.
**Cons:** Does not add visible product features for clinic staff; still no frontend.

### C. Deployment / Secrets Foundation

Set up a Docker production image, CI/CD pipeline, secrets manager integration (AWS Secrets Manager or equivalent), and production environment config.

**Pros:** Required before any real production traffic; enables proper `JWT_SECRET_KEY` rotation.
**Cons:** Does not add visible features; requires cloud infrastructure decisions.

### D. Provider Workflow Hardening

Add Vapi webhook replay protection (timestamp/nonce checks), Vapi tool route production smoke tests, n8n Google Calendar OAuth integration, and multi-clinic routing validation.

**Pros:** Closes remaining integration gaps proven in Sprint 6.
**Cons:** Does not unblock the frontend or address auth hardening gaps.

---

## 8. Recommended Next Path

**Sprint 8 / Module 66 — Frontend Dashboard Foundation**

**Reason:** The backend PHI layer is now complete and correctly secured behind JWT. Every human-facing API route enforces:

1. Bearer JWT presence and validity
2. Active user status
3. Clinic tenant isolation
4. Role-level access control

This means a frontend built against these routes will work with real security semantics from day one. Building the frontend next achieves:

- **End-to-end validation** of the login → JWT → protected API → data flow in a real browser
- **Pilot user testing** — clinic staff can see appointment queues and notification feeds without requiring any backend changes
- **Unblocks doctor review** — the clinical summary approval workflow exists in the backend but has no UI; this is the most valuable clinical feature to expose

Auth hardening (Option B) should be addressed in parallel or immediately after the first frontend milestone, before opening to real clinic users. Deployment (Option C) follows as a prerequisite for any real traffic.

The recommended sequence: Module 66 (frontend login + dashboard skeleton) → Module 67 (refresh tokens + rate limiting) → Module 68 (production secrets + deployment foundation).
