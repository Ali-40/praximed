# Sprint 19 / Module 132 — Real Clinic Onboarding Backend Foundation

Status: pending implementation.

## Context

Module 131 complete:
- `docs/runtime/STAGING_END_TO_END_DEMO_EXECUTION_EVIDENCE.md` — 15-section evidence doc
  for the fake-data end-to-end staging flow after the compliance gate.
- `backend/tests/test_staging_e2e_demo_execution_evidence_contract.py` — 35 tests, all pass.
- 3288/3288 backend tests pass.
- Commit: Sprint 19 / Module 131 — Real staging end-to-end demo execution evidence

Sprint 19 Operational track complete:
- Module 130 (operational): Vapi assistant setup, demo runbook, data flow map
- Module 130 (compliance): enforce_phi_safeguard, pseudonymization, language foundation, route wiring
- Module 131: Staging end-to-end evidence (docs only)

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Build the backend data model and API foundation for real clinic onboarding requests —
the first step toward a real pilot clinic workflow. This is still fake-data / staging only.
No real PHI. No automatic production activation.

## What Module 132 must implement

### 1. Database schema — `clinic_onboarding_requests` table

New table in `backend/app/db/schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS clinic_onboarding_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_name     TEXT NOT NULL,
    doctor_name     TEXT NOT NULL,
    specialty       TEXT NOT NULL,
    city            TEXT NOT NULL,
    country         TEXT NOT NULL DEFAULT 'AT',
    contact_email   TEXT NOT NULL,
    contact_phone   TEXT,
    primary_language TEXT NOT NULL DEFAULT 'de',
    preferred_languages TEXT[] NOT NULL DEFAULT ARRAY['de', 'en'],
    workflow_notes  TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ,
    reviewer_notes  TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Status values: `pending`, `under_review`, `approved`, `rejected`.

### 2. Repository — `clinic_onboarding_request_repo.py`

`backend/app/db/repositories/clinic_onboarding_request_repo.py`:
- `create_onboarding_request(pool, data: dict) -> dict`
- `get_onboarding_request(pool, request_id: UUID) -> dict | None`
- `list_onboarding_requests(pool, status: str | None = None, limit: int = 50) -> list[dict]`
- `update_onboarding_request_status(pool, request_id: UUID, status: str, reviewer_notes: str | None) -> dict | None`

### 3. Pydantic schemas — `clinic_onboarding.py`

`backend/app/schemas/clinic_onboarding.py`:
- `ClinicOnboardingRequestCreate`: clinic_name, doctor_name, specialty, city, country (default AT), contact_email, contact_phone (optional), primary_language (default de), preferred_languages (default [de, en]), workflow_notes (optional)
- `ClinicOnboardingRequestRead`: all fields + id, status, submitted_at, created_at, updated_at
- `ClinicOnboardingStatusUpdate`: status, reviewer_notes (optional)
- `ClinicOnboardingListResponse`: items: list[ClinicOnboardingRequestRead], total: int

Validation:
- `contact_email`: valid email format
- `primary_language`: must be in preferred_languages
- `status`: must be one of `pending`, `under_review`, `approved`, `rejected`
- `country`: uppercase 2-letter ISO code

### 4. API routes — `clinic_onboarding.py`

`backend/app/api/routes/clinic_onboarding.py`:
- `POST /clinic-onboarding/requests` — submit a new onboarding request
  - No auth required (public intake form)
  - Returns 201 + ClinicOnboardingRequestRead
- `GET /clinic-onboarding/requests` — list onboarding requests (admin use)
  - Requires authenticated session (existing auth dependency)
  - Optional ?status= filter
  - Returns ClinicOnboardingListResponse
- `GET /clinic-onboarding/requests/{request_id}` — get single request (admin use)
  - Requires authenticated session
  - Returns ClinicOnboardingRequestRead
- `PATCH /clinic-onboarding/requests/{request_id}/status` — update status (admin use)
  - Requires authenticated session
  - Body: ClinicOnboardingStatusUpdate
  - Returns ClinicOnboardingRequestRead

No `enforce_phi_safeguard` on onboarding routes — onboarding submissions do not process
existing patient PHI. Contact details (email, phone) are clinic admin info, not patient PHI.

Wire router into `backend/app/api/router.py`.

### 5. Tests

- `backend/tests/test_schema_contract.py` — extended with `clinic_onboarding_requests` table assertions
- `backend/tests/test_clinic_onboarding_request_repo.py` — repository contract tests (pure Python, no DB)
- `backend/tests/test_clinic_onboarding_schemas.py` — Pydantic schema validation tests
- `backend/tests/test_clinic_onboarding_routes.py` — FastAPI route tests (TestClient)

### 6. Docs

- `docs/claude/CURRENT_STATE.md` — Module 132 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 133

## Constraints

- No real clinic PHI in tests — use synthetic clinic names and fake contact info.
- No automatic pilot activation — status `approved` is an internal admin marker only.
- No email sending, no SMS, no external notifications in this module.
- No production readiness claim.
- No secrets committed.
- No frontend changes in this module — backend foundation only.
- `enforce_phi_safeguard` is NOT applied to onboarding routes (no patient PHI involved).
- Full test suite must remain green after implementation.
