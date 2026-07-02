# Frontend Browser Smoke Results — PraxisMed Sprint 9 / Module 75

**Date:** 2026-07-02
**Verdict:** PASS

---

## 1. Purpose

This document records evidence that the PraxisMed frontend runs successfully in a real
browser against the local backend. It proves that the full login → dashboard →
data-load flow works end-to-end under local development conditions.

This is not a production deployment proof. See Section 7 for what this smoke does
not prove.

---

## 2. Environment

| Component | Details |
|---|---|
| PostgreSQL | Local Docker container — `docker-compose.postgres.yml` (port 5433) |
| Backend | `uvicorn backend.app.main:app --reload --port 8000` on `http://127.0.0.1:8000` |
| Frontend | `npm run dev` on `http://localhost:3000` |
| JWT_SECRET_KEY | Local-dev value only — not committed; not used in production |
| CORS | `CORSMiddleware` allows `http://localhost:3000` and `http://127.0.0.1:3000` |
| Tunnel | None — no ngrok or external tunnel required |
| Seed data | Deterministic fake data from `backend/scripts/seed_local_data.py` |

---

## 3. Steps Completed

| Step | Command / Action | Result |
|---|---|---|
| 1. Start PostgreSQL | `docker-compose -f docker-compose.postgres.yml up -d` | Container started |
| 2. Run migrations | `alembic upgrade head` | All migrations applied including `0002_password_hash` |
| 3. Seed data | `python backend/scripts/seed_local_data.py` | Clinic, doctor user, patient, consultation session inserted |
| 4. Start backend | `uvicorn backend.app.main:app --reload --port 8000` with `JWT_SECRET_KEY` set | Backend running on `http://127.0.0.1:8000` |
| 5. Start frontend | `npm run dev` in `frontend/` | Next.js dev server on `http://localhost:3000` |
| 6. Browser login | Opened `http://localhost:3000`, filled login form | Redirect to `/dashboard` |
| 7. Dashboard load | All four sections rendered | Appointments, Patients, Notifications, Consultations loaded |
| 8. Logout | Clicked Logout button | Redirect to `/login` |

---

## 4. Evidence

### curl — Backend Auth Works
```
curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor.local@praximed.test","password":"local-dev-password","clinic_id":"11111111-1111-1111-1111-111111111111"}'

→ HTTP 200
→ {"access_token": "<jwt>", "token_type": "bearer", ...}
```

### Browser Login
- URL: `http://localhost:3000/login`
- Credentials: Clinic ID `11111111-1111-1111-1111-111111111111`, Email `doctor.local@praximed.test`, Password `local-dev-password`
- Result: Redirect to `http://localhost:3000/dashboard` — login succeeded

### Dashboard Sections
All four sections rendered after successful login:

| Section | Observed State |
|---|---|
| Appointments | Section visible; loading → empty (no appointment requests in seed data) |
| Patients | Section visible; loading → "Local Test Patient" (seeded) |
| Notifications | Section visible; loading → empty (no notifications in seed data) |
| Consultations | Section visible; loading → "Local Test Consultation Session" (seeded) |

### CORS Preflight
- `OPTIONS /auth/login` with `Origin: http://localhost:3000` → HTTP 200
- `Access-Control-Allow-Origin: http://localhost:3000` present in response
- Browser preflight no longer returns 405

### Logout
- Logout button clicked → `praximed_access_token` removed from `sessionStorage`
- Redirect to `/login` confirmed
- Pressing back and navigating to `/dashboard` redirected back to `/login` (auth guard active)

---

## 5. Previous Blockers Fixed

| Module | Blocker | Fix |
|---|---|---|
| 73 | `alembic_version VARCHAR(32)` overflow — revision ID was 42 chars | `revision = "0002_password_hash"` (16 chars) |
| 73 | `ModuleNotFoundError: No module named 'backend'` from seed script | `_PROJECT_ROOT` sys.path insertion added |
| 73 | `[Errno 48] Address already in use` — no guidance in runbook | Kill command + restart instructions added to runbook |
| 74 | `OPTIONS /auth/login → 405` — browser preflight rejected | `CORSMiddleware` added to `backend/app/main.py` |

---

## 6. What This Proves

| Claim | Status |
|---|---|
| Local full-stack login works in a real browser | PROVEN |
| JWT auth works end-to-end (form → backend → JWT → sessionStorage) | PROVEN |
| Dashboard can call protected backend APIs with Bearer token | PROVEN |
| All four dashboard sections (Appointments, Patients, Notifications, Consultations) render | PROVEN |
| CORS preflight from `http://localhost:3000` passes | PROVEN |
| Logout clears token and auth guard redirects unauthenticated users | PROVEN |
| Seed script creates a login-capable local user | PROVEN |
| Migrations run cleanly including `0002_password_hash` | PROVEN |

---

## 7. What This Does Not Prove

| Gap | Detail |
|---|---|
| Production deployment | No production build, CI/CD, or HTTPS tested |
| Production auth storage | JWT is in `sessionStorage` — httpOnly cookie path not implemented |
| Token refresh | Expired JWT shows a generic error rather than redirecting to login |
| Logout / revocation | `clearToken` removes the local token but does not invalidate it on the backend |
| Polished UI | Minimal inline styles; no mobile viewport or accessibility testing |
| Create / edit flows | Dashboard is read-only; no forms for creating or editing records |
| Real patient data | All data is deterministic fake seed data |
| Role-based section visibility | All four sections render for all roles; backend 403s show as generic errors |

---

## 8. Future Language Note

The current MVP targets **German (de-AT)** and **English (en)** only. Clinic
communications, assistant prompts, and UI copy should be kept in these two languages
for now.

The architecture supports future language expansion through clinic-level and
assistant-level configuration (e.g. a `locale` field on the `clinics` table already
exists). When the product grows to serve additional communities, the following languages
may be prioritised:

- Arabic (ar) — large patient community in Austria
- Turkish (tr)
- French (fr)
- Italian (it)
- Spanish (es)
- Balkan languages (e.g. Bosnian/Croatian/Serbian)

**Do not build multilingual expansion yet.** This note is for roadmap awareness only.
When multilingual support is ready to implement, it should be a dedicated sprint with
proper locale infrastructure, translation tooling, and content review.

---

## 9. Module 76 — Demo Data Added (seed polish)

**Sprint 9 / Module 76 — Dashboard Empty-State and Local Demo Data Polish**

The Appointments and Notifications sections showed empty state during the Module 75 smoke.
Module 76 adds two deterministic fake rows to `seed_local_data.py`:

| New row | Table | ID |
|---|---|---|
| Fake appointment request | `appointment_requests` | `55555555-5555-5555-5555-555555555555` |
| Fake notification | `clinic_notifications` | `66666666-6666-6666-6666-666666666666` |

After re-running `python backend/scripts/seed_local_data.py` all four dashboard
sections should render list state (not empty state).

See `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` for updated runbook notes.
