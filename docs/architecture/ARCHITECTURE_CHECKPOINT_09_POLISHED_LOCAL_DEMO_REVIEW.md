# Architecture Checkpoint 09 — Polished Local Demo Review

**Date:** 2026-07-02
**Sprint:** Sprint 10 complete (Modules 78–80)
**Backend tests:** 1560/1560 passed
**Status:** Local demo polished and confirmed — workflow feature sprint ready

---

## 1. Current Status

Sprint 10 resolved the two remaining demo-credibility gaps identified in Architecture
Checkpoint 08: the patient name display fallback (`"—"`) and the overall visual
presentation. The local demo now looks professional and is presentable to a stakeholder.
This checkpoint reviews what Sprint 10 delivered, the current demo state, and what to
build next.

---

## 2. Sprint 10 Work Completed

| Module | Description | Outcome |
|---|---|---|
| 78 | Patient display fix — `full_name` added to `Patient` TypeScript interface | Patient row shows "Local Test Patient" instead of `"—"` |
| 79 | Dashboard visual polish — header subtitle, count pills, badge tokens, footer | "Clinic Dashboard" header, "Clinic Overview" heading, polished badges, demo label |
| 80 | Polished demo browser smoke | All changes confirmed in real browser; verdict PASS |

**Tests added in Sprint 10:** 13 new contract tests (3 patient list + 10 visual polish); 1560 total.

**Key changes delivered:**
- `frontend/lib/api.ts` — `full_name: string | null` added to `Patient` interface
- `frontend/app/dashboard/page.tsx` — patient display expression uses `full_name`; `BADGE_STYLES` map; `CountPill` component; "Clinic Overview" heading; "Clinic Dashboard" header subtitle; local-demo footer
- `frontend/app/globals.css` — badge colour CSS tokens (`--badge-blue-*`, `--badge-green-*`, `--badge-red-*`, `--badge-neutral-*`)

---

## 3. What Is Now Demo-Ready

| Feature | Status | Notes |
|---|---|---|
| Login form | DEMO READY | Clinic ID + email + password; generic error on failure |
| JWT auth (login → backend → token → sessionStorage) | DEMO READY | Full end-to-end confirmed in browser |
| CORS (frontend → backend in browser) | DEMO READY | `CORSMiddleware` with explicit allowed origins |
| Auth guard (unauthenticated → /login) | DEMO READY | Confirmed via back-button test after logout |
| Logout | DEMO READY | Clears sessionStorage token; redirects to /login |
| Dashboard — "Clinic Overview" heading | DEMO READY | Module 79 |
| Dashboard — "Clinic Dashboard" header subtitle | DEMO READY | Module 79 |
| Appointments section (live) | DEMO READY | "Local Test Patient", status: new, count pill: 1 |
| Patients section (live, name fixed) | DEMO READY | "Local Test Patient", status: active, count pill: 1 |
| Notifications section (live) | DEMO READY | "Local Test Notification", priority: normal, count pill: 1 |
| Consultations section (live) | DEMO READY | "Local Test Consultation Session", count pill: 1 |
| Status badge colours | DEMO READY | Blue/green/red/neutral by value via CSS token variables |
| Local-demo footer label | DEMO READY | "Local demo — all data is fake and for development only" |
| Seed script (idempotent, 6 rows) | DEMO READY | clinic, user, patient, consultation, appointment request, notification |

---

## 3b. Sprint 11 Follow-Up (Modules 81–82)

Sprint 11 partially addressed the highest-priority gap identified in this checkpoint.

| Module | Description | Outcome |
|---|---|---|
| 81 | Appointment Confirm action — `confirmAppointmentRequest` helper + Confirm button on `status === 'new'` rows | Frontend can now mutate appointment request status via PATCH; 10 contract tests; 1570/1570 |
| 82 | Appointment workflow browser smoke | End-to-end Confirm flow confirmed in real browser: new → confirmed; button disappears; dashboard stable |

**Remaining appointment workflow gap:** Reject, Assign, Callback, and Archive actions are not yet built.
**Next integration target:** Prove a real or simulated Vapi appointment capture creates a dashboard-reviewable
request without the manual seed script — closing the AI intake → staff action loop.
See `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` for the full integration prep plan.

---

## 4. What Is Still Missing

### 4.1 Appointment Request Workflow Actions

**Partially resolved in Sprint 11 (Modules 81–82).**

The Confirm action (`PATCH /appointment-requests/{id}/status` with `status: "confirmed"`)
is now wired in the frontend dashboard and browser-smoke confirmed. The remaining
actions are not yet built:

- `PATCH /appointment-requests/{id}/status` with `status: "rejected"` — **not yet built**
- `PATCH /appointment-requests/{id}/assign` — assign to a user — **not yet built**
- `POST /appointment-requests/{id}/callback-needed` — flag for callback — **not yet built**
- `POST /appointment-requests/{id}/archive` — archive — **not yet built**

**Priority:** Medium for Reject (next most common staff action); lower for Assign/Archive.

### 4.2 Patient Detail Page

No drill-down exists for a patient record. Clicking a patient row does nothing. There
is no `/patients/[id]` page showing contact details, linked consultations, or history.

**Priority:** Medium — useful for demo depth but not the primary workflow.

### 4.3 Consultation Detail Page

No drill-down exists for a consultation session. The list row shows title, approval
status, and source — but there is no page showing transcript, AI summary draft, or
doctor approval/rejection controls.

**Priority:** Medium — important for the doctor documentation assistant use case but
not the first workflow to build.

### 4.4 Notification Action UI

Notifications are listed (title, priority, type) but there is no way to mark one as
read or dismiss it. The backend `POST /notifications/{id}/read` route exists.

**Priority:** Low for initial demo.

### 4.5 No Create / Edit Flows

The dashboard is entirely read-only. No forms exist for creating or editing records
on any table. All data comes from the deterministic local seed.

**Priority:** Medium — needed before a full demo of the intake workflow.

### 4.6 No Production Auth Storage

JWT tokens are stored in `sessionStorage`. Explicitly marked local-dev only throughout
the codebase. The httpOnly cookie path (`POST /auth/session` backend endpoint) is not
yet built.

**Priority:** High before any real users touch the system.

### 4.7 No Token Refresh

When the JWT expires, all four sections show generic "Could not load…" errors. There
is no automatic redirect to `/login`. Workaround: re-login before a demo session.

**Priority:** Medium.

### 4.8 No Production Deployment

No production build, HTTPS, CI/CD pipeline, or hosting configuration exists. This
remains a local-dev-only stack.

**Priority:** Future sprint.

---

## 5. Security Status

| Concern | Status |
|---|---|
| JWT backend auth end-to-end | ACTIVE — `POST /auth/login` issues JWT; all PHI routes require Bearer token |
| Password storage | SAFE — bcrypt hash; plaintext never stored or logged |
| Local-dev credentials | SAFE — fake values only; not committed; clearly labeled fake/local |
| CORS | SAFE — explicit allowed origins; no wildcard; `FRONTEND_CORS_ORIGINS` env override |
| Tenant separation | ENFORCED — all PHI routes check `clinic_id` from JWT |
| Real patient data | NONE — all seed data is deterministic fake/local only |
| sessionStorage auth | LOCAL-DEV ONLY — flagged in code, docs, and visible in the UI footer |
| No hardcoded secrets | CONFIRMED — no tokens, keys, or passwords in committed code |
| Audit logging | ACTIVE — PHI mutations logged via `audit_logger` on all protected routes |

No security regressions in Sprint 10.

---

## 6. Recommended Next Sprint Options

### Option A — Appointment Request Workflow UI (recommended)
Add action buttons (Confirm / Reject / Flag for callback) to the appointment request
rows on the dashboard. The backend routes exist (Modules 17 + 64); this is a pure
frontend task. The backend already enforces auth and tenant guards on these routes.

**Why prioritise:** Appointment requests are the direct output of the Vapi AI phone
receptionist — the primary product use case. Clinic staff currently have no way to
action a captured request from the dashboard. This is the most impactful next step
for product credibility.

### Option B — Patient Detail UI
Add a `/patients/[id]` page with contact details and linked consultations.

**Why prioritise:** Deepens the demo but requires a new page scaffold and additional
API calls. Less urgent than the appointment workflow for the Vapi use case.

### Option C — Consultation Detail UI
Add a `/consultations/[id]` page with transcript, AI summary draft, and
approve/reject controls.

**Why prioritise:** Important for the doctor documentation assistant use case (Sprint 2
backend work) but requires a complex multi-step UI. Better tackled after the simpler
appointment workflow.

### Option D — Deployment Preparation
Switch JWT storage to httpOnly cookies, add `POST /auth/session`, and create a
production build configuration.

**Why prioritise:** Required before real users. Not needed for local demo expansion.

---

## 7. Recommendation

**Sprint 11 / Module 81 — Appointment Request Workflow UI Foundation**

Build the first appointment request action on the dashboard: a **Confirm** button on
each appointment request row that calls `PATCH /appointment-requests/{id}/status` with
`status: "confirmed"`. Keep scope small — one action per row, one API call, one status
badge update. No modal or form required for the first iteration.

**Rationale:** Appointment requests are the core Vapi business flow. After Vapi captures
a patient's appointment request by phone, clinic staff must review and confirm or reject
it. Without action buttons, the dashboard is read-only — impressive visually but not
useful as a working tool. Adding the Confirm action makes the demo interactive and
demonstrates the full loop: AI captures → staff actions → status updated.

The backend already enforces auth, tenant checks, and audit logging for this route.
The frontend only needs to wire the UI.

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
| Sprint 10 | Dashboard demo polish | 78–80 | 1560 |
