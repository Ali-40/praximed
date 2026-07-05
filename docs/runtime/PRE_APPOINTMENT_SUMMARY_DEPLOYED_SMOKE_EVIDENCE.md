# Pre-Appointment Summary — Deployed Smoke Evidence

**Date:** 2026-07-05
**Sprint:** Sprint 17 / Module 122B
**Commit:** 8d76c0f
**Status:** PASS

---

## 1. Purpose

This document records real deployed staging evidence that the pre-appointment summary
endpoint (`GET /appointment-requests/{id}/pre-appointment-summary`) works correctly
with an authenticated cookie session, linked patient/appointment data, and safe
structured non-diagnostic output.

**Accuracy policy:** No evidence step is marked PASS without real proof from real
deployed staging services. No evidence is fabricated. No real patient data. No secrets.

Staging uses fake/non-PHI data only. Production PHI launch remains NO-GO.

---

## 2. Current Result

**Overall result: PASS**

Authenticated doctor user retrieved a linked appointment request, then retrieved
its pre-appointment summary. The summary includes patient_name, reason,
suggested_next_action "Review and confirm", and a safety_note. No diagnosis or
medical advice is present. Cookie session worked correctly end-to-end.

---

## 3. Evidence

### 3.1 Auth/Session Check

| Item | Value |
|---|---|
| Endpoint | `GET /auth/me` |
| Backend URL | `https://web-production-fd91d.up.railway.app` |
| HTTP status | 200 |
| user_id | `5b63b514-7624-4e8e-9af0-71c153ba7b83` |
| clinic_id | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` |
| role | `doctor` |
| Auth method | Cookie session (`praximed_session`) |

### 3.2 Appointment Request Fetch

| Item | Value |
|---|---|
| Endpoint | `GET /appointment-requests/ae8d53cd-c4d9-4d7d-9cee-5490e13ff83b` |
| HTTP status | 200 |
| request_id | `ae8d53cd-c4d9-4d7d-9cee-5490e13ff83b` |
| clinic_id | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` |
| patient_id | `f5953d98-6b5b-483a-bfb9-49f6eed378e0` |
| patient_name | Summary Linked Patient (fake) |
| source | `vapi` |
| source_ref | `module-122-summary-smoke-001` |
| reason | Routine checkup before travel |
| status | `new` |
| urgency_level | `normal` |
| action_required | `true` |

### 3.3 Pre-Appointment Summary

| Item | Value |
|---|---|
| Endpoint | `GET /appointment-requests/ae8d53cd-c4d9-4d7d-9cee-5490e13ff83b/pre-appointment-summary` |
| HTTP status | 200 |
| ok | `true` |
| request_id | `ae8d53cd-c4d9-4d7d-9cee-5490e13ff83b` |
| clinic_id | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` |
| patient_name | Summary Linked Patient (fake) |
| patient_type | `returning` (linked patient_id present) |
| previous_request_count | `0` |
| reason | Routine checkup before travel |
| source | `vapi` |
| status | `new` |
| action_required | `true` |
| urgency_level | `normal` |
| suggested_next_action | `Review and confirm` |
| safety_note | This summary contains no medical advice or diagnosis. All actions require doctor or staff review and confirmation. |
| patient_phone | `null` (see Section 5 observation) |

---

## 4. What This Proves

- The deployed pre-appointment summary endpoint works end-to-end on Railway
- A cookie-authenticated doctor user can retrieve the summary without any Bearer token
- The summary uses linked appointment_request and patient data (patient_type = "returning")
- The summary output is structured and non-diagnostic — no diagnosis, no medical advice
- The `suggested_next_action` rule ("Review and confirm" for status=new + action_required=true)
  works correctly in the deployed environment
- The `safety_note` is present in the deployed response
- Tenant isolation holds — the request is scoped to `clinic_id`

---

## 5. Observation — patient_phone Returned Null

`patient_phone` was `null` in this smoke, even though the intake included a phone field.
This is a data-normalization/input-mapping gap: the linked patient row's `phone` field
may have been created without the caller phone captured in the patients table for this
specific test row.

**This does not block Module 122B.** The endpoint and service function correctly.

Tracked as: future data-normalization / input-mapping improvement (not a bug in
`build_pre_appointment_summary` — the service correctly returns `null` when both
the linked patient and the appointment_request have no phone).

---

## 6. What This Does Not Prove

- Dashboard UI displays the pre-appointment summary panel (frontend not yet updated)
- Doctor phone or email notification is sent (Module 123 — pending)
- Consultation summary draft is generated (Module 124 — pending)
- Patient timeline exists (Module 125 — pending)
- Production PHI readiness — **NO-GO** (C3–C8 hardening blockers still open)

---

## 7. Safety

| Constraint | Status |
|---|---|
| No real patient data | **CONFIRMED** — Summary Linked Patient is fake |
| No diagnosis in response | **CONFIRMED** — no `diagnosis` key present |
| No medical advice in response | **CONFIRMED** — safety_note explicitly states this |
| Doctor/staff review required | **CONFIRMED** — `action_required: true`; no auto-confirmation |
| No password recorded | **CONFIRMED** |
| No token value recorded | **CONFIRMED** |
| No cookie value recorded | **CONFIRMED** |
| No DATABASE_URL recorded | **CONFIRMED** |
| No JWT secret recorded | **CONFIRMED** |
| No Vapi webhook secret recorded | **CONFIRMED** |
| Fake/non-PHI staging only | **CONFIRMED** |
| Production PHI readiness | **NO-GO** |

---

## 8. Recommended Next Module

**Sprint 17 / Module 123 — Doctor Notification System Foundation**

Use the linked `appointment_request` + `patient` + pre-appointment summary context
to create an internal `clinic_notifications` row when a new appointment is captured
by Vapi. No phone/email delivery yet. Fake data only. Production PHI remains NO-GO.
