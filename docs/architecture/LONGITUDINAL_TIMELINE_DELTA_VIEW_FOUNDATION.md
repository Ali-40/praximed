# Longitudinal Timeline and Delta View Foundation

**Sprint 20 / Module 156**
**Date:** 2026-07-09
**Status:** Complete

## Purpose

After intake → AI structuring → staff review/merge (Modules 151–154), the doctor needs one
clean chronological view of what is approved, what is still unverified, and what changed
since the last appointment. This module creates that aggregated timeline foundation.

No diagnosis. No medical advice. No triage scoring. No treatment recommendations.
No new patient history writes. No external LLM calls.
Approved history and unverified proposals are clearly and permanently separated.
Synthetic/fake staging only. Production PHI remains NO-GO.

## Why Timeline Comes After Review/Merge

The timeline is only meaningful once the review/merge layer (Module 154) exists.
Without it, all history proposals would remain unverified and the timeline would
only show workflow events (intake, consent, appointments) with no approved clinical content.

The chronological order is:
1. Patient submits intake (Module 151) → consent_event + intake_submission created
2. AI structuring (Module 153) → history_proposals created as unverified
3. Staff review/merge (Module 154) → approved patient_history_* rows created
4. Timeline view (this module) aggregates all of the above into one view

## Timeline Sources

Six event source types are aggregated, all read from existing tables:

| item_type           | item_source                      | Source table(s)                          |
|---------------------|----------------------------------|------------------------------------------|
| appointment_request | appointment_requests             | appointment_requests                     |
| intake_submission   | patient_intake_submissions       | patient_intake_submissions               |
| consent_event       | consent_events                   | consent_events                           |
| structuring_run     | patient_history_structuring_runs | patient_history_structuring_runs         |
| history_proposal    | patient_history_proposals        | patient_history_proposals                |
| approved_history    | patient_history_*                | 7 approved history tables (see below)    |

### Approved History Tables

All 7 FHIR-aligned tables are queried for `status = 'approved'` rows only:
- `patient_history_allergies` → history_type=allergies, fhir=AllergyIntolerance
- `patient_history_medications` → history_type=medications, fhir=MedicationStatement
- `patient_history_conditions` → history_type=conditions, fhir=Condition
- `patient_history_procedures` → history_type=procedures, fhir=Procedure
- `patient_history_immunizations` → history_type=immunizations, fhir=Immunization
- `patient_history_family_history` → history_type=family-history, fhir=FamilyMemberHistory
- `patient_history_social_history` → history_type=social-history, fhir=Observation

Only `status = 'approved'` rows appear as `approved_history` items.
`status = 'unverified'` or `status = 'rejected'` rows from patient_history_* are excluded.

## Approved History vs Unverified Proposals

This distinction is critical:

| Property | approved_history item | unverified_proposal item |
|---|---|---|
| item_type | approved_history | history_proposal |
| source | patient_history_* table | patient_history_proposals table |
| is_approved_history | true | false |
| is_unverified_proposal | false | true (if status=unverified) |
| Badge | APPROVED HISTORY (green) | UNVERIFIED PROPOSAL (amber) |
| Staff action required? | Already done | Still pending |

An unverified proposal from `patient_history_proposals` is never shown as `approved_history`.
A rejected proposal is not shown as approved history.
The two streams are never mixed.

## Delta Since Last Visit

`GET /clinics/{clinic_id}/patients/{patient_id}/timeline/delta`

Uses the most recent `appointment_request` for the patient as the visit anchor.
Returns only timeline events newer than that anchor's `created_at`.

If no appointment_request exists for the patient:
- `delta_anchor_status = "no_prior_visit_anchor"`
- All available timeline events are returned
- The caller is informed that there is no prior visit anchor

If an anchor is found:
- `delta_anchor_status = "changed_since_last_visit"`
- `delta_anchor_at` = the appointment's `created_at` timestamp
- Only events after that timestamp are returned

`GET /clinics/{clinic_id}/patients/{patient_id}/timeline/delta-since`

Accepts an explicit `since` ISO datetime query parameter.
Returns only events after the given datetime.
Useful for custom date ranges independent of visit history.

## Tenant Isolation

All queries include both `clinic_id` and `patient_id` in the WHERE clause.
No cross-clinic data is accessible.
No wildcard patient queries (patient_id is required on all timeline queries).

## No New Writes

This module creates no new tables, no new rows.
No migration is included. All queries are read-only (SELECT).
No `INSERT`, `UPDATE`, or `DELETE` is issued by this module.

## Routes

All routes require authenticated session. No public routes.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/clinics/{clinic_id}/patients/{patient_id}/timeline` | Full chronological timeline |
| GET | `/clinics/{clinic_id}/patients/{patient_id}/timeline/delta` | Delta since last visit anchor |
| GET | `/clinics/{clinic_id}/patients/{patient_id}/timeline/delta-since` | Delta since explicit date (`?since=...`) |

No DELETE. No POST. No write routes.

## No Diagnosis, No Medical Advice, No Treatment Recommendations, No Triage Scoring, No Auto-Approval

- No auto-approval. No auto-merge. This module only reads data — it writes nothing.
- No diagnosis fields in any response
- No clinical_confidence or risk_score surfaced
- No medical advice generated
- No treatment recommendations
- No triage scoring
- `extraction_confidence` labeled "Extraction confidence only — not a medical judgment."
- No LLM call made to interpret or summarize the timeline
- No medical interpretation generated

## Frontend Review UI

`/developer-console/patient-timeline`

Dark developer/admin theme. Features:
- Clinic ID + patient ID inputs
- include_unverified checkbox (default checked)
- Load timeline button
- Load delta since last visit button
- Timeline summary: counts by type
- APPROVED HISTORY badge (green) for approved patient_history_* rows
- UNVERIFIED PROPOSAL badge (amber) for unverified proposals
- CONSENT / INTAKE / APPOINTMENT / STRUCTURING badges for workflow events
- Delta view panel: `changed_since_last_visit` or `no_prior_visit_anchor` status badge
- Safety panel: explicit prohibition list

## Synthetic/Fake Staging Only

- `production_phi_enabled = false` enforced at schema, service, and route levels
- `synthetic_demo = true` on all items
- No real patient data — synthetic/fake staging only
- Production PHI remains NO-GO

## Files Added

- `backend/app/schemas/patient_timeline.py`
- `backend/app/db/repositories/patient_timeline_repo.py`
- `backend/app/services/patient_timeline.py`
- `backend/app/api/routes/patient_timeline.py`
- `frontend/app/developer-console/patient-timeline/page.tsx`
- `backend/tests/test_longitudinal_timeline_delta_view_foundation.py`
- `docs/architecture/LONGITUDINAL_TIMELINE_DELTA_VIEW_FOUNDATION.md`

## Files Modified

- `backend/app/api/router.py` — added `patient_timeline` router
- `frontend/lib/api.ts` — added 3 timeline API helpers
- `frontend/app/developer-console/page.tsx` — added "Longitudinal Patient Timeline" card

## What Remains

- Live smoke evidence (Module 157): deploy, load staging timeline with real synthetic data
- Patient story pre-visit narrative generation
- Clinical dashboard integration (outside developer console)
- Full Arabic/RTL foundation
- Gulf readiness architecture review
- Production readiness/security/legal gates
