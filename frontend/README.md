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

## Status

Sprint 8 / Module 66 — skeleton only. Login flow wired to backend in Module 67.
