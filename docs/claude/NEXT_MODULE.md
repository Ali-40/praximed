# Sprint 20 / Module 149 — Patient History Data Model Foundation

Status: pending implementation.

## Context

Module 148 complete:
- `backend/migrations/versions/0006_consent_events.py` — consent_events table, 4 CHECK constraints, 9 indexes
- `backend/app/schemas/consent_event.py` — ConsentEventCreate/Read/Revoke/Response/ListResponse
- `backend/app/db/repositories/consent_event_repo.py` — CRUD, append-only, no DELETE
- `backend/app/services/consent_ledger.py` — history write gate: assert_valid_consent_for_history_write
- `backend/app/api/routes/consent_events.py` — 4 protected routes (POST/GET/GET/PATCH), no DELETE
- `backend/app/api/router.py` (updated) — consent_events router registered
- `backend/tests/test_patient_history_consent_ledger_foundation.py` — ≥60 tests
- `docs/architecture/PATIENT_HISTORY_CONSENT_LEDGER_FOUNDATION.md`
- production_phi_enabled always False
- No real patient PHI. No diagnosis. No medical advice. No triage scoring.
- Production PHI remains NO-GO.

Sprint 20 is in progress. The consent ledger foundation is in place. Any future
patient history write must call `assert_valid_consent_for_history_write` before writing.

## Goal

Create the patient_history_entries table and repository layer. This is the data model
that will store structured patient history collected during intake calls or onboarding
forms. Consent is required before any write. This module builds the table and CRUD
repository only — no service orchestration, no routes, no history writes yet.

No real patient data. Synthetic staging only. No PHI processing unlocked.
Production PHI remains NO-GO.

## What Module 149 must implement

### 1. Migration

`backend/migrations/versions/0007_patient_history_entries.py` (new):

Revision: `0007_patient_history_entries`
Down revision: `0006_consent_events`

```sql
CREATE TABLE IF NOT EXISTS patient_history_entries (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
    entry_type              TEXT        NOT NULL,
    entry_source            TEXT        NOT NULL,
    language                TEXT        NOT NULL DEFAULT 'de',
    collected_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    recorded_by_user_id     UUID,
    recorded_by_system      TEXT,
    history_data            JSONB       NOT NULL DEFAULT '{}'::jsonb,
    metadata                JSONB       NOT NULL DEFAULT '{}'::jsonb,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT phi_entries_production_phi_check CHECK (
        production_phi_enabled = false
    ),
    CONSTRAINT phi_entries_entry_type_check CHECK (
        entry_type IN ('chief_complaint', 'medication_list', 'allergy_list',
                       'past_medical_history', 'family_history', 'social_history',
                       'symptom_checklist', 'free_text_note', 'demo_seed')
    ),
    CONSTRAINT phi_entries_entry_source_check CHECK (
        entry_source IN ('phone_call', 'onboarding_form', 'staff_console',
                         'intake_link', 'import_demo')
    ),
    CONSTRAINT phi_entries_language_check CHECK (
        language IN ('de', 'en', 'ar')
    )
);
```

Indexes: clinic_id, patient_id, consent_event_id, entry_type, entry_source,
language, collected_at, production_phi_enabled.

### 2. Schema SQL

`backend/app/db/schema.sql` (updated): patient_history_entries table + indexes added.

### 3. Pydantic schemas

`backend/app/schemas/patient_history_entry.py` (new):

```python
class PatientHistoryEntryCreate(BaseModel):
    clinic_id: str
    patient_id: str
    consent_event_id: str
    entry_type: str       # CHECK enum
    entry_source: str     # CHECK enum
    language: str = "de"  # de/en/ar
    history_data: Dict[str, Any] = {}  # structured history data (non-PHI labels)
    metadata: Dict[str, Any] = {}      # operational metadata

class PatientHistoryEntryRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    consent_event_id: str
    entry_type: str
    entry_source: str
    language: str
    collected_at: Any
    history_data: Dict[str, Any]
    metadata: Dict[str, Any]
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any

class PatientHistoryEntryResponse(BaseModel):
    ok: bool
    entry: Optional[Dict[str, Any]] = None
    production_phi_enabled: bool = False

class PatientHistoryEntryListResponse(BaseModel):
    ok: bool
    entries: List[Dict[str, Any]]
    total: int
    production_phi_enabled: bool = False
```

Validators:
- entry_type: CHECK enum (9 values)
- entry_source: CHECK enum (5 values)
- language: de/en/ar
- clinic_id, patient_id, consent_event_id: not empty
- history_data: reject keys containing diagnosis, medical_advice, triage, prescription,
  sk-, vapi_live, jwt, password, secret
- metadata: same forbidden key patterns

### 4. Repository

`backend/app/db/repositories/patient_history_entry_repo.py` (new):

```python
async def create_patient_history_entry(
    pool, clinic_id, patient_id, consent_event_id,
    entry_type, entry_source, language, history_data, metadata,
    recorded_by_user_id, recorded_by_system
) -> dict

async def get_patient_history_entry_by_id(pool, entry_id) -> dict | None
async def list_patient_history_entries_for_patient(pool, clinic_id, patient_id, limit=50) -> list[dict]
async def list_patient_history_entries_for_clinic(pool, clinic_id, limit=50) -> list[dict]
async def list_patient_history_entries_by_consent_event(pool, consent_event_id, limit=50) -> list[dict]
```

Rules:
- All SQL parameterised
- clinic_id scoped on all queries (tenant isolation)
- production_phi_enabled never written as true (DB enforces)
- No DELETE
- Errors: InvalidPatientHistoryEntryError, PatientHistoryEntryNotFoundError

### 5. Tests

`backend/tests/test_patient_history_data_model_foundation.py` (new — ≥60 tests):

- Migration: file exists, revision/down_revision, all columns, all CHECK constraints, downgrade
- Schema SQL: patient_history_entries present
- Pydantic: accepts all valid entry_types/entry_sources/languages, rejects invalid values,
  rejects forbidden history_data/metadata keys, accepts safe data
- Repo: create, get by id, list by patient, list by clinic, list by consent_event,
  production_phi_enabled never true
- Static checks: no diagnosis/medical_advice/triage vocabulary, no DATABASE_URL/JWT,
  no actual PHI content

### 6. Architecture doc

`docs/architecture/PATIENT_HISTORY_DATA_MODEL_FOUNDATION.md` (new):
- Purpose: data model for structured patient history, gated by consent
- Table design: columns, CHECK constraints, FK to consent_events (RESTRICT = cannot delete consent if history exists)
- entry_type values and what each captures
- entry_source values
- Consent gate requirement: consent_event_id FK is mandatory
- Tenant isolation
- No PHI stored — only structured labels and patient-provided answers
- production_phi_enabled always False
- What this enables next: Module 150 service + routes for history write

### 7. Docs

- `docs/claude/CURRENT_STATE.md` — Module 149 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 150

## Constraints

- No live external calls
- No real patient PHI stored (no raw names, phone numbers, addresses, health record IDs)
- production_phi_enabled remains False in all schemas and responses
- All SQL parameterised
- Tenant isolation enforced: clinic_id scoped on all queries
- consent_event_id FK uses ON DELETE RESTRICT — a consent event cannot be deleted if history entries reference it
- Full test suite must remain green
- Commit message:
  Sprint 20 / Module 149 — Patient history data model foundation
