# Auth/Session Hardening Implementation Plan — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 13 / Module 98
**Status:** Planning only — no backend code changed; no frontend code changed; no auth
behavior modified in this module

---

## 1. Current Authentication Architecture

### 1.1 Login Flow (As-Built)

```
Browser (staff)
  │
  ├─ POST /auth/login  { email, password, clinic_id }
  │       ↓
  │  backend/app/api/routes/auth.py
  │    get_user_by_email() → verify_password() → create_access_token()
  │    Returns JSON: { access_token, token_type, expires_in_seconds, user }
  │       ↓
  ├─ frontend/app/login/page.tsx
  │    result = await loginUser(email, password, clinicId)
  │    storeToken(result.access_token)           ← sessionStorage
  │    router.push('/dashboard')
  │
  └─ frontend/lib/auth.ts
       sessionStorage.setItem('praximed_access_token', token)
```

### 1.2 Authenticated Request Flow (As-Built)

```
frontend/app/dashboard/page.tsx
  │
  ├─ getToken()      → sessionStorage.getItem('praximed_access_token')
  ├─ getClinicId()   → decode JWT payload client-side via atob(); extract clinic_id claim
  │
  └─ apiFetch('/appointment-requests?clinic_id=...', {}, token)
       ↓
     frontend/lib/api.ts
       headers['Authorization'] = `Bearer ${token}`
       fetch(API_BASE_URL + path, { headers })
         ↓
       backend/app/api/dependencies/current_user.py
         get_current_user()
           credentials = HTTPBearer(auto_error=False)   ← reads Authorization header
           decode_access_token(credentials.credentials)
           get_user_by_id(pool, user_id)
           Returns AuthContext
```

### 1.3 Logout Flow (As-Built)

```
frontend/app/dashboard/page.tsx (Logout button)
  clearToken()   → sessionStorage.removeItem('praximed_access_token')
  router.push('/login')
```

No backend logout route exists. Session termination is purely client-side.

### 1.4 Auth Guard (As-Built)

```
frontend/app/dashboard/page.tsx
  useEffect(() => {
    if (!isAuthenticated()) router.push('/login')   ← client-side only; JS-dependent
  }, [])
```

No server-side auth guard (Next.js middleware) is implemented.

### 1.5 Key Files

| File | Role |
|---|---|
| `frontend/lib/auth.ts` | `storeToken`, `getToken`, `clearToken`, `isAuthenticated`, `getClinicId` |
| `frontend/lib/api.ts` | `apiFetch` — manually injects `Authorization: Bearer <token>` |
| `frontend/app/login/page.tsx` | Login form; calls `storeToken` after successful login |
| `frontend/app/dashboard/page.tsx` | Auth guard; calls `clearToken` on logout |
| `backend/app/api/routes/auth.py` | `POST /auth/login` — returns JSON body with access token |
| `backend/app/api/dependencies/current_user.py` | `get_current_user` — reads `Authorization: Bearer` header |
| `backend/app/core/jwt_tokens.py` | `create_access_token`, `decode_access_token`, `_get_jwt_secret` |
| `backend/app/main.py` | `CORSMiddleware` with `allow_credentials=True`; `_cors_origins()` |

### 1.6 Current Limitations

| Issue | Risk Level | Notes |
|---|---|---|
| `sessionStorage` JWT — XSS-accessible | **High / PHI blocker** | JavaScript on the same origin can read the token; XSS attack extracts the JWT |
| No server-side logout | **Medium** | Client-side `clearToken()` removes the local copy; server cannot invalidate the token |
| Client-side auth guard only | **Medium** | `useEffect` guard is JavaScript-dependent; server-rendered requests bypass it |
| `getClinicId()` decodes JWT client-side | **Low** (informational only) | Verification still happens server-side; but token visibility is the primary risk |
| No token refresh | **Medium** | 60-minute expiry causes silent session failure; no auto-redirect |
| No CSP header | **Medium** | No Content-Security-Policy reduces (but does not eliminate) XSS risk mitigation |
| `auth.ts` comment says "local development only" | Acknowledged | `frontend/lib/auth.ts` line 3–5 explicitly labels this local-dev only |

---

## 2. Production Target Architecture

```
Browser (staff)
  │
  ├─ POST /auth/login  { email, password, clinic_id }
  │       ↓
  │  backend/app/api/routes/auth.py
  │    (same credential check)
  │    response.set_cookie(
  │      'praximed_session', jwt_token,
  │      httponly=True, secure=True, samesite='lax',
  │      path='/', max_age=3600, domain=<domain-policy>
  │    )
  │    Returns JSON: { user: { id, clinic_id, email, role } }  ← no access_token in body
  │       ↓
  ├─ frontend/app/login/page.tsx
  │    result = await loginUser(email, password, clinicId)
  │    storeClinicId(result.user.clinic_id)   ← non-secret; non-httpOnly or state
  │    router.push('/dashboard')
  │
  └─ Cookie: praximed_session=<JWT>
       HttpOnly — not readable by JavaScript
       Secure   — HTTPS only
       SameSite — Lax (same-domain) or None (cross-domain staging)
       Path=/
```

Authenticated request flow:

```
frontend/app/dashboard/page.tsx
  │
  └─ apiFetch('/appointment-requests?clinic_id=...', { credentials: 'include' })
       ↓
     frontend/lib/api.ts
       fetch(url, { credentials: 'include' })   ← browser auto-sends cookie
       (no manual Authorization header)
         ↓
       backend/app/api/dependencies/current_user.py
         get_current_user()
           token = request.cookies.get('praximed_session')
           decode_access_token(token)
           Returns AuthContext
```

---

## 3. Cookie Strategy

### 3.1 Cookie Attributes

| Attribute | Value | Reason |
|---|---|---|
| `HttpOnly` | `True` | JavaScript cannot read the cookie; eliminates XSS-based token theft |
| `Secure` | `True` | Cookie is sent only over HTTPS; plain HTTP connections cannot receive or transmit the cookie |
| `SameSite` | See §3.2 | Controls cross-site cookie sending; key CSRF mitigation |
| `Path` | `/` | Cookie is sent for all backend API paths |
| `Max-Age` | `3600` (1 hour) | Matches the current 60-minute JWT expiry; browser deletes cookie after expiry |
| `Domain` | See §3.3 | Controls which subdomains receive the cookie |
| Cookie name | `praximed_session` | Descriptive; no functional constraints |

### 3.2 SameSite Policy by Deployment Tier

**This is the most deployment-topology-sensitive decision in the migration.**

| Tier | Frontend Domain | Backend Domain | Same Registrable Domain? | Required SameSite |
|---|---|---|---|---|
| **Local** | `http://localhost:3000` | `http://127.0.0.1:8000` | Same host (localhost) | `Lax` or omit; browsers treat `localhost` as secure context |
| **Staging (Railway + Vercel)** | `*.vercel.app` | `*.up.railway.app` | **No** — different eTLD+1 | `None; Secure` (**cross-site**) |
| **Production (custom domain)** | `app.praximed.example.com` | `api.praximed.example.com` | **Yes** — same `praximed.example.com` | `Lax` |

**Key implications:**
- **Staging** uses different registered domains (Vercel and Railway). The browser treats
  fetch requests from `staging-app.vercel.app` to `staging-api.up.railway.app` as
  cross-site. `SameSite=Lax` does NOT send the cookie for cross-site fetch/XHR requests.
  Staging requires `SameSite=None; Secure` to work — and `SameSite=None` weakens the
  default CSRF protection, requiring an explicit CSRF strategy.
- **Production** on a single registrable domain (both frontend and backend under
  `praximed.example.com`) is the target. `SameSite=Lax` provides CSRF protection without
  requiring a CSRF token. This is the canonical pattern for same-domain API + frontend.
- **Staging `SameSite=None`** is acceptable for fake-data staging only. Production must
  use a single registrable domain with `SameSite=Lax`.

### 3.3 Domain Attribute Policy

| Tier | Domain Attribute | Behavior |
|---|---|---|
| **Local** | Omit (defaults to request host) | Cookie scoped to `127.0.0.1` or `localhost` |
| **Staging** | Omit (defaults to request host) | Cookie scoped to `staging-api.up.railway.app`; sent on requests to that host |
| **Production** | `Domain=praximed.example.com` | Cookie shared across `api.praximed.example.com` and `app.praximed.example.com`; `SameSite=Lax` provides CSRF protection |

Setting `Domain=praximed.example.com` allows both backend and frontend subdomains
to receive the cookie. Without it, the cookie is scoped to the exact host that set it.

### 3.4 Expiry

- Current JWT expiry: 60 minutes (`DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60`)
- Cookie `Max-Age`: 3600 seconds (matches JWT expiry)
- On cookie expiry: browser deletes the cookie; next request gets HTTP 401; frontend
  must redirect to `/login`
- A refresh token strategy is documented in §5 but is **deferred** to a later sprint

---

## 4. Access Token Lifecycle

| Phase | Current | Target |
|---|---|---|
| **Issuance** | `POST /auth/login` → JSON body `{ access_token }` | `POST /auth/login` → `Set-Cookie: praximed_session=<JWT>; HttpOnly; Secure; SameSite=...; Max-Age=3600` + JSON body `{ user: { id, clinic_id, email, role } }` (no token in body) |
| **Storage** | `sessionStorage` via `storeToken()` | `HttpOnly` cookie — browser manages; JavaScript cannot read |
| **Transmission** | Manual `Authorization: Bearer <token>` header via `apiFetch()` | Browser auto-sends cookie on every request to the cookie domain/path |
| **Verification** | `get_current_user` reads `Authorization` header via `HTTPBearer` | `get_current_user` reads `request.cookies.get('praximed_session')` |
| **Expiry** | JWT exp claim enforced on every request; no client-side expiry detection | Same; browser also deletes cookie at `Max-Age`; HTTP 401 on expired cookie |
| **Invalidation** | No server-side invalidation; `clearToken()` removes local copy only | `POST /auth/logout` → `Set-Cookie: praximed_session=; Max-Age=0` clears cookie in browser |
| **Visibility** | Token visible to all JavaScript on origin | Token invisible to JavaScript; cannot be stolen via XSS |

### 4.1 `clinic_id` After Token Migration

Currently, `getClinicId()` decodes `clinic_id` from the JWT payload client-side (via `atob`).
After the httpOnly cookie migration, the JWT is not readable by JavaScript.

**Target strategy:** The login JSON response body already includes `user.clinic_id`.
The frontend stores `clinic_id` in a non-secret client-side store:

- **Option 1:** Store `clinic_id` in `localStorage` (persists across tabs and page reloads; not a
  secret; acceptable since `clinic_id` is a tenant identifier, not a credential)
- **Option 2:** Store in React state / context and re-fetch from `/auth/me` on page reload
- **Option 3:** Add a minimal `/auth/me` endpoint returning user info; call it on dashboard load

Option 1 is simplest for the current architecture. Option 3 is cleanest long-term.
**Recommendation:** Option 1 (localStorage for `clinic_id`) during initial migration;
Option 3 added when a `/auth/me` endpoint is built.

`clinic_id` is not a secret — it is a tenant identifier that appears in API query params
and JWT payload claims. Storing it in localStorage is not a security concern.

---

## 5. Refresh Token Lifecycle

**Status: Deferred to Sprint 14 or later.**

The current architecture has no refresh token. A 60-minute session expiry causes silent
failures (dashboard stops loading data after 60 minutes without a visible error).

A full refresh strategy requires:
1. A separate refresh token (longer-lived; stored in a second httpOnly cookie)
2. A `POST /auth/refresh` endpoint that verifies the refresh token and issues a new
   access token cookie
3. Frontend interceptor that detects HTTP 401 → attempts refresh → retries the original
   request → redirects to `/login` on refresh failure

**Why deferred:** Refresh tokens add significant complexity. The 60-minute expiry is
acceptable for the initial production launch if clinic staff re-login when the session
expires. The priority is eliminating the XSS vulnerability (`sessionStorage`), which
this plan accomplishes without refresh tokens.

**Deferred to:** Sprint 14 or a dedicated auth sprint after staging deployment is confirmed.

---

## 6. CSRF Protection

### 6.1 SameSite=Lax (Production — Same Registrable Domain)

`SameSite=Lax` is the primary CSRF defense for production:

- Cross-site `POST`, `PATCH`, `DELETE` requests do NOT include the cookie → CSRF
  attacks from other origins cannot forge authenticated mutations
- Cross-site top-level navigation `GET` requests DO include the cookie → no impact
  on API security since PHI mutation routes use `POST`/`PATCH`/`DELETE`
- No CSRF token required when frontend and backend share the same registrable domain
  and `SameSite=Lax` is in effect

### 6.2 SameSite=None (Staging — Cross-Domain)

Staging (Railway + Vercel on different registered domains) requires `SameSite=None; Secure`.
`SameSite=None` does NOT protect against cross-site CSRF — any origin could forge
requests and the browser would include the cookie.

**Mitigations for staging `SameSite=None`:**

1. **`Origin` header check (recommended for staging):** The backend checks that the
   `Origin` header of each state-mutating request matches `FRONTEND_CORS_ORIGINS`.
   FastAPI's `CORSMiddleware` already enforces this for browser requests. An explicit
   check in the auth dependency adds defense-in-depth.

2. **CSRF double-submit token (optional for staging):** A short-lived CSRF token is
   returned in the login response body; the frontend stores it (e.g., in `sessionStorage`
   or state) and sends it as a custom header (`X-CSRF-Token`) on every mutating request;
   the backend verifies it. Cross-site attackers cannot read the response body due to
   CORS, so they cannot obtain the CSRF token.

3. **Staging is fake-data only:** CSRF on staging means a staging test attacker can
   create fake appointments or confirm fake appointment rows. No PHI is at risk.

**Conclusion for production:** `SameSite=Lax` on a single registrable domain is
sufficient and is the target. The `SameSite=None` staging configuration is acceptable
for fake-data staging only. Production must not use `SameSite=None`.

### 6.3 CORS as Defense Layer

The existing `FRONTEND_CORS_ORIGINS` enforcement (exact origin; no wildcard) means that
browser `fetch` requests from unauthorized origins are rejected at the preflight stage.
This is a complementary defense but not a CSRF substitute — non-simple cross-origin
requests are blocked, but same-site or no-origin requests are not affected by CORS.

---

## 7. Logout Flow

### 7.1 Target Logout Sequence

```
Browser (staff clicks Logout)
  │
  ├─ POST /auth/logout  (credentials: 'include')
  │       ↓
  │  backend: new route in backend/app/api/routes/auth.py
  │    response.delete_cookie('praximed_session', path='/', domain=<policy>)
  │    Returns { "ok": true }
  │       ↓
  ├─ Browser removes cookie immediately (Max-Age=0 in Set-Cookie response)
  │
  └─ frontend: router.push('/login')
       clearClinicId()   ← remove non-secret clinic_id from localStorage
```

### 7.2 Backend Logout Route (Plan)

```python
# New route to add to backend/app/api/routes/auth.py

@router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie(
        key="praximed_session",
        path="/",
        domain=None,          # or domain-policy per environment
        secure=True,
        httponly=True,
        samesite="lax",       # or "none" for staging cross-domain
    )
    return {"ok": True}
```

This route does not require authentication (the cookie is deleted whether valid or not).
A client with an expired cookie can still call logout to ensure a clean state.

### 7.3 Token Blacklisting

Full server-side token blacklisting (invalidating the JWT on the server before its exp
claim) is **not in scope for the initial migration**. It requires a cache layer
(Redis, in-memory store) to track invalidated token IDs. The initial migration achieves
session termination by deleting the cookie — the JWT still technically remains valid
until its exp claim, but without the cookie, the browser cannot send it.

If a user's device is stolen and the cookie is extracted from browser storage (only
possible with OS-level access since the cookie is httpOnly), the JWT could be replayed.
This risk is accepted for the initial migration and can be addressed with token
blacklisting in a later sprint.

---

## 8. Browser Behavior

### 8.1 Login

1. Browser sends `POST /auth/login` — no cookie sent (first request)
2. Backend returns `200 OK` with `Set-Cookie: praximed_session=<JWT>; HttpOnly; Secure; SameSite=...; Max-Age=3600`
3. Browser stores the cookie; JavaScript cannot read it (httpOnly)
4. Frontend reads `result.user.clinic_id` from the JSON response body; stores in localStorage

### 8.2 Authenticated Request

1. Browser sends `GET /appointment-requests?clinic_id=...` with `credentials: 'include'`
2. Browser automatically includes `Cookie: praximed_session=<JWT>` in the request header
3. Backend reads `request.cookies.get('praximed_session')`, decodes JWT, authorizes request
4. No `Authorization: Bearer` header is sent by the frontend

### 8.3 Unauthenticated Request

1. Browser has no `praximed_session` cookie (not logged in or cookie expired)
2. Browser sends request; no cookie header included
3. Backend: `request.cookies.get('praximed_session')` returns `None`
4. Backend returns `HTTP 401 Unauthorized`
5. Frontend detects 401; redirects to `/login`

### 8.4 Logout

1. Browser sends `POST /auth/logout` with `credentials: 'include'`
2. Backend responds with `Set-Cookie: praximed_session=; Max-Age=0; Path=/`
3. Browser immediately expires and removes the cookie
4. Frontend redirects to `/login`

### 8.5 Page Reload

- Cookie persists across page reloads (it is a browser-level cookie, not sessionStorage)
- On page reload, dashboard makes API requests → cookie is sent → user remains authenticated
- **Difference from current `sessionStorage` behavior:** `sessionStorage` is cleared when
  the tab is closed. The httpOnly cookie persists until `Max-Age` expires or logout is called.
  This is a UX improvement but slightly changes session lifetime expectations.

### 8.6 Local Development

- Browsers treat `localhost` as a secure context; `Secure` cookie attribute does not
  prevent the cookie from being set or sent on `http://localhost`
- `SameSite=Lax` on localhost: `http://localhost:3000` → `http://127.0.0.1:8000` is
  technically cross-origin (different host) but same-site behavior may vary by browser
- **Pragmatic local dev approach:** For local development, `SameSite=Lax` with no
  `Secure` flag may be needed to avoid cookie issues across `localhost:3000` ↔
  `127.0.0.1:8000`. Alternatively, a cookie-exempt local dev mode (Bearer header fallback)
  can be preserved during the transition period.

---

## 9. Backend Changes Required

### 9.1 `POST /auth/login` — `backend/app/api/routes/auth.py`

**Current:** Returns JSON body with `access_token` field; no `Set-Cookie` header.

**Target changes:**
1. Import `Response` from FastAPI
2. Add `response: Response` parameter to the `login` handler
3. Call `response.set_cookie(...)` with httpOnly, Secure, SameSite, Max-Age, Path, domain
4. Change response body: keep `user` object; remove `access_token` from response body
   (or keep it for a migration window while old clients exist)

**Exact method (FastAPI):**
```python
from fastapi import Response

@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    response: Response,
    pool: Any = Depends(get_db_pool),
) -> LoginResponse:
    # ... existing credential check and token creation ...
    response.set_cookie(
        key="praximed_session",
        value=token,
        httponly=True,
        secure=True,           # False for localhost-only dev mode
        samesite="lax",        # "none" for cross-domain staging
        path="/",
        max_age=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return LoginResponse(
        access_token="",       # empty or removed during migration
        token_type="cookie",
        expires_in_seconds=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=LoginUserInfo(...),
    )
```

### 9.2 New `POST /auth/logout` Route — `backend/app/api/routes/auth.py`

```python
@router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie(
        key="praximed_session",
        path="/",
        secure=True,
        httponly=True,
        samesite="lax",
    )
    return {"ok": True}
```

No authentication required. No DB call. Returns 200 always.

### 9.3 `get_current_user` — `backend/app/api/dependencies/current_user.py`

**Current:** Uses `HTTPBearer(auto_error=False)` to extract token from `Authorization: Bearer`.

**Target changes:**
1. Add `request: Request` parameter
2. Try `request.cookies.get('praximed_session')` first
3. Fall back to `Authorization` Bearer header during migration window
4. Remove Bearer fallback once all clients are migrated to cookie auth

**Target flow:**
```python
async def get_current_user(
    request: Request,
    pool=Depends(get_db_pool),
) -> AuthContext:
    # Try cookie first
    token = request.cookies.get("praximed_session")
    # Optional migration window: fall back to Bearer header
    if not token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # ... existing decode + user load logic unchanged ...
```

### 9.4 CORS Configuration — `backend/app/main.py`

`allow_credentials=True` is already set. No change required. The `FRONTEND_CORS_ORIGINS`
must remain an exact origin (no wildcard) — already enforced by `_cors_origins()`.

### 9.5 Environment-Specific Cookie Attributes

The `samesite` and `secure` values differ by deployment tier. Options:
1. **Single code path with env var:** `COOKIE_SAMESITE=lax` (production) vs
   `COOKIE_SAMESITE=none` (staging cross-domain). An `APP_ENV` check is also possible.
2. **Hardcode production target:** Always use `SameSite=Lax; Secure`; accept that
   staging on cross-domain Railway/Vercel will require custom domain setup.

**Recommendation:** For the initial Sprint 14 implementation, implement
`SameSite=Lax; Secure` (production-target values). Test on staging with a custom domain
if available, or use the Bearer-header fallback for staging-only testing until custom
domains are configured.

---

## 10. Frontend Changes Required

### 10.1 `frontend/lib/auth.ts`

**Remove:**
- `storeToken(token)` — no longer needed; cookie set by backend
- `getToken()` — cookie not readable by JS
- `clearToken()` — cookie cleared by backend via logout route
- `isAuthenticated()` based on `getToken()` — no longer works without readable token

**Add:**
- `storeClinicId(clinicId: string)` — stores `clinic_id` from login response in `localStorage`
- `getClinicId()` — read from `localStorage` instead of decoding JWT
- `clearClinicId()` — remove from `localStorage` on logout
- `isAuthenticated()` — alternative: attempt `/auth/me` call; or rely on API 401 response;
  or store a non-secret `authenticated=true` flag in `localStorage`

### 10.2 `frontend/lib/api.ts`

**Change `apiFetch`:**
- Remove `token?: string` parameter (cookie is sent automatically)
- Remove `Authorization: Bearer` header injection
- Add `credentials: 'include'` to all fetch calls

**All helper functions** (`fetchAppointmentRequests`, `fetchPatients`, etc.) that
currently accept a `token` parameter must remove it.

**Impact on callers:** All dashboard data-fetch calls in `dashboard/page.tsx` that
pass a token must be updated to remove the token argument.

### 10.3 `frontend/app/login/page.tsx`

**Remove:** `storeToken(result.access_token)` call.
**Add:** `storeClinicId(result.user.clinic_id)` to persist non-secret tenant ID.
**Keep:** `router.push('/dashboard')` — unchanged.

### 10.4 `frontend/app/dashboard/page.tsx`

**Remove:**
- `getToken()` calls (token no longer accessible)
- Token passing to all `fetchXxx(clinicId, token)` calls
- `clearToken()` on logout

**Add:**
- `POST /auth/logout` call before redirect to `/login`
- `clearClinicId()` on logout

**Auth guard:** The `useEffect` → `isAuthenticated()` guard remains but the
`isAuthenticated()` implementation changes (see §10.1).

**Optional:** Add Next.js middleware (`frontend/middleware.ts`) for server-side
route protection — checks for cookie presence; redirects unauthenticated requests
to `/login` before page render.

---

## 11. Testing Strategy

### 11.1 Backend Unit Tests

New tests for `backend/tests/test_auth_login_route.py` (extend existing):
- `POST /auth/login` response sets `Set-Cookie` header
- Cookie has `httponly` attribute
- Cookie has `secure` attribute (when enabled)
- Cookie name is `praximed_session`
- Cookie `Max-Age` matches JWT expiry
- Response body no longer contains `access_token` (or contains an empty string)
- Response body still contains `user.clinic_id`, `user.email`, `user.role`

New tests for `backend/tests/test_auth_logout_route.py`:
- `POST /auth/logout` returns HTTP 200
- Response sets `Set-Cookie` with `Max-Age=0` (or equivalent deletion)
- Does not require an authenticated session to call
- No DB call in the logout handler

New/updated tests for `backend/tests/test_current_user_dependency.py`:
- `get_current_user` accepts a valid `praximed_session` cookie
- `get_current_user` returns HTTP 401 when no cookie and no Bearer header
- `get_current_user` during migration window: also accepts Bearer header
- Expired cookie returns HTTP 401
- Invalid JWT in cookie returns HTTP 401

### 11.2 Frontend Contract Tests

New static contract tests (extend or add to existing frontend contract tests):
- `frontend/lib/auth.ts` does not contain `sessionStorage` (after migration)
- `frontend/lib/api.ts` contains `credentials: 'include'`
- `frontend/lib/api.ts` does not inject `Authorization: Bearer` header
- `frontend/app/login/page.tsx` calls `storeClinicId` not `storeToken`
- `frontend/app/dashboard/page.tsx` calls `POST /auth/logout` before redirect

### 11.3 Integration Tests

After implementation, the local smoke runbook must be re-executed:
- Login → cookie set → dashboard loads (via cookie auth)
- Vapi machine auth routes are unaffected (they use machine auth headers, not JWT cookie)
- n8n webhook routes are unaffected (they use HMAC signature, not JWT cookie)
- Staff Confirm works via cookie auth (PATCH route protected by `get_current_user`)
- Logout clears cookie; dashboard redirects to login

### 11.4 Regression Tests

All existing PHI route tests that use `get_current_user` must pass. No PHI route
logic changes — only the auth dependency input source changes (cookie vs Bearer header).

---

## 12. Rollback Strategy

If the cookie migration fails or causes regressions:

1. **Backend rollback:** Revert `auth.py` to return `access_token` in JSON body;
   revert `get_current_user` to use only Bearer header; remove logout route.
2. **Frontend rollback:** Revert `auth.ts` to restore `storeToken`/`getToken`/`clearToken`;
   revert `api.ts` to restore Bearer header injection.
3. **Migration window approach:** During implementation, keep the Bearer header fallback
   in `get_current_user` — this allows the old frontend to continue working while the
   new cookie-based frontend is deployed. Roll back the frontend only if the new frontend
   has issues.
4. **No DB changes:** The auth migration touches only code and cookie behavior; no schema
   or migration changes are required. Rollback is a code-only operation.

---

## 13. Migration Sequence

Recommended implementation order for Sprint 14:

| Step | Action | Files Changed | Can Roll Back? |
|---|---|---|---|
| 1 | Add `POST /auth/logout` route | `auth.py` | Yes — remove route |
| 2 | Update `POST /auth/login` to set httpOnly cookie | `auth.py` | Yes — remove `set_cookie` call |
| 3 | Update `get_current_user` to try cookie first, fall back to Bearer | `current_user.py` | Yes — revert to Bearer-only |
| 4 | Add backend unit tests (login cookie, logout, current_user) | test files | Yes — delete test files |
| 5 | Update `frontend/lib/auth.ts` — add `storeClinicId`, `getClinicId` from localStorage, `clearClinicId` | `auth.ts` | Yes — revert file |
| 6 | Update `frontend/lib/api.ts` — add `credentials: 'include'`; remove Bearer header injection | `api.ts` | Yes — revert file |
| 7 | Update `frontend/app/login/page.tsx` — replace `storeToken` with `storeClinicId` | `login/page.tsx` | Yes — revert file |
| 8 | Update `frontend/app/dashboard/page.tsx` — remove token passing; add logout call | `dashboard/page.tsx` | Yes — revert file |
| 9 | Run full test suite — confirm 1865+ tests pass with no regressions | CI | N/A |
| 10 | Run local smoke runbook with cookie auth | Manual | Revert if smoke fails |
| 11 | Deploy to staging; run staging smoke runbook | Manual | Railway/Vercel rollback |

**Step 3 (Bearer fallback)** is important: keeping the Bearer header as a secondary
option during the transition ensures that any client still using the old token-in-body
approach continues to work until the frontend migration is deployed. Remove the fallback
in a subsequent commit once the full cookie migration is confirmed working end-to-end.

---

## 14. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Staging cross-domain cookie incompatibility | **High** | Railway + Vercel are different registered domains; `SameSite=Lax` will not send cross-site cookies; requires `SameSite=None; Secure` for staging or a custom domain |
| `clinic_id` no longer client-accessible after cookie migration | **Medium** | Resolved by reading `clinic_id` from login JSON body and storing in `localStorage`; or adding `/auth/me` endpoint |
| `sessionStorage` tab isolation lost (cookie persists across tabs) | **Low** | Intentional UX improvement; session now persists until `Max-Age` or logout; document for clinic staff |
| Missing `POST /auth/logout` call in edge cases | **Medium** | Client-side logout must always call the backend logout route; test all logout paths |
| `Secure` flag breaks local dev (`http://` localhost) | **Low** | Chrome/Firefox exemptions for localhost; or add `secure=False` in `APP_ENV=local` mode |
| 60-minute session expiry causes silent failures | **Medium** | Deferred to refresh token sprint; document expected behavior: re-login required after 60 min |
| JWT token blacklisting not implemented | **Low** | Without blacklisting, tokens remain valid until exp even after logout; accepted for initial migration; cookie deletion prevents browser from sending the token |
| CSRF on staging (SameSite=None) | **Low** | Staging uses fake data; CSRF attacker can only affect fake appointments; add `Origin` header check as defense-in-depth |
| Tests using Bearer header stop working after migration | **Medium** | Keep Bearer fallback in `get_current_user` during migration; update test client fixtures to use cookie-based auth after migration window closes |

---

## 15. Final Recommendation

### 15.1 Decision

**Proceed with the httpOnly Secure SameSite cookie migration in Sprint 14.**

This is the single highest-priority production blocker. The `sessionStorage` JWT is
explicitly labeled "local development only" in `frontend/lib/auth.ts`. No real clinic
PHI can be processed while JWT tokens are stored in XSS-accessible `sessionStorage`.

### 15.2 Scope for Sprint 14

| In scope | Out of scope |
|---|---|
| `POST /auth/login` sets httpOnly cookie | Refresh token endpoint |
| `POST /auth/logout` route | Token blacklisting |
| `get_current_user` reads cookie (Bearer fallback during migration) | CSP header implementation |
| Frontend removes `sessionStorage` token storage | Next.js server-side middleware guard |
| Frontend adds `credentials: 'include'` | Appointment workflow expansion |
| `clinic_id` stored in `localStorage` from login response | Fabel 5 / frontend UX sprint |
| Full test suite updated | Calendar handoff |

### 15.3 Production Launch Dependency

After the Sprint 14 cookie migration:
- The `sessionStorage` JWT blocker is resolved
- 11 remaining blockers from Architecture Checkpoint 12 still apply
- Production PHI launch requires all 12 blockers resolved

This migration alone does not approve a production launch. It resolves the highest-risk
PHI security blocker. The staging deployment (Modules 95–97) confirms the deployment
infrastructure; the auth migration (Module 98 plan, Sprint 14 implementation) confirms
the session security model.

---

## Appendix: Change Impact Matrix

| File | Change Type | Breaking? |
|---|---|---|
| `backend/app/api/routes/auth.py` | Add `Set-Cookie` to login; add logout route | No (Bearer fallback preserved) |
| `backend/app/api/dependencies/current_user.py` | Try cookie first; fallback to Bearer | No (fallback) |
| `backend/app/main.py` | No change | — |
| `frontend/lib/auth.ts` | Replace `sessionStorage` functions with `localStorage` for `clinic_id` | Breaking if rolled back without also reverting API layer |
| `frontend/lib/api.ts` | Add `credentials: 'include'`; remove Bearer header | Breaking for endpoints that receive no cookie |
| `frontend/app/login/page.tsx` | Replace `storeToken` with `storeClinicId` | Breaking if `api.ts` not also updated |
| `frontend/app/dashboard/page.tsx` | Remove token passing; add logout route call | Breaking if `api.ts` not also updated |
