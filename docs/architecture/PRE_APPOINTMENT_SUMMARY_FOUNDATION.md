# Pre-Appointment Summary Foundation — Sprint 17 / Module 122

Status: IMPLEMENTED — fake-data staging only. Production PHI: NO-GO.

---

## 1. Purpose

Module 122 builds on the patient/appointment linking established in Module 121.
It generates a structured, factual pre-appointment brief that clinic staff or the
doctor can review before confirming an appointment request.

This replaces the need to manually re-read the raw Vapi intake form. It surfaces
only safe, explicitly captured intake data — no clinical inference, no diagnosis,
no medical advice.

---

## 2. Data Sources

| Field | Source |
|---|---|
| `patient_name` | `appointment_requests.patient_name` (captured at intake) |
| `patient_phone` | `patients.phone` (linked row) or `appointment_requests.patient_phone` (fallback) |
| `reason` | `appointment_requests.reason` (captured at intake) |
| `preferred_starts_at` / `preferred_ends_at` | `appointment_requests.preferred_starts_at/ends_at` |
| `source` | `appointment_requests.source` (e.g. `vapi`) |
| `status` | `appointment_requests.status` |
| `action_required` | `appointment_requests.action_required` |
| `urgency_level` | `appointment_requests.urgency_level` (intake metadata only) |
| `patient_type` | Derived: `"returning"` if `patient_id` is set, `"new"` if not |
| `previous_request_count` | `COUNT(appointment_requests WHERE patient_id = X AND id != current)` |
| `suggested_next_action` | Rule-based (see Section 4) — no AI inference |

---

## 3. Files

| File | Role |
|---|---|
| `backend/app/services/pre_appointment_summary.py` | Pure service — builds the summary dict from input dicts; no DB, no external calls |
| `backend/app/db/repositories/appointment_request_repo.py` | Added `count_requests_for_patient` helper |
| `backend/app/api/routes/appointment_requests.py` | Added `GET /appointment-requests/{id}/pre-appointment-summary` route |
| `backend/tests/test_pre_appointment_summary.py` | 25 tests: 18 service unit + 7 route integration |

---

## 4. Suggested Next Action Logic

Rule-based mapping from `status` + `action_required` to a plain-language prompt:

| Status | action_required | Suggested Next Action |
|---|---|---|
| `new` | `True` | Review and confirm |
| `callback_needed` | any | Call patient |
| `confirmed` | any | Appointment confirmed — no further action needed |
| `rejected` / `cancelled` / `archived` | any | No action required |
| other | any | Review appointment request |

No AI is involved in this mapping. The mapping is deterministic and documented here.

---

## 5. Safety Rules

Every summary enforces these constraints by construction:

- **No diagnosis.** The summary dict contains no `diagnosis`, `medical_recommendation`,
  `treatment`, or `prognosis` key.
- **No patient history hallucinated.** Only explicitly captured intake fields are shown.
- **No urgency escalation.** `urgency_level` is surfaced verbatim from the intake record;
  no escalation or inference is applied.
- **No autonomous confirmation.** `action_required` reflects the DB value; the route
  never modifies it. Staff must use the Confirm button.
- **Tenant isolation enforced.** The route requires `clinic_id` as a query param and
  validates it against the caller's auth context (`require_staff_clinic_access`).
  Cross-clinic access returns HTTP 403. Queries are scoped by `clinic_id`.
- **Doctor/staff approval required.** The summary contains a `safety_note` field:
  *"This summary contains no medical advice or diagnosis. All actions require doctor
  or staff review and confirmation."*

---

## 6. API

### `GET /appointment-requests/{request_id}/pre-appointment-summary`

**Auth:** Cookie (`praximed_session`) or Bearer token. Staff-level or higher.

**Query params:**
- `clinic_id` (required): must match the caller's clinic from JWT.

**Response 200:**
```json
{
  "ok": true,
  "summary": {
    "request_id": "...",
    "clinic_id": "...",
    "patient_name": "...",
    "patient_phone": "...",
    "patient_type": "returning",
    "previous_request_count": 2,
    "reason": "Routine checkup",
    "preferred_starts_at": null,
    "preferred_ends_at": null,
    "source": "vapi",
    "status": "new",
    "action_required": true,
    "urgency_level": "normal",
    "suggested_next_action": "Review and confirm",
    "generated_at": "2026-07-05T10:00:00+00:00",
    "safety_note": "This summary contains no medical advice or diagnosis. All actions require doctor or staff review and confirmation."
  }
}
```

**Response 404:** Appointment request not found for this clinic.
**Response 401:** Missing or invalid auth token.
**Response 403:** Caller's clinic_id does not match the requested clinic_id.

---

## 7. What This Enables Next

| Module | Feature | Dependency on Module 122 |
|---|---|---|
| 123 | Doctor/Staff Notification | Notification payload uses the pre-appointment summary fields |
| Frontend dashboard | Pre-appointment brief panel | Fetches summary from this endpoint |
| Demo quality | Sales/pilot demo value | Doctors can see intake reason + next action in one panel |

---

## 8. Compatibility

- Existing Vapi intake flow (`capture_vapi_appointment_request`) is unchanged.
- Existing staff Confirm action (`PATCH /appointment-requests/{id}/status`) is unchanged.
- All pre-Module-122 appointment_request rows (with `patient_id=null`) return a valid
  summary with `patient_type="new"` and `previous_request_count=0`.
- No migrations required for this module.

---

## 9. Safety Constraints

- No real patient data in any test or staging fixture.
- Production PHI readiness: **NO-GO** (C3–C8 hardening blockers still open).
- No secrets committed.
- No external AI API called.
- No autonomous clinical decisions made.
