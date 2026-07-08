# AI Structuring Service Foundation

**Sprint 20 / Module 153**
**Date:** 2026-07-09
**Status:** Complete

## Overview

Adds the proposal layer between raw intake submissions and approved patient history entries.
Local deterministic demo extraction only in this module — no external LLM, no API keys,
no Anthropic/OpenAI/Vapi calls.

All proposals remain `status=unverified` until a staff member or doctor explicitly approves
them in a future module. No auto-approval. No diagnosis. No medical advice. No triage scoring.
`extraction_confidence` is extraction quality only, never a clinical judgment.

## Scope

Module 153 does NOT write to `patient_history_*` tables. The proposal layer is a staging
buffer — proposals sit as `unverified` until a future review/merge module handles approval.

## New Tables

### `patient_history_structuring_runs`

One record per structuring attempt on an intake submission. Stores:
- Which submission and consent_event were processed
- Which provider ran extraction (`local_demo_extractor` in this module)
- How many proposals were created
- Status of the run (`completed`, `failed`, `skipped`)

DB constraints enforce `synthetic_demo = true`, `production_phi_enabled = false`,
`proposals_count >= 0`. No `raw_prompt` or `raw_model_response` column exists.

### `patient_history_proposals`

One record per extracted history item. Stores:
- `history_type` (allergies, medications, conditions, procedures, immunizations, family-history, social-history)
- `fhir_resource_type` (AllergyIntolerance, MedicationStatement, Condition, Procedure, Immunization, FamilyMemberHistory, Observation)
- `proposed_fields` and `proposed_fhir_payload` as JSONB
- `extraction_confidence` (NUMERIC 0.0–1.0) — extraction quality only
- `staff_review_required = true` (DB CHECK, always enforced)
- `proposal_status` defaults to `unverified`

Allowed status transitions in this module: `rejected`, `archived_demo`.
`merged` is reserved for the future doctor review/merge module.

## Local Deterministic Extraction

The `local_demo_extractor` provider maps intake answers to proposals by following the
`history_target` field on each template question:

| `history_target`    | `history_type`   | `fhir_resource_type`  |
|---------------------|------------------|-----------------------|
| `allergies`         | allergies        | AllergyIntolerance    |
| `medications`       | medications      | MedicationStatement   |
| `conditions`        | conditions       | Condition             |
| `procedures`        | procedures       | Procedure             |
| `immunizations`     | immunizations    | Immunization          |
| `family-history`    | family-history   | FamilyMemberHistory   |
| `social-history`    | social-history   | Observation           |
| `none`              | skipped          | —                     |
| `appointment-context` | skipped        | —                     |

Empty or blank answers are skipped. No scoring, no semantic reasoning.

## Routes

All routes require authenticated session. No public routes in this module.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/clinics/{clinic_id}/intake-submissions/{submission_id}/structure` | Trigger structuring |
| GET | `/clinics/{clinic_id}/history-proposals` | List proposals |
| GET | `/clinics/{clinic_id}/structuring-runs/{run_id}` | Get run + proposals |
| GET | `/clinics/{clinic_id}/structuring-runs/{run_id}/proposals` | List run proposals |
| PATCH | `/clinics/{clinic_id}/history-proposals/{proposal_id}/reject` | Reject proposal |
| PATCH | `/clinics/{clinic_id}/history-proposals/{proposal_id}/archive-demo` | Archive demo proposal |

No DELETE route. No approval route (future module).

## Safety Invariants

- `extraction_confidence` is labeled as extraction confidence only — never clinical confidence.
- No `clinical_confidence`, `diagnosis_score`, `risk_score`, `triage_score`, `medical_advice`,
  or `treatment_recommendation` fields allowed anywhere in the proposal layer.
- `production_phi_enabled = false` enforced at DB CHECK, service, and route levels.
- `synthetic_demo = true` enforced at DB CHECK.
- `staff_review_required = true` enforced at DB CHECK.
- No external API calls. No API keys. No network requests to LLM providers.
- Logs are pseudonymized — no raw answer text, no patient name, no identifiers in log statements.
- All structuring results: `status = unverified`. No path to auto-approved state.

## Files Added

- `backend/migrations/versions/0010_patient_history_structuring.py`
- `backend/app/schemas/patient_history_structuring.py`
- `backend/app/db/repositories/patient_history_structuring_repo.py`
- `backend/app/services/patient_history_structuring.py`
- `backend/app/api/routes/patient_history_structuring.py`
- `backend/tests/test_ai_structuring_service_foundation.py`

## Files Modified

- `backend/app/api/router.py` — added `patient_history_structuring` router
- `backend/app/db/schema.sql` — added both structuring tables

## What This Module Does NOT Do

- No external LLM API calls (Anthropic, OpenAI, Vapi, or any other provider)
- No API keys (ANTHROPIC_API_KEY is a future-module concern)
- No patient_history_* writes (no approved entries created)
- No automatic approval of any proposal
- No diagnosis generation
- No medical advice or treatment recommendations
- No triage scoring or risk scoring
- No production PHI — synthetic/fake staging only

## Next Module

Module 154 — Doctor Review & Merge UI: allow staff/doctors to review proposals,
approve them, and merge approved proposals into `patient_history_*` entries.
