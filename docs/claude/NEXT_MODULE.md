# Sprint 1 / Module 15 — PraxisMed Appointment Request Schema Contract

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
1. Module 1: config loader
2. Module 2: asyncpg pool
3. Module 3: PostgreSQL schema contract
4. Module 4: calendar repository
5. Module 5: availability engine
6. Module 6: calendar sync service
7. Module 7: FastAPI skeleton and health routes
8. Module 8: n8n calendar sync webhook route
9. Modules 9–10: availability schemas and API routes
10. Modules 11–12: Vapi prompt builder and tool routes
11. Modules 13–14: Vapi call logs and call event webhook

All are committed. Do not modify completed modules unless absolutely required.

## Task scope
Your task is strictly limited to adding the appointment request schema contract.

Create or update only:

1. `backend/app/db/schema.sql`
2. `backend/tests/test_schema_contract.py`

## Purpose
Add a new PostgreSQL table for appointment requests captured by phone AI, WhatsApp, web forms, or clinic staff.

Do not create repository code yet.
Do not create FastAPI routes yet.
Do not modify Vapi modules yet.
Do not build WhatsApp.
Do not build frontend.
No real database connection during tests.

## Schema requirement

Add table:

`appointment_requests`

Required columns:
- `id UUID PRIMARY KEY`
- `clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE`
- `source TEXT NOT NULL`
- `source_ref TEXT`
- `patient_name TEXT NOT NULL`
- `patient_phone TEXT`
- `patient_email TEXT`
- `date_of_birth DATE`
- `reason TEXT`
- `preferred_starts_at TIMESTAMPTZ`
- `preferred_ends_at TIMESTAMPTZ`
- `status TEXT NOT NULL DEFAULT 'new'`
- `urgency_level TEXT NOT NULL DEFAULT 'normal'`
- `action_required BOOLEAN NOT NULL DEFAULT true`
- `assigned_user_id UUID REFERENCES clinic_users(id) ON DELETE SET NULL`
- `raw_payload JSONB`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`

## Constraints
- `CHECK (preferred_ends_at IS NULL OR preferred_starts_at IS NULL OR preferred_ends_at > preferred_starts_at)`
- `CHECK (status IN ('new', 'confirmed', 'rejected', 'callback_needed', 'cancelled', 'archived'))`
- `CHECK (urgency_level IN ('low', 'normal', 'urgent', 'emergency'))`
- `CHECK (source IN ('vapi', 'whatsapp', 'web', 'staff', 'system'))`

## Indexes
- `appointment_requests(clinic_id, created_at)`
- `appointment_requests(clinic_id, status)`
- `appointment_requests(clinic_id, action_required)`
- `appointment_requests(clinic_id, urgency_level)`
- `appointment_requests(clinic_id, preferred_starts_at)`
- `appointment_requests(clinic_id, source)`

## Update `test_schema_contract.py` to verify
1. `appointment_requests` table exists.
2. All critical columns exist.
3. Foreign key references `clinics(id)`.
4. `assigned_user_id` references `clinic_users(id)`.
5. Status check constraint exists.
6. Urgency check constraint exists.
7. Source check constraint exists.
8. Preferred time range check exists.
9. All required indexes exist.
10. Existing schema contract tests still pass.

## Run
`pytest -v backend/tests/test_schema_contract.py`

Then run all tests:
`pytest -v backend/tests`

## Acceptance criteria
- All Module 15 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Only the schema contract is changed.
- No repository code yet.
- No API route yet.
- No Vapi integration yet.
