# Patient History Data Model Foundation

**Sprint 20 / Module 149**
**Date:** 2026-07-08
**Status:** Complete

## Purpose

Build the FHIR R4-aligned, tenant-scoped, append-only/versioned patient history data model as the foundation of the Longitudinal Patient History & Anamnesis Engine.

Every history row requires a valid, granted, non-revoked `consent_event_id` — enforced in the service layer via `assert_valid_consent_for_history_write`. No history write may proceed without explicit consent.

No real patient PHI. No diagnosis generated. No medical advice. No treatment recommendations. No triage scoring. Synthetic/fake staging only. Production PHI remains NO-GO.

## Why Consent Ledger Must Come First

Module 148 (consent ledger) is a hard prerequisite. Every patient history row references `consent_events(id)` with `ON DELETE RESTRICT` — meaning a consent event cannot be deleted while any history row references it. The service gate (`assert_valid_consent_for_history_write`) validates:

- consent event exists
- same clinic_id (tenant isolation)
- `granted = true`
- `revoked_at IS NULL`
- purpose is `patient_history_collection` or `phone_history_questions`
- `production_phi_enabled = false`

No bypass. No default-to-granted. Explicit consent is required.

## Seven FHIR R4 Tables

### 1. patient_history_allergies — AllergyIntolerance

Captures patient-reported or staff-entered allergy and intolerance records.

Table-specific columns: `substance_text`, `reaction_text`, `severity`, `clinical_status`, `verification_status`, `category`, `criticality`, `onset_text`.

### 2. patient_history_medications — MedicationStatement

Captures current and historical medication statements.

Table-specific columns: `medication_text`, `dosage_text`, `frequency_text`, `route_text`, `medication_status`, `start_text`, `end_text`, `reason_text`.

### 3. patient_history_conditions — Condition (patient-reported/staff-entered only)

Captures past medical conditions as reported by the patient or entered by staff. **This table stores patient-reported or staff-entered condition history only. No diagnosis is generated here.** Conditions require doctor review and approval before any clinical use.

Table-specific columns: `condition_text`, `clinical_status`, `verification_status`, `onset_text`, `abatement_text`, `body_site_text`, `severity_text`, `patient_reported` (boolean, default true).

### 4. patient_history_procedures — Procedure

Captures past surgical and clinical procedures.

Table-specific columns: `procedure_text`, `performed_text`, `body_site_text`, `outcome_text`, `performer_text`, `reason_text`.

### 5. patient_history_immunizations — Immunization

Captures vaccination history.

Table-specific columns: `vaccine_text`, `occurrence_text`, `lot_number`, `site_text`, `route_text`, `dose_number`, `series_text`, `immunization_status`.

### 6. patient_history_family_history — FamilyMemberHistory

Captures family medical history as reported by the patient.

Table-specific columns: `relationship_text`, `condition_text`, `age_text`, `deceased`, `note_text`.

### 7. patient_history_social_history — Observation (social context only)

Captures non-diagnostic social context (smoking, alcohol, occupation, etc.).

Table-specific columns: `observation_category`, `observation_text`, `value_text`, `period_text`.

Suggested `observation_category` values: `occupation`, `smoking`, `alcohol`, `exercise`, `living_situation`, `other`.

## Common Columns (All Tables)

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | gen_random_uuid() |
| `clinic_id` | UUID NOT NULL | FK → clinics(id), tenant isolation |
| `patient_id` | UUID NOT NULL | FK → patients(id) |
| `appointment_request_id` | UUID | FK → appointment_requests(id), nullable |
| `consent_event_id` | UUID NOT NULL | FK → consent_events(id) ON DELETE RESTRICT |
| `version_group_id` | UUID NOT NULL | Groups all versions of the same entry |
| `version_number` | INTEGER NOT NULL | Default 1, must be ≥ 1 |
| `supersedes_entry_id` | UUID | Points to the entry this corrects |
| `correction_reason` | TEXT | Why a correction was made |
| `status` | TEXT NOT NULL | unverified / approved / rejected / superseded |
| `source_type` | TEXT NOT NULL | staff_console / intake_link / phone_call / ai_proposal / demo_seed / import_demo |
| `source_ref` | TEXT | Opaque source reference |
| `entered_by_user_id` | UUID | Staff member who entered this |
| `reviewed_by_user_id` | UUID | Doctor/staff who reviewed |
| `reviewed_at` | TIMESTAMPTZ | When review happened |
| `review_note` | TEXT | Reviewer note |
| `effective_start_date` | DATE | When condition/medication started |
| `effective_end_date` | DATE | When condition/medication ended |
| `notes` | TEXT | Free-text notes |
| `fhir_resource_type` | TEXT NOT NULL | FHIR R4 resource type name |
| `fhir_payload` | JSONB NOT NULL | Structured FHIR-aligned payload |
| `metadata` | JSONB NOT NULL | Operational metadata |
| `production_phi_enabled` | BOOLEAN NOT NULL | Always false — enforced by DB CHECK |
| `created_at` | TIMESTAMPTZ NOT NULL | Row creation time |
| `updated_at` | TIMESTAMPTZ NOT NULL | Last modification time |

## CHECK Constraints (All Tables)

- `{table}_phi_check`: `production_phi_enabled = false`
- `{table}_status_check`: `status IN ('unverified','approved','rejected','superseded')`
- `{table}_source_type_check`: `source_type IN ('staff_console','intake_link','phone_call','ai_proposal','demo_seed','import_demo')`
- `{table}_version_check`: `version_number >= 1`
- `UNIQUE (version_group_id, version_number)` — prevents duplicate version numbers within a correction chain

## Tenant Isolation and Patient Scoping

All queries must include `clinic_id` and `patient_id`. No cross-clinic data access. The service layer verifies clinic and patient existence before any write.

## consent_event_id Required on Every Row

Every history row has `consent_event_id NOT NULL` referencing `consent_events(id) ON DELETE RESTRICT`. The service gate `assert_valid_consent_for_history_write` is called on every create operation. No history row can be written without a valid, active consent record.

## Append-Only / Versioned Principle

History rows are never deleted. Corrections create a new row with:
- same `version_group_id`
- incremented `version_number`
- `supersedes_entry_id` pointing to the previous row
- `correction_reason` explaining why

The previous row is updated to `status = 'superseded'`. No DELETE route exists at service or API level.

## Status Model

| Status | Description |
|---|---|
| `unverified` | Default on create — awaiting staff/doctor review |
| `approved` | Doctor or authorised staff confirmed this entry |
| `rejected` | Entry rejected after review (kept for audit) |
| `superseded` | Replaced by a newer version |

**Staff/doctor review is required** before any entry reaches `approved`. The API provides a PATCH status endpoint for this workflow.

## No Deletion Route

There is no DELETE endpoint. The service layer has no delete function. Corrections supersede; reviews approve or reject; nothing is removed. This ensures a complete audit trail.

## Indexes

Each table has 9 indexes: `clinic_id`, `patient_id`, `consent_event_id`, `appointment_request_id`, `status`, `source_type`, `version_group_id`, `created_at`, `production_phi_enabled`.

## Safety Summary

| Invariant | Enforcement |
|---|---|
| `production_phi_enabled = false` | DB CHECK + service injection + route response |
| No DELETE | No DELETE SQL, no DELETE route |
| Consent required | Service gate on every write |
| No diagnosis generated | Not in any service or route logic |
| No medical advice | Not in any service or route logic |
| No treatment recommendations | Not in service or routes |
| No triage scoring | Not in service or routes |
| Staff/doctor review required | `status = 'unverified'` default, PATCH route for approval |
| Tenant isolation | `clinic_id` scoped on all queries |
| Append-only | Corrections create new rows; `superseded` status for old ones |

## API Routes

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/clinics/{clinic_id}/patients/{patient_id}/history/{history_type}` | required | Create history entry |
| GET | `/clinics/{clinic_id}/patients/{patient_id}/history` | required | Full timeline |
| GET | `/clinics/{clinic_id}/patients/{patient_id}/history/{history_type}` | required | List by type |
| GET | `/patient-history/{history_type}/{entry_id}` | required | Get single entry |
| PATCH | `/patient-history/{history_type}/{entry_id}/status` | required | Update review status |

No DELETE route.

## Files Changed

| File | Action |
|---|---|
| `backend/migrations/versions/0007_patient_history_data_model.py` | New |
| `backend/app/db/schema.sql` | Updated — 7 history tables added |
| `backend/app/schemas/patient_history.py` | New |
| `backend/app/db/repositories/patient_history_repo.py` | New |
| `backend/app/services/patient_history.py` | New |
| `backend/app/api/routes/patient_history.py` | New |
| `backend/app/api/router.py` | Updated |
| `backend/tests/test_patient_history_data_model_foundation.py` | New |
| `docs/architecture/PATIENT_HISTORY_DATA_MODEL_FOUNDATION.md` | New |

## What Remains

The following features are out of scope for this module and remain for future sprints:

- **Anamnesis template engine** — clinic-configurable questionnaire templates per specialty
- **Intake link flow** — patient-facing URL for self-reported history via consent
- **AI structuring service** — proposed FHIR structuring from free-text (Module 150+)
- **Doctor review and merge UI** — frontend for reviewing, editing, and approving entries
- **Longitudinal timeline view** — chronological patient history dashboard
- **Patient story / pre-visit narrative** — condensed history summary for doctor use
- **Arabic/RTL foundation** — full Arabic UI support for Gulf markets
- **Gulf readiness architecture** — Saudi Arabia and UAE deployment considerations
