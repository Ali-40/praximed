# Deployed Dashboard Notification and Summary UI Smoke Evidence — PraxisMed Sprint 17 / Module 125B

**Date:** 2026-07-05
**Sprint:** Sprint 17 / Module 125B
**Status:** PASS — deployed dashboard summary UI working; View summary / Hide summary confirmed; Confirm flow compatible

---

## 1. Purpose

This document records the real deployed browser evidence that the PraxisMed dashboard
UI exposes pre-appointment summaries (Module 125) and keeps the existing appointment
list and Confirm flow working after the deployment of commit `ab08b7a`.

**Accuracy policy:** No step is marked PASS without real evidence from real deployed
Vercel. No evidence is fabricated. No secrets, no real patient data, no production PHI
in this document.

Staging uses fake/non-PHI data only. Production PHI readiness: NO-GO.

---

## 2. Current Result: PASS — Deployed Dashboard Summary UI

Pre-appointment summary UI is confirmed working on the deployed Vercel dashboard.

- Commit deployed: `ab08b7a` — Sprint 17 / Module 125 — Dashboard notification and summary UI foundation
- Full backend test suite: **2754/2754 passed**
- Frontend URL: `https://praximed.vercel.app`
- Dashboard URL: `https://praximed.vercel.app/dashboard`
- Vercel production deployment status: **Ready**

**What is proven:**
- Dashboard loads while logged in
- Appointments count visible in Appointments section
- Fake appointment rows visible (e.g. Doctor Notification Patient)
- "View summary" button visible on each appointment row
- Clicking "View summary" opens an inline summary panel
- "Hide summary" button visible after panel opens
- Summary panel shows all required safe structured fields
- Safety note visible and complete
- Confirm button remains visible and compatible for unconfirmed rows
- Confirmed status badges remain visible for previously confirmed rows
- Existing appointment list and patient sections remain usable

**What is not proven:**
- Notification section UI display — internal notification DB foundation was proven in Module 124;
  notification list display in dashboard UI is not separately verified in this browser smoke session
- Fabel 5 premium UI/UX polish (Sprint 18)
- External phone/email/SMS/WhatsApp notification delivery (future module)
- Production PHI readiness (NO-GO — C3–C8 hardening blockers open)

---

## 3. Deployed Staging Evidence

### 3.1 Vercel deployment

| Item | Value | Status |
|---|---|---|
| Vercel production deployment status | Ready | **PASS** |
| Deployed commit | `ab08b7a` — Sprint 17 / Module 125 | **PASS** |
| Frontend URL | `https://praximed.vercel.app` | **PASS** |
| Dashboard URL | `https://praximed.vercel.app/dashboard` | **PASS** |
| Full backend test suite | 2754/2754 passed | **PASS** |

### 3.2 Dashboard loads

| Item | Value | Status |
|---|---|---|
| Dashboard loads while logged in | Confirmed | **PASS** |
| Appointments count visible | 9 | **PASS** |
| Doctor Notification Patient rows visible | Confirmed | **PASS** |

### 3.3 View summary / summary panel

| Item | Value | Status |
|---|---|---|
| "View summary" button visible on appointment rows | Confirmed | **PASS** |
| Clicking "View summary" opens inline summary panel | Confirmed | **PASS** |
| "Hide summary" button visible after panel opens | Confirmed | **PASS** |
| Summary panel: Patient field visible | Confirmed | **PASS** |
| Summary panel: Type field visible | Confirmed | **PASS** |
| Summary panel: Reason field visible | Confirmed | **PASS** |
| Summary panel: Urgency field visible | Confirmed | **PASS** |
| Summary panel: Prior visits field visible | Confirmed | **PASS** |
| Summary panel: Suggested action field visible | Confirmed | **PASS** |
| Summary panel: Safety note visible | Confirmed | **PASS** |

### 3.4 Safety note text

> "This summary contains no medical advice or diagnosis. All actions require doctor or staff review and confirmation."

### 3.5 Confirm flow compatibility

| Item | Value | Status |
|---|---|---|
| Confirm button remains visible for unconfirmed rows | Confirmed | **PASS** |
| Confirmed status badges visible for previously confirmed rows | Confirmed | **PASS** |
| Existing appointment list and patient sections remain usable | Confirmed | **PASS** |

---

## 4. Safety Constraints

| Constraint | Status |
|---|---|
| No diagnosis in summary panel | **CONFIRMED** — summary shows structured factual fields only |
| No medical advice in summary panel | **CONFIRMED** — suggested_next_action is a staff workflow prompt, not clinical advice |
| Safety note visible | **CONFIRMED** — text requires doctor/staff review and confirmation |
| Doctor/staff review required | **CONFIRMED** — Confirm action requires explicit staff interaction |
| No auto-confirmation | **CONFIRMED** — summary panel is read-only; Confirm button remains staff-initiated |
| No real patient data | **CONFIRMED** — fake/non-PHI staging data only (e.g. "Doctor Notification Patient") |
| No password recorded | **CONFIRMED** |
| No token recorded | **CONFIRMED** |
| No cookie value recorded | **CONFIRMED** |
| No DATABASE_URL recorded | **CONFIRMED** |
| No JWT/webhook/Vapi secrets recorded | **CONFIRMED** |
| No secrets recorded | **CONFIRMED** |
| Fake/non-PHI staging only | **CONFIRMED** |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |

---

## 5. What This Proves

1. The deployed Vercel dashboard fetches and displays the pre-appointment summary for
   each appointment row via `GET /appointment-requests/{id}/pre-appointment-summary`.
2. The summary panel opens and closes inline — "View summary" / "Hide summary" toggle works.
3. All required safe structured fields are visible: Patient, Type, Reason, Urgency, Prior
   visits, Suggested action, Safety note.
4. The safety note is visible and clearly states no medical advice or diagnosis is present.
5. The Confirm button remains functional and compatible — staff must still click Confirm
   to update appointment status; no auto-confirmation.
6. Confirmed status badges remain visible for previously confirmed rows.
7. The existing appointment list and patient sections remain usable after Module 125.

---

## 6. What This Does Not Prove

- Notification section UI display (internal notification DB was proven in Module 124;
  the notification list in the dashboard UI was not separately verified in this browser
  smoke session — marked as partially pending)
- Fabel 5 premium UI/UX polish (Sprint 18 — Module 126)
- External phone/email/SMS/WhatsApp notification delivery (future module)
- Production PHI readiness (NO-GO — C3–C8 hardening blockers still open)

---

## 7. Next Steps

- **Sprint 18 / Module 126** — Fabel 5 Premium Dashboard UI/UX Polish:
  transform the functional dashboard into a premium, doctor-facing product for demo
  quality and sales conversion.
- **Production hardening track (parallel):** C3–C8 blockers must be resolved before
  production PHI launch.
