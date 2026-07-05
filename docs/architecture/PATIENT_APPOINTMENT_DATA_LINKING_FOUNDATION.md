# Patient and Appointment Data Linking Foundation — Sprint 17 / Module 121

Status: IMPLEMENTED — fake-data staging only. Production PHI: NO-GO.

---

## 1. Purpose

Module 121 establishes the relational backbone that links every appointment request to a
durable patient identity. Without this link, downstream workflows — doctor notifications,
pre-appointment summaries, consultation drafts, patient timelines, and follow-up messages —
have no stable subject to reference.

This module adds no UI, no AI inference, and no automated confirmation. It only closes the
data gap between Vapi phone intake and a well-formed patient record.

---

## 2. Schema Changes

### 2.1 New column: `appointment_requests.patient_id`

```sql
ALTER TABLE appointment_requests
    ADD COLUMN IF NOT EXISTS patient_id UUID
    REFERENCES patients(id) ON DELETE SET NULL;
```

- **Nullable**: pre-Module-121 rows and staff-entered requests without phone matching
  retain NULL. Nothing breaks.
- **ON DELETE SET NULL**: if a patient row is deleted, linked appointment requests
  lose the FK reference but are not deleted.
- **Forward reference note**: `appointment_requests` appears before `patients` in
  `schema.sql` for historical reasons. The FK is applied via Alembic migration 0003
  (`ALTER TABLE ... ADD COLUMN`) rather than inline in the CREATE TABLE block.
- **Applied by**: `backend/migrations/versions/0003_patient_id_appt_requests.py`
  (revision `"0003_patient_id_appt_requests"`, 29 chars ≤ 32-char alembic_version limit)

### 2.2 New index

```sql
CREATE INDEX IF NOT EXISTS idx_appointment_requests_clinic_patient
    ON appointment_requests (clinic_id, patient_id);
```

Supports multi-tenant queries such as "all appointment requests for patient X in clinic Y".

---

## 3. Migration 0003

File: `backend/migrations/versions/0003_patient_id_appt_requests.py`

```
revision      = "0003_patient_id_appt_requests"
down_revision = "0002_password_hash"
```

- **upgrade()**: adds `patient_id UUID REFERENCES patients(id) ON DELETE SET NULL` and
  the `idx_appointment_requests_clinic_patient` index.
- **downgrade()**: drops the index, then drops the column.

Idempotent (`IF NOT EXISTS` / `IF EXISTS`) — safe to run against a DB that already has
the column (e.g. repeated migration runs in staging).

---

## 4. Patient Matching Logic

### 4.1 `patient_repo.find_or_create_patient_from_vapi`

File: `backend/app/db/repositories/patient_repo.py`

**Algorithm:**

1. Normalize `phone`: strip whitespace; treat blank/whitespace-only as `None`.
2. If `normalized_phone` is not None:
   - `SELECT * FROM patients WHERE clinic_id=$1 AND phone=$2 ORDER BY created_at ASC LIMIT 1`
   - If a row is found, return it. No new patient is created.
3. If no phone or no match:
   - Call `create_patient(...)` with `(clinic_id, full_name, phone, email, date_of_birth)`.
   - Return the newly created patient row.

**Why phone-only matching (not name):**

Name-based matching causes false positives (two patients named "Maria Müller"). Phone-based
matching is safe because phone numbers are unique per person and already normalized to E.164
by Vapi. When no phone is available, a new patient row is created — a small number of
duplicate rows is preferable to incorrect linking.

**Tenant isolation:**

All SELECTs are scoped by `clinic_id` as the first query parameter. Cross-clinic patient
linking is impossible by construction. A patient with the same phone in Clinic A and Clinic B
produces two distinct patient rows, each scoped to their respective clinic.

---

## 5. Appointment Request Linking

### 5.1 `appointment_request_repo.create_appointment_request`

- Added `patient_id: Optional[str] = None` parameter (before `raw_payload`).
- SQL INSERT includes `patient_id` as `$15`; `raw_payload` promoted to `$16::jsonb`.
- Backward compatible: existing callers that omit `patient_id` receive NULL in the column.

### 5.2 `vapi_appointment_capture.capture_vapi_appointment_request`

Updated call sequence (simplified):

```
config = await config_loader.load(clinic_ref)
clinic_id = config.tenant_id

patient = await patient_repo.find_or_create_patient_from_vapi(
    pool=pool,
    clinic_id=clinic_id,
    full_name=patient_name,
    phone=caller_phone,
    email=patient_email,
    date_of_birth=date_of_birth,
)
patient_id = patient["id"]

row = await appointment_request_repo.create_appointment_request(
    ...,
    patient_id=patient_id,
    ...
)

return {
    "ok": True,
    "clinic_id": clinic_id,
    "patient_id": patient_id,
    "request": row,
    ...
}
```

No behavior changes to the Vapi dashboard loop, the staff Confirm action, or the
existing notification creation block.

---

## 6. Data Flow

```
Vapi phone call
    → capture_vapi_appointment_request(caller_phone, patient_name, ...)
        → patient_repo.find_or_create_patient_from_vapi(clinic_id, phone)
            → SELECT patients WHERE clinic_id + phone   (match → return existing)
            → OR create_patient(...)                    (no match → new row)
        → appointment_request_repo.create_appointment_request(..., patient_id=...)
            → INSERT appointment_requests ... patient_id = $15
    → return { patient_id, request, ... }

Staff dashboard
    → GET /appointment-requests (unchanged)
    → Staff Confirm action (unchanged)
```

---

## 7. What This Enables Next

Each item below requires `appointment_requests.patient_id` to be populated before it
can be built safely.

| Module | Feature | Dependency on Module 121 |
|--------|---------|--------------------------|
| 122 | Pre-Appointment Summary | Needs `patient_id` to fetch patient history |
| 123 | Doctor/Staff Notification | Needs `patient_id` to personalize alert |
| 124 | Consultation Summary Draft | Needs `patient_id` as subject of the draft |
| 125 | Patient Timeline | Needs `patient_id` as the stable anchor |
| 126 | Follow-up / Reminder Workflow | Needs `patient_id` to address the right patient |

---

## 8. Safety Constraints

- **No real patient data.** All development and staging data is fake.
- **No production PHI.** Production PHI readiness remains NO-GO (C3–C8 blockers open).
- **No secrets committed.** No credentials, tokens, or connection strings in this module.
- **No automated confirmation.** `action_required=True` and `status="new"` are enforced
  in `vapi_appointment_capture.py`. Staff must explicitly confirm every request.
- **No diagnosis or medical advice.** Patient rows store identity (name, phone, email,
  DOB) only. No clinical data is stored or inferred in this module.
- **Tenant isolation enforced.** All patient SELECTs and INSERTs are scoped by
  `clinic_id`. Multi-tenant contract tested in `test_patient_appointment_linking.py`.

---

## 9. Test Coverage

| File | Tests | What is covered |
|------|-------|-----------------|
| `test_patient_appointment_linking.py` | 17 | find_or_create logic; phone normalization; tenant isolation; vapi capture integration; backward compat; error propagation; no real patient data |
| `test_vapi_appointment_capture.py` | 31 | existing capture tests + autouse fixture that patches `find_or_create_patient_from_vapi` so all 31 tests continue to pass |
| `test_schema_contract.py` | updated | `patient_id` column and `idx_appointment_requests_clinic_patient` index verified in schema.sql |
| `test_migration_contract.py` | +3 | migration 0003 file exists; revision ID `"0003_patient_id_appt_requests"` ≤32 chars; `patient_id`/`patients`/`appointment_requests` mentioned |

---

## 10. Files Modified

| File | Change |
|------|--------|
| `backend/app/db/schema.sql` | Added `patient_id UUID` column to `appointment_requests`; added `idx_appointment_requests_clinic_patient` index |
| `backend/migrations/versions/0003_patient_id_appt_requests.py` | New migration: adds `patient_id` FK column and index |
| `backend/app/db/repositories/patient_repo.py` | Added `find_or_create_patient_from_vapi` function |
| `backend/app/db/repositories/appointment_request_repo.py` | Added `patient_id` parameter to `create_appointment_request`; updated SQL INSERT |
| `backend/app/modules/vapi/vapi_appointment_capture.py` | Added patient matching call; passes `patient_id` to appointment create; includes `patient_id` in return dict |
| `backend/tests/test_vapi_appointment_capture.py` | Added autouse fixture to patch patient matching for all 31 tests |
| `backend/tests/test_schema_contract.py` | Added `patient_id` column and index assertions |
| `backend/tests/test_migration_contract.py` | Added 3 tests for migration 0003 |
| `backend/tests/test_patient_appointment_linking.py` | New file — 17 tests for Module 121 |
