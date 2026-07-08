# Patient History Consent Ledger Foundation

**Sprint 20 / Module 148**
**Date:** 2026-07-08
**Status:** Complete

## Purpose

Establish the consent ledger prerequisite for any future longitudinal patient history write. Before any patient history data can be collected or stored, an explicit, recorded consent event must exist. This module builds the complete backend foundation for that gate.

No patient history data is written in this module. No real patient PHI. No diagnosis. No medical advice. No triage scoring. Synthetic/fake staging only. Production PHI remains NO-GO.

## Safety Invariants

- `production_phi_enabled` is always `False` — enforced at DB CHECK constraint, service layer, and every route response.
- No DELETE route exists. Consent events are append-only. Revocation uses a `revoked_at` marker.
- No diagnosis vocabulary, no medical advice language, no triage scoring anywhere in this module.
- No real patient PHI stored or returned.
- No call recordings. No transcript storage.

## Database Migration

**File:** `backend/migrations/versions/0006_consent_events.py`
**Revision:** `0006_consent_events`
**Down revision:** `0005_clinic_vapi_bindings`

### Table: consent_events

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | gen_random_uuid() |
| `clinic_id` | UUID NOT NULL | FK → clinics(id) ON DELETE CASCADE |
| `patient_id` | UUID | FK → patients(id) ON DELETE SET NULL, nullable |
| `appointment_request_id` | UUID | FK → appointment_requests(id) ON DELETE SET NULL, nullable |
| `consent_subject_type` | TEXT NOT NULL | Default: 'patient' |
| `consent_subject_ref` | TEXT | Opaque reference, no PHI |
| `purpose` | TEXT NOT NULL | CHECK constraint (5 valid values) |
| `scope` | TEXT NOT NULL | Consent scope description |
| `channel` | TEXT NOT NULL | CHECK constraint (6 valid values) |
| `language` | TEXT NOT NULL | CHECK constraint (de/en/ar) |
| `consent_text_version` | TEXT NOT NULL | Version tag for the consent text |
| `consent_text_snapshot` | TEXT NOT NULL | Immutable snapshot of text shown to user |
| `granted` | BOOLEAN NOT NULL | Default: true |
| `revoked_at` | TIMESTAMPTZ | Null = active |
| `revoked_by_user_id` | UUID | |
| `revocation_reason` | TEXT | |
| `captured_by_user_id` | UUID | |
| `captured_by_system` | TEXT | |
| `source_ip_hash` | TEXT | Hashed, not raw IP |
| `user_agent_hash` | TEXT | Hashed, not raw UA |
| `metadata` | JSONB NOT NULL | Default: {} |
| `production_phi_enabled` | BOOLEAN NOT NULL | Always false — enforced by CHECK |
| `created_at` | TIMESTAMPTZ NOT NULL | Default: now() |
| `updated_at` | TIMESTAMPTZ NOT NULL | Default: now() |

### CHECK Constraints

- `consent_events_production_phi_check`: `production_phi_enabled = false`
- `consent_events_channel_check`: `channel IN ('onboarding_form','intake_link','phone_call','staff_console','developer_console','import_demo')`
- `consent_events_language_check`: `language IN ('de','en','ar')`
- `consent_events_purpose_check`: `purpose IN ('appointment_intake','patient_history_collection','phone_history_questions','demo_seed','data_processing_acknowledgement')`

### Indexes (9 total)

`idx_consent_events_clinic_id`, `idx_consent_events_patient_id`, `idx_consent_events_appointment_request_id`, `idx_consent_events_purpose`, `idx_consent_events_channel`, `idx_consent_events_language`, `idx_consent_events_granted`, `idx_consent_events_created_at`, `idx_consent_events_revoked_at`

## Schemas

**File:** `backend/app/schemas/consent_event.py`

- `ConsentEventCreate` — validates purpose, channel, language enums; rejects empty required fields; rejects metadata keys containing forbidden patterns (diagnosis, medical_advice, triage, prescription, sk-, vapi_live, jwt, password, secret).
- `ConsentEventRead` — read model with all DB columns.
- `ConsentEventRevoke` — `revocation_reason` + optional `revoked_at`.
- `ConsentEventResponse` — `ok`, `event`, optional `message`, `production_phi_enabled=False`.
- `ConsentEventListResponse` — `ok`, `events`, `total`, `production_phi_enabled=False`.

## Repository

**File:** `backend/app/db/repositories/consent_event_repo.py`

All SQL is parameterised. All queries are tenant-scoped by `clinic_id`. No DELETE.

| Function | Description |
|---|---|
| `create_consent_event` | INSERT RETURNING * — validates enums before SQL |
| `get_consent_event_by_id` | SELECT by UUID |
| `list_consent_events_for_clinic` | ORDER BY created_at DESC, LIMIT up to 200 |
| `list_consent_events_for_patient` | Scoped by clinic_id AND patient_id |
| `revoke_consent_event` | UPDATE revoked_at/reason, RETURNING * |
| `has_valid_consent_for_purpose` | Boolean EXISTS check: granted=true AND revoked_at IS NULL |

Errors: `InvalidConsentEventError`, `ConsentEventNotFoundError`.

## Service

**File:** `backend/app/services/consent_ledger.py`

Orchestrates clinic/patient/appointment-request existence checks before any write.

| Function | Description |
|---|---|
| `create_consent_event` | Verifies clinic, optional patient, optional appt-request; creates; injects `production_phi_enabled=False` |
| `get_consent_event` | Pass-through with `production_phi_enabled=False` injection |
| `list_clinic_consent_events` | Verifies clinic; lists; injects flag |
| `revoke_consent_event` | Revokes; raises `ConsentEventNotFoundError` if row missing |
| `assert_valid_consent_for_history_write` | **Gate check** — validates event exists, same clinic, granted=True, not revoked, purpose is a history write purpose, phi disabled |

### History Write Gate

`assert_valid_consent_for_history_write` must be called before any longitudinal patient history write. Valid purposes for history writes:

```
patient_history_collection
phone_history_questions
```

Errors raised: `ConsentValidationError` with descriptive messages.

## API Routes

**File:** `backend/app/api/routes/consent_events.py`
**Tag:** `consent-events`

All routes require authenticated session (`get_current_user`). No public access.

| Method | Path | Status | Description |
|---|---|---|---|
| POST | `/clinics/{clinic_id}/consent-events` | 201 | Record consent event |
| GET | `/clinics/{clinic_id}/consent-events` | 200 | List clinic consent events |
| GET | `/consent-events/{consent_event_id}` | 200 | Get single event |
| PATCH | `/consent-events/{consent_event_id}/revoke` | 200 | Revoke (append-only) |

No DELETE route exists.

## Consent Required Before History Write

Any future module that writes longitudinal patient history data **must** call `assert_valid_consent_for_history_write` before writing. This gate is the purpose of this module.

The consent event ID must be passed to the history write operation and validated at service layer entry. No bypass. No default-to-granted. Explicit consent only.

## Safety Summary

| Invariant | Enforcement |
|---|---|
| `production_phi_enabled = False` | DB CHECK + service injection + route response |
| No DELETE | No DELETE SQL, no DELETE route |
| No PHI | No PHI columns; no raw names, dates, or identifiers |
| No diagnosis | Vocabulary check in tests; not in any source file |
| No medical advice | Vocabulary check in tests; not in any source file |
| No triage | Not in any source file |
| Metadata safety | Schema rejects keys with forbidden patterns |
| Append-only | Revocation uses `revoked_at`; original row preserved |
| Consent gate | `assert_valid_consent_for_history_write` must precede any history write |

## Files Changed

| File | Action |
|---|---|
| `backend/migrations/versions/0006_consent_events.py` | New |
| `backend/app/db/schema.sql` | Updated — consent_events table added |
| `backend/app/schemas/consent_event.py` | New |
| `backend/app/db/repositories/consent_event_repo.py` | New |
| `backend/app/services/consent_ledger.py` | New |
| `backend/app/api/routes/consent_events.py` | New |
| `backend/app/api/router.py` | Updated — consent_events router registered |
| `backend/tests/test_patient_history_consent_ledger_foundation.py` | New |
| `docs/architecture/PATIENT_HISTORY_CONSENT_LEDGER_FOUNDATION.md` | New |

## Next Module

Sprint 20 / Module 149 — Patient History Data Model Foundation

Builds the `patient_history_entries` table and repository. Requires a valid consent event (via the gate established in this module) before any write is permitted.
