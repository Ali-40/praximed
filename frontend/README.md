# PraxisMed Frontend

Next.js TypeScript dashboard for PraxisMed clinic management.

## Prerequisites

- Node.js 18+
- npm (or yarn / pnpm)
- PraxisMed backend running locally (see `../docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md`)

## Local setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Create a local env file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and set:

```
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

3. Start the development server:

```bash
npm run dev
```

The app runs at `http://localhost:3000`.

## Pages

| Route | Description |
|---|---|
| `/` | Redirects to `/login` |
| `/login` | Login form (wired to backend in Module 67) |
| `/dashboard` | Clinic dashboard (placeholder — data in Module 67) |

## Auth

JWT tokens are stored in `sessionStorage` during local development only. For production,
tokens must be stored in httpOnly cookies via the backend session endpoint. See
`lib/auth.ts` for the full note.

## Backend API

The backend exposes:
- `POST /auth/login` — returns a JWT access token
- `GET /appointment-requests` — lists appointment requests (requires JWT)
- `GET /notifications` — lists notifications (requires JWT)

All API calls go through `lib/api.ts`. Set `NEXT_PUBLIC_API_BASE_URL` to change the
target backend.

## Login flow (Module 67)

The login form collects **Clinic ID**, **Email**, and **Password**, then calls
`POST /auth/login` on the backend. On success the JWT access token is stored in
`sessionStorage` (local development only — see auth note above) and the browser
navigates to `/dashboard`.

On failure a generic error is shown — the message does not reveal whether the email
or password was wrong.

The dashboard performs a client-side auth check on load. If no token is found in
`sessionStorage`, the user is redirected to `/login`. The **Logout** button in the
header clears the token and returns to `/login`.

To test the full login flow locally:
1. Ensure the backend is running (`uvicorn backend.app.main:app --reload`).
2. Seed a user in the local database (see `backend/scripts/seed_local_data.py`).
3. Start the frontend (`npm run dev`) and open `http://localhost:3000`.
4. Enter the seeded Clinic ID, email, and password.

## Dashboard data (Module 68)

After login, the **Appointments** section fetches `GET /appointment-requests?clinic_id=<id>`
from the backend using the stored JWT as `Authorization: Bearer <token>`. The `clinic_id`
is decoded from the JWT payload client-side (no extra library — plain `atob`).

The section shows:
- **Loading** — while the request is in flight
- **Error** — generic message if the request fails
- **Empty** — if the clinic has no appointment requests yet
- **List** — patient name, status badge, and urgency level for each request

## Dashboard data — Patients (Module 69)

The **Patients** section fetches `GET /patients?clinic_id=<id>` from the backend using
the stored JWT as `Authorization: Bearer <token>`.

The section shows:
- **Loading** — while the request is in flight
- **Error** — generic message if the request fails
- **Empty** — if the clinic has no patients yet
- **List** — full name (first + last) and status badge for each patient

`fetchPatients(clinicId, token)` in `lib/api.ts` handles the request. The `clinic_id`
is decoded from the JWT payload by `getClinicId()` in `lib/auth.ts`.

## Dashboard data — Notifications (Module 70)

The **Notifications** section fetches `GET /notifications?clinic_id=<id>` from the backend
using the stored JWT as `Authorization: Bearer <token>`.

The section shows:
- **Loading** — while the request is in flight
- **Error** — generic message if the request fails
- **Empty** — if the clinic has no notifications yet
- **List** — title, priority badge (red for urgent/emergency), and notification type for each entry

`fetchNotifications(clinicId, token)` in `lib/api.ts` handles the request.

## Dashboard data — Consultations (Module 71)

The **Consultations** section fetches `GET /consultations?clinic_id=<id>` from the backend
using the stored JWT as `Authorization: Bearer <token>`.

The section shows:
- **Loading** — while the request is in flight
- **Error** — generic message if the request fails
- **Empty** — if the clinic has no consultation sessions yet
- **List** — title, approval status badge (green for approved), and source for each session

`fetchConsultations(clinicId, token)` in `lib/api.ts` handles the request.

All four dashboard sections (Appointments, Patients, Notifications, Consultations) are now live.

## Status

Sprint 8 / Module 71 — All dashboard sections wired to backend.
