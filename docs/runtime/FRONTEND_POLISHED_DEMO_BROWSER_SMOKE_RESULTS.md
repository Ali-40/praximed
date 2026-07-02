# Frontend Polished Demo Browser Smoke Results — PraxisMed Sprint 10 / Module 80

**Date:** 2026-07-02
**Verdict:** PASS

---

## 1. Purpose

This document records evidence that the PraxisMed dashboard runs correctly after the
visual polish changes from Module 79. It confirms that the polished header, section
count pills, badge colours, patient name fix, and local-demo footer all render
correctly in a real browser against the local backend.

This smoke builds on:
- `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` (Module 75 — login/auth/CORS)
- `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (Module 77 — demo seed data)

This document focuses on the post-polish rendering verification only.

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
| 1. Rerun seed | `python backend/scripts/seed_local_data.py` | All 6 rows upserted (idempotent) |
| 2. Restart backend | `uvicorn backend.app.main:app --reload --port 8000` | Backend running |
| 3. Start frontend | `npm run dev` in `frontend/` | Next.js dev server on `http://localhost:3000` |
| 4. Browser login | Opened `http://localhost:3000`, filled login form | Redirect to `/dashboard` |
| 5. Dashboard load | All four sections rendered | List state with polished visual elements |

---

## 4. Evidence

### Header

- Brand name "PraxisMed" visible in top-left.
- "Clinic Dashboard" subtitle visible below brand (Module 79 addition).
- Logout button visible in top-right.

### Page Heading

- "Clinic Overview" heading visible below header (Module 79 — replaced "Welcome to PraxisMed").

### Dashboard Sections — All Four with Count Pills

| Section | Count Pill | Row Content |
|---|---|---|
| Appointments (1) | Visible — shows "1" | "Local Test Patient" — status: new, urgency: normal |
| Patients (1) | Visible — shows "1" | "Local Test Patient" — status: active |
| Notifications (1) | Visible — shows "1" | "Local Test Notification" — priority: normal, type: appointment_request |
| Consultations (1) | Visible — shows "1" | "Local Test Consultation Session" — status: not_ready, source: manual |

### Patient Name Fix

- Patient row displays "Local Test Patient" correctly.
- No longer shows fallback `"—"` (fixed in Module 78; confirmed working after Module 79 polish).

### Status Badge Colours

- Appointments status "new" — blue badge (correct).
- Patients status "active" — green badge (correct).
- Notifications priority "normal" — neutral/grey badge (correct; not urgent/emergency so no red).
- Consultations approval_status "not_ready" — neutral/grey badge (correct; not approved so no green).

### Footer Label

- "Local demo — all data is fake and for development only" visible at bottom of page.

### Logout

- Logout button clicked → token cleared → redirect to `/login`.

---

## 5. What This Proves

| Claim | Status |
|---|---|
| Polished local dashboard demo runs in a real browser | PROVEN |
| Login → JWT → protected API calls → dashboard rendering works end-to-end | PROVEN |
| All four dashboard sections render seeded data in list state | PROVEN |
| Per-section row count pills render correctly | PROVEN |
| Patient name displays as "Local Test Patient" (Module 78 fix confirmed) | PROVEN |
| "Clinic Dashboard" subtitle and "Clinic Overview" heading render correctly | PROVEN |
| Status badges use correct colour coding by value | PROVEN |
| Local-demo footer label is visible | PROVEN |
| Logout clears token and redirects to /login | PROVEN |

---

## 6. What Remains

| Gap | Detail |
|---|---|
| No create / edit flows | Dashboard is read-only; no forms for creating or editing records |
| No appointment workflow actions | Approve / reject / assign buttons not yet built (backend routes exist) |
| No notification action UI | Mark-as-read / dismiss not yet wired on frontend |
| No consultation detail page | No drill-down page for session transcript/summary/review |
| No production auth storage | JWT in `sessionStorage` — httpOnly cookie path not implemented |
| No token refresh | Expired JWT shows generic "Could not load…" error |
| No production deployment | Local-dev only — no production build, HTTPS, or CI/CD |
| Role-based section visibility | All four sections render for all roles |

---

## Module 81 — Confirm Action Added (Sprint 11)

Sprint 11 / Module 81 added a **Confirm** button to appointment request rows with `status === 'new'`.

- Button calls `PATCH /appointment-requests/{id}/status` with `{"status": "confirmed", "action_required": false}`.
- Button disabled and shows "Confirming…" while in-flight.
- On success: appointments list re-fetched; row status updates to "confirmed"; button disappears.
- On failure: generic error message below the appointments list.
- 10 new contract tests added: `backend/tests/test_frontend_appointment_workflow_contract.py`.
- Full backend tests: 1570/1570 passed.

---

## 7. Recommended Next Step

**Architecture Checkpoint 09 — Polished Local Demo Review**

The PraxisMed local demo is now genuinely presentable:
- Professional header with clinic context
- All four sections with data
- Correct patient names
- Consistent badge colours
- Clear local-demo labeling

Before continuing to new features, an architecture checkpoint should review what Sprint 10
has delivered, assess readiness for a real stakeholder demo, and recommend the next sprint
focus — most likely the appointment request workflow UI or the path to production
deployment.
