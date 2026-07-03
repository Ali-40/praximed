# Staging Deployment Topology Plan — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 13 / Module 95
**Status:** Planning only — no deployment executed in this module; no runtime code changed

---

## 1. Purpose

This document selects and defines the staging deployment topology for PraxisMed.
Staging uses fake/non-PHI data only. No production launch. No real clinic staff or
patients involved.

**What this document is:**
- A comparison of realistic staging platform options
- A decision on the recommended staging topology
- A definition of staging domains, env var placeholders, DB strategy, Vapi/n8n
  configuration, and CORS plan for the chosen topology
- The basis for Module 96 (Staging Environment Variable Matrix)

**What this document is not:**
- A deployment execution guide (no commands are run against real infrastructure)
- A production launch plan
- An auth/session hardening plan (that is Module 98)
- A Fabel 5 / UX sprint plan

---

## 2. Current Decision Baseline

From Architecture Checkpoint 12:

| Decision | Status |
|---|---|
| Production PHI launch | **NO-GO** — 12 unresolved blockers; `sessionStorage` JWT is PHI-incompatible |
| Staging fake-data deployment prep | **GO** — integration loop proven; env contract and smoke runbook ready |
| Auth/session hardening (httpOnly cookie) | Plan in Module 98; implement Sprint 14 |
| Fabel 5 / frontend UX sprint | Deferred until staging topology confirmed |
| Appointment workflow expansion | Deferred |

The PraxisMed stack at this point:
- **Backend:** Python / FastAPI / asyncpg / uvicorn — listens on port 8000
- **Frontend:** Next.js 14.2.3 (`npm run build` + `npm start`)
- **Database:** PostgreSQL 16 (local Docker); asyncpg connection pool; Alembic migrations
- **Auth:** JWT Bearer (`sessionStorage` — acceptable for fake-data staging; not PHI-safe for production)
- **Vapi:** server-to-machine via stable HTTPS URL + machine auth headers
- **n8n:** server-to-machine via HMAC-signed webhook

---

## 3. Deployment Target Options Compared

### Option A — Railway (Backend + PostgreSQL) + Vercel (Frontend)

**Railway** is a PaaS that supports Python/FastAPI services and includes managed
PostgreSQL as a first-class add-on. **Vercel** is the canonical deployment target for
Next.js.

| Dimension | Assessment |
|---|---|
| Backend fit | Excellent — Railway detects Python; supports `uvicorn`; env vars set via dashboard or CLI |
| Frontend fit | Vercel is the native deployment platform for Next.js; zero-config build and deploy |
| PostgreSQL fit | Railway PostgreSQL: managed, provisioned in the same project, connection string injected as `DATABASE_URL` automatically |
| Secrets management | Platform env vars set via Railway dashboard and Vercel dashboard; no secrets manager required at staging scale |
| HTTPS/domain | Railway auto-provisions `*.up.railway.app` subdomains with TLS; custom domains supported; Vercel auto-provisions `*.vercel.app` with TLS |
| Logs/observability | Railway provides a real-time log stream in the dashboard; Vercel provides function logs |
| Migration workflow | `python backend/scripts/run_migrations.py` can run as a one-shot service or Railway start command |
| Vapi stable URL | Railway public URL (`https://<service>.up.railway.app`) is stable and serves as the Vapi tool URL |
| n8n compatibility | n8n can POST to the Railway stable URL with HMAC headers — server-to-server, no CORS |
| Operational complexity | Low — Railway deploys from GitHub on push; Vercel deploys from GitHub on push |
| Cost/credit risk | Railway free tier limited (sleep after inactivity); Starter plan ~$5/mo; Vercel Hobby tier is free |
| Vendor lock-in | Low — standard Python service; no platform-specific code; `DATABASE_URL` abstraction preserves portability |
| **Recommendation score** | **★★★★★ — Recommended** |

### Option B — Render (Backend + PostgreSQL) + Vercel (Frontend)

**Render** is another PaaS supporting Python web services and managed PostgreSQL.
Frontend on Vercel.

| Dimension | Assessment |
|---|---|
| Backend fit | Good — Render supports Python/uvicorn; build and start commands configurable |
| Frontend fit | Vercel (same as Option A) |
| PostgreSQL fit | Render managed PostgreSQL; free tier has 90-day expiry; paid tiers persist |
| Secrets management | Environment variables set via Render dashboard; secret files supported |
| HTTPS/domain | Render auto-provisions `*.onrender.com` with TLS; custom domains supported |
| Logs/observability | Render provides a log tail in dashboard; slightly less real-time than Railway |
| Migration workflow | Run as a one-off job or `pre-deploy` command in `render.yaml` |
| Vapi stable URL | `https://<service>.onrender.com` is stable |
| n8n compatibility | Same as Option A |
| Operational complexity | Low — GitHub-connected deploys; similar to Railway |
| Cost/credit risk | Free tier services spin down after 15 minutes of inactivity (cold start); Starter $7/mo avoids this |
| Vendor lock-in | Low |
| **Recommendation score** | **★★★★☆ — Good alternative** |

### Option C — Fly.io (Backend) + Neon or Supabase (PostgreSQL) + Vercel (Frontend)

**Fly.io** deploys Docker containers globally. **Neon** or **Supabase** provide
serverless/managed PostgreSQL with free tiers. Frontend on Vercel.

| Dimension | Assessment |
|---|---|
| Backend fit | Good — Docker-based; full control over runtime; more operational overhead |
| Frontend fit | Vercel (same as Option A) |
| PostgreSQL fit | Neon: serverless PostgreSQL with branching; Supabase: PostgreSQL + extras |
| Secrets management | Fly secrets CLI (`fly secrets set`); Neon/Supabase connection string injected manually |
| HTTPS/domain | Fly auto-provisions `*.fly.dev` with TLS; custom domains supported |
| Logs/observability | `fly logs` in terminal; less visual than Railway |
| Migration workflow | Can run as a Fly release command; slightly more configuration |
| Vapi stable URL | `https://<app>.fly.dev` is stable |
| n8n compatibility | Same as other options |
| Operational complexity | **Medium** — requires Dockerfile or Fly configuration file; more steps than Railway/Render |
| Cost/credit risk | Fly free tier generous; Neon free tier limited compute-hours; Supabase free tier includes 500MB PostgreSQL |
| Vendor lock-in | Low (Docker-based) |
| **Recommendation score** | **★★★☆☆ — Viable but more complex for staging** |

### Option D — Single VPS / Container Host (e.g., Hetzner / DigitalOcean) + Managed PostgreSQL

Self-hosted VPS running Docker Compose for backend and frontend; managed PostgreSQL
from Neon, Supabase, or the same provider.

| Dimension | Assessment |
|---|---|
| Backend fit | Full control; familiar Docker Compose pattern |
| Frontend fit | Requires Nginx or separate Next.js process management |
| PostgreSQL fit | External managed DB; or VPS PostgreSQL (not recommended for staging isolation) |
| Secrets management | `.env` file on host or Docker secrets; no secret manager |
| HTTPS/domain | Manual Nginx/Caddy + Let's Encrypt or Cloudflare |
| Logs/observability | Manual setup required (journald, logrotate) |
| Migration workflow | SSH to host + run migration script |
| Operational complexity | **High** — manual server setup, TLS renewal, process management |
| Cost/credit risk | Hetzner CX11 ~€4/mo; DigitalOcean Droplet $6/mo; lowest cost but highest ops overhead |
| **Recommendation score** | **★★☆☆☆ — Avoid for staging; too much ops overhead** |

### Option E — All-in-One Platform (e.g., Heroku, Coolify, Porter)

Heroku supports Python and Postgres but has limited free tier. Coolify is a self-hosted
PaaS. Porter orchestrates Kubernetes on existing cloud providers.

| Dimension | Assessment |
|---|---|
| Backend fit | Heroku: excellent but no free tier; Coolify: self-hosted (same ops overhead as D) |
| Frontend fit | Heroku supports Node.js; Vercel remains superior for Next.js |
| Operational complexity | Variable; Heroku simple but paid; Coolify complex |
| **Recommendation score** | **★★☆☆☆ — Not recommended for this project at this stage** |

---

## 4. Recommended Staging Topology

**Chosen topology: Railway (Backend + PostgreSQL) + Vercel (Frontend)**

### Why Railway + Vercel

1. **Zero infrastructure management** — Railway auto-provisions TLS, subdomains, and log
   streams. Vercel is the canonical Next.js platform with zero-config builds.

2. **Stable HTTPS URLs immediately** — `https://<service>.up.railway.app` is available
   without custom domain setup. This is exactly what the Vapi test assistant needs as its
   tool server URL (replacing ngrok).

3. **DATABASE_URL injected automatically** — Railway PostgreSQL add-on populates
   `DATABASE_URL` in the service environment. No manual connection string assembly.

4. **Secrets via dashboard UI** — all other env vars (`JWT_SECRET_KEY`,
   `VAPI_WEBHOOK_SECRET`, etc.) are set via the Railway and Vercel dashboards — no
   secrets manager required at staging scale.

5. **Low ops overhead** — GitHub-connected; deploy on push; no Dockerfile required for
   FastAPI. Both platforms have free or low-cost tiers adequate for fake-data staging.

6. **Portability preserved** — no Railway-specific code in the backend. `DATABASE_URL`
   abstraction means the same backend image/code deploys to any PostgreSQL-backed
   platform. Switching to production infrastructure later requires only env var changes.

7. **sessionStorage JWT acceptable for staging** — the staging environment uses fake
   data and no real clinic staff. The PHI-incompatible `sessionStorage` JWT is not a
   blocker at this stage. Production PHI launch remains blocked until Module 98+
   implements httpOnly cookie auth.

---

## 5. Staging Architecture — Text Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  STAGING ENVIRONMENT (fake data only — no PHI)                  │
│                                                                 │
│  Vapi test assistant                                            │
│    │  X-Vapi-Service-Name: vapi                                 │
│    │  X-Vapi-Clinic-Id: <staging-fake-clinic-uuid>             │
│    │  X-Vapi-Scopes: vapi:tool                                  │
│    ▼                                                            │
│  staging API (Railway)                                          │
│    https://staging-api.up.railway.app                           │
│    POST /vapi/tools/capture-appointment-request                 │
│    │  adapt_vapi_tool_call_body → validate → insert             │
│    ▼                                                            │
│  staging PostgreSQL (Railway)                                   │
│    appointment_requests (status=new, source=vapi)              │
│                                                                 │
│  Browser (staff)                                                │
│    │  GET https://staging-app.vercel.app/dashboard              │
│    │  Authorization: Bearer <JWT>                               │
│    │  CORS: Access-Control-Allow-Origin: https://staging-app.vercel.app
│    ▼                                                            │
│  staging API                                                    │
│    GET /appointment-requests?clinic_id=<staging-fake-clinic>   │
│    │                                                            │
│    ├── Returns new Vapi row                                     │
│    ▼                                                            │
│  staging frontend (Vercel)                                      │
│    Confirm button clicked by staff                              │
│    │  PATCH /appointment-requests/{id}/status                   │
│    │  Bearer JWT required                                       │
│    ▼                                                            │
│  staging API → staging PostgreSQL (status=confirmed)           │
│                                                                 │
│  n8n staging workflow                                           │
│    POST https://staging-api.up.railway.app/webhooks/n8n/calendar-sync
│    X-N8N-Signature: sha256=<hmac>                              │
│    Server-to-server — no browser CORS                          │
│                                                                 │
│  Machine auth path (Vapi/n8n)                                   │
│    get_machine_auth_context → clinic_id from X-Vapi-Clinic-Id  │
│    → no browser CORS involved                                   │
│                                                                 │
│  Human JWT path (staff browser)                                 │
│    POST /auth/login → { access_token }                          │
│    → sessionStorage (staging acceptable; not PHI-safe)          │
│    → Authorization: Bearer <token>                              │
│    → get_current_user → PHI routes                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Environment Mapping

All values are staging placeholders. Real staging secrets are set in Railway and Vercel
dashboards at execution time — never in code or docs.

| Variable | Component | Staging Placeholder Format | Secret? | Storage Location |
|---|---|---|---|---|
| `DATABASE_URL` | Backend (Railway) | Auto-injected by Railway PostgreSQL add-on | Yes | Railway dashboard (auto) |
| `JWT_SECRET_KEY` | Backend (Railway) | `<32-byte-hex-generated-per-env>` | Yes | Railway environment variable |
| `VAPI_WEBHOOK_SECRET` | Backend (Railway) | `<32-byte-hex-generated-per-env>` | Yes | Railway environment variable |
| `N8N_WEBHOOK_SECRET` | Backend (Railway) | `<32-byte-hex-generated-per-env>` | Yes | Railway environment variable |
| `INTERNAL_WEBHOOK_SECRET` | Backend (Railway) | `<32-byte-hex-generated-per-env>` | Yes | Railway environment variable |
| `FRONTEND_CORS_ORIGINS` | Backend (Railway) | `https://staging-app.vercel.app` (exact) | No | Railway environment variable |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend (Vercel) | `https://staging-api.up.railway.app` | No | Vercel environment variable |
| `POSTGRES_DB` | Railway DB provisioning | _(auto-set by Railway; not needed separately)_ | No | Railway auto-managed |
| `POSTGRES_USER` | Railway DB provisioning | _(auto-set by Railway; not needed separately)_ | No | Railway auto-managed |
| `POSTGRES_PASSWORD` | Railway DB provisioning | _(auto-set by Railway; not needed separately)_ | Yes | Railway auto-managed |

**Rules:**
- Every staging secret is a unique high-entropy value — not the local placeholder (e.g., not `local-dev-jwt-secret-key-change-in-production`)
- No staging secret is reused in production
- No staging secret appears in this document, in git, or in logs

---

## 7. Domain / CORS Plan for Staging

| Item | Value |
|---|---|
| Staging backend URL | `https://staging-api.up.railway.app` (Railway auto-provisioned) |
| Staging frontend URL | `https://staging-app.vercel.app` (Vercel auto-provisioned) |
| `FRONTEND_CORS_ORIGINS` | `https://staging-app.vercel.app` (exact; no wildcard; no localhost) |
| `NEXT_PUBLIC_API_BASE_URL` | `https://staging-api.up.railway.app` |

**CORS rules (unchanged from production plan):**
- No wildcard `*` origin — the `_cors_origins()` function never returns a wildcard
- No ngrok URL in `FRONTEND_CORS_ORIGINS`
- No localhost in staging CORS config
- Allowed methods: `GET`, `POST`, `PATCH`, `DELETE`, `OPTIONS`, `PUT`
- Allowed headers: `Content-Type`, `Authorization`
- Machine auth headers (`X-Vapi-*`, `X-N8N-*`, `X-Vapi-Signature`) are server-to-server
  and do not need to appear in browser `allow_headers`

**Custom domain (optional for staging):** If a custom domain is registered, the staging
pattern would be `https://staging-api.praximed.example.com` and
`https://staging-app.praximed.example.com`. Without a custom domain, the `*.up.railway.app`
and `*.vercel.app` auto-provisioned URLs are sufficient for staging.

---

## 8. Database Strategy

### 8.1 Staging Database

| Property | Value |
|---|---|
| Type | Railway managed PostgreSQL (same Railway project as the backend service) |
| Isolation | Completely separate from local Docker DB and any future production DB |
| Data type | Fake/synthetic only — no real patient records; no real clinic data |
| `DATABASE_URL` | Auto-injected by Railway into the backend service environment |
| Migration strategy | Run `python backend/scripts/run_migrations.py` as the backend start command or a one-shot Railway service before first deploy |

### 8.2 Migration Gate

Migrations must complete before any backend traffic is routed. On Railway, this can
be enforced by running migrations as part of the service `startCommand`:

```
python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Migration failure (non-zero exit) prevents the service from starting. This is the safe
default behavior.

### 8.3 Seed Strategy

**Do not run `backend/scripts/seed_local_data.py` in staging.** The seed script uses
local deterministic UUIDs (`11111111-...`) intended for local dev only.

Staging tenant provisioning strategy:
1. A staging-specific fake clinic is created directly via a one-time SQL insert or
   a staging seed script (to be created in Module 96 or later)
2. The staging clinic UUID is a separate UUID not used in local dev or production
3. All staging data (clinic, staff user, test appointments) uses this staging UUID
4. No real names, real email addresses, or real phone numbers are used

### 8.4 Backup Expectations

Staging DB does not require production-grade backups. Railway PostgreSQL provides basic
snapshotting. Data loss in staging is acceptable — re-run migrations and re-seed.

---

## 9. Vapi Staging Strategy

| Item | Value |
|---|---|
| Vapi assistant | Staging Vapi test assistant (separate from local test assistant and any future production assistant) |
| Server URL | `https://staging-api.up.railway.app/vapi/tools/capture-appointment-request` |
| `X-Vapi-Service-Name` | `vapi` |
| `X-Vapi-Clinic-Id` | Staging fake clinic UUID (not `11111111-...` local seed UUID; not a production UUID) |
| `X-Vapi-Scopes` | `vapi:tool` (singular — `vapi:tools` plural is rejected with HTTP 403) |
| Webhook secret | `VAPI_WEBHOOK_SECRET` set in Railway; matches Vapi staging assistant signing secret |
| Data | Fake patient names and phone numbers only; no real calls from real patients |
| ngrok | Not used in staging — the Railway URL is stable and does not require a tunnel |

Expected behavior after a test call:
- HTTP 200 from staging backend
- Appointment row created: `status=new`, `source=vapi`, `action_required=True`
- Row visible in staging dashboard after staff login
- Staff Confirm transitions status to `confirmed`
- No auto-confirmation
- No calendar booking

---

## 10. n8n Staging Strategy

| Item | Value |
|---|---|
| n8n instance | Staging n8n workflow (isolated from local and production) |
| Webhook URL | `https://staging-api.up.railway.app/webhooks/n8n/calendar-sync` |
| `X-Service-Name` | `n8n` |
| `X-Service-Clinic-Id` | Staging fake clinic UUID |
| `X-Service-Scopes` | `calendar:sync` |
| `N8N_WEBHOOK_SECRET` | Staging-specific value set in Railway; matches n8n staging workflow secret |
| Calendar | Test/fake calendar only — no production calendar writes |
| CORS | n8n is server-to-server; no browser CORS dependency |

If n8n is not configured for staging, this check is marked "NOT ENABLED" in the smoke
runbook and deferred to a later module.

---

## 11. CI/CD and Migration Strategy (Planning Only)

No CI/CD is built in this module. The following is the target approach for Sprint 13
or a dedicated DevOps module:

| Step | Approach |
|---|---|
| **Branch strategy** | `main` → production; `staging` branch → staging Railway/Vercel deploy |
| **Test gate** | `pytest backend/tests/` must pass before deploy; Railway build step or GitHub Actions |
| **Frontend build gate** | `npm run build` must succeed before Vercel deploy |
| **Migration gate** | `run_migrations.py` runs before uvicorn starts; non-zero exit blocks service start |
| **Smoke gate** | After deploy, run smoke runbook checklist manually (Section 15 of the runbook) |
| **Rollback** | Railway: re-deploy previous deployment via dashboard; Vercel: re-deploy previous build |
| **No auto-promotion** | Staging deploy never auto-promotes to production; production requires a separate deliberate deploy |

---

## 12. Security Constraints for Staging

| Constraint | Enforcement |
|---|---|
| Fake/non-PHI data only | No real clinic IDs, patient names, phone numbers, or email addresses |
| Staging secrets isolated | Each secret is a unique value distinct from local-dev placeholders and production secrets |
| No real clinic traffic | No real Vapi production assistant; no real patients calling the staging number |
| No real patients | All appointment intake tests use fake names and synthetic scenarios |
| No production assistant | Staging Vapi assistant is separate; points only to staging API URL |
| No production DB | Staging DB is isolated in Railway; separate from any future production database |
| No long-lived local secrets | Staging secrets live in Railway and Vercel dashboards; not in shell exports or `.env` files |
| No secrets in logs/docs | All Railway log output must be checked post-deploy; no token or DB password values |
| `sessionStorage` JWT | Acceptable for fake-data staging (no PHI); not acceptable for production PHI launch |
| Tenant isolation | `clinic_id` from machine auth header; patient payload cannot select tenant |
| Staff Confirm boundary | No auto-confirmation at any layer; human Confirm click required |

---

## 13. Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| `sessionStorage` JWT in staging | **Low** (no PHI in staging) | Acceptable for fake-data staging only; production PHI launch remains blocked; documented in Checkpoint 12 |
| Railway env var misconfiguration | **Medium** | Verify via `for var in ...` presence check from smoke runbook before routing traffic |
| CORS wrong origin in `FRONTEND_CORS_ORIGINS` | **High** | Set to exact Vercel URL; verify in browser devtools Network tab on first login |
| Vapi URL misconfigured (ngrok or wrong URL) | **High** | Verify Vapi staging assistant server URL is the Railway stable URL before testing |
| DB migration failure on first deploy | **Medium** | Migrations run before uvicorn; non-zero exit blocks service; inspect Railway logs |
| Accidental real data | **High (PHI risk)** | Use only fake patient names and synthetic clinic UUIDs; no real calls; no real Vapi production assistant |
| Staging/production secret mixup | **High** | Staging secrets are unique values generated per-environment; production secrets do not exist yet |
| ngrok accidentally used in staging | **Medium** | Railway URL replaces ngrok entirely; verify no ngrok URL in any staging env var |
| Missing rollback | **Medium** | Railway and Vercel both support one-click re-deploy to previous build; verify before first deploy |
| Frontend build failure on Vercel | **Medium** | `npm run build` must pass locally before pushing; `NEXT_PUBLIC_API_BASE_URL` must be set in Vercel |

---

## 14. Decision

**Chosen staging topology: Railway (Backend + PostgreSQL) + Vercel (Frontend)**

- Staging prep can proceed to Module 96 (Staging Environment Variable Matrix)
- No deployment execution in this module
- Production PHI launch remains NO-GO
- Staging uses fake/non-PHI data only
- `sessionStorage` JWT is acceptable for staging; not acceptable for production PHI

Staging domain placeholders (finalized in Module 96):
- Staging API: `https://staging-api.up.railway.app` (or custom subdomain)
- Staging Frontend: `https://staging-app.vercel.app` (or custom subdomain)

---

## 15. Non-Goals

- No deployment execution in this module
- No production launch
- No auth/session refactor (httpOnly cookie is Module 98)
- No Fabel 5 / frontend UX sprint
- No appointment workflow expansion (Reject, Assign, Archive)
- No real patient data
- No production secrets or production domains
