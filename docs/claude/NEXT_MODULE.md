# Sprint 16 / Module 116 — Backend Staging Login Smoke Evidence

Status: pending manual backend login smoke against Railway staging backend.

## Context

Module 115 complete:
- Fake staging clinic provisioned: `id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056` `slug=staging-fake-clinic` `status=active`
- Fake staging user provisioned: `id=5b63b514-7624-4e8e-9af0-71c153ba7b83` `email=doctor.staging@praximed.test` `role=doctor` `status=active`
- No password/hash/DATABASE_URL recorded
- Full test suite: 2379/2379 passed
- Commit: (see git log)

Railway backend URL: `https://web-production-fd91d.up.railway.app`
Fake staging credentials exist privately (password in developer password manager).

## Scope

Evidence doc + static tests. No deployment by Claude.
No real secrets. No production data. No token values recorded.

### The developer must:

1. Make a direct HTTP POST to the Railway backend login endpoint using curl or a REST client:

```
POST https://web-production-fd91d.up.railway.app/auth/login
Content-Type: application/json

{
  "clinic_id": "1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
  "email": "doctor.staging@praximed.test",
  "password": "<staging-password-from-password-manager>"
}
```

2. Capture sanitized response (no token value, no password):
   - HTTP status: expected `200`
   - Response body fields present: `access_token`, `token_type`, `expires_in_seconds`, `user`
   - `user.email`: expected `doctor.staging@praximed.test`
   - `user.role`: expected `doctor`
   - `user.clinic_id`: expected `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`
   - Do NOT record the actual token value

3. Also test GET /health/ready — expected HTTP 200:
```
GET https://web-production-fd91d.up.railway.app/health/ready
```
   - Expected: `{"status":"ready","checks":{"app":"ok","db":"ok"}}`

4. Record results as PASS or BLOCKED/PENDING with exact failure if any

### Evidence to capture (no secret values):

- HTTP method and URL (no password in URL)
- HTTP status code: expected `200`
- Response field names present (not values): `access_token`, `token_type`, `user`
- `user.email`, `user.role`, `user.clinic_id` — these are not secrets
- `GET /health/ready` HTTP status and response body
- Confirmation: no password, no token value, no JWT_SECRET_KEY in evidence

### Module 116 will create/update:

1. `docs/runtime/BACKEND_STAGING_LOGIN_SMOKE_EVIDENCE.md` (new) — PASS or BLOCKED/PENDING
2. Contract tests for login smoke evidence
3. Update `STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — mark login PASS if confirmed
4. Update `STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — mark check 2 (health/ready) and check 6 (fake login) PASS if confirmed; overall still BLOCKED/PENDING until Vercel/CORS/Vapi
5. Update `CURRENT_STATE.md` and `NEXT_MODULE.md` → Module 117 (Vercel frontend creation evidence)

## What not to do

- Do not deploy Railway from Claude
- Do not record the JWT token value in any document
- Do not record the staging password
- Do not record JWT_SECRET_KEY
- Do not fabricate PASS evidence
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint

## Acceptance

- `docs/runtime/BACKEND_STAGING_LOGIN_SMOKE_EVIDENCE.md` created (PASS or BLOCKED/PENDING with real evidence)
- PASS only with real HTTP 200 + expected fields from real Railway backend
- Contract tests pass
- Full test suite passes (2379/2379 minimum)
- Commit: `Sprint 16 / Module 116 — Backend staging login smoke evidence`
