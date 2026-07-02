# Sprint 8 / Module 67 — Frontend Login Flow Integration

Status: pending Module 66 review.

## Context

Module 66 created the Next.js frontend skeleton with:
- `/login` — email/password form UI (not yet connected to backend)
- `/dashboard` — placeholder cards for Patients, Appointments, Notifications, Consultations
- `lib/api.ts` — `apiFetch` helper with `NEXT_PUBLIC_API_BASE_URL`
- `lib/auth.ts` — `loginUser`, `storeToken`, `getToken`, `clearToken`, `isAuthenticated`

The backend already has `POST /auth/login` returning a JWT (Module 60). The helpers
exist; they just need to be wired to the form.

## Scope

- Wire the login form in `frontend/app/login/page.tsx` to call `loginUser()` from `lib/auth.ts`.
- On success: store the token and redirect to `/dashboard`.
- On failure: display an error message below the form.
- Add a route guard to `/dashboard/page.tsx`: redirect to `/login` if no token in storage.
- Add a logout button to the dashboard header that calls `clearToken()` and redirects to `/login`.
- Add static contract tests confirming the form has an `onSubmit` handler and the dashboard has a logout trigger.

## What not to do

- Do not add refresh token logic.
- Do not switch to httpOnly cookies in this module (deferred to auth hardening sprint).
- Do not fetch real data from the backend yet (Patients/Appointments/Notifications list fetching is Module 68+).
- Do not modify any backend routes.
- Do not use real patient data.

## Acceptance

- Submitting the login form with correct credentials stores a token and loads `/dashboard`.
- Submitting with wrong credentials shows an error without crashing.
- Navigating to `/dashboard` without a token redirects to `/login`.
- Dashboard logout button clears the token and redirects to `/login`.
- Full backend tests pass.
- Commit: `Sprint 8 / Module 67 — Frontend login flow integration`
