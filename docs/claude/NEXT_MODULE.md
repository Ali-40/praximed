# Sprint 8 / Module 66 — Frontend Dashboard Foundation

Status: pending Architecture Checkpoint 06 review.

## Context

Sprint 7 (Modules 59–65) completed the full human auth layer:
- JWT login endpoint (`POST /auth/login`)
- `get_current_user` dependency enforcing Bearer JWT on all PHI routes
- All five PHI route groups now require JWT: `/patients`, `/consultations`,
  `/clinical-workflows`, `/appointment-requests`, `/notifications`

The backend is auth-complete for human users. Machine routes (Vapi, n8n, webhooks)
remain on header-based machine auth and are unchanged.

A frontend can now be built against real JWT-secured API endpoints.

## Scope

Build a minimal Next.js frontend skeleton:
- Login page: email + password form → `POST /auth/login` → store JWT
- Session handling: secure JWT storage (httpOnly cookie preferred)
- Clinic dashboard layout: sidebar, route guards for authenticated pages
- Appointment request queue: list view fetching `GET /appointment-requests`
- Notification feed: list view fetching `GET /notifications`

Do not build:
- Doctor review / clinical workflow UI (deferred)
- Patient record editing UI (deferred)
- Full CRUD forms beyond minimal read views

## What not to do

- Do not add auth hardening (refresh tokens, rate limiting) in this module.
- Do not modify any backend routes.
- Do not use real patient data.
- Do not deploy to production.

## Acceptance

- Login page authenticates against the backend and stores the JWT.
- Dashboard loads and displays appointment requests and notifications for the logged-in clinic.
- Unauthenticated navigation redirects to login.
- Commit: `Sprint 8 / Module 66 — Frontend dashboard foundation`
