# Staging Environment Wiring Runbook — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 15 / Module 108
**Status:** Planning only — no deployment executed by Claude in this module

---

## 1. Purpose

This is a human-executable guide for wiring the PraxisMed fake-data staging environment
together: connecting Railway backend, Railway PostgreSQL, Vercel frontend, Vapi test
assistant, and n8n staging workflow into a fully functional staging system.

**What this runbook is:**
- The final wiring guide after all individual services have been created
- A checklist for confirming env vars, CORS, API endpoints, and integrations are
  connected correctly before running full smoke (Module 109)
- A failure triage reference for wiring-specific issues

**What this runbook is not:**
- A deployment executed by Claude — no Railway or Vercel API calls are made here
- A production launch plan — production PHI launch remains NO-GO
- A guide for creating the Railway backend service — that is Module 105
- A guide for provisioning Railway PostgreSQL — that is Module 106
- A guide for creating the Vercel frontend project — that is Module 107
- A full smoke execution guide — that is Module 109
- A document containing real secrets — all values are placeholders

Staging uses fake/non-PHI data only. No deployment is executed by Claude in this module.
No real patient data. No production secrets. No fabricated success.

---

## 2. Wiring Map

The following diagram describes the target wiring for PraxisMed fake-data staging.
All traffic flows are one-way (initiator → target):

```
Browser
  └─→ Vercel frontend (*.vercel.app)
        └─→ Railway backend API (*.up.railway.app)
              └─→ Railway PostgreSQL (private .railway.internal URL)

Vapi test assistant
  └─→ Railway backend /vapi/tools/capture-appointment-request

n8n staging workflow (if enabled)
  └─→ Railway backend /<n8n-endpoint>
```

**Component roles:**

| Component | Platform | URL Pattern | Connects To |
|---|---|---|---|
| Railway backend API | Railway | `https://<service>.up.railway.app` | Railway PostgreSQL (internal) |
| Railway PostgreSQL | Railway (managed add-on) | `.railway.internal` (private) | Railway backend only |
| Vercel frontend | Vercel | `https://<project>.vercel.app` | Railway backend API (HTTPS) |
| Vapi test assistant | Vapi dashboard | (outbound only) | Railway backend `/vapi/tools/capture-appointment-request` |
| n8n staging workflow | n8n (external) | (outbound only) | Railway backend `/` + n8n endpoint |

**Wiring dependencies (order matters):**
1. Railway PostgreSQL → injects `DATABASE_URL` into Railway backend
2. Railway backend URL → becomes `NEXT_PUBLIC_API_BASE_URL` in Vercel
3. Vercel frontend URL → becomes `FRONTEND_CORS_ORIGINS` on Railway backend
4. Railway backend URL → becomes tool server URL in Vapi test assistant
5. Railway backend URL → becomes staging endpoint in n8n staging workflow

---

## 3. Required External URLs

All URLs are HTTPS. No HTTP. No ngrok. No localhost.

| Component | URL Placeholder | Notes |
|---|---|---|
| Railway backend | `https://<railway-backend-staging-url>.up.railway.app` | Assigned by Railway; confirmed in Module 105 |
| Vercel frontend | `https://<vercel-project>.vercel.app` | Assigned by Vercel; confirmed in Module 107 |
| Vapi tool endpoint | `https://<railway-backend-staging-url>.up.railway.app/vapi/tools/capture-appointment-request` | Exact path required; Railway backend URL + fixed path |
| n8n staging endpoint | `https://<railway-backend-staging-url>.up.railway.app/<n8n-endpoint>` | n8n staging only; not production calendar |

---

## 4. Required Env Var Wiring

### 4.1 Railway Backend Variables

Set all of the following in Railway service → **Variables** panel.

| Variable | Value Placeholder | Secret? | Where Set | Set When | Validation Method |
|---|---|---|---|---|---|
| `DATABASE_URL` | Auto-injected by Railway PostgreSQL add-on | Yes | Railway (auto-injected) | After Module 106 PostgreSQL creation | `GET /health/ready` → 200; `db_smoke_test.py` passes |
| `JWT_SECRET_KEY` | `<staging-high-entropy-secret>` — `openssl rand -hex 32` | Yes | Railway Variables panel | Before first deploy (Module 105) | `POST /auth/login` with fake credentials → 200 |
| `VAPI_WEBHOOK_SECRET` | `<staging-high-entropy-secret>` — must match Vapi signing secret | Yes | Railway Variables panel | Before Vapi smoke (Module 109) | Vapi test call → `POST /vapi/tools/capture-appointment-request` → 200 |
| `N8N_WEBHOOK_SECRET` | `<staging-high-entropy-secret>` — must match n8n workflow signing | Yes | Railway Variables panel | Before n8n smoke (Module 109) | Signed n8n POST → 200 |
| `INTERNAL_WEBHOOK_SECRET` | `<staging-high-entropy-secret>` — PraxisMed internal only | Yes | Railway Variables panel | Before first deploy (Module 105) | Internal webhook call → 200 |
| `FRONTEND_CORS_ORIGINS` | Exact Vercel URL: `https://<vercel-project>.vercel.app` | No | Railway Variables panel | After Vercel URL is known (this module) | CORS preflight OPTIONS → 200/204 with correct `Access-Control-Allow-Origin` |
| `APP_ENV` | `staging` | No | Railway Variables panel | Optional | Informational only |

**FRONTEND_CORS_ORIGINS rules:**
- Value must be the exact Vercel HTTPS URL including scheme and domain
- No trailing slash: `https://praxismed-staging.vercel.app` not `https://praxismed-staging.vercel.app/`
- No wildcard: `*` is forbidden — the `_cors_origins()` function never returns `*`
- No ngrok URL: Railway URL is stable; ngrok is not used in staging
- No localhost: `http://localhost:3000` will not match Vercel origin in browser
- Railway backend must be redeployed after this variable is set

### 4.2 Vercel Frontend Variables

Set in Vercel project → **Settings → Environment Variables**.

| Variable | Value Placeholder | Secret? | Where Set | Set When | Validation Method |
|---|---|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `https://<railway-backend-staging-url>.up.railway.app` | No (browser-visible) | Vercel Environment Variables | Before first Vercel deploy (Module 107) | Browser DevTools → Network → API calls show correct host |

**NEXT_PUBLIC_API_BASE_URL rules:**
- Must be the Railway backend HTTPS URL
- No trailing slash
- Value is baked into the Next.js build bundle at build time
- Changing this value requires a full Vercel redeploy; the running deployment does not pick it up
- This is a public variable — it appears in the compiled browser JS; never put secrets here

### 4.3 Vapi Test Assistant Configuration

Set in the Vapi dashboard → test assistant → **Server URL** and **Headers**.

| Item | Value Placeholder | Notes |
|---|---|---|
| Server URL | `https://<railway-backend-staging-url>.up.railway.app/vapi/tools/capture-appointment-request` | Exact path; no trailing slash |
| `X-Vapi-Service-Name` header | `vapi` | Static value |
| `X-Vapi-Clinic-Id` header | `<staging-fake-clinic-uuid>` | Must match clinic UUID in Railway PostgreSQL staging DB |
| `X-Vapi-Scopes` header | `vapi:tool` | **Singular** — `vapi:tools` (plural) returns HTTP 403 |
| Webhook signing secret | Must match `VAPI_WEBHOOK_SECRET` in Railway | Same value in both places; HTTP 401 if they differ |
| Call type | Fake test calls only | No real phone numbers; no real patients |

### 4.4 n8n Staging Workflow Configuration

Set in the n8n workflow HTTP request node (if n8n is enabled for staging).

| Item | Value Placeholder | Notes |
|---|---|---|
| Staging API endpoint | `https://<railway-backend-staging-url>.up.railway.app/<n8n-endpoint>` | Staging workflow; not production calendar |
| HMAC signing secret | Must match `N8N_WEBHOOK_SECRET` in Railway | Signature headers: `X-N8N-Signature`, `X-N8n-Signature`, or `X-Signature` |
| Calendar events | Fake/test events only | No production calendar writes |
| n8n status | **Optional for Module 108–109 smoke** | Vapi smoke can pass without n8n; defer n8n if not yet configured |

---

## 5. Wiring Order

Follow this exact order. Steps are dependencies — skipping ahead causes failures.

| Step | Action | Prerequisite | Done When |
|---|---|---|---|
| 1 | Create Railway backend service | Railway account; GitHub access | `/health` returns 200 |
| 2 | Set `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET` on Railway | Step 1 complete | Variables visible in Railway Variables panel (names only) |
| 3 | Create Railway PostgreSQL add-on | Step 1 complete | PostgreSQL shows "Running" |
| 4 | Confirm `DATABASE_URL` auto-injected into Railway backend | Step 3 complete | `DATABASE_URL` visible in Railway Variables panel |
| 5 | Redeploy Railway backend | Step 4 complete | `/health/ready` returns 200 |
| 6 | Run migrations: `python backend/scripts/run_migrations.py` | Step 5 complete | Exit code 0; `alembic current` shows `0002_password_hash (head)` |
| 7 | Run `db_smoke_test.py` | Step 6 complete | 4 tables confirmed |
| 8 | Provision staging fake clinic and user via SQL | Step 6 complete | `SELECT` confirms rows exist |
| 9 | Create Vercel frontend project; root dir = `frontend` | Railway backend URL from Step 1 | Vercel project created |
| 10 | Set `NEXT_PUBLIC_API_BASE_URL` to Railway backend URL | Step 9 + Step 1 | Env var set in Vercel before first build |
| 11 | Trigger Vercel first deploy | Step 10 complete | Build succeeds; Vercel URL assigned |
| 12 | Set `FRONTEND_CORS_ORIGINS` to exact Vercel URL | Step 11 complete — Vercel URL now known | Variable set in Railway Variables panel |
| 13 | Redeploy/restart Railway backend | Step 12 complete | Railway backend picks up new `FRONTEND_CORS_ORIGINS` |
| 14 | Configure Vapi test assistant URL and headers | Steps 1 + 8 complete | Tool URL set; headers set; signing secret matches Railway |
| 15 | Configure n8n staging workflow (if enabled) | Step 1 complete | Endpoint URL and HMAC secret set |
| 16 | Run full staging smoke (Module 109) | Steps 1–14 complete | Smoke PASS evidence captured |

---

## 6. Validation Checks

After completing wiring, verify each component before proceeding to full smoke (Module 109).

| Check | Method | Expected Pass Signal |
|---|---|---|
| Railway backend `/health` | `curl https://<railway-url>/health` | `{"status": "ok", "service": "PraxisMed API"}` — HTTP 200 |
| Railway backend `/health/ready` | `curl https://<railway-url>/health/ready` | `{"status": "ready", "checks": {"app": "ok", "db": "ok"}}` — HTTP 200 |
| Migrations applied | `alembic current` via Railway "Run Command" | `0002_password_hash (head)` |
| DB tables | `python backend/scripts/db_smoke_test.py` via Railway "Run Command" | 4 tables confirmed: clinics, patients, consultation_sessions, audit_log |
| Vercel `/login` loads | Open Vercel URL in browser | Login page renders; no 404; no blank page |
| Browser API call / CORS preflight | Browser DevTools → Network → filter OPTIONS | OPTIONS to Railway backend → `Access-Control-Allow-Origin: https://<vercel-url>` — HTTP 200 or 204 |
| Fake login | Submit fake credentials on `/login` | JWT stored in sessionStorage; redirect to `/dashboard` |
| Protected dashboard | Navigate to `/dashboard` | Appointment list renders (may be empty for new staging DB) |
| Vapi fake call | Initiate test call from Vapi dashboard | Vapi sends POST to `/vapi/tools/capture-appointment-request`; response 200; row visible in dashboard |
| Vapi-created row in dashboard | Staff dashboard refresh | New appointment request appears; `status=new`; `action_required=True` |
| Staff Confirm / no auto-confirm | Check row status before and after Vapi call | Status remains `new` until staff manually confirms — no automatic status change |
| n8n fake sync (if enabled) | Trigger test event in n8n staging workflow | n8n POST to Railway backend → 200; no production calendar write |

---

## 7. Common Wiring Failures

| Symptom | Likely Cause | Safe Next Action |
|---|---|---|
| Frontend API calls go to `127.0.0.1:8000` | `NEXT_PUBLIC_API_BASE_URL` not set or Vercel deploy used old build | Set `NEXT_PUBLIC_API_BASE_URL` in Vercel → redeploy frontend |
| CORS error in browser: origin mismatch | `FRONTEND_CORS_ORIGINS` value does not match exact Vercel origin (trailing slash; wrong subdomain; HTTP vs HTTPS) | Confirm exact Vercel URL; update `FRONTEND_CORS_ORIGINS` on Railway → redeploy Railway backend |
| `GET /health/ready` returns 503 after Railway PostgreSQL created | `DATABASE_URL` not yet injected; Railway backend not redeployed after add-on link | Verify auto-injection in Railway Variables panel → trigger redeploy |
| Vapi returns HTTP 403 | `X-Vapi-Scopes` header is `vapi:tools` (plural) | Set header to `vapi:tool` (singular) in Vapi test assistant config |
| Vapi returns HTTP 401 | `VAPI_WEBHOOK_SECRET` in Railway does not match signing secret in Vapi dashboard | Re-generate and set matching value in both places |
| Vapi call succeeds but URL reachable is wrong | Vapi test assistant server URL points to wrong Railway backend URL | Update Vapi server URL to current Railway backend HTTPS URL |
| n8n POST returns HTTP 401 | `N8N_WEBHOOK_SECRET` in Railway does not match n8n workflow HMAC secret | Re-generate and set matching value in both places |
| Login fails with "clinic not found" or 404 | Staging fake clinic not provisioned; `X-Vapi-Clinic-Id` does not match DB clinic UUID | Run staging fake clinic SQL insert; confirm UUID matches |
| `/health` returns 200 but `/health/ready` returns 503 before PostgreSQL | `DATABASE_URL` not yet set | Expected before Module 106; proceed to Module 106 |
| Migration fails | `DATABASE_URL` not visible; Railway PostgreSQL not "Running" yet; wrong working directory | Verify PostgreSQL status; confirm `DATABASE_URL` in Variables panel; run command from repo root |
| Railway backend not updated after `FRONTEND_CORS_ORIGINS` set | Railway backend not redeployed after env var change | Trigger manual redeploy in Railway dashboard or push a commit |
| Vercel build uses old `NEXT_PUBLIC_API_BASE_URL` | Env var changed after build; running deployment uses baked value | Trigger Vercel redeploy to pick up new env var value |

---

## 8. Safety Rules

The following safety rules apply throughout staging wiring:

| Rule | Detail |
|---|---|
| No real patients | No real patient names, phone numbers, dates of birth, or medical records in any staging DB row, log, or Vapi test call |
| No production secrets | All secrets are staging-only values generated with `openssl rand -hex 32`; no value is shared with production |
| No production DB | `DATABASE_URL` in Railway points to Railway-provisioned staging PostgreSQL only; never a production connection string |
| No local-dev password | `local-dev-password` hash from `seed_local_data.py` must not appear in staging; staging fake user uses a staging-only bcrypt hash |
| No ngrok in staging | Railway URL is stable; ngrok is not needed and creates an unauditable tunnel |
| No wildcard CORS | `FRONTEND_CORS_ORIGINS` must be the exact Vercel HTTPS URL; `*` is forbidden |
| Vapi test assistant only | Use a Vapi test assistant, not the production Vapi assistant |
| Staff Confirm required | Appointment requests must remain in `status=new` with `action_required=True` until staff manually confirms; any automatic status change is a stop condition |
| No auto-confirmation | The backend hardcodes `status='new'` and `action_required=True` on every appointment request creation; stop if any auto-confirmation occurs |
| sessionStorage JWT is fake-data-only | The frontend stores JWT in `sessionStorage` (XSS-accessible); this is acceptable for fake-data staging but must be replaced with httpOnly cookie auth before production PHI access |

---

## 9. Evidence to Capture

Record the following after wiring is complete. Record only sanitized information — no
secret values, no `DATABASE_URL` connection strings, no JWT values.

| Component | Evidence Item | Record | Notes |
|---|---|---|---|
| Railway backend | Service URL | `https://<service>.up.railway.app` | Public HTTPS URL only |
| Railway backend | Env var names confirmed set | `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`, `FRONTEND_CORS_ORIGINS`, `APP_ENV` | Names only — never values |
| Railway backend | `/health` response | `{"status": "ok", ...}` — 200 | Curl output |
| Railway backend | `/health/ready` response | `{"status": "ready", ...}` — 200 | After DB wiring and migrations |
| Railway backend | `FRONTEND_CORS_ORIGINS` value confirmed (no wildcard) | Exact Vercel URL | Confirm no `*`; no trailing slash |
| Railway backend | Timestamp of `FRONTEND_CORS_ORIGINS` set | ISO 8601 | When variable was set |
| Railway PostgreSQL | `DATABASE_URL` auto-injected confirmed | Yes / No | Do not record value |
| Railway PostgreSQL | Migration exit status | `0` | `run_migrations.py` exit code |
| Railway PostgreSQL | `alembic current` output | `0002_password_hash (head)` | Run via Railway "Run Command" |
| Railway PostgreSQL | `db_smoke_test.py` result | 4 tables confirmed | Run via Railway "Run Command" |
| Railway PostgreSQL | Staging fake clinic UUID | `<staging-uuid>` | Not a secret; stable identifier |
| Railway PostgreSQL | Staging fake user email | `doctor.staging@praximed.test` | Confirm row exists |
| Vercel frontend | Project URL | `https://<project>.vercel.app` | Public HTTPS URL |
| Vercel frontend | `NEXT_PUBLIC_API_BASE_URL` name confirmed | `NEXT_PUBLIC_API_BASE_URL` | Name only — value is Railway backend URL |
| Vercel frontend | Build status | Success | From Vercel dashboard |
| Vercel frontend | Commit SHA deployed | Full SHA | From Vercel deployment detail |
| Vercel frontend | `/login` loads in browser | Yes / No | Timestamp |
| CORS wiring | OPTIONS preflight to Railway backend | Status 200 or 204; `Access-Control-Allow-Origin` matches Vercel URL | Browser DevTools screenshot description |
| CORS wiring | No wildcard in `Access-Control-Allow-Origin` | Confirmed | `*` must not appear |
| Vapi | Test assistant server URL | `https://<railway-url>/vapi/tools/capture-appointment-request` | URL only; not signing secret |
| Vapi | Headers set: `X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes` | Names confirmed | No secret values |
| Vapi | `X-Vapi-Scopes` value confirmed | `vapi:tool` (singular) | Must not be `vapi:tools` |
| n8n | Staging endpoint URL set | Yes / No | If n8n enabled |
| n8n | Staging HMAC secret set | Yes / No (name only) | If n8n enabled |

**Do not record:**
- Secret values (`JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, etc.)
- `DATABASE_URL` connection string
- Passwords or bcrypt hashes
- Real patient data of any kind

---

## 10. Stop Rules

Stop staging wiring immediately if any of the following are observed:

| Stop Rule | Trigger |
|---|---|
| Backend secrets appear in Vercel env vars | `DATABASE_URL`, `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, or `INTERNAL_WEBHOOK_SECRET` set in Vercel — stop and remove immediately |
| Wildcard CORS | `FRONTEND_CORS_ORIGINS` is `*` or contains `*` — never acceptable |
| Production secrets requested or used | Any prompt for production values; staging and production must be fully isolated |
| Real patient data in any component | Any real name, phone number, DOB, or medical record in staging DB, Vapi test call, or log |
| Local-dev password used in staging | `local-dev-password` or local UUIDs (`11111111-...`) appear in staging — stop and re-provision staging fake user |
| ngrok URL used for any staging component | Ngrok creates an unauditable tunnel; Railway URL is stable |
| Auto-confirmation observed | If an appointment request is automatically set to `status=confirmed` — stop and investigate backend code |
| Secrets appear in any log or evidence doc | Any `openssl`-generated value, JWT token, or `DATABASE_URL` password visible in recorded output |

---

## 11. Result States

| State | Meaning |
|---|---|
| **PASS** | All wiring validated: CORS preflight passes; fake login succeeds; Vapi test call creates row; no real data or secrets |
| **BLOCKED/PENDING** | One or more external services not yet created or wiring evidence not yet provided; this is an accurate status, not a failure |
| **FAIL** | Wiring attempted but validation failed; specific failure documented |

**Current result: BLOCKED/PENDING**

No user-provided evidence of wiring exists. The runbook is ready for manual execution.
Proceed to `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` to record real evidence.

---

## 12. What This Runbook Does Not Cover

| Topic | Covered In |
|---|---|
| Railway backend service creation (Procfile, Nixpacks, first deploy) | Module 105 |
| Railway PostgreSQL provisioning and migration execution | Module 106 |
| Vercel frontend project creation and first deploy | Module 107 |
| Full staging smoke execution (Vapi full call, dashboard, staff Confirm) | Module 109 |
| Auth/session hardening (httpOnly cookie, SameSite=None) | Post-staging-smoke; Sprint 15 |
| n8n production calendar sync | NOT for staging; n8n deferred |
| Production launch | Production PHI launch remains NO-GO |
| Fabel 5 / frontend UX sprint | Deferred |

---

## 13. Recommended Next Step — Module 109

**Sprint 15 / Module 109 — Staging Smoke Execution Evidence**

After completing this wiring runbook and capturing evidence:

1. Open the Vercel frontend URL in a browser
2. Confirm `/login` renders without errors
3. Submit fake credentials; confirm JWT stored in sessionStorage; confirm redirect to `/dashboard`
4. Initiate a Vapi test call; confirm row appears in dashboard with `status=new`
5. Staff Confirm the appointment; confirm no auto-confirmation occurred
6. Confirm CORS preflight passes for all API calls
7. Capture sanitized evidence for each step
8. Update `docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md` from BLOCKED/PENDING to PASS
