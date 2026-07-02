# Architecture Checkpoint 08 — Local Demo Readiness Review

**Date:** 2026-07-02
**Sprint:** Sprint 9 complete (Modules 72–77)
**Backend tests:** 1547/1547 passed
**Status:** Local demo viable — readiness review complete

---

## 1. Current Status

Sprint 9 brought the PraxisMed frontend from zero browser-level validation to a fully
functional local demo. A real browser can now sign in, view all four dashboard sections
with realistic (but entirely fake) data, and sign out. The full login → data → logout
flow is proven end-to-end.

This checkpoint reviews what is demo-ready, what is still rough, and what the next
sprint should focus on.

---

## 2. Sprint 9 Work Completed

| Module | Description | Outcome |
|---|---|---|
| 72 | Seed script updated with bcrypt login user; 9-step smoke runbook created | Local login credentials created; runbook written |
| 73 | Three runtime blockers fixed | Alembic revision ID, seed sys.path, port-conflict docs resolved |
| 74 | `CORSMiddleware` added to FastAPI | Browser preflight `OPTIONS /auth/login → 200`; browser login unblocked |
| 75 | Full browser smoke executed | login → dashboard → logout confirmed PASS in real browser |
| 76 | Demo seed data added (appointment request + notification) | All four sections show list state after re-seed |
| 77 | Demo data browser smoke re-executed | All four sections confirmed list state in real browser; minor UI issue noted |

**Tests added in Sprint 9:** 12 new contract tests (4 migration + 8 seed); 1547 total.

---

## 3. What Is Now Locally Demo-Ready

| Feature | Status | Notes |
|---|---|---|
| Login form | DEMO READY | Clinic ID + email + password; generic error on failure |
| JWT auth (login → backend → token → sessionStorage) | DEMO READY | Full end-to-end confirmed in browser |
| CORS (frontend → backend in browser) | DEMO READY | `CORSMiddleware` with explicit allowed origins |
| Auth guard (unauthenticated access → /login) | DEMO READY | Confirmed via back-button test after logout |
| Logout | DEMO READY | Clears sessionStorage token; redirects to /login |
| Dashboard page | DEMO READY | Four sections with loading → list state transition |
| Appointments section | DEMO READY | Shows "Local Test Patient", status: new, urgency: normal |
| Patients section | DEMO READY (with caveat) | Row visible; name displays as `"—"` (see §4) |
| Notifications section | DEMO READY | Shows "Local Test Notification", priority: normal |
| Consultations section | DEMO READY | Shows "Local Test Consultation Session", source: manual |
| Seed script | DEMO READY | Idempotent; creates 6 deterministic fake/local rows |
| No ngrok needed | DEMO READY | Full demo runs locally without external tunnel |

---

## 4. What Is Still Not Demo-Polished

### 4.1 Patient Name Display ~~(known issue from Module 77)~~ — Fixed in Module 78

~~The Patients section renders patient rows with `"—"` for the name.~~ **Resolved in
Sprint 10 / Module 78.** `full_name` was added to the `Patient` TypeScript interface in
`frontend/lib/api.ts`, and the display expression in `dashboard/page.tsx` was updated to
use `patient.full_name` first, falling back to `first_name + last_name`, then to
`'Unnamed patient'`. The patient row now displays "Local Test Patient" after re-seeding.

### 4.2 No Create / Edit Flows

The dashboard is entirely read-only. There are no forms for:
- Booking or editing an appointment request
- Adding or editing a patient record
- Creating a consultation session

**Priority:** Medium — a demo can work without this if framed as "intake view only",
but it limits what can be shown.

### 4.3 No Appointment Request Workflow Actions

The appointment request row shows status/urgency badges, but there are no UI controls
to approve, reject, assign, or flag a request for callback. The backend routes for all
these actions already exist (Module 17 + 64) — the frontend just does not expose them.

**Priority:** Medium — important for demonstrating the clinic staff workflow.

### 4.4 No Notification Action UI

Notifications are listed (title, priority, type) but there is no way to mark one as
read or dismiss it from the dashboard. The backend `POST /notifications/{id}/read` route
exists — the frontend does not wire it up.

**Priority:** Low for initial demo; medium for a staff-facing demo.

### 4.5 No Consultation Detail Page

The consultations section shows a list row with title, approval status, and source.
There is no detail view for a session — no transcript, no summary, no approve/reject
workflow. The backend clinical workflow routes exist (Modules 29, 35, 62-63) but no
frontend detail page exists.

**Priority:** Low for initial demo.

### 4.6 No Production Auth Storage

JWT tokens are stored in `sessionStorage`. This is explicitly marked local-dev only
throughout the codebase. For production, tokens must be stored in httpOnly cookies set
by a backend `/auth/session` endpoint (not yet built). See `frontend/lib/auth.ts`.

**Priority:** High before any production deployment.

### 4.7 No Token Refresh

When the JWT expires the frontend shows a generic "Could not load…" error in each
section. There is no automatic redirect to `/login` or a refresh flow. Depending on
`ACCESS_TOKEN_EXPIRE_MINUTES`, this could interrupt a demo if the session runs long.

**Priority:** Medium — workaround is to re-login before a demo.

### 4.8 No Production Deployment

No production build, HTTPS, CI/CD pipeline, or hosting configuration exists. This is
a local-dev-only stack. Frontend runs on `npm run dev` and backend on `uvicorn --reload`.

**Priority:** Not needed now; addressed in a future sprint.

---

## 5. Security Status

| Concern | Status |
|---|---|
| JWT backend auth end-to-end | IMPLEMENTED — `POST /auth/login` issues JWT; all PHI routes require Bearer token |
| Password storage | SAFE — bcrypt hash via `hash_password()`; plaintext never stored or logged |
| Local-dev credentials | SAFE — fake credentials only; never committed; clearly labeled fake/local |
| CORS | SAFE — explicit allowed origins only; no wildcard; `FRONTEND_CORS_ORIGINS` env override |
| Tenant separation | ENFORCED — all PHI routes check `clinic_id` from JWT; `require_staff_clinic_access` active |
| Real patient data | NONE — all seed data is deterministic fake/local only |
| sessionStorage auth | LOCAL-DEV ONLY — explicitly flagged in code and docs; httpOnly cookie path not built |
| No hardcoded secrets | CONFIRMED — no tokens, keys, or passwords in committed code |
| Audit logging | ACTIVE — PHI mutations logged via `audit_logger` on all protected routes |

---

## 6. Recommended Next Sprint Options

### Option A — Demo UI Polish (recommended)
Fix the patient name display issue and polish the dashboard so it looks credible in
a live demo. Minimum scope: map `full_name` into the patient row display expression.
Optional: improve badge styling, add row counts, add section headings with counts.

**Why prioritise:** Any stakeholder demo will immediately notice the `"—"` name
fallback. Fixing it is small, high-impact, and unblocks demo credibility.

### Option B — Appointment Workflow UI
Add approve / reject / assign UI controls to the appointment request rows on the
dashboard. The backend routes exist; this is a pure frontend task.

**Why prioritise:** Demonstrates the core clinic staff workflow — the primary use case
for the PraxisMed product.

### Option C — Patient Detail UI
Add a patient detail page (`/patients/[id]`) showing full patient record and linked
consultation sessions.

**Why prioritise:** Useful for a demo but requires more frontend scaffolding than
Option A or B.

### Option D — Deployment Preparation
Switch JWT storage to httpOnly cookies, add `POST /auth/session`, and create a
production build config.

**Why prioritise:** Not needed for local demo but required before any real users touch
the system.

---

## 7. Recommendation

**Sprint 10 / Module 78 — Dashboard Demo Polish and Patient Display Fix**

Before adding new workflows, fix the visible patient name fallback and polish the
current demo dashboard so it looks credible in front of a stakeholder.

**Rationale:** The patient `"—"` issue is the most visible defect in the current demo.
It is small to fix (a single display expression change), high-impact (immediately
visible in any demo), and a prerequisite for framing the dashboard as clinic-ready.
Fixing it first keeps the next demo-path module small and delivers tangible
demo-readiness improvement before expanding to new workflows.

Scope for Module 78:
- Fix patient row name display: use `full_name` from the backend response.
- Add a `full_name` field to the `Patient` TypeScript interface in `frontend/lib/api.ts`.
- Update the patient list render expression in `frontend/app/dashboard/page.tsx`.
- Add static contract tests confirming `full_name` is used in the patient row.
- Manual browser verification: patient row shows "Local Test Patient".
- No backend changes required.

---

## 8. Sprint Summary

| Sprint | Scope | Modules | Tests at End |
|---|---|---|---|
| Sprint 1 | Backend API foundation | 1–23 | 545 |
| Sprint 2 | Clinical documentation engine | 24–34 | 908 |
| Sprint 3 | Clinical workflow API routes + access control | 35–40 | 1083 |
| Sprint 4 | Database migration + audit logging | 41–44 | 1193 |
| Sprint 5 | Local PostgreSQL + smoke test | 45–51 | 1312 |
| Sprint 6 | External integration compatibility | 52–58 | 1386 |
| Sprint 7 | Production auth and JWT wiring | 59–65 | 1461 |
| Sprint 8 | Frontend dashboard foundation | 66–71 | 1521 |
| Sprint 9 | Local runtime smoke, CORS, browser demo | 72–77 | 1547 |
