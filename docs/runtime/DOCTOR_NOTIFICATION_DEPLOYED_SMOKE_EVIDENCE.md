# Deployed Doctor Notification Smoke Evidence — PraxisMed Sprint 17 / Module 124

**Date:** 2026-07-05
**Sprint:** Sprint 17 / Module 124
**Status:** PASS — internal clinic notification row created by Vapi appointment capture; no external delivery

---

## 1. Purpose

This document records the real deployed staging evidence that Vapi appointment capture
now creates an internal `clinic_notifications` row linked to the appointment request.

**Accuracy policy:** No step is marked PASS without real evidence from real deployed
Railway PostgreSQL. No evidence is fabricated. No secrets, no real patient data, no
production PHI in this document.

Staging uses fake/non-PHI data only. Production PHI readiness: NO-GO.

---

## 2. Current Result: PASS — Internal Notification Foundation

Internal clinic notification is created by Vapi appointment capture and confirmed
in Railway PostgreSQL.

- Commit deployed: `b74a7ee` — Sprint 17 / Module 123A — Doctor notification creation blocker fix
- Full backend test suite: **2709/2709 passed**
- Railway DB notification count after fake Vapi call: `notification_count=1` — **PASS**

**What is proven:**
- Vapi appointment capture creates a `clinic_notifications` row
- Notification is scoped to the clinic by `clinic_id`
- Notification links to the appointment request via `related_resource_id`
- Notification message includes safe factual context (patient name, reason, suggested action)
- No external delivery (email/SMS/WhatsApp/phone) was attempted
- No diagnosis or medical advice in notification content

**What is not proven:**
- Dashboard notification UI is wired (UI display pending — Module 125)
- Doctor phone notification (future module)
- Email / SMS / WhatsApp delivery (future module)
- Production PHI readiness (NO-GO — C3–C8 hardening blockers open)

---

## 3. Previous Blocker and Root Cause (Module 123A)

**Blocker:** After Module 123 was deployed, `notification_count` remained 0. The
notification insert was being attempted but failing silently.

**Root cause:** asyncpg returns UUID columns as `uuid.UUID` Python objects from
`RETURNING *`. The notification block passed `row.get("id")` (a `uuid.UUID` object)
directly as `related_resource_id` to the `clinic_notifications` INSERT, where the
column type is `TEXT`. asyncpg encodes `uuid.UUID` with the UUID binary OID;
PostgreSQL rejected it for the TEXT column (implicit UUID→TEXT cast not applied in
the binary-protocol parameter context). The exception was silently swallowed by
`except Exception: notification_created = False` with no logging — making it
completely invisible in Railway logs.

**Fix applied in Module 123A (commit `b74a7ee`):**
1. `str(row["id"])` — convert asyncpg `uuid.UUID` to plain `str` before passing
   as `related_resource_id` (TEXT column).
2. `logger.error(...)` — notification failures now logged at ERROR level; no longer
   invisible.
3. `notification_error` — added to the return dict; `None` on success, error string
   on failure; allows observability and testability.

**Why tests passed before the fix:** All Module 123 tests mocked
`create_appointment_request_notification` at the module level — the real asyncpg
INSERT call was never exercised by the test suite.

---

## 4. Deployed Staging Evidence

### 4.1 Commit and test baseline

| Item | Value | Status |
|---|---|---|
| Deployed commit | `b74a7ee` — Sprint 17 / Module 123A | **PASS** |
| Full backend test suite | 2709/2709 passed | **PASS** |

### 4.2 Railway DB notification check

| Item | Value | Status |
|---|---|---|
| notification_count (after fake Vapi call) | 1 | **PASS** |

### 4.3 Notification row fields

| Field | Value |
|---|---|
| id | `5d84860d-0adc-45bb-995b-955e388d46e5` |
| clinic_id | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` |
| channel | `internal` |
| notification_type | `appointment_request` |
| priority | `normal` |
| title | `New appointment request` |
| message | `New appointment request from Doctor Notification Patient. Reason: Routine checkup doctor notification smoke. Action: Review and confirm.` |
| status | `pending` |
| related_resource_type | `appointment_requests` |
| related_resource_id | `a7d25ac1-31a8-4179-904e-6a06617e040f` |
| error_message | `None` |
| raw_payload | `None` |

### 4.4 Dashboard evidence

| Item | Value | Status |
|---|---|---|
| Appointments count | 9 | **PASS** |
| Fake patient visible in dashboard | Doctor Notification Patient | **PASS** |
| Patients count | 6 | **PASS** |
| Dashboard notification UI display | Not proven — notifications section UI wiring pending | **PENDING** |

---

## 5. Safety Constraints

| Constraint | Status |
|---|---|
| Internal notification only — no external delivery | **CONFIRMED** — `channel: internal`; no SMS/push/email/webhook sent |
| No diagnosis in notification content | **CONFIRMED** — message is factual intake summary only |
| No medical advice in notification content | **CONFIRMED** — `suggested_next_action` is a staff workflow prompt, not clinical advice |
| Doctor/staff approval still required | **CONFIRMED** — appointment remains `status=new, action_required=true` |
| No auto-confirmation | **CONFIRMED** — notification does not confirm appointment |
| No real patient data | **CONFIRMED** — fake name "Doctor Notification Patient"; fake reason |
| No password recorded | **CONFIRMED** |
| No token recorded | **CONFIRMED** |
| No cookie value recorded | **CONFIRMED** |
| No DATABASE_URL recorded | **CONFIRMED** |
| No secrets recorded | **CONFIRMED** |
| No real patient data | **CONFIRMED** — fake/non-PHI staging only |
| Fake/non-PHI staging only | **CONFIRMED** |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |

---

## 6. What This Proves

1. Vapi appointment capture creates a `clinic_notifications` row after successful
   appointment request insertion.
2. Notification is scoped by `clinic_id` — tenant isolation holds.
3. Notification links to the appointment request via `related_resource_id`.
4. Notification message includes: patient name, reason, and "Review and confirm" action.
5. No diagnosis or medical advice in notification body.
6. No external delivery channel (internal only).
7. The Module 123A fix (UUID→str conversion + logging) resolved the silent failure.

---

## 7. What This Does Not Prove

- Dashboard notification UI is wired and displays the notification to clinic staff
  (this requires Module 125 — Dashboard Notification and Summary UI Foundation)
- Doctor phone notification via outbound Vapi call (future module)
- Email / SMS / WhatsApp delivery (future module)
- Production PHI readiness (NO-GO — hardening track C3–C8 still open)

---

## 8. Next Steps

- **Module 125** — Dashboard Notification and Summary UI Foundation:
  display internal notifications in the dashboard; display pre-appointment summary
  for appointment request rows; prepare for Fabel 5 premium polish.
- **Sprint 18** — Fabel 5 premium UI/UX polish: transform the functional dashboard
  into a premium, doctor-facing product for demo quality and sales conversion.
- **Production hardening track (parallel):** C3–C8 blockers must be resolved before
  production PHI launch.
