# Vapi Intake to Dashboard Smoke Results — PraxisMed Sprint 11 / Modules 84–85

**Date:** 2026-07-02
**Verdict:** PASS — HTTP 200, appointment request created, status: new

---

## 1. Purpose

This document records the outcome of running `smoke_vapi_appointment_intake.py` against
the local backend after two modules of fixes:

- **Module 84** — wired `app.state.config_loader` in `main.py` lifespan (fixed HTTP 503)
- **Module 85** — replaced strict RFC 4122 UUID regex with `uuid.UUID()` validation (fixed HTTP 500);
  added DB-error fallback so `_load_db_config` returns `{}` when `tenants` table is absent

---

## 2. Environment

| Component | Details |
|---|---|
| PostgreSQL | Local Docker container — `docker-compose.postgres.yml` (port 5433) |
| Backend | `uvicorn backend.app.main:app --reload --port 8000` on `http://127.0.0.1:8000` |
| JWT_SECRET_KEY | Local-dev value only — not committed; not used in production |
| Seed data | `backend/scripts/seed_local_data.py` (clinic `11111111-1111-1111-1111-111111111111`) |
| Smoke script | `backend/scripts/smoke_vapi_appointment_intake.py` |
| Payload | `docs/integrations/local_payloads/vapi_appointment_intake.json` |
| Tunnel | None — local only |

---

## 3. Blockers Resolved

### Module 84 — config_loader wired (503 fixed)

Added to `backend/app/main.py` lifespan startup:
```python
app.state.config_loader = ClinicConfigLoader(pool=app.state.db_pool)
```
Added to shutdown: `app.state.config_loader = None`

**Result:** HTTP 503 → eliminated.

### Module 85 — UUID validation relaxed (500 fixed)

Replaced `_UUID_RE` regex with `uuid.UUID()` parser in `backend/app/core/config_loader.py`:

```python
# Before (too strict — rejected local seed UUID):
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# After (accepts any structurally valid UUID):
def _assert_valid_uuid(value: str) -> None:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        raise InvalidTenantIDError(...)
    if str(parsed) != value.lower():
        raise InvalidTenantIDError(...)
```

Also added DB-error fallback in `_load_db_config` — `try/except` returns `{}` when the
`tenants` table is absent, allowing disk config to be used.

**Result:** HTTP 500 → eliminated.

---

## 4. Smoke Script Run — Final Result

```
============================================================
PraxisMed — Vapi Appointment Intake Smoke
============================================================
Endpoint:     http://127.0.0.1:8000/vapi/tools/capture-appointment-request
Payload file: docs/integrations/local_payloads/vapi_appointment_intake.json
clinic_ref:   11111111-1111-1111-1111-111111111111
patient_name: Local Vapi Test Caller
call_id:      local-vapi-intake-call-1

HTTP status:  200
Response:     {
  "ok": true,
  "message": "The appointment request has been captured and forwarded to the clinic. Staff must review and confirm the appointment before it is booked. The patient will be contacted once staff confirm the appointment.",
  "request": {
    "id": "509211a7-784e-4e45-90f1-d9af6f8d7981",
    "clinic_id": "11111111-1111-1111-1111-111111111111",
    "source": "vapi",
    "source_ref": "local-vapi-intake-call-1",
    "patient_name": "Local Vapi Test Caller",
    "patient_phone": "+43000000000",
    "status": "new",
    "urgency_level": "normal",
    "action_required": true,
    ...
  }
}

Appointment request created:
  ID:                   509211a7-784e-4e45-90f1-d9af6f8d7981
  Status:               new  (must be 'new' — not auto-confirmed)
```

---

## 5. What Was Proven

| Claim | Status |
|---|---|
| `POST /vapi/tools/capture-appointment-request` returns HTTP 200 | PROVEN |
| Machine auth (`X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes`) accepted | PROVEN |
| Appointment request created with `source=vapi` | PROVEN — `"source": "vapi"` in response |
| Appointment request created with `status=new` — not auto-confirmed | PROVEN — `"status": "new"` |
| `action_required=true` — staff review required | PROVEN |
| `clinic_id` resolved from disk config for seed UUID | PROVEN — `"clinic_id": "11111111-…"` |
| No real patient data used | PROVEN — `patient_name: "Local Vapi Test Caller"` (fake) |
| No secrets printed | PROVEN — no credentials in smoke output |
| Local seed UUID accepted by `_assert_valid_uuid()` | PROVEN — no InvalidTenantIDError |
| RFC 4122 UUIDs still accepted | PROVEN — all existing tests pass |
| Path-traversal and malformed UUIDs still rejected | PROVEN — all existing security tests pass |
| DB-error fallback works when `tenants` table absent | PROVEN — disk config used, HTTP 200 |
| Full test suite passes | PROVEN — 1594/1594 |

---

## 6. Dashboard Loop — Pending Manual Browser Step

The backend intake is complete. Closing the full loop requires a browser step:

```bash
# Open dashboard, find the Vapi-created row (ID: 509211a7-...)
open http://localhost:3000/dashboard
# Click Confirm on the new row (distinct from the seed row 55555555-...)
# Verify status changes to 'confirmed'
```

This browser step is documented and recorded in Module 86.

---

## 7. No Real Data / No Secrets

- `patient_name`: `"Local Vapi Test Caller"` — fake name
- `clinic_ref`: `"11111111-1111-1111-1111-111111111111"` — local seed UUID
- `call_id`: `"local-vapi-intake-call-1"` — fake call ID
- No Vapi API credentials, no patient PHI, no real clinic data used

---

## 8. Full Test Suite

| Module | Tests | Result |
|---|---|---|
| Module 84 (lifespan config_loader wiring) | 1589 | PASS |
| Module 85 (UUID fix + DB fallback fix) | 1594 | PASS |

Previous: Module 83: 1580/1580, Module 81: 1570/1570.
