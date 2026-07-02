# Frontend Local Runtime Smoke — PraxisMed Sprint 9 / Module 72
Updated: Sprint 9 / Module 73 — runtime blockers fixed; runbook updated

This runbook walks through a complete local browser smoke test: start the stack,
seed a login-capable fake user, sign in at `/login`, and verify all four dashboard
sections load data from the backend.

**All credentials and data here are fake and local-dev only. Never use them in
production.**

---

## Known Runtime Blockers (fixed in Module 73)

Before running this runbook, ensure you have the Module 73 fixes applied:

| Blocker | Cause | Fix |
|---|---|---|
| `value too long for type character varying(32)` during migration | Alembic revision ID `0002_add_password_hash_to_clinic_users` was 42 chars | Shortened to `0002_password_hash` (16 chars) in `0002_add_password_hash_to_clinic_users.py` |
| `ModuleNotFoundError: No module named 'backend'` from seed script | Script lacked `sys.path` project-root insertion for direct execution | Added `_PROJECT_ROOT` path safety at top of `seed_local_data.py` |
| `[Errno 48] Address already in use` on backend start | Previous Uvicorn process still running on port 8000 | Stop old process first (see Step 4 below) |

---

## Prerequisites

- Docker Desktop running (for PostgreSQL)
- Python 3.11+ with `asyncpg` and `bcrypt` installed (`pip install -r backend/requirements.txt`)
- Node.js 18+ with npm
- No ngrok or external tunnel needed — all traffic is local

---

## Step 1 — Start PostgreSQL

```bash
docker-compose -f docker-compose.postgres.yml up -d
```

Expected: container `praxismed_postgres` starts and listens on port 5433.

Verify:
```bash
docker ps | grep praxismed
```

---

## Step 2 — Run Migrations

```bash
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local

cd backend
alembic upgrade head
cd ..
```

Expected: Alembic prints `Running upgrade ... -> ...` for each migration and exits
with code 0. The `clinic_users` table will include the `password_hash` column added
in migration `0002`.

---

## Step 3 — Run Seed Data Script

```bash
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local

python backend/scripts/seed_local_data.py
```

Expected output (example — password_hash is never printed):

```
Seeding local test data...
Local seed data inserted successfully (fake/local only — not production data):
  clinic_id:               11111111-1111-1111-1111-111111111111
  doctor_user_id:          22222222-2222-2222-2222-222222222222
  patient_id:              33333333-3333-3333-3333-333333333333
  consultation_session_id: 44444444-4444-4444-4444-444444444444

LOCAL-DEV LOGIN (fake/local only — NOT for production):
  clinic_id: 11111111-1111-1111-1111-111111111111
  email:     doctor.local@praximed.test
  password:  local-dev-password
```

The script is idempotent — safe to run multiple times.

---

## Step 4 — Start the Backend

**If port 8000 is already in use** (e.g. from a previous session), stop the old
Uvicorn process first:

```bash
# Option A — use Ctrl+C in the terminal where Uvicorn is running
# Option B — find and kill the process
lsof -ti:8000 | xargs kill -9
```

In a new terminal, start the backend with both required environment variables:

```bash
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
export JWT_SECRET_KEY=local-dev-jwt-secret-key-change-in-production

uvicorn backend.app.main:app --reload --port 8000
```

Both `DATABASE_URL` and `JWT_SECRET_KEY` must be set. If `JWT_SECRET_KEY` is missing,
`POST /auth/login` returns HTTP 503.

Expected: Uvicorn starts on `http://127.0.0.1:8000`. Check the health endpoint:

```bash
curl http://127.0.0.1:8000/health
# {"ok": true}
```

---

## Step 5 — Start the Frontend

In another new terminal:

```bash
cd frontend
npm install          # first time only
```

Create `.env.local` if it does not exist:

```bash
echo "NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000" > .env.local
```

Start the dev server:

```bash
npm run dev
```

Expected: Next.js starts on `http://localhost:3000`.

Optional TypeScript check (no browser required):

```bash
npx tsc --noEmit
```

---

## Step 6 — Open /login in a Browser

Navigate to: `http://localhost:3000`

Expected: browser redirects to `http://localhost:3000/login`.

---

## Step 7 — Log In with Local-Dev Credentials

Fill in the login form:

| Field | Value |
|---|---|
| Clinic ID | `11111111-1111-1111-1111-111111111111` |
| Email | `doctor.local@praximed.test` |
| Password | `local-dev-password` |

Click **Sign in**.

Expected:
- POST `/auth/login` returns HTTP 200 with a JWT.
- Browser redirects to `http://localhost:3000/dashboard`.
- JWT is stored in `sessionStorage` under the key `praximed_access_token`.

If you see "Sign-in failed. Please check your details and try again.":
- Confirm the backend is running and reachable at `http://127.0.0.1:8000`.
- Confirm Step 3 (seed) completed without errors.
- Confirm `JWT_SECRET_KEY` is set in the backend terminal.

---

## Step 8 — Confirm Dashboard Loads

After login the dashboard should show four sections. Each section goes through:
**Loading → Data** (or **Empty** if no additional records exist beyond the seed row).

| Section | Expected minimum |
|---|---|
| **Appointments** | Loading state, then either empty or the seed appointment request |
| **Patients** | Loading state, then "Local Test Patient" (seeded in Step 3) |
| **Notifications** | Loading state, then empty (no notifications seeded) |
| **Consultations** | Loading state, then "Local Test Consultation Session" (seeded in Step 3) |

Open the browser developer tools → Network tab to confirm:
- `GET /appointment-requests?clinic_id=11111111-...` → HTTP 200
- `GET /patients?clinic_id=11111111-...` → HTTP 200
- `GET /notifications?clinic_id=11111111-...` → HTTP 200
- `GET /consultations?clinic_id=11111111-...` → HTTP 200

All four requests should include `Authorization: Bearer <token>` in the request
headers.

---

## Step 9 — Log Out

Click the **Logout** button in the top-right corner of the dashboard.

Expected:
- `praximed_access_token` is removed from `sessionStorage`.
- Browser redirects to `http://localhost:3000/login`.
- Pressing the browser back button and returning to `/dashboard` should redirect
  back to `/login` (auth guard triggers).

---

## Known Limitations

| Limitation | Detail |
|---|---|
| **sessionStorage is local-dev only** | JWTs are stored in `sessionStorage` which is accessible to JavaScript. For production, tokens must be stored in httpOnly cookies set by the backend. See `frontend/lib/auth.ts`. |
| **No production auth storage** | The httpOnly cookie path (`/auth/session` backend endpoint) has not been built. |
| **No token refresh** | The JWT expires after the configured `ACCESS_TOKEN_EXPIRE_MINUTES`. The frontend shows a generic error on expiry rather than redirecting to `/login`. |
| **No real patient data** | All data comes from the deterministic local seed — no real clinic, patient, or appointment data is used. |
| **No deployment proof** | This runbook covers local development only. No production build, CI/CD pipeline, or HTTPS configuration exists yet. |
| **Role-based section visibility not enforced on frontend** | The backend enforces clinical-role guards (403 for staff on consultations), but the dashboard renders all four sections regardless of role. A `staff` user will see "Could not load consultations…" instead of a hidden section. |

---

## Tear Down

```bash
docker-compose -f docker-compose.postgres.yml down
```

This stops and removes the local PostgreSQL container. The volume data is preserved
unless you add `-v` to also remove it.
