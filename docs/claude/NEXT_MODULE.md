# Sprint 8 / Module 68 — Frontend Appointment List Integration

Status: pending Module 67 review.

## Context

Module 67 wired the login form to `POST /auth/login` and added a client-side auth
guard to the dashboard. The token is now stored and available via `getToken()`.

The dashboard currently shows four disabled placeholder cards. The backend already
has `GET /appointment-requests` (requires Bearer JWT, Module 64). This module wires
that endpoint to the Appointments card on the dashboard.

## Scope

- In `frontend/app/dashboard/page.tsx`, fetch `GET /appointment-requests` using
  `apiFetch` with the stored JWT and render the returned list under the Appointments
  section.
- Show a loading state while fetching and an error state on failure.
- Do not build a full CRUD table — a simple read-only list of request IDs,
  patient names, and status is sufficient.
- Add static contract tests confirming:
  - dashboard calls the appointments endpoint
  - dashboard handles loading and error states
  - dashboard renders appointment list data

## What not to do

- Do not fetch patients, consultations, or notifications yet.
- Do not add real patient data to tests.
- Do not modify backend routes.
- Do not remove the auth guard added in Module 67.

## Acceptance

- Dashboard fetches appointment requests for the logged-in clinic and displays them.
- Loading and error states are handled gracefully.
- Full backend tests pass.
- Commit: `Sprint 8 / Module 68 — Frontend appointment list integration`
