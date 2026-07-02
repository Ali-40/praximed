# Frontend Demo Data Browser Smoke Results — PraxisMed Sprint 9 / Module 77

**Date:** 2026-07-02
**Verdict:** PASS

---

## 1. Purpose

This document records evidence that the PraxisMed dashboard renders **list state in all
four sections** after the Module 76 demo seed data was added. It proves that the full
login → dashboard → all-four-sections-populated → logout flow works with the updated
seed script.

This complements `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` (Module 75), which
proved the login/auth/CORS layer. This smoke focuses specifically on the demo data path:
does re-running `seed_local_data.py` produce visible list rows in every dashboard section?

This is not a production deployment proof. See Section 7 for what this smoke does not prove.

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
| Seed data | Deterministic fake data from `backend/scripts/seed_local_data.py` (re-run after Module 76) |

---

## 3. Steps Completed

| Step | Command / Action | Result |
|---|---|---|
| 1. Rerun seed script | `python backend/scripts/seed_local_data.py` | All 6 rows upserted: clinic, user, patient, consultation, appointment request, notification |
| 2. Browser login | Opened `http://localhost:3000`, filled login form with local-dev credentials | Redirect to `/dashboard` |
| 3. Dashboard load | All four sections rendered | Appointments, Patients, Notifications, Consultations showed list state |
| 4. Logout | Clicked Logout button | Redirect to `/login` |

---

## 4. Evidence

### Seed Script Output

```
Seeding local test data...
Local seed data inserted successfully (fake/local only — not production data):
  clinic_id:                11111111-1111-1111-1111-111111111111
  doctor_user_id:           22222222-2222-2222-2222-222222222222
  patient_id:               33333333-3333-3333-3333-333333333333
  consultation_session_id:  44444444-4444-4444-4444-444444444444
  appointment_request_id:   55555555-5555-5555-5555-555555555555
  notification_id:          66666666-6666-6666-6666-666666666666

LOCAL-DEV LOGIN (fake/local only — NOT for production):
  clinic_id: 11111111-1111-1111-1111-111111111111
  email:     doctor.local@praximed.test
  password:  local-dev-password
```

### Dashboard Sections — All Four in List State

| Section | Observed State |
|---|---|
| Appointments | List state — "Local Test Patient", status: new, urgency: normal |
| Patients | List state — patient row visible, status: active (see known issue §6 for display note) |
| Notifications | List state — "Local Test Notification", priority: normal, type: appointment_request |
| Consultations | List state — "Local Test Consultation Session", status: not_ready, source: manual |

### Logout

- Logout button visible in dashboard header.
- Logout button clicked → `praximed_access_token` removed from `sessionStorage`.
- Redirect to `/login` confirmed.

---

## 5. What This Proves

| Claim | Status |
|---|---|
| Seed script inserts deterministic appointment request and notification | PROVEN |
| Appointments section renders list state after re-seeding | PROVEN |
| Patients section renders list state (seeded since Module 72) | PROVEN |
| Notifications section renders list state after re-seeding | PROVEN |
| Consultations section renders list state (seeded since Module 72) | PROVEN |
| Local full-stack demo is viable for all four dashboard sections | PROVEN |
| Frontend can render protected API data from all four API endpoints | PROVEN |
| Logout button visible and functional | PROVEN |

---

## 6. Known Minor UI Issue

The **Patients** section patient row displays the fallback `"—"` instead of the patient
full name. The dashboard renders `first_name + last_name` separately (from the
`Patient` TypeScript interface), but the backend returns `full_name` as a single field.
The patient data loads correctly — the section is in list state and the status badge
is visible — but the name display falls back to `"—"`.

**Severity:** Minor cosmetic / display issue. Does not block local demo flow.

**Resolution:** Acceptable for this smoke. The fix (mapping `full_name` to display name
in the frontend) is a UI polish task for a future module.

---

## 7. What This Does Not Prove

| Gap | Detail |
|---|---|
| Production deployment | No production build, CI/CD, or HTTPS tested |
| Production auth storage | JWT is in `sessionStorage` — httpOnly cookie path not implemented |
| Token refresh | Expired JWT shows a generic error rather than redirecting to login |
| Patient name display | `full_name` not split into `first_name`/`last_name` — row shows `"—"` |
| Create / edit flows | Dashboard is read-only; no forms for creating or editing records |
| Real patient data | All data is deterministic fake seed data |
| Role-based section visibility | All four sections render for all roles; backend 403s show as generic errors |
| Clinic-ready UI polish | Minimal inline styles; no mobile viewport or accessibility testing |

---

## 8. Recommended Next Step

**Architecture Checkpoint 08 — Local Demo Readiness Review**

The local full-stack demo is now end-to-end viable: login, all four dashboard sections
with realistic (but fake) data, and logout all work in a real browser. Before continuing
to production-readiness work, an architecture checkpoint should document what Sprint 9
has proven, what gaps remain, and recommend the next sprint focus.

Scope for Architecture Checkpoint 08:
- Review Modules 72–77 (Sprint 9: local runtime smoke, CORS fix, browser smoke, demo
  data, demo re-smoke).
- Document current state: what the local demo proves and does not prove.
- Identify the highest-priority gaps (e.g. patient name display, token refresh, httpOnly
  cookies, role-based section visibility, production build).
- Recommend Sprint 10 focus.
