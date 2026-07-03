# Deployment Smoke Runbook — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 12 / Module 94
**Status:** Planning document — no deployment executed in this module

---

## 1. Purpose

This runbook defines the smoke verification steps that must be executed after each
PraxisMed deployment to confirm the backend, frontend, database, auth, CORS, Vapi,
and n8n paths are functioning correctly.

**What this runbook is:**
- A step-by-step verification plan for local, staging, and production-like environments
- A pass/fail checklist for each deployment tier
- A failure triage reference

**What this runbook is not:**
- A production launch approval (see Section 16)
- A CI/CD pipeline specification
- A secrets or domain provisioning guide
- An auth/session refactor plan (that is Module 95+)
- A real deployment guide (no commands will deploy to production)

All commands use placeholder secrets and domain names. Real values must be supplied
from the secrets manager or platform env at execution time — never hardcoded.

---

## 2. Scope

**In scope:**
- Backend API (`/health`, auth, PHI routes, Vapi tool route)
- Frontend Next.js app (login page, dashboard, data rendering)
- PostgreSQL (connectivity, migration status)
- Auth/login flow and protected-route enforcement
- CORS (allowed origins, preflight)
- Vapi tool smoke (`POST /vapi/tools/capture-appointment-request`)
- n8n/calendar sync smoke (`POST /webhooks/n8n/calendar-sync`)
- Appointment intake loop and staff Confirm action
- Rollback plan verification

**Out of scope:**
- Real patient data
- Production launch approval
- Auth session refactor (httpOnly cookie — Module 95+)
- UI/UX polish (Fabel 5 — future sprint)
- Appointment workflow expansion (Reject, Assign, Archive)
- Calendar handoff or patient notification on Confirm
- CI/CD pipeline configuration

---

## 3. Prerequisites

Before running any smoke tier, confirm each item is true for the target environment.

### 3.1 Environment and Secrets

- [ ] All required env vars are set per `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md`
- [ ] No local-dev placeholder values (e.g., `local-dev-jwt-secret-key-change-in-production`) are present in staging or production env
- [ ] `FRONTEND_CORS_ORIGINS` is set to the exact target environment frontend URL
- [ ] `NEXT_PUBLIC_API_BASE_URL` is set to the exact target environment backend URL
- [ ] `DATABASE_URL` points to the correct tier database (not the local Docker DB in staging/prod)
- [ ] `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET` are all set to high-entropy non-placeholder values (for staging/prod)

### 3.2 Infrastructure

- [ ] PostgreSQL is reachable from the backend host
- [ ] Alembic migrations have been applied (or are about to be applied as step 1 of the runbook)
- [ ] No seed data (`seed_local_data.py`) has been run in staging or production
- [ ] Reverse proxy / TLS is configured (staging/prod); backend is served over HTTPS
- [ ] Stable domain is configured and DNS is propagated (staging/prod)
- [ ] Vapi (staging/prod) or ngrok (local) is configured to point to the correct backend URL for the target tier
- [ ] n8n (if enabled) is configured to point to the correct backend URL for the target tier

### 3.3 Rollback Plan

- [ ] A database backup exists (or the database is empty/throwaway) before any production migration
- [ ] You know how to stop the backend process without data loss
- [ ] You know how to restore the previous Docker image or code version
- [ ] No real patient traffic is routed to the environment until smoke passes

---

## 4. Smoke Tiers

### Tier A — Local Smoke

| Property | Value |
|---|---|
| **Purpose** | Verify the full stack works on a developer workstation |
| **Allowed data** | Fake/seed data only; deterministic local UUIDs; no real patients |
| **Backend URL** | `http://127.0.0.1:8000` |
| **Frontend URL** | `http://localhost:3000` |
| **Who can run** | Any developer; standard setup per `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` |
| **Pass criteria** | All checks in Section 15 pass; no errors in browser console; no backend stack traces |

### Tier B — Staging Smoke

| Property | Value |
|---|---|
| **Purpose** | Verify the stack works in a persistent non-local environment before production |
| **Allowed data** | Fake/synthetic data only; no real patient records |
| **Backend URL** | `https://api-staging.praximed.example.com` (placeholder) |
| **Frontend URL** | `https://app-staging.praximed.example.com` (placeholder) |
| **Who can run** | Developer or QA; requires access to staging secrets and Vapi staging config |
| **Pass criteria** | All checks in Section 15 pass over HTTPS; CORS errors absent; TLS valid |

### Tier C — Production-Like Pre-Traffic Smoke

| Property | Value |
|---|---|
| **Purpose** | Verify production environment is configured correctly before enabling real traffic |
| **Allowed data** | No real patient data; a dedicated non-PHI test clinic may be provisioned |
| **Backend URL** | `https://api.praximed.example.com` (placeholder) |
| **Frontend URL** | `https://app.praximed.example.com` (placeholder) |
| **Who can run** | Authorized deployment operator only; not a developer machine |
| **Pass criteria** | All checks in Section 15 pass; no local UUIDs/secrets in env; no ngrok URLs; TLS valid |

### Tier D — Post-Deployment Monitoring Smoke

| Property | Value |
|---|---|
| **Purpose** | Re-run a reduced subset of checks after each new deployment to production |
| **Allowed data** | Dedicated non-PHI test clinic only |
| **Checks** | Health, login, dashboard load, Vapi intake round-trip, Confirm action, CORS |
| **Who can run** | Any team member with access to test credentials |
| **Pass criteria** | Reduced checklist passes within expected response times |

---

## 5. Local Smoke Runbook

Run from the project root: `/Users/aliabdeltawab/Documents/praximed`

### Step 1 — Start Local PostgreSQL

```bash
docker compose -f docker-compose.postgres.yml up -d
# Wait for healthy status:
docker compose -f docker-compose.postgres.yml ps
```

Expected: `praxismed_postgres_local` shows `healthy`.

### Step 2 — Export Required Env Vars

```bash
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
export JWT_SECRET_KEY=local-dev-jwt-secret-key-change-in-production
export VAPI_WEBHOOK_SECRET=local-vapi-secret-change-me
export N8N_WEBHOOK_SECRET=local-n8n-secret-change-me
export INTERNAL_WEBHOOK_SECRET=local-internal-secret-change-me
# FRONTEND_CORS_ORIGINS: leave unset; defaults to localhost:3000
```

### Step 3 — Run Migrations

```bash
python backend/scripts/run_migrations.py
```

Expected: `Alembic upgrade head` completes with exit code 0. Output ends with `Running upgrade -> 0002_password_hash`.

### Step 4 — Seed Local Data

```bash
python backend/scripts/seed_local_data.py
```

Expected: exit code 0; seed rows inserted for clinic `11111111-1111-1111-1111-111111111111`.

### Step 5 — Start Backend

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Expected log: `Application startup complete`. No stack traces.

### Step 6 — Verify Health Endpoints

```bash
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
curl -s http://127.0.0.1:8000/health/ready | python3 -m json.tool
```

Expected `/health`: `{"status": "ok", "service": "PraxisMed API"}`
Expected `/health/ready`: `{"status": "ready", "checks": {"app": "ok"}}`

### Step 7 — Run Backend Tests

```bash
python -m pytest backend/tests/ -q
```

Expected: all tests pass; minimum 1729/1729.

### Step 8 — Start Frontend

```bash
# Local dev (do not use npm run dev in staging/prod):
cd frontend && npm run dev
```

Expected: Next.js server starts on `http://localhost:3000`. No compilation errors.

### Step 9 — Verify Frontend Login Page

Open browser: `http://localhost:3000`

Expected: 307 redirect to `http://localhost:3000/login`; login form renders.

### Step 10 — Login with Local Fake User

Enter:
- Clinic ID: `11111111-1111-1111-1111-111111111111`
- Email: _(from seed script — e.g., `doctor@localclinic.test`)_
- Password: _(from seed script)_

Expected: redirects to `http://localhost:3000/dashboard`; dashboard renders all four sections.

### Step 11 — Verify Dashboard Data

Confirm each section renders rows (from seed data):
- [ ] Appointment requests section
- [ ] Patients section
- [ ] Consultations section
- [ ] Notifications section

No browser console errors. No "Failed to load" errors.

### Step 12 — Run Local Vapi Intake Smoke

```bash
# In a separate terminal (backend still running):
python backend/scripts/smoke_vapi_appointment_intake.py
```

Expected: HTTP 200; JSON response contains `status: "new"`, `source: "vapi"`, `action_required: true`.

### Step 13 — Verify Appointment Row in Dashboard

Reload the dashboard. Confirm the new appointment request row appears with:
- `status: new`
- `source: vapi`
- Confirm button visible

### Step 14 — Staff Confirm Action

Click the Confirm button on the new appointment row.

Expected:
- Button label changes to "Confirming…" while in-flight
- Status badge changes to "confirmed"
- Confirm button disappears
- No calendar event created
- No auto-confirmation by AI

### Step 15 — Verify No Real Data

Confirm:
- [ ] All patient names are fake (e.g., "Local Test Patient")
- [ ] All UUIDs are the deterministic local `11111111-...` pattern
- [ ] No real email addresses or phone numbers

### Step 16 — Stop Local Environment

```bash
# Stop backend: Ctrl+C in uvicorn terminal
# Stop frontend: Ctrl+C in Next.js terminal
docker compose -f docker-compose.postgres.yml down
```

---

## 6. Staging Smoke Runbook

Use placeholders below. Replace with actual staging values at execution time.
**Do not store staging secrets in this document.**

### Step 1 — Verify Staging Env Vars

On the staging host or in the deployment platform:

```bash
# Confirm required vars are present (do not print values):
for var in DATABASE_URL JWT_SECRET_KEY VAPI_WEBHOOK_SECRET N8N_WEBHOOK_SECRET \
           INTERNAL_WEBHOOK_SECRET FRONTEND_CORS_ORIGINS; do
  if [ -z "${!var}" ]; then echo "MISSING: $var"; else echo "PRESENT: $var"; fi
done
```

Expected: all 6 vars show `PRESENT`.

### Step 2 — Verify Staging DB Connectivity

```bash
python backend/scripts/run_migrations.py
```

Expected: `upgrade head` completes; exit code 0; no plaintext credential in output.

### Step 3 — Start Staging Backend

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
# Or per the platform's process manager (systemd, Docker, etc.)
```

Expected log: `Application startup complete`; `Database pool initialised successfully`.

### Step 4 — Verify Staging Health Endpoints

```bash
curl -s https://api-staging.praximed.example.com/health
curl -s https://api-staging.praximed.example.com/health/ready
```

Expected: `{"status": "ok", ...}` and `{"status": "ready", ...}`. HTTPS handshake succeeds.

### Step 5 — Build and Start Staging Frontend

```bash
cd frontend
NEXT_PUBLIC_API_BASE_URL=https://api-staging.praximed.example.com npm run build
npm start
```

Expected: build completes without errors; frontend starts on the staging server.

### Step 6 — Verify HTTPS Frontend Loads

Open browser: `https://app-staging.praximed.example.com`

Expected: login page loads over HTTPS; no TLS warning; no mixed-content errors.

### Step 7 — Verify CORS from Staging Frontend to Staging API

In the browser devtools (Network tab), log in:
- Origin: `https://app-staging.praximed.example.com`
- Backend: `https://api-staging.praximed.example.com`

Expected: no CORS errors in console; `Access-Control-Allow-Origin` header in login response matches the staging frontend origin exactly.

### Step 8 — Test Login with Staging Fake User

Login with staging-only fake test credentials (not real clinic staff).

Expected: JWT returned; dashboard loads.

### Step 9 — Verify Dashboard

Confirm all four sections render (or show empty state if no seed data is present in staging).

### Step 10 — Staging Vapi Intake Smoke

Configure a staging Vapi assistant (or test harness) to call:
```
POST https://api-staging.praximed.example.com/vapi/tools/capture-appointment-request
```

With machine auth headers:
```
X-Vapi-Service-Name: vapi
X-Vapi-Clinic-Id: <staging-test-clinic-uuid>
X-Vapi-Scopes: vapi:tool
```

Expected: HTTP 200; appointment row created; `status: new`; `source: vapi`.

### Step 11 — Staging Staff Confirm

Confirm the appointment row in the staging dashboard.

Expected: status → confirmed; button disappears; no calendar event; no auto-confirmation.

### Step 12 — Verify No Secrets in Logs

Review backend log output:
- [ ] No `JWT_SECRET_KEY` value visible
- [ ] No `Authorization: Bearer` header values logged
- [ ] No raw Vapi/n8n payloads with patient names or phone numbers
- [ ] No `DATABASE_URL` (containing password) logged

---

## 7. Production-Like Pre-Traffic Smoke

**Only run after all prerequisites in Section 3 are satisfied.**
**Do not enable real patient traffic until all checks pass.**

### Step 1 — Verify Production Env Vars Are Present

```bash
for var in DATABASE_URL JWT_SECRET_KEY VAPI_WEBHOOK_SECRET N8N_WEBHOOK_SECRET \
           INTERNAL_WEBHOOK_SECRET FRONTEND_CORS_ORIGINS NEXT_PUBLIC_API_BASE_URL; do
  if [ -z "${!var}" ]; then echo "MISSING: $var"; else echo "PRESENT: $var"; fi
done
```

Do not print values. Check for presence only.

### Step 2 — Verify No Local Placeholder Values

```bash
# Fail if local-dev placeholder is still set:
if echo "$JWT_SECRET_KEY" | grep -q "local-dev"; then
  echo "FAIL: JWT_SECRET_KEY is still a local placeholder"; exit 1
fi
if echo "$VAPI_WEBHOOK_SECRET" | grep -q "change-me"; then
  echo "FAIL: VAPI_WEBHOOK_SECRET is still a local placeholder"; exit 1
fi
```

Expected: no placeholder markers in any secret.

### Step 3 — Verify Production DB Connectivity and Migration Status

```bash
python backend/scripts/run_migrations.py
# Then check migration version:
psql "$DATABASE_URL" -c "SELECT version_num FROM alembic_version;"
```

Expected: `0002_password_hash` is the current version. No migration errors.

### Step 4 — Verify No Demo Seed Data in Production DB

```bash
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM clinic_users WHERE email LIKE '%localclinic.test%';"
```

Expected: `0`. No local test accounts in production.

### Step 5 — Verify Production Health Endpoints

```bash
curl -sv https://api.praximed.example.com/health
curl -sv https://api.praximed.example.com/health/ready
```

Expected: HTTP 200 with valid TLS certificate; response body contains `"status": "ok"`.

### Step 6 — Verify HTTPS Frontend Loads

Open browser: `https://app.praximed.example.com`

Expected: login page loads over HTTPS; TLS certificate is valid; no mixed-content warnings.

### Step 7 — Verify CORS for Production Origin

In browser devtools (Network tab), inspect the login request:
- `Origin` header: `https://app.praximed.example.com`
- `Access-Control-Allow-Origin` response header: `https://app.praximed.example.com` (exact match)

Expected: no `*` wildcard; no ngrok URL; no localhost origin.

### Step 8 — Verify HTTPS/TLS

```bash
openssl s_client -connect api.praximed.example.com:443 -brief
```

Expected: certificate chain validates; no expired or self-signed certificate.

### Step 9 — Verify Vapi Production URL

Confirm in the Vapi production assistant configuration:
- Server URL contains `https://api.praximed.example.com/vapi/tools/capture-appointment-request`
- Server URL does NOT contain `ngrok`
- Server URL does NOT contain `localhost` or `127.0.0.1`
- Machine auth headers use the production clinic UUID (not `11111111-...`)
- `X-Vapi-Scopes` is `vapi:tool` (singular)

### Step 10 — Verify n8n Production Endpoint (if enabled)

Confirm in the n8n production workflow:
- Webhook URL contains `https://api.praximed.example.com/webhooks/n8n/calendar-sync`
- Webhook URL does NOT contain `ngrok` or `localhost`
- Machine auth headers use the production clinic UUID
- `N8N_WEBHOOK_SECRET` in n8n matches `N8N_WEBHOOK_SECRET` in backend env

### Step 11 — Optionally Run a Non-PHI Test Login

Using a dedicated non-PHI test clinic (not real clinic data):
- Log in with test credentials
- Verify dashboard loads
- Verify no real patient data is visible

Do not proceed to real clinic traffic until all checks pass.

---

## 8. Vapi Smoke Checks

### 8.1 Background

The full Vapi intake loop is proven in the local/test environment (Sprint 11 / Module 90).
Staging and production require a stable HTTPS backend URL instead of ngrok.

### 8.2 Endpoint

```
POST /vapi/tools/capture-appointment-request
```

### 8.3 Required Machine Auth Headers

```
X-Vapi-Service-Name: vapi
X-Vapi-Clinic-Id: <target-tier-clinic-uuid>
X-Vapi-Scopes: vapi:tool
```

**Note:** `vapi:tool` is singular. `vapi:tools` (plural) is rejected with HTTP 403.

### 8.4 Expected Behavior

| Check | Expected |
|---|---|
| HTTP response | 200 |
| Response body | `{"id": "...", "status": "new", "source": "vapi", "action_required": true, ...}` |
| No auto-confirmation | `status` must be `"new"`, not `"confirmed"` |
| No calendar booking | No calendar event created |
| Appointment row visible | Row appears in dashboard after Vapi call |
| Staff Confirm works | Status transitions to `"confirmed"` after human click |

### 8.5 Clinic ID Security

The `clinic_id` for the appointment is always taken from the `X-Vapi-Clinic-Id`
machine auth header — never from patient-supplied arguments. Any `clinic_ref` field in
the Vapi tool call arguments is silently ignored. This is enforced by
`adapt_vapi_tool_call_body` in the backend.

### 8.6 Log Safety

After the smoke call, check backend logs:
- [ ] No raw patient name, phone number, or transcript text logged
- [ ] No full tool-call argument body logged
- [ ] `raw_payload` column in DB stores the captured payload (this is correct behavior — it is the audit trail)

---

## 9. n8n / Calendar Sync Smoke Checks

### 9.1 Endpoint

```
POST /webhooks/n8n/calendar-sync
```

### 9.2 Required Headers

```
X-Service-Name: n8n
X-Service-Clinic-Id: <target-tier-clinic-uuid>
X-Service-Scopes: calendar:sync
X-N8N-Signature: sha256=<hmac-sha256-hex-digest>
```

### 9.3 Sign a Test Payload

```bash
N8N_SIG=$(python backend/scripts/sign_webhook_payload.py \
  --secret "$N8N_WEBHOOK_SECRET" \
  --payload-file docs/integrations/local_payloads/n8n_calendar_sync.json)
```

### 9.4 Expected Behavior

| Check | Expected |
|---|---|
| HTTP response | 200 |
| Machine auth | Valid `X-Service-Name`, `X-Service-Clinic-Id`, `X-Service-Scopes` accepted |
| HMAC verified | Valid `X-N8N-Signature` accepted; wrong signature → 401 |
| No browser CORS | n8n is server-to-server; no CORS check applies |
| No calendar event | Production calendar handoff remains a future module; verify no calendar event is created unless explicitly implemented |

### 9.5 n8n Not Enabled

If n8n is not configured for the target tier, this check is:
- **Local:** Run using the local payload and `sign_webhook_payload.py` (per `LOCAL_INTEGRATION_RUNBOOK.md`)
- **Staging/Production:** Mark as "NOT ENABLED" in the checklist and note as a future enablement step

---

## 10. CORS Smoke Checks

### 10.1 Allowed Origin (per tier)

| Tier | Allowed Origin |
|---|---|
| Local | `http://localhost:3000` |
| Staging | `https://app-staging.praximed.example.com` |
| Production | `https://app.praximed.example.com` |

### 10.2 Browser Smoke (Happy Path)

In the browser devtools (Network tab), trigger a login request from the frontend:

Expected:
- Response header `Access-Control-Allow-Origin` is the exact frontend origin
- No `*` wildcard
- No CORS error in console
- No `Access-Control-Allow-Origin: http://localhost:3000` in staging/prod responses

### 10.3 Rejected Origin (Negative Test)

From a different origin (e.g., a browser tab opened via `localhost` while testing staging):

Expected: CORS rejection; browser blocks the response; `Access-Control-Allow-Origin` is absent or mismatched.

### 10.4 OPTIONS Preflight (PATCH/POST)

The browser sends a preflight `OPTIONS` before `PATCH /appointment-requests/{id}/status`.

Expected:
- `OPTIONS` response: HTTP 200
- `Access-Control-Allow-Methods` includes `PATCH`
- `Access-Control-Allow-Headers` includes `Authorization` and `Content-Type`

### 10.5 Machine Auth Headers Do Not Need CORS

`X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes`, `X-Vapi-Signature`, and
`X-N8N-Signature` are not sent by the browser. They are Vapi/n8n machine-to-machine
headers. They do not need to appear in `Access-Control-Allow-Headers` and are not
part of the browser CORS check.

---

## 11. Auth / Session Smoke Checks

### 11.1 Current Flow (Local and Staging)

```
POST /auth/login → { access_token, expires_in_seconds: 3600 }
  → client stores in sessionStorage
  → all API calls: Authorization: Bearer <token>
  → 60 minutes until expiry
  → no auto-refresh
```

### 11.2 Login Smoke

- [ ] `POST /auth/login` with valid credentials → HTTP 200; `access_token` in response
- [ ] `POST /auth/login` with wrong password → HTTP 401; `"Invalid credentials"` detail
- [ ] `POST /auth/login` with missing `JWT_SECRET_KEY` → HTTP 503

### 11.3 Protected Route Smoke

- [ ] `GET /appointment-requests?clinic_id=<uuid>` without token → HTTP 401 or 403
- [ ] `GET /appointment-requests?clinic_id=<uuid>` with valid token → HTTP 200
- [ ] `GET /appointment-requests?clinic_id=<uuid>` with expired token → HTTP 401

### 11.4 Logout Smoke

- [ ] Click logout in dashboard → `sessionStorage` cleared → redirect to `/login`
- [ ] After logout, navigating to `/dashboard` redirects to `/login`

### 11.5 Production PHI Note

**The `sessionStorage` JWT mechanism is intentionally labeled local-dev only in the
code (`frontend/lib/auth.ts` line 4–5). It is not suitable for production PHI without
additional security hardening.**

Before a production deployment serving real clinic data, the auth session hardening
decision from Module 93 must be made and implemented:
- Option B (recommended): httpOnly Secure SameSite=Lax cookie — requires Module 95+ implementation
- Option A (accepted risk): retain sessionStorage with strict CSP + short expiry

This smoke runbook does not approve the sessionStorage path for real PHI production.

---

## 12. Database / Migration Smoke Checks

### 12.1 Migration Smoke

```bash
# Verify migrations run cleanly:
python backend/scripts/run_migrations.py

# Verify current migration version:
psql "$DATABASE_URL" -c "SELECT version_num FROM alembic_version;"
```

Expected: `0002_password_hash` is the head revision.

### 12.2 Migration Failure Protocol

If `run_migrations.py` exits non-zero:
1. Do NOT start the backend
2. Do NOT route traffic
3. Inspect Alembic output for the failing migration
4. Restore the database backup if the migration partially ran
5. Fix the migration and retry in a test environment before production

### 12.3 DB Connectivity Smoke

```bash
python backend/scripts/db_smoke_test.py
```

Expected: exit code 0; no connection errors.

### 12.4 No Demo Seed in Staging/Production

```bash
# Confirm no seed accounts in staging/prod:
psql "$DATABASE_URL" -c \
  "SELECT COUNT(*) FROM clinic_users WHERE email LIKE '%localclinic.test%' OR email LIKE '%test%';"
```

Expected: `0` (or known intentional test accounts documented separately).

### 12.5 Backup Before Production Migration

Before applying migrations to a production database that contains real data:
1. Confirm a point-in-time backup is available and recent
2. Test the migration against a copy of the production DB in staging first
3. Confirm rollback path: restore from backup if migration fails

Tenant provisioning (creating clinic records and initial staff accounts) is a separate
operational step not covered by this runbook.

---

## 13. Observability / Logging Smoke

### 13.1 Backend Startup Logs

Expected at startup:
```
INFO:     Application startup complete.
INFO:     Database pool initialised successfully
```

If `DATABASE_URL` is not set:
```
WARNING: DATABASE_URL is not set — app.state.db_pool is None.
```

### 13.2 Request Logs

Expected for a successful `POST /auth/login`:
```
INFO:     127.0.0.1 - "POST /auth/login HTTP/1.1" 200
```

No JWT token value, no password value, no email address in the log line.

### 13.3 What Must NOT Appear in Logs

- [ ] No `JWT_SECRET_KEY` value
- [ ] No `Authorization: Bearer <token>` header value
- [ ] No `DATABASE_URL` (contains DB password)
- [ ] No raw Vapi/n8n tool call body with patient name, phone number, or transcript text
- [ ] No raw `caller_phone`, `patient_name`, `date_of_birth` values from API payloads

### 13.4 Current Observability Gaps

| Gap | Risk | Notes |
|---|---|---|
| No structured/JSON logging | Medium | `uvicorn` default logs are not structured; harder to query in production |
| No request IDs | Medium | Tracing a specific request across services is difficult without correlation IDs |
| No APM/tracing | Low for now | Future sprint; not a blocker for first staging smoke |
| `raw_payload` column in DB | PHI note | Contains Vapi tool call body; must be access-controlled in production; review before PHI launch |

---

## 14. Failure Triage Table

| Smoke Check | Common Failure | Likely Cause | Where to Look | Safe Next Action |
|---|---|---|---|---|
| `GET /health` returns 404 | Backend not started or wrong port | Uvicorn started on wrong port or not running | `ps aux | grep uvicorn`; check startup logs | Confirm correct port; restart backend |
| `GET /health` returns 503 | App started but DB pool failed | `DATABASE_URL` missing or wrong | Backend startup logs: `app.state.db_pool is None` | Set `DATABASE_URL`; restart backend |
| Frontend cannot reach API | CORS error or wrong `NEXT_PUBLIC_API_BASE_URL` | Env var not set; frontend using localhost fallback in staging/prod | Browser console CORS error; Network tab | Set `NEXT_PUBLIC_API_BASE_URL`; rebuild frontend |
| CORS error in browser | Origin mismatch | `FRONTEND_CORS_ORIGINS` not set or wrong value | Response headers: `Access-Control-Allow-Origin` absent or mismatched | Set `FRONTEND_CORS_ORIGINS` to exact frontend URL; restart backend |
| Login returns 503 | `JWT_SECRET_KEY` not set | `MissingJWTSecretError` at first JWT operation | Backend logs: `503 SERVICE_UNAVAILABLE` | Set `JWT_SECRET_KEY`; restart backend |
| Login returns 401 | Wrong credentials or wrong clinic UUID | Seed data not run; wrong test user | Verify `clinic_id` matches seed; check `clinic_users` table | Re-run seed (local only); verify test user credentials |
| Dashboard shows empty sections | API returns 401 or wrong `clinic_id` | Token expired; `clinic_id` mismatch | Browser Network tab: check request `clinic_id` query param and response status | Re-login; verify `getClinicId()` returns the seeded clinic UUID |
| Vapi returns 403 | Wrong scope or wrong service name | `X-Vapi-Scopes: vapi:tools` (plural) or missing header | Backend logs: `403 Forbidden`; check `require_vapi_tool_access` | Set `X-Vapi-Scopes: vapi:tool` (singular) |
| Vapi returns 422 | Payload validation failed | Adapter did not normalize the body correctly | Backend logs: `422 Unprocessable Entity`; check raw body shape | Inspect payload with `inspect_vapi_tool_payload.py`; check adapter output |
| Vapi returns 500 | Config loader error or DB error | `ClinicConfigLoader` cannot find clinic config; DB pool broken | Backend logs: stack trace | Check `backend/tenants/configs/<clinic-id>/clinic_config.json` exists; check DB |
| n8n returns 401 | HMAC signature mismatch | `N8N_WEBHOOK_SECRET` mismatch between n8n and backend | Backend logs: `401 Unauthorized`; check signature header | Verify `N8N_WEBHOOK_SECRET` matches in both places |
| Migrations fail | SQL error or missing revision | DB schema already partially applied; revision not found | Alembic output; `alembic history` | Restore DB backup; fix migration in a safe environment first |
| DB connection fails | Wrong `DATABASE_URL` or DB not running | Local Docker not started; production DB credentials wrong | Backend startup log: pool initialization error | Start DB; verify `DATABASE_URL` connection string |
| HTTPS/TLS error | Certificate not configured or expired | Reverse proxy not started; cert expired; wrong domain | `openssl s_client -connect <host>:443 -brief` | Renew cert; check Nginx/Caddy config; verify DNS points to reverse proxy |

---

## 15. Pass / Fail Checklist

Run through this checklist after completing the smoke steps for the target tier.
**All items must be checked before declaring smoke PASS.**

### Backend

- [ ] `GET /health` returns `{"status": "ok"}` — HTTP 200
- [ ] `GET /health/ready` returns `{"status": "ready"}` — HTTP 200
- [ ] Backend startup logs contain no stack traces
- [ ] `DATABASE_URL` is set and DB pool initialized (not `app.state.db_pool is None`)

### Database / Migrations

- [ ] `run_migrations.py` completes with exit code 0
- [ ] `alembic_version` table shows `0002_password_hash`
- [ ] No demo seed data in staging/production DB
- [ ] DB backup confirmed (staging/prod only)

### Frontend

- [ ] Frontend loads over HTTPS (staging/prod) or HTTP (local)
- [ ] Login page renders correctly
- [ ] `NEXT_PUBLIC_API_BASE_URL` is set to the correct tier backend URL
- [ ] No browser console errors on load

### Auth / Session

- [ ] Login with valid fake test credentials → dashboard loads
- [ ] Login with wrong credentials → HTTP 401; error message shown
- [ ] Protected dashboard rejects unauthenticated access → redirects to `/login`
- [ ] Logout clears session → redirects to `/login`

### Dashboard Data

- [ ] Appointment requests section renders (or shows empty state)
- [ ] Patients section renders (or shows empty state)
- [ ] Consultations section renders (or shows empty state)
- [ ] Notifications section renders (or shows empty state)

### Appointment Intake Loop

- [ ] Vapi intake (harness or Vapi assistant) → HTTP 200 → row appears in dashboard
- [ ] Row has `status: new`, `source: vapi`, `action_required: true`
- [ ] Staff Confirm → status → `confirmed` → Confirm button disappears
- [ ] No auto-confirmation by AI
- [ ] No calendar booking

### CORS

- [ ] Login request from frontend origin → no CORS error in browser console
- [ ] `Access-Control-Allow-Origin` response header matches the exact frontend origin
- [ ] No `*` wildcard in `Access-Control-Allow-Origin`
- [ ] `OPTIONS` preflight for `PATCH` request returns HTTP 200 with correct headers

### Vapi / n8n

- [ ] Vapi tool call to correct tier URL → HTTP 200
- [ ] n8n webhook to correct tier URL → HTTP 200 (or: NOT ENABLED, documented)
- [ ] No ngrok URL in any production env var
- [ ] Vapi machine auth headers use tier-correct clinic UUID (not `11111111-...` in staging/prod)

### Secrets / Logs

- [ ] No local placeholder values in staging/production env
- [ ] No secrets visible in backend logs
- [ ] No `Authorization: Bearer` token values in logs
- [ ] No raw patient data in logs

---

## 16. Production Launch Gate

**Passing this smoke runbook does NOT approve a production launch.**

This runbook confirms the technical stack is functioning. A production launch also
requires the following, which are not verified here:

| Requirement | Status |
|---|---|
| Auth session hardening decision (sessionStorage → httpOnly cookie or accepted-risk CSP plan) | Pending Module 95+ |
| Stable HTTPS production domain registered and configured | Pending infrastructure |
| Managed PostgreSQL with backups and point-in-time recovery | Pending infrastructure |
| Secrets in production-grade secret manager (not shell exports) | Pending infrastructure |
| Production Vapi assistant configured (not test assistant) | Pending Vapi configuration |
| Production CORS origins set (not staging origins) | Pending domain confirmation |
| Legal / GDPR / Austrian healthcare compliance review | Not started |
| Monitoring, alerting, and on-call runbook | Not started |

**Recommended next step:** Architecture Checkpoint 12 — Production Readiness Review

---

## 17. Appendix — Current Local Commands Reference

Compact reference for the local development environment. Use placeholder secrets shown;
replace with real values from `backend/.env.example`.

```bash
# 1. Start local database
docker compose -f docker-compose.postgres.yml up -d

# 2. Set environment variables
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
export JWT_SECRET_KEY=local-dev-jwt-secret-key-change-in-production
export VAPI_WEBHOOK_SECRET=local-vapi-secret-change-me
export N8N_WEBHOOK_SECRET=local-n8n-secret-change-me
export INTERNAL_WEBHOOK_SECRET=local-internal-secret-change-me

# 3. Run migrations
python backend/scripts/run_migrations.py

# 4. Seed local data (local only — never in staging/production)
python backend/scripts/seed_local_data.py

# 5. Start backend
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

# 6. Start frontend (separate terminal)
cd frontend && npm run dev

# 7. Run all backend tests
python -m pytest backend/tests/ -q

# 8. Run local Vapi intake smoke
python backend/scripts/smoke_vapi_appointment_intake.py

# 9. Sign a webhook payload (local testing only)
python backend/scripts/sign_webhook_payload.py \
  --secret "$VAPI_WEBHOOK_SECRET" \
  --payload-file docs/integrations/local_payloads/vapi_call_event.json

# 10. Check git status
git status && git log --oneline -5

# 11. Stop local database
docker compose -f docker-compose.postgres.yml down
```
