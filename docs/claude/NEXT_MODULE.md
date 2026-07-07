# Sprint 20 / Module 148 — Patient History Consent Ledger Foundation

Status: pending implementation.

## Context

Module 147 complete:
- `docs/runtime/LIVE_VAPI_BINDING_METADATA_SMOKE_EVIDENCE.md` — PASS: create/load/update
  Vapi binding metadata on staging using reference names only
- `backend/tests/test_live_vapi_binding_metadata_smoke_evidence_contract.py` — 55 tests, all pass
- 4264/4264 backend tests pass
- Commit: Sprint 19 / Module 147 — Live Vapi binding metadata smoke evidence

Sprint 19 is complete. The full Vapi binding metadata stack is deployed end to end:
migration → repo → service → routes → admin UI → smoke evidence.
Secret reference names only. No actual secrets. No live Vapi calls.
production_phi_enabled remains False. C3–C8 blockers remain open.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Create the consent ledger foundation: a consent_events table and service that records
who consented to what, when, and for what purpose, scoped per tenant. This is a
prerequisite for any future patient history write — no appointment history, summary,
or clinical data may be written for a patient without a consent reference.

No real patient data. Synthetic staging only. No PHI processing unlocked.
Production PHI remains NO-GO.

## What Module 148 must implement

### 1. Migration

`backend/migrations/versions/0006_consent_events.py` (new):

```sql
CREATE TABLE IF NOT EXISTS consent_events (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id           UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id          UUID        REFERENCES patients(id) ON DELETE SET NULL,
    consent_type        TEXT        NOT NULL,
    channel             TEXT        NOT NULL DEFAULT 'verbal',
    language            TEXT        NOT NULL DEFAULT 'de',
    purpose             TEXT        NOT NULL,
    revoked_at          TIMESTAMPTZ,
    consented_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    recorded_by_user_id UUID,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT consent_events_channel_check CHECK (
        channel IN ('verbal', 'written', 'digital', 'phone')
    ),
    CONSTRAINT consent_events_language_check CHECK (
        language IN ('de', 'en')
    )
);
CREATE INDEX IF NOT EXISTS idx_consent_events_clinic_id ON consent_events (clinic_id);
CREATE INDEX IF NOT EXISTS idx_consent_events_patient_id ON consent_events (patient_id);
CREATE INDEX IF NOT EXISTS idx_consent_events_consent_type ON consent_events (consent_type);
CREATE INDEX IF NOT EXISTS idx_consent_events_consented_at ON consent_events (consented_at);
```

### 2. Schema SQL

`backend/app/db/schema.sql` (updated): consent_events table + indexes added.

### 3. Pydantic schemas

`backend/app/schemas/consent_event.py` (new):

```python
class ConsentEventCreate(BaseModel):
    clinic_id: str
    patient_id: Optional[str] = None
    consent_type: str        # e.g. "data_processing", "ai_intake", "recording"
    channel: str = "verbal"  # verbal/written/digital/phone
    language: str = "de"     # de/en
    purpose: str             # free text, non-empty, max 500 chars

class ConsentEventRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: Optional[str]
    consent_type: str
    channel: str
    language: str
    purpose: str
    revoked_at: Any
    consented_at: Any
    recorded_by_user_id: Optional[str]
    created_at: Any
    updated_at: Any
    production_phi_enabled: bool = False

class ConsentEventRevoke(BaseModel):
    revoked_at: Optional[str] = None  # ISO datetime; defaults to now() if omitted

class ConsentEventResponse(BaseModel):
    ok: bool
    event: Optional[Dict[str, Any]] = None
    production_phi_enabled: bool = False
```

### 4. Repository

`backend/app/db/repositories/consent_event_repo.py` (new):

```python
async def create_consent_event(pool, clinic_id, patient_id, consent_type,
                                channel, language, purpose, recorded_by_user_id) -> dict
async def get_consent_event_by_id(pool, event_id) -> dict | None
async def list_consent_events_for_patient(pool, clinic_id, patient_id, limit=50) -> list[dict]
async def list_consent_events_for_clinic(pool, clinic_id, limit=50) -> list[dict]
async def revoke_consent_event(pool, event_id, revoked_at=None) -> dict | None
async def is_consent_active(pool, clinic_id, patient_id, consent_type) -> bool
```

Rules:
- clinic_id scoped on all queries (tenant isolation)
- production_phi_enabled never stored or returned from repo
- No actual patient PHI stored — consent reference only
- All SQL parameterised

### 5. Service

`backend/app/services/consent_event.py` (new):

```python
async def record_consent(pool, payload, actor_user) -> dict
    # 1. Verify clinic exists
    # 2. If patient_id given, verify patient belongs to clinic (tenant isolation)
    # 3. Create consent_event row
    # 4. Log: event_id, clinic_id, consent_type, channel, language, actor
    # 5. Return row with production_phi_enabled=False

async def get_consent_event(pool, event_id, actor_user) -> dict | None
async def revoke_consent(pool, event_id, revoked_at, actor_user) -> dict
async def check_patient_consent(pool, clinic_id, patient_id, consent_type) -> bool
```

Rules:
- No live external calls
- No PHI stored beyond what is already in patients table
- production_phi_enabled=False always
- Consent check used as gate before any patient history write

### 6. Routes

`backend/app/api/routes/consent_events.py` (new):

```python
POST /clinics/{clinic_id}/consent-events        — record consent; auth required
GET  /clinics/{clinic_id}/consent-events         — list events; auth required
GET  /consent-events/{event_id}                  — get event; auth required
POST /consent-events/{event_id}/revoke           — revoke; auth required
GET  /clinics/{clinic_id}/patients/{patient_id}/consent-check?consent_type=... — active check
```

All routes: authenticated session required. No public access.
No PHI returned beyond consent metadata. production_phi_enabled=False always.

### 7. Router

`backend/app/api/router.py` (updated): consent_events router wired.

### 8. Tests

`backend/tests/test_consent_ledger_foundation.py` (new — ≥60 tests):
- Migration: table, columns, constraints, indexes
- Schema SQL: consent_events present
- Pydantic: valid create, invalid channel/language, empty purpose, missing clinic_id
- Repo: create, get by id, list by patient, list by clinic, revoke, is_consent_active
- Service: record, get, revoke, check
- Routes: POST 201 auth required, GET auth required, revoke auth required, consent-check
- PHI checks: no patient name/phone/transcript/recording in any response
- production_phi_enabled=False in all responses
- Arch doc: exists, mentions consent_type/channel/language/purpose/revoked_at/tenant isolation/NO-GO

### 9. Architecture doc

`docs/architecture/PATIENT_HISTORY_CONSENT_LEDGER_FOUNDATION.md` (new):
- Purpose: prerequisite for any patient history write
- Table design and column notes
- Consent types planned: data_processing, ai_intake, recording, clinical_summary
- Channel: verbal/written/digital/phone
- Revocation: soft delete via revoked_at timestamp
- Tenant isolation: all queries clinic_id scoped
- No PHI. No patient data beyond consent reference. production_phi_enabled always False.
- What this enables next: audit-complete patient history in Modules 149+

### 10. Docs

- `docs/claude/CURRENT_STATE.md` — Module 148 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 149

## Constraints

- No live external calls
- No actual patient PHI stored in consent_events (name/phone/reason/transcript)
- No PHI. No recording. No transcript.
- production_phi_enabled remains False in all schemas and responses
- All SQL parameterised
- Tenant isolation enforced: clinic_id scoped on all queries
- Full test suite must remain green
- Commit message:
  Sprint 20 / Module 148 — Patient history consent ledger foundation
