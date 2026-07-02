# Architecture Checkpoint 07 — Frontend Dashboard Review

**Sprint:** 8 (Modules 66–71)
**Date:** 2026-07-02
**Status:** Complete

---

## 1. Current Status

Sprint 8 is complete. The PraxisMed frontend now exists as a Next.js 14 TypeScript
application with a working login flow and a live dashboard that fetches data from all
four backend sections. All static contract tests pass; no backend routes were modified
during this sprint.

Full backend test suite: **1521/1521 passed**.

---

## 2. Completed Sprint 8 Work

### Module 66 — Frontend Dashboard Foundation
- Next.js 14 + TypeScript skeleton created under `frontend/`.
- Pages: `/` redirects to `/login`; `/login` form scaffold; `/dashboard` placeholder.
- `frontend/lib/api.ts` — `apiFetch` helper with `NEXT_PUBLIC_API_BASE_URL` env var
  and `http://127.0.0.1:8000` fallback.
- `frontend/lib/auth.ts` — `loginUser`, `storeToken`, `getToken`, `clearToken`,
  `isAuthenticated`; `sessionStorage` used with explicit local-dev-only warning.
- `frontend/app/globals.css` — minimal CSS custom properties (brand colour, border,
  surface, danger, radius, shadow).
- Static contract tests: 10/10.

### Module 67 — Login Flow Integration
- `/login` form wired to `POST /auth/login` via `loginUser`.
- On success: `storeToken` + `router.push('/dashboard')`.
- On failure: generic error — does not reveal whether email or password was wrong.
- `/dashboard` auth guard: `useEffect` redirects to `/login` if no token in
  `sessionStorage`.
- Logout button: `clearToken` + `router.push('/login')`.
- Static contract tests: 10/10.

### Module 68 — Appointment Requests Live
- `AppointmentRequest` interface + `fetchAppointmentRequests(clinicId, token)` added
  to `lib/api.ts`.
- `getClinicId()` added to `lib/auth.ts` — decodes `clinic_id` from stored JWT
  payload via `atob` (no extra library; backend verifies signature on every request).
- Dashboard Appointments section: loading / error / empty / list states.
- List shows patient name, status badge (blue for `new`), and urgency level.
- Static contract tests: 10/10.

### Module 69 — Patients Live
- `Patient` interface + `fetchPatients(clinicId, token)` added to `lib/api.ts`.
- Dashboard Patients section: loading / error / empty / list states.
- List shows full name (first + last, with `—` fallback) and status badge
  (green for `active`).
- Static contract tests: 10/10.

### Module 70 — Notifications Live
- `Notification` interface + `fetchNotifications(clinicId, token)` added to
  `lib/api.ts`.
- Dashboard Notifications section: loading / error / empty / list states.
- List shows title, priority badge (red for `urgent`/`emergency`), and
  `notification_type`.
- Static contract tests: 10/10.

### Module 71 — Consultations Live
- `ConsultationSession` interface + `fetchConsultations(clinicId, token)` added to
  `lib/api.ts`.
- Dashboard Consultations section: loading / error / empty / list states.
- List shows title, approval status badge (green for `approved`), and source.
- Consultations placeholder card removed; `PLACEHOLDER_SECTIONS` array eliminated.
- All four dashboard sections are now live.
- Static contract tests: 10/10.

---

## 3. What Is Proven

| Claim | Evidence |
|---|---|
| Frontend skeleton exists | `frontend/` directory with `package.json`, `tsconfig.json`, `next.config.js`, `app/`, `lib/` present |
| Login calls backend auth | `loginUser` POSTs to `/auth/login`; form submit wired in `login/page.tsx` |
| Dashboard auth guard exists | `useEffect` checks `isAuthenticated()` and `getClinicId()` before fetching |
| JWT Bearer pattern established | `apiFetch` sets `Authorization: Bearer <token>` on every authenticated call |
| All four sections fetch backend | `fetchAppointmentRequests`, `fetchPatients`, `fetchNotifications`, `fetchConsultations` each call their respective routes with Bearer JWT |
| Loading / error / empty / list states | Each section has four render branches controlled by loading/error/data state variables |
| clinic_id decoded from JWT | `getClinicId()` in `auth.ts` extracts the `clinic_id` claim via `atob` without a library |
| No hard-coded secrets or real data | Static contract tests assert no JWT literals, no `sk-` keys, no real patient markers |
| Backend routes unchanged | All 1521 backend tests pass; no route file was modified in Sprint 8 |

---

## 4. What Is Not Proven

| Gap | Detail |
|---|---|
| Real browser end-to-end | No `npm install` or `npm run dev` was executed; no browser session tested login → dashboard → data load |
| Production auth storage | `sessionStorage` is marked local-dev only; `httpOnly` cookie pattern not implemented |
| Token refresh | JWT expires (currently set by `ACCESS_TOKEN_EXPIRE_MINUTES`); no refresh endpoint or client-side refresh logic exists |
| Logout / token revocation | `clearToken` removes the token from `sessionStorage` but does not invalidate it on the backend; a stolen token remains valid until expiry |
| Frontend runtime errors | TypeScript type errors and Next.js build errors not verified — `tsc --noEmit` and `next build` not run |
| Role-based section visibility | All four sections are rendered for every authenticated user; consultations and clinical workflows require `owner/admin/doctor` on the backend, but the frontend does not hide them for `staff` or `viewer` roles |
| Polished UI / responsive design | Minimal inline styles only; no mobile viewport testing; no accessibility audit |
| Create / edit flows | Dashboard is read-only; no forms for creating patients, appointments, consultations, or notifications |
| Error message detail | Fetch errors show a single generic string; HTTP status codes (401, 403, 503) are not surfaced distinctly to the user |
| Deployment | No production build, no CI/CD pipeline, no HTTPS configuration, no Docker image for the frontend |

---

## 5. Security Review

### Confirmed Good
- **No hard-coded credentials or tokens.** All six frontend files checked by static
  contract tests for JWT literals, `sk-` prefixes, and real patient data markers.
- **Generic login error.** The login page shows "Sign-in failed. Please check your
  details and try again." — does not reveal whether email or password was wrong
  (no user enumeration).
- **Backend validates JWT per request.** The frontend decodes `clinic_id` from the JWT
  payload only for URL construction. Signature verification and expiry checking happen
  on the backend for every API call.
- **Tenant separation intact.** Every fetch passes `clinic_id` as a query parameter;
  backend `require_staff_clinic_access` / `require_clinical_clinic_access` enforce that
  the caller's `clinic_id` matches the requested resource's clinic.

### Remaining Concerns
- **`sessionStorage` is not production-safe.** JWTs stored in `sessionStorage` are
  accessible to any JavaScript on the page. The comment in `lib/auth.ts` flags this
  explicitly, but the replacement path (httpOnly cookies via a `/auth/session` backend
  endpoint) has not been built.
- **No token expiry handling on the frontend.** An expired token causes API calls to
  return HTTP 401. The dashboard currently shows the generic error string "Could not
  load …" rather than redirecting to `/login`, which could confuse users.
- **No CSRF protection.** SessionStorage-based auth avoids the classic CSRF vector for
  cookies, but the production httpOnly cookie path will require CSRF mitigations.

---

## 6. Main Risks Before Demo

| Risk | Severity | Detail |
|---|---|---|
| Frontend has never run in a browser | High | `npm install` and `npm run dev` have not been executed in this session; TypeScript compilation errors or missing peer dependencies could block the demo |
| No seeded login tested end-to-end | High | `backend/scripts/seed_local_data.py` exists but the full flow (seed → login form → JWT → dashboard data) has not been manually verified |
| Expired JWT shows generic error | Medium | After token expiry the user sees "Could not load …" for all four sections rather than a redirect to login |
| Role mismatch silently fails | Medium | A `staff` user will see "Could not load consultations…" because the backend returns 403, but no UI distinction is made |
| No frontend build validation | Medium | `next build` has not been run; build-time errors would surface only at deploy time |
| No HTTPS | Low (local) | Local dev uses HTTP; a production deployment without HTTPS would transmit JWTs in plaintext |

---

## 7. Recommended Next Sprint Options

### Option A — Frontend Local Runtime Smoke (Recommended)
Run `npm install` + `npm run dev`, seed a local user, and manually verify the full
login → dashboard → data load flow in a real browser. Fix any TypeScript or runtime
errors discovered. Adds confidence before any further feature work.

### Option B — Create/Edit Patient UI
Add a "New Patient" form and a patient detail page. Requires frontend routing (dynamic
`/patients/[id]` page) and `POST /patients` + `PATCH /patients/:id` API helpers.
High product value but depends on Option A being validated first.

### Option C — Appointment Request Workflow UI
Add the ability for clinic staff to change appointment request status (accept/decline)
directly from the dashboard. Requires a `PATCH /appointment-requests/:id` call and
inline status controls.

### Option D — Auth Hardening
Implement token refresh (new backend endpoint + frontend polling), move token storage
to httpOnly cookies (requires backend `/auth/session` endpoint), and add a server-side
logout/revocation endpoint. Prerequisite for production deployment.

---

## 8. Recommendation

**Sprint 9 / Module 72 — Frontend Local Runtime Smoke and Seed Login**

Run the frontend in a real browser against the local backend. The goal is to prove
that the code written in Sprint 8 actually works end-to-end before building more
features on top of it. Specifically:

1. `npm install` in `frontend/`.
2. `npm run dev` — verify the dev server starts without errors.
3. `npx tsc --noEmit` — verify no TypeScript compilation errors.
4. Seed a local user via `backend/scripts/seed_local_data.py`.
5. Open `http://localhost:3000`, log in with the seeded credentials.
6. Verify all four dashboard sections reach the backend and render loading → data
   (or empty if the clinic has no records yet).
7. Log out and confirm redirect to `/login`.
8. Document results in `docs/integrations/FRONTEND_LOCAL_SMOKE_RESULTS.md`.

This gives a solid foundation for Option B (patient forms) or Option D (auth hardening)
in the subsequent module.

---

## Sprint 8 Summary

| Item | Count |
|---|---|
| Modules completed | 6 (66–71) |
| Frontend files created | 10 |
| API helpers added | 4 (appointments, patients, notifications, consultations) |
| Static contract tests | 60 (10 per module) |
| Backend tests (unchanged) | 1521/1521 |
| Backend routes modified | 0 |
