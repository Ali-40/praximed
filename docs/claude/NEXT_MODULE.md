# Sprint 2 / Module 27 — Consultation Session Schema Contract

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Module 24: patient schema contract committed.
- Sprint 2, Module 25: patient repository committed.
- Sprint 2, Module 26: patient API routes committed.

Do not modify completed modules unless absolutely required.

## Task scope
Add the database schema contract for consultation sessions.

## Purpose
PraxisMed needs a consultation session table before building audio upload, transcription, AI draft summaries, doctor approval, and patient timelines.

## Create or update only

1. `backend/app/db/schema.sql`
2. `backend/tests/test_schema_contract.py`
3. `docs/claude/CURRENT_STATE.md`
4. `docs/claude/NEXT_MODULE.md`

Do not create repository code yet.
Do not create API routes yet.
Do not create audio upload code yet.
Do not create transcription code.
Do not create AI summary code.
Do not create doctor approval workflow yet.
Do not build frontend.
Do not build authentication.
No real database connection during tests.

## Schema requirement

Table: `consultation_sessions`

### Columns
- `id` UUID PRIMARY KEY
- `clinic_id` UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE
- `patient_id` UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE
- `doctor_user_id` UUID REFERENCES clinic_users(id) ON DELETE SET NULL
- `source` TEXT NOT NULL DEFAULT 'manual'
- `status` TEXT NOT NULL DEFAULT 'created'
- `title` TEXT
- `reason_for_visit` TEXT
- `audio_file_path` TEXT
- `transcript_text` TEXT
- `draft_summary` JSONB
- `approved_summary` JSONB
- `approval_status` TEXT NOT NULL DEFAULT 'not_ready'
- `approved_by_user_id` UUID REFERENCES clinic_users(id) ON DELETE SET NULL
- `approved_at` TIMESTAMPTZ
- `rejected_reason` TEXT
- `raw_payload` JSONB
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### Constraints
- CHECK (source IN ('manual', 'vapi', 'web', 'doctor_mobile', 'system'))
- CHECK (status IN ('created', 'recording', 'audio_uploaded', 'transcribing', 'transcribed', 'draft_ready', 'approved', 'rejected', 'archived'))
- CHECK (approval_status IN ('not_ready', 'pending_review', 'approved', 'rejected'))
- CHECK ((approval_status = 'approved' AND approved_at IS NOT NULL) OR approval_status <> 'approved')

### Indexes
- consultation_sessions(clinic_id, created_at)
- consultation_sessions(clinic_id, patient_id)
- consultation_sessions(clinic_id, doctor_user_id)
- consultation_sessions(clinic_id, status)
- consultation_sessions(clinic_id, approval_status)
- consultation_sessions(clinic_id, approved_at)
- consultation_sessions(clinic_id, source)

## Tests required (schema contract)

1. consultation_sessions table exists.
2. All critical columns exist.
3. clinic_id references clinics(id).
4. patient_id references patients(id).
5. doctor_user_id references clinic_users(id).
6. approved_by_user_id references clinic_users(id).
7. Source check constraint exists.
8. Status check constraint exists.
9. Approval status check constraint exists.
10. Approved timestamp check exists.
11. All required indexes exist.
12. Existing schema contract tests still pass.

## Run

```
pytest -v backend/tests/test_schema_contract.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 27 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Only schema contract and orchestration docs are changed.
- No repository code yet.
- No API route yet.
- No audio/transcription/summary code yet.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 27 — Consultation session schema contract`
