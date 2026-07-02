# Appointment Workflow Browser Smoke Results — PraxisMed Sprint 11 / Module 82

**Date:** 2026-07-02
**Verdict:** PASS

---

## 1. Purpose

This document records evidence that the appointment request **Confirm** action added in
Module 81 works end-to-end in a real browser against the local backend. It proves that
a clinic staff member can log in, see a pending appointment request, click Confirm, and
have the status update reflected immediately in the dashboard UI without a page reload.

This smoke builds on:
- `docs/runtime/FRONTEND_POLISHED_DEMO_BROWSER_SMOKE_RESULTS.md` (Module 80 — polished demo)
- `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (Module 77 — demo seed data)

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
| Seed data | Deterministic fake data from `backend/scripts/seed_local_data.py` (re-run) |

---

## 3. Steps Completed

| Step | Action | Result |
|---|---|---|
| 1. Rerun seed | `python backend/scripts/seed_local_data.py` | All 6 rows upserted (idempotent); appointment request `55555555-…` at status: new |
| 2. Restart backend | `uvicorn backend.app.main:app --reload --port 8000` | Backend running |
| 3. Start frontend | `npm run dev` in `frontend/` | Next.js dev server on `http://localhost:3000` |
| 4. Browser login | Opened `http://localhost:3000`, filled login form with local-dev credentials | Redirect to `/dashboard` |
| 5. Dashboard load | Appointments section rendered | Row showed "Local Test Patient", status badge "new", Confirm button visible |
| 6. Click Confirm | Clicked Confirm button on appointment row | Button disabled; label changed to "Confirming…" while PATCH request was in flight |
| 7. Observe result | PATCH completed | Row status badge updated from "new" to "confirmed"; Confirm button disappeared |
| 8. Verify stability | Checked other dashboard sections | Patients (1), Notifications (1), Consultations (1) all remained visible and unchanged |
| 9. Check footer/logout | Scrolled to bottom; checked header | Local-demo footer and Logout button both remained visible |

---

## 4. Evidence

### Appointment Row — Before Confirm

| Field | Observed value |
|---|---|
| Patient name | "Local Test Patient" |
| Status badge | "new" (blue) |
| Urgency | "normal" |
| Confirm button | Visible and enabled |

### During Confirm (in-flight)

| Field | Observed value |
|---|---|
| Confirm button | Disabled — label showed "Confirming…" |
| Row | No layout shift; other content stable |

### Appointment Row — After Confirm

| Field | Observed value |
|---|---|
| Status badge | "confirmed" (green) |
| Confirm button | Gone — not rendered for confirmed rows |
| Error message | None — action succeeded without error |

### Other Dashboard Sections (stable throughout)

| Section | Count Pill | Row Content |
|---|---|---|
| Patients (1) | Visible | "Local Test Patient" — status: active |
| Notifications (1) | Visible | "Local Test Notification" — priority: normal, type: appointment_request |
| Consultations (1) | Visible | "Local Test Consultation Session" — status: not_ready, source: manual |

---

## 5. What This Proves

| Claim | Status |
|---|---|
| Frontend Confirm button triggers `PATCH /appointment-requests/{id}/status` with Bearer JWT | PROVEN |
| Backend appointment status update route works from a real browser request | PROVEN |
| Button shows loading/disabled state while PATCH is in flight | PROVEN |
| Appointments list is re-fetched after successful Confirm | PROVEN |
| Row status badge updates from "new" to "confirmed" on success | PROVEN |
| Confirm button disappears from confirmed rows | PROVEN |
| No error message shown on success | PROVEN |
| Other dashboard sections remain stable and unaffected by the action | PROVEN |
| Full local staff workflow loop is viable: login → view request → confirm → status updated | PROVEN |

---

## 6. What This Does Not Prove

| Gap | Detail |
|---|---|
| Real Vapi-created appointment request in dashboard | All requests come from the deterministic local seed script — not from a live Vapi call |
| Full staff scheduling confirmation | No calendar event created; no patient notification sent |
| Calendar event creation | No calendar integration wired on Confirm action |
| Notification side effects | Confirming does not trigger a notification to patient/staff in this local loop |
| Reject / Assign / Callback / Archive actions | Only Confirm is implemented (Module 81); remaining actions are future modules |
| Production auth storage | JWT is in `sessionStorage` — httpOnly cookie path not implemented |
| Token refresh | Expired JWT would show generic error; no auto-redirect yet |
| Production deployment | Local-dev only — no production build, HTTPS, or CI/CD |

---

## 7. Result

**PASS** — The appointment Confirm workflow works end-to-end in a real browser:
- Staff logs in → sees pending appointment request → clicks Confirm → status updates to confirmed → button disappears.
- The local human staff workflow loop is now fully viable for demo purposes.
