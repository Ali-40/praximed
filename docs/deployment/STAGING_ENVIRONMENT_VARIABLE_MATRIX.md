# Staging Environment Variable Matrix — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 13 / Module 96
**Status:** Planning only — no deployment executed in this module; no runtime code changed

---

## 1. Purpose

This document defines the exact environment variable matrix for every component in the
PraxisMed staging environment. It specifies what each variable is, where it lives, how
it is injected, whether it is a secret, and what happens if it is missing or wrong.

**What this document is:**
- The staging-specific companion to `ENVIRONMENT_AND_SECRETS_CONTRACT.md`
- A complete per-variable specification for Railway backend, Railway PostgreSQL, Vercel
  frontend, Vapi test assistant, and n8n staging workflow
- The input reference for Module 97 (Staging Deployment Dry-Run Checklist)

**What this document is not:**
- A deployment execution guide — no deployment is run in this module
- A production env var specification — production values are not defined here
- An auth/session hardening plan — that is Module 98
- A Fabel 5 / frontend UX sprint
- A document that contains real secrets

**Staging constraint:** staging uses fake/non-PHI data only. No real clinic staff, no
real patients, no real Vapi production assistant, no production database.

---

## 2. Environment Boundary

### 2.1 Three Active Tiers

| Tier | Purpose | Data Type | Secret Type |
|---|---|---|---|
| **Local** | Developer workstation; manual testing | Fake seed data; deterministic UUIDs | Placeholder values (`.env.example`) |
| **Staging** | Pre-production validation; Vapi integration smoke | Fake/synthetic only; staging UUID | High-entropy values distinct from local and production |
| **Production** | Real clinic use; real patients; real staff | Real PHI; GDPR-applicable | High-entropy production secrets; no overlap with staging |

### 2.2 Isolation Rules

- **Staging must not reuse local secrets.** The local-dev placeholder values (e.g.
  `local-dev-jwt-secret-key-change-in-production`) must never appear in any staging
  environment variable. They identify developer workstations; using them in staging
  removes the security boundary between tiers.

- **Staging must not reuse production secrets.** Production secrets do not exist yet
  (production PHI launch is NO-GO per Architecture Checkpoint 12). When they are
  created, they must be independent values distinct from staging.

- **Staging uses fake/non-PHI data only.** No real patient names, phone numbers, or
  medical records may appear in any staging database row, log line, or Vapi test call.

- **Production PHI remains NO-GO.** Architecture Checkpoint 12 identified 12 unresolved
  blockers. This staging matrix does not resolve any of them. Staging approval does not
  imply production PHI approval.

- **`sessionStorage` JWT is acceptable only for fake-data staging.** The frontend stores
  the JWT access token in `sessionStorage` — an XSS-accessible location, explicitly
  labeled `local-dev only` in `frontend/lib/auth.ts`. This is acceptable in staging
  because no real PHI is present. It must be replaced with httpOnly cookie auth (Module
  98) before any real clinic staff access a production instance.

---

## 3. Staging Components

| Component | Platform | Role | Public/Private | Data Policy |
|---|---|---|---|---|
| **Railway backend API** | Railway (PaaS) | FastAPI server; handles all API requests | Private endpoint; accessible over HTTPS | Fake/synthetic data only; no PHI |
| **Railway PostgreSQL** | Railway (managed DB) | PostgreSQL 16; persists appointment requests, patients, consultations, audit logs | Private; accessible only from Railway backend | Fake staging clinic UUID; no real records |
| **Vercel frontend** | Vercel (PaaS) | Next.js 14 static build + Edge runtime; staff-facing dashboard | Public URL; HTTPS | No PHI; no secrets; session token in `sessionStorage` |
| **Vapi test assistant** | Vapi dashboard | Makes test calls to staging API capture endpoint | Outbound to Railway API only | Fake patient names only; no real calls |
| **n8n staging workflow** | n8n (external) | Posts signed calendar sync webhooks to Railway API | Outbound to Railway API only; server-to-server | Test calendar events only; no production writes |
| **Staging domain / DNS** | Railway + Vercel auto-provisioned | `*.up.railway.app` and `*.vercel.app` | Public HTTPS | Not custom domain; no DNS management required for staging |

---

## 4. Backend Staging Environment Variable Matrix

All backend env vars are set in the **Railway service environment** via the Railway
dashboard or Railway CLI. No `.env` file is used in staging. No env var is committed
to git.

### 4.1 Complete Table

| Variable | Required in Railway? | Staging Placeholder | Secret? | Source / Owner | Consumed By | Failure if Missing |
|---|---|---|---|---|---|---|
| `DATABASE_URL` | **Yes — auto-injected** | `<railway-postgres-private-url>` | Yes | Railway PostgreSQL add-on | `backend/app/main.py` lifespan; `backend/migrations/env.py` | DB pool not created; all DB-backed routes return HTTP 503 |
| `JWT_SECRET_KEY` | **Yes** | `<staging-high-entropy-secret-32-bytes>` | Yes | Railway dashboard | `backend/app/core/jwt_tokens.py` `_get_jwt_secret()` | `MissingJWTSecretError` on first login; `/auth/login` returns HTTP 500 |
| `VAPI_WEBHOOK_SECRET` | **Yes** | `<staging-vapi-hmac-secret-32-bytes>` | Yes | Railway dashboard; must match Vapi staging assistant signing secret | `backend/app/core/webhook_provider_config.py` `get_provider_secret_from_env("vapi")` | `MissingWebhookSecretError` on first Vapi webhook call; returns HTTP 503 |
| `N8N_WEBHOOK_SECRET` | **Yes** | `<staging-n8n-hmac-secret-32-bytes>` | Yes | Railway dashboard; must match n8n staging workflow signing secret | `backend/app/core/webhook_provider_config.py` `get_provider_secret_from_env("n8n")` | `MissingWebhookSecretError` on first n8n webhook call; returns HTTP 503 |
| `INTERNAL_WEBHOOK_SECRET` | **Yes** | `<staging-internal-hmac-secret-32-bytes>` | Yes | Railway dashboard; PraxisMed internal only | `backend/app/core/webhook_provider_config.py` `get_provider_secret_from_env("internal")` | `MissingWebhookSecretError` on first internal webhook call; returns HTTP 503 |
| `FRONTEND_CORS_ORIGINS` | **Yes** | `https://staging-app.vercel.app` | No | Railway dashboard; set to exact Vercel staging frontend origin | `backend/app/main.py` `_cors_origins()` → `CORSMiddleware` | Defaults to `http://localhost:3000` — staging frontend blocked by CORS on all requests |
| `POSTGRES_DB` | No (Railway auto-manages) | _(Railway auto-provisioned)_ | No | Railway managed DB | Docker Compose only (not used in Railway deployment) | No app failure; Railway manages DB directly via `DATABASE_URL` |
| `POSTGRES_USER` | No (Railway auto-manages) | _(Railway auto-provisioned)_ | No | Railway managed DB | Docker Compose only | No app failure |
| `POSTGRES_PASSWORD` | No (Railway auto-manages) | _(Railway auto-provisioned; embedded in DATABASE_URL)_ | Yes | Railway managed DB | Embedded in `DATABASE_URL` | Exposed only if `DATABASE_URL` is leaked; never set independently |
| `APP_ENV` | Optional | `staging` | No | Railway dashboard | Informational; not consumed by app logic | No failure; informational only |
| `API_HOST` | Optional | Not set (Railway manages host binding) | No | Not applicable in Railway | Railway uses `$PORT`; not `API_HOST` | No failure |
| `API_PORT` | Optional | Not set (Railway uses `$PORT` automatically) | No | Railway auto-sets `$PORT` | Start command uses `$PORT` | No failure; Railway always sets `$PORT` |

### 4.2 Variable Notes

**`DATABASE_URL`**
- Railway PostgreSQL add-on injects this automatically when attached to the backend service.
- Format: `postgresql://<user>:<password>@<host>.railway.internal:<port>/<db>`
- The private URL uses Railway's internal network (`.railway.internal`); faster and not
  publicly accessible.
- Never hardcoded. Never printed in logs. Never set manually if Railway auto-injects it.
- Alembic's `backend/migrations/env.py` also reads this var to apply migrations.

**`JWT_SECRET_KEY`**
- Set in Railway dashboard → Service → Variables.
- Must be a high-entropy value generated with `openssl rand -hex 32` or equivalent.
- Must not be the local placeholder `local-dev-jwt-secret-key-change-in-production`.
- Rotating this value invalidates all active staging JWT sessions — all staging users
  must re-login.
- Consumed by `backend/app/core/jwt_tokens.py` — every `POST /auth/login` call and
  every token verification via `get_current_user`.

**`VAPI_WEBHOOK_SECRET`**
- Set in Railway dashboard AND configured as the signing secret in the Vapi staging
  test assistant webhook settings.
- Both sides must match exactly; if they differ, all Vapi webhook calls return HTTP 401.
- Consumed by `backend/app/core/webhook_provider_config.py`; accepted headers:
  `X-Vapi-Signature`, `X-Vapi-Hmac-Sha256`, `X-Signature` (in priority order).

**`N8N_WEBHOOK_SECRET`**
- Set in Railway dashboard AND configured in the n8n staging workflow HTTP request node
  as the HMAC signing secret.
- Accepted headers: `X-N8N-Signature`, `X-N8n-Signature`, `X-Signature`.

**`INTERNAL_WEBHOOK_SECRET`**
- PraxisMed internal only. No external service dependency.
- Set in Railway dashboard to a unique staging value.
- Accepted header: `X-Internal-Signature`, `X-Signature`.

**`FRONTEND_CORS_ORIGINS`**
- Must be set to the exact Vercel staging frontend origin.
- Example placeholder: `https://staging-app.vercel.app`
- No wildcard (`*`). No localhost. No ngrok URL. No trailing slash.
- The `_cors_origins()` function in `main.py` never returns a wildcard; if
  `FRONTEND_CORS_ORIGINS` contains `*`, it is passed through as-is and will fail
  preflight checks in browsers that reject wildcard with credentials.
- If not set, `_cors_origins()` defaults to `["http://localhost:3000",
  "http://127.0.0.1:3000"]` — the staging frontend is blocked with CORS errors.

**`$PORT` (Railway auto-set)**
- Railway injects `$PORT` automatically. The backend start command must use `$PORT`:
  ```
  python backend/scripts/run_migrations.py && \
  python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
  ```
- This is not a secret and is not set by the operator.

---

## 5. Frontend Staging Environment Variable Matrix

All frontend env vars are set in the **Vercel project settings → Environment Variables**,
scoped to the **Production** or **Preview** environment (depending on branch strategy).

| Variable | Required in Vercel? | Staging Value Placeholder | Secret? | Consumed By | Failure if Wrong |
|---|---|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | **Yes** | `https://staging-api.up.railway.app` | No (public — browser-visible) | `frontend/lib/api.ts` — prefixed to every API call | If wrong URL: all API calls go to wrong host; login fails; dashboard shows no data |

### 5.1 `NEXT_PUBLIC_API_BASE_URL` Detail

- **Classification:** Public. The `NEXT_PUBLIC_` prefix causes Next.js to embed this value
  in the browser bundle at build time. Anyone can inspect it in page source. It is not a
  secret.
- **Value for staging:** The exact Railway backend API URL, e.g.
  `https://staging-api.up.railway.app`. No trailing slash.
- **Production must differ:** The production value will be a different HTTPS URL. If
  staging and production share this value, staging traffic hits the production backend.
- **Fallback in code:** `frontend/lib/api.ts` falls back to `http://127.0.0.1:8000` if
  `NEXT_PUBLIC_API_BASE_URL` is not set. This fallback never works in a Vercel deployment
  (the browser cannot reach `127.0.0.1:8000` on Railway). The variable must be set.
- **Build-time variable:** Vercel builds the frontend when a new commit is pushed. The
  value of `NEXT_PUBLIC_API_BASE_URL` is baked into the build. If the Railway URL changes
  after a Vercel build, the frontend must be rebuilt and redeployed.

### 5.2 What Must NOT Be in Frontend Env Vars

The following must never be set as frontend environment variables (i.e., in Vercel or
in `frontend/.env.example`):

- `DATABASE_URL` — backend secret; exposes DB credentials to browser
- `JWT_SECRET_KEY` — backend secret; exposes signing key to browser
- `VAPI_WEBHOOK_SECRET` / `N8N_WEBHOOK_SECRET` / `INTERNAL_WEBHOOK_SECRET` — backend
  secrets; exposing them allows forged webhook requests
- Any `POSTGRES_*` credentials
- Any API keys from third-party services

---

## 6. PostgreSQL Staging Matrix

### 6.1 Platform: Railway Managed PostgreSQL

| Property | Staging Value |
|---|---|
| Platform | Railway PostgreSQL add-on (same Railway project as backend) |
| PostgreSQL version | 16 (Railway default) |
| `DATABASE_URL` | Auto-injected by Railway; format: `postgresql://<user>:<pass>@<host>.railway.internal:<port>/<db>` |
| Public access | Railway exposes a separate public URL for migrations or one-off access if needed; internal URL for service-to-service |
| Isolation | Completely separate from local Docker DB (port 5433) and any future production DB |
| Data type | Fake/synthetic only — no real patient records; no real clinic data |
| Backup policy | Railway PostgreSQL provides basic snapshotting; data loss in staging is acceptable — re-run migrations and re-seed |

### 6.2 Local Docker DB vs. Staging DB

| Property | Local | Staging |
|---|---|---|
| Platform | Docker Compose (`docker-compose.postgres.yml`) | Railway managed PostgreSQL |
| Port | 5433 (local Docker) | Managed by Railway |
| `DATABASE_URL` format | `postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local` | `<railway-postgres-private-url>` |
| Seed data | `backend/scripts/seed_local_data.py` (local UUIDs) | **Do not run** `seed_local_data.py` — local UUIDs must not appear in staging |
| Clinic UUID | `11111111-1111-1111-1111-111111111111` (local deterministic) | `<staging-fake-clinic-uuid>` (unique per-staging UUID; not a local or production UUID) |

### 6.3 Migration Strategy

Migrations must be applied before any backend traffic. The recommended Railway start
command runs migrations as a gate:

```
python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

If `run_migrations.py` exits non-zero, the `&&` short-circuits and uvicorn does not start.
Railway marks the deploy as failed. This is the safe default: never route traffic to a
backend that has not passed migrations.

### 6.4 Staging Seed Strategy

- Do NOT run `backend/scripts/seed_local_data.py` in staging.
- The local seed uses `11111111-...` deterministic UUIDs that must stay local.
- A staging-specific seed approach:
  1. Generate a staging fake clinic UUID (different from local `11111111-...` UUID).
  2. Insert a staging clinic row and a staging staff user row via a one-time SQL script
     or a staging-specific seed script (to be created in Module 97 or a later module).
  3. Record the staging fake clinic UUID as a documented placeholder — not a secret, but
     must be a stable value across all staging components (Vapi header, n8n header, DB
     row, staff JWT).
- Staging clinic UUID placeholder: `<staging-fake-clinic-uuid>` — to be assigned when
  the staging database is provisioned.

### 6.5 No Production DB

Staging must never connect to a production database. `DATABASE_URL` in Railway points to
the Railway-provisioned staging PostgreSQL only. No production connection string is ever
set in the staging Railway environment.

---

## 7. Vapi Staging Matrix

The Vapi test assistant is configured in the Vapi dashboard (not in Railway or Vercel).
No Vapi credentials are environment variables on the backend — Vapi calls the backend
using machine auth headers, not credentials.

### 7.1 Vapi Staging Configuration

| Item | Staging Value |
|---|---|
| Assistant type | Vapi **test assistant** — not a production assistant |
| Server URL (tool endpoint) | `https://staging-api.up.railway.app/vapi/tools/capture-appointment-request` |
| `X-Vapi-Service-Name` header | `vapi` |
| `X-Vapi-Clinic-Id` header | `<staging-fake-clinic-uuid>` (must match the clinic UUID in the staging DB) |
| `X-Vapi-Scopes` header | `vapi:tool` (**singular** — `vapi:tools` plural is rejected with HTTP 403) |
| Webhook signing secret | `VAPI_WEBHOOK_SECRET` (set in Railway) must match the signing secret in Vapi staging assistant settings |
| Calls | Fake calls only — no real phone numbers, no real patients |
| ngrok | **Not used in staging** — Railway URL is stable; ngrok is not needed |

### 7.2 Machine Auth Headers (Not Backend Env Vars)

The Vapi machine auth headers are configured in the Vapi dashboard as HTTP headers sent
with every tool call. They are not backend env vars. The backend reads them via:
- `request.headers.get("x-vapi-service-name")`
- `request.headers.get("x-vapi-clinic-id")` — this is the authoritative `clinic_id`;
  any `clinic_ref` in the Vapi function arguments is silently ignored
- `request.headers.get("x-vapi-scopes")`

### 7.3 Expected Outcome of a Staging Vapi Test Call

1. Vapi test assistant fires `capture_appointment_request` tool
2. Vapi POSTs to `https://staging-api.up.railway.app/vapi/tools/capture-appointment-request`
   with machine auth headers and fake patient arguments
3. Backend adapter (`adapt_vapi_tool_call_body`) normalizes nested/flat Vapi payload shape
4. Appointment row created: `status=new`, `source=vapi`, `action_required=True`,
   `clinic_id=<staging-fake-clinic-uuid>`
5. Staging dashboard shows the new row after staff login
6. Staff Confirm button transitions status to `confirmed`
7. No auto-confirmation. No calendar booking.

---

## 8. n8n Staging Matrix

The n8n staging workflow posts to the Railway backend webhook endpoint. This is a
server-to-server call — no browser CORS dependency.

### 8.1 n8n Staging Configuration

| Item | Staging Value |
|---|---|
| n8n instance | Staging n8n workflow (isolated from local and any production workflow) |
| Webhook URL | `https://staging-api.up.railway.app/webhooks/n8n/calendar-sync` |
| `X-Service-Name` header | `n8n` |
| `X-Service-Clinic-Id` header | `<staging-fake-clinic-uuid>` (must match staging DB) |
| `X-Service-Scopes` header | `calendar:sync` |
| Webhook signature header | `X-N8N-Signature: sha256=<hmac>` (HMAC-SHA256 with `N8N_WEBHOOK_SECRET`) |
| `N8N_WEBHOOK_SECRET` | Set in Railway dashboard; must match the HMAC secret in the n8n workflow HTTP request node |
| Calendar | Test/fake calendar only — no production calendar writes |
| CORS | Not applicable — server-to-server; no browser involved |

### 8.2 n8n Backend Env Var

`N8N_WEBHOOK_SECRET` is the only env var the backend needs for n8n integration. It is
set in Railway and used by `get_provider_secret_from_env("n8n")` to verify the HMAC
signature on each incoming n8n webhook request.

### 8.3 n8n Staging Status

If n8n is not configured for staging, the n8n smoke check is marked **NOT ENABLED** in
the smoke runbook and deferred to a later module. The backend does not require n8n to
start or serve requests.

---

## 9. Domain and CORS Variable Mapping

### 9.1 Staging Domain Placeholders

| Item | Staging Placeholder |
|---|---|
| Backend (Railway) | `https://staging-api.up.railway.app` |
| Frontend (Vercel) | `https://staging-app.vercel.app` |

These are Railway/Vercel auto-provisioned subdomains. Custom domains are not required
for staging.

### 9.2 CORS Variable Mapping

| Variable | Where Set | Staging Value | Rule |
|---|---|---|---|
| `FRONTEND_CORS_ORIGINS` | Railway dashboard | `https://staging-app.vercel.app` | Exact origin; no wildcard; no localhost; no ngrok |
| `NEXT_PUBLIC_API_BASE_URL` | Vercel dashboard | `https://staging-api.up.railway.app` | Exact URL; no trailing slash; must match Railway backend URL |

### 9.3 CORS Hard Rules

- **No wildcard `*` origin.** The `_cors_origins()` function in `main.py` never returns
  a wildcard. Any request from a non-listed origin is blocked.
- **No ngrok URL.** ngrok is a local testing tunnel. Railway provides a stable HTTPS URL
  that replaces ngrok entirely in staging.
- **HTTPS only.** Plain HTTP origins are not accepted in staging. Railway and Vercel both
  auto-provision TLS.
- **Staging and production domains must be separate.** `FRONTEND_CORS_ORIGINS` in
  staging must not list the production frontend URL, and vice versa.
- **Machine auth (Vapi/n8n) is server-to-server.** Vapi and n8n send requests directly
  to the Railway API without going through the browser. They are not affected by
  `FRONTEND_CORS_ORIGINS` and do not require browser CORS headers (`X-Vapi-*` headers
  are not in `allow_headers` — this is correct).

---

## 10. Secret Generation Rules for Staging

1. **Generate independent high-entropy values for each secret.**

   Use a cryptographically secure source:
   ```
   openssl rand -hex 32
   ```
   Run once per secret. Each secret must be a unique value — do not reuse the same
   value for `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, and
   `INTERNAL_WEBHOOK_SECRET`.

2. **No local-dev placeholder values in staging.**

   The following values from `backend/.env.example` must never appear in Railway:
   - `local-dev-jwt-secret-key-change-in-production`
   - `local-vapi-secret-change-me`
   - `local-n8n-secret-change-me`
   - `local-internal-secret-change-me`
   - `praxismed_local_password`

3. **No production secrets in staging.**

   Production secrets do not exist yet. When they are created, they must be distinct
   values from staging. No staging secret may ever be promoted to production.

4. **No secrets in git, docs, screenshots, or logs.**

   - Railway dashboard stores secrets as encrypted env vars — copy the generated value
     directly into the Railway variable field; never paste it in a doc or Slack message.
   - Vercel dashboard stores env vars — `NEXT_PUBLIC_API_BASE_URL` is not a secret, but
     webhook secrets must never appear in Vercel vars (they belong in Railway only).
   - Application logs must not emit secret values. The backend does not log raw env var
     values. Confirm in Railway log stream after first deploy.

5. **Store in Railway and Vercel secret managers, not in files.**

   Staging secrets live in the Railway and Vercel dashboards. No `backend/.env` file
   is used in the Railway deployment.

6. **Rotate if exposed.**

   If any staging secret is accidentally logged, committed, or shared, rotate it
   immediately: generate a new value, update the Railway env var, update the
   corresponding external service (Vapi dashboard, n8n workflow), and redeploy.

---

## 11. Staging Env Setup Checklist

The following items must be completed before the staging smoke runbook (Module 97) can
be executed. No deployment is performed in this module — this checklist is the input
for Module 97.

### 11.1 Railway Setup

- [ ] Railway project created
- [ ] Railway PostgreSQL add-on provisioned and attached to the backend service
- [ ] `DATABASE_URL` auto-injected by Railway (verify in Railway service → Variables)
- [ ] `JWT_SECRET_KEY` set in Railway service variables (high-entropy; not local placeholder)
- [ ] `VAPI_WEBHOOK_SECRET` set in Railway service variables
- [ ] `N8N_WEBHOOK_SECRET` set in Railway service variables
- [ ] `INTERNAL_WEBHOOK_SECRET` set in Railway service variables
- [ ] `FRONTEND_CORS_ORIGINS` set to exact Vercel staging frontend origin
- [ ] `APP_ENV=staging` set (optional; informational)
- [ ] Backend start command set to run migrations then uvicorn with `$PORT`
- [ ] GitHub repository connected for auto-deploy on push

### 11.2 Vercel Setup

- [ ] Vercel project created and linked to the PraxisMed repository
- [ ] `NEXT_PUBLIC_API_BASE_URL` set to exact Railway backend URL (no trailing slash)
- [ ] Build command: `npm run build`
- [ ] Output directory: `.next`
- [ ] GitHub repository connected for auto-deploy on push

### 11.3 Staging Database

- [ ] Migrations applied cleanly to staging DB (non-zero exit blocks deploy)
- [ ] Staging fake clinic UUID decided (not `11111111-...`; not a real UUID)
- [ ] Staging staff user inserted with known fake credentials (no real email; fake name)
- [ ] No real patient data in staging DB
- [ ] `seed_local_data.py` NOT run against staging DB

### 11.4 Vapi

- [ ] Vapi test assistant created (or existing test assistant repurposed)
- [ ] Server URL updated to `https://staging-api.up.railway.app/vapi/tools/capture-appointment-request`
- [ ] Machine auth headers configured:
  - `X-Vapi-Service-Name: vapi`
  - `X-Vapi-Clinic-Id: <staging-fake-clinic-uuid>`
  - `X-Vapi-Scopes: vapi:tool` (singular)
- [ ] Webhook signing secret in Vapi dashboard matches `VAPI_WEBHOOK_SECRET` in Railway
- [ ] ngrok removed from Vapi assistant server URL

### 11.5 n8n (Optional for Staging)

- [ ] n8n staging workflow created (or marked NOT ENABLED if deferred)
- [ ] Webhook URL updated to `https://staging-api.up.railway.app/webhooks/n8n/calendar-sync`
- [ ] HMAC signing secret in n8n matches `N8N_WEBHOOK_SECRET` in Railway
- [ ] Test calendar configured; no production calendar writes

### 11.6 Final Checks

- [ ] No local-dev placeholder secrets in any Railway or Vercel variable
- [ ] No production secrets in any staging variable
- [ ] `FRONTEND_CORS_ORIGINS` is exact (no wildcard; no trailing slash)
- [ ] `NEXT_PUBLIC_API_BASE_URL` is exact (no trailing slash; HTTPS)
- [ ] Smoke runbook (Module 97) ready to execute

---

## 12. Validation Checklist

For each variable, the following shows how to validate it without printing the secret value.

| Variable | Safe Validation Method |
|---|---|
| `DATABASE_URL` | `GET /health/ready` returns `{"status": "ready", "checks": {"app": "ok"}}`; if DB pool failed, it returns `503` |
| `JWT_SECRET_KEY` | `POST /auth/login` with staging staff credentials returns `{"access_token": "..."}` (non-empty token); if key missing, returns HTTP 500 |
| `VAPI_WEBHOOK_SECRET` | Send a correctly signed fake Vapi webhook; returns HTTP 200. Send an unsigned or wrong-signature request; returns HTTP 401 |
| `N8N_WEBHOOK_SECRET` | Send a correctly signed fake n8n webhook; returns HTTP 200. Send wrong signature; returns HTTP 401 |
| `INTERNAL_WEBHOOK_SECRET` | Send a correctly signed internal webhook; returns HTTP 200 |
| `FRONTEND_CORS_ORIGINS` | Open browser devtools → Network → preflight `OPTIONS` request from Vercel frontend to Railway API; verify `Access-Control-Allow-Origin` matches exact Vercel URL |
| `NEXT_PUBLIC_API_BASE_URL` | Open Vercel frontend `/login`; verify login form submits to Railway API URL in Network tab (not `127.0.0.1`) |
| `DATABASE_URL` (migration) | Check Railway deploy logs for `run_migrations.py` exit code 0 before uvicorn starts |
| Staging clinic UUID (Vapi) | After a fake Vapi test call, check the created appointment row; `clinic_id` must match `<staging-fake-clinic-uuid>` |

### 12.1 End-to-End Validation Sequence

1. `GET https://staging-api.up.railway.app/health` → `{"status": "ok"}`
2. `GET https://staging-api.up.railway.app/health/ready` → `{"status": "ready"}`
3. Open `https://staging-app.vercel.app/login` in browser → login form visible
4. Login with staging staff credentials → redirected to `/dashboard`; token in `sessionStorage`
5. Dashboard shows empty appointment list (expected before any Vapi calls)
6. Trigger Vapi test call → verify row appears in dashboard with `status=new`
7. Click Confirm → row transitions to `status=confirmed`; button disappears
8. Trigger n8n test webhook (if enabled) → verify HTTP 200 in Railway logs
9. Logout → `sessionStorage` cleared; redirect to `/login`

---

## 13. Failure Matrix

| Symptom | Likely Bad Variable | Safe Check | Safe Fix |
|---|---|---|---|
| Frontend cannot reach API at all | `NEXT_PUBLIC_API_BASE_URL` wrong or not set | Browser Network tab: check where login POST is going | Update Vercel env var; rebuild frontend |
| CORS error in browser on login or API call | `FRONTEND_CORS_ORIGINS` wrong or not set | Browser devtools → Network → OPTIONS preflight response headers | Set `FRONTEND_CORS_ORIGINS` to exact Vercel origin in Railway; redeploy backend |
| Login returns HTTP 500 | `JWT_SECRET_KEY` missing or empty | Railway logs: look for `MissingJWTSecretError` | Set `JWT_SECRET_KEY` in Railway variables |
| Vapi tool call returns HTTP 401 | `VAPI_WEBHOOK_SECRET` mismatch | Send test webhook with known-good signature; if HTTP 401, secret is wrong | Regenerate secret; update Railway and Vapi dashboard simultaneously |
| Vapi tool call returns HTTP 403 | `X-Vapi-Scopes: vapi:tools` (plural) vs `vapi:tool` (singular) | Check `X-Vapi-Scopes` header in Vapi assistant config | Set scope to `vapi:tool` in Vapi dashboard |
| Vapi tool call returns HTTP 422 | Missing or malformed Vapi arguments | Check Railway logs for Pydantic validation error | Verify Vapi tool call argument schema matches `VapiAppointmentCaptureRequest` |
| Vapi tool call returns HTTP 500 | `adapt_vapi_tool_call_body` parse failure or DB error | Check Railway logs for stack trace | Fix argument shape or DB issue |
| n8n webhook returns HTTP 401 | `N8N_WEBHOOK_SECRET` mismatch or wrong signature header | Test with `sign_webhook_payload.py` | Update Railway and n8n workflow simultaneously |
| DB connection failure on startup | `DATABASE_URL` not injected or malformed | `GET /health/ready` returns 503; Railway logs show pool error | Verify Railway PostgreSQL add-on is attached; check DATABASE_URL in variables |
| Migration failure on deploy | `DATABASE_URL` wrong; missing migrations; DB not provisioned | Railway deploy logs: non-zero exit from `run_migrations.py` | Provision DB; fix `DATABASE_URL`; re-deploy |
| Dashboard shows empty data after login | Staging clinic UUID in JWT ≠ staging clinic UUID in DB | Decode JWT payload: check `clinic_id` field | Re-seed staging DB with correct clinic UUID; re-issue tokens |
| Wrong clinic/tenant in Vapi appointments | `X-Vapi-Clinic-Id` header ≠ staging fake clinic UUID in DB | Check appointment row `clinic_id` vs `X-Vapi-Clinic-Id` in Vapi config | Update `X-Vapi-Clinic-Id` in Vapi test assistant headers |
| Secret accidentally logged | Any secret printed in Railway logs | Check Railway log stream for known secret patterns | Rotate secret immediately; update Railway and external service |
| `sessionStorage` token visible in browser | Expected behavior (staging only; no PHI) | Not a staging blocker | Remains acceptable for fake-data staging; production PHI requires httpOnly cookie (Module 98) |

---

## 14. Production Separation

### 14.1 Explicit Statements

- **Production values must be separate.** No staging env var value may be reused as a
  production env var. When production secrets are generated (in a future sprint), they
  will be independent high-entropy values distinct from staging.

- **Production PHI launch remains NO-GO.** Architecture Checkpoint 12 documented 12
  unresolved blockers. This module does not resolve any of them. Defining the staging
  env var matrix does not constitute production readiness.

- **This matrix is not production approval.** The staging environment is for fake-data
  validation only. Approving a staging smoke test result approves staging, not production.

- **httpOnly cookie auth hardening remains a future blocker.** The `sessionStorage` JWT
  is acceptable in staging (fake data only). It must be replaced before any real clinic
  staff access a production instance. Implementation plan is in Module 98; execution is
  Sprint 14.

- **Fabel 5 / UX sprint remains deferred.** The frontend UX investment is deferred until
  the staging deployment topology and env var matrix are confirmed. This module completes
  that prerequisite.

### 14.2 Future Production Env Vars

When production is ready, the following will differ from staging:

| Variable | Staging | Production (future placeholder) |
|---|---|---|
| `DATABASE_URL` | Railway staging PostgreSQL | Production managed PostgreSQL (separate service) |
| `JWT_SECRET_KEY` | Staging-specific high-entropy value | Production-specific high-entropy value |
| `VAPI_WEBHOOK_SECRET` | Staging-specific | Production-specific; matches production Vapi assistant |
| `N8N_WEBHOOK_SECRET` | Staging-specific | Production-specific; matches production n8n workflow |
| `INTERNAL_WEBHOOK_SECRET` | Staging-specific | Production-specific |
| `FRONTEND_CORS_ORIGINS` | `https://staging-app.vercel.app` | `https://app.praximed.example.com` (or equivalent) |
| `NEXT_PUBLIC_API_BASE_URL` | `https://staging-api.up.railway.app` | `https://api.praximed.example.com` (or equivalent) |

---

## 15. Recommended Next Step

**Sprint 13 / Module 97 — Staging Deployment Dry-Run Checklist**

Module 97 produces a step-by-step dry-run checklist for the Railway + Vercel deployment.
It covers:
- Railway project and service creation steps (no execution — checklist format)
- Railway PostgreSQL provisioning steps
- Environment variable injection steps (Railway dashboard and Vercel dashboard)
- Migration execution gate
- Vercel project creation and build configuration
- Vapi test assistant reconfiguration steps
- n8n staging workflow setup steps (or NOT ENABLED deferred note)
- Post-deploy smoke verification sequence

No deployment is executed in Module 97. No code changes. The checklist output is the
artifact used to execute the actual staging deployment in a future module.
