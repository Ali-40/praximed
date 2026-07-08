# Doctor Review & Merge UI Foundation

**Sprint 20 / Module 154**
**Date:** 2026-07-09
**Status:** Complete

## Purpose

This module creates the human-in-the-loop safety bridge between unverified AI-structured
patient history proposals (from Module 153) and approved patient_history_* entries.

PraxisMed's core value: AI organizes patient-provided information into reviewable proposals.
The doctor or staff member decides what enters the longitudinal patient history.
No auto-approval. No AI writes to approved history. No automatic confirmation.

## Why Review/Merge Is the Safety Bridge

Every proposal from the AI structuring service (Module 153) starts as `status=unverified`.
No proposal can become an approved patient history entry without:
1. An authenticated staff/doctor user loading the review queue
2. Inspecting the proposal detail and optionally editing the structured fields
3. Explicitly ticking the "I confirm staff/doctor review before merging" checkbox
4. Submitting the approve-merge action

The approved patient_history_* row is only created after this explicit human action.

## Proposal Queue

GET `/clinics/{clinic_id}/patient-history-review-queue`

Returns all unverified (or filtered by status) proposals for a clinic.
Supports filtering by patient_id, history_type, and status.
All items include `extraction_confidence` labeled as "Extraction confidence only — not a medical judgment."

## Staff/Doctor Review Required

Every proposal from Module 153 has `staff_review_required = true` enforced by DB CHECK.
The service layer validates this flag before allowing merge.
No proposal with `staff_review_required = false` can be merged.

## Approve/Merge Behavior

1. Load proposal by ID, verify clinic_id matches.
2. Assert `proposal_status = unverified`. Reject if already merged/rejected.
3. Assert `staff_review_required = true`.
4. Assert `production_phi_enabled = false` on proposal.
5. Assert `patient_id` is present (required for patient_history_* write).
6. Validate `edited_fields` — reject forbidden keys:
   `clinical_confidence`, `diagnosis_score`, `risk_score`, `triage_score`,
   `medical_advice`, `treatment_recommendation`, `diagnosis_generated`, `auto_approved`, `auto_confirmed`.
7. Call `assert_valid_consent_for_history_write(...)` — consent gate enforced.
8. Create exactly ONE row in the matching `patient_history_*` table:
   - `status = approved`
   - `source_type = ai_proposal`
   - `source_ref = proposal:{proposal_id}`
   - `consent_event_id` copied from proposal
   - `fhir_payload` from edited/approved payload
   - `production_phi_enabled = false`
9. Update proposal: `proposal_status = merged`, set `merged_history_entry_id`.
10. Return merge result with `merged_history_entry_id`.

## Reject Behavior

PATCH `/patient-history-proposals/{proposal_id}/reject-review`

- Only unverified proposals can be rejected.
- Sets `proposal_status = rejected`, `rejected_reason`, `reviewed_by_user_id`, `reviewed_at`.
- No `patient_history_*` row created.
- Returns confirmation.

## Edited Fields Before Merge

The staff can edit the `proposed_fields` JSON before confirming the merge.
Forbidden keys are rejected by both Pydantic schema validation and service-level guard.
The primary text field (e.g. `substance_text` for allergies) is extracted from `edited_fields`,
falling back to `proposed_fields.raw_answer` if not provided.

## Consent Gate Before Merge

`assert_valid_consent_for_history_write(pool, clinic_id, consent_event_id, purpose)`
is called before any history write. If consent is missing, revoked, or wrong clinic, merge fails.

## patient_history_* Row Created Only After Staff Action

The approved row is written using the existing `patient_history_repo` create functions:
- `create_allergy_history` for allergies
- `create_medication_history` for medications
- `create_condition_history` for conditions
- `create_procedure_history` for procedures
- `create_immunization_history` for immunizations
- `create_family_history` for family-history
- `create_social_history` for social-history

All rows get `status = approved`, `source_type = ai_proposal`.

## No Auto-Approval

There is no function, route, or code path that creates an approved history row
without explicit `confirm_staff_review = true` from the request body.

## No AI Diagnosis, No Medical Advice, No Treatment Recommendations, No Triage Scoring

- No diagnosis fields allowed in `edited_fields`
- No medical advice fields allowed
- No treatment recommendation fields allowed
- No triage score fields allowed
- `extraction_confidence` is extraction quality only — never clinical confidence

## Extraction Confidence

`extraction_confidence` (0.0–1.0) measures how well the free-text answer maps to
a FHIR field. It is NOT a clinical confidence score, risk score, or diagnosis probability.
It is labeled "Extraction confidence only — not a medical judgment." everywhere it appears.

## Synthetic/Fake Staging Only

- `synthetic_demo = true` on all proposals
- `production_phi_enabled = false` enforced at DB, service, and route levels
- No real patient data — synthetic/fake staging only
- Production PHI remains NO-GO

## Routes

All routes require authenticated session. No public routes.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/clinics/{clinic_id}/patient-history-review-queue` | List review queue |
| GET | `/patient-history-proposals/{proposal_id}/review` | Get proposal detail |
| PATCH | `/patient-history-proposals/{proposal_id}/approve-merge` | Merge after staff confirmation |
| PATCH | `/patient-history-proposals/{proposal_id}/reject-review` | Reject proposal |

No DELETE route. No bulk approval. No auto-merge endpoint.

## Frontend Review UI

`/developer-console/history-review`

Dark developer/admin theme. Features:
- Clinic ID input + patient_id filter + history_type filter
- Queue list with extraction confidence labeled correctly
- Detail panel with proposed_fields JSON, consent/intake IDs
- Editable JSON field block
- Mandatory "I confirm staff/doctor review before merging" checkbox
- Approve & merge button (disabled until checkbox confirmed)
- Reject panel with reason

Success: "Proposal merged into patient history after staff review."
Reject: "Proposal rejected."
Errors: explicit messages for missing auth, ineligible proposals, missing patient.

## Files Added

- `backend/app/schemas/patient_history_review.py`
- `backend/app/services/patient_history_review.py`
- `backend/app/api/routes/patient_history_review.py`
- `frontend/app/developer-console/history-review/page.tsx`
- `backend/tests/test_doctor_review_merge_ui_foundation.py`
- `docs/architecture/DOCTOR_REVIEW_MERGE_UI_FOUNDATION.md`

## Files Modified

- `backend/app/api/router.py` — added `patient_history_review` router
- `frontend/lib/api.ts` — added 4 review API helpers
- `frontend/app/developer-console/page.tsx` — added "Patient History Review" card

## What Remains

- Live smoke evidence (Module 155): deploy, create intake → structure → review → merge
- Longitudinal history timeline & delta view
- Patient story pre-visit narrative generation
- Full Arabic/RTL foundation
- Gulf readiness architecture review
- Production readiness/security/legal gates
