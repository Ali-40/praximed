# Sprint 20 / Module 154 — Doctor Review & Merge UI

Status: pending implementation.

## Context

Module 153 complete (AI Structuring Service Foundation):
- patient_history_structuring_runs and patient_history_proposals tables created.
- Local deterministic demo extraction maps intake answers to FHIR-typed proposals.
- All proposals land as proposal_status=unverified.
- Staff/doctor review required before any approval. No auto-approval.
- No patient_history_* writes occurred in Module 153.
- Production PHI remains NO-GO.

## Goal

Allow staff and doctors to review unverified history proposals, approve them
(merge into patient_history_* entries), or reject/archive them.
No auto-approval. Staff/doctor must explicitly act on each proposal.

## What Module 154 must implement

### 1. Proposal review backend routes

New routes in `backend/app/api/routes/patient_history_structuring.py` (or new file):

- PATCH /clinics/{clinic_id}/history-proposals/{proposal_id}/merge
  - Auth required (doctor/admin session)
  - Validates proposal is in unverified status
  - Creates corresponding patient_history_* entry (type determined by history_type)
  - Updates proposal_status = "merged", sets merged_history_entry_id
  - Returns: merged entry ID
  - No diagnosis. No triage. No treatment recommendation.
  - All merged entries must still be marked synthetic_demo=true, production_phi_enabled=false

No DELETE. No bulk operations. One proposal at a time.

### 2. patient_history_* write layer

The merge step creates entries in the appropriate patient_history_* tables
(conditions, medications, allergies, etc.) with:
- source_type = "ai_proposal"
- source_proposal_id = proposal_id
- status = "active" (or equivalent reviewed status)
- Staff must set their user ID as reviewed_by

### 3. Frontend review UI

`frontend/app/developer-console/history-proposals/page.tsx` (new):
- Dark admin console theme
- List all unverified proposals for a clinic
- Per-proposal actions: Approve (merge) / Reject / Archive Demo
- Show extraction_confidence (labeled as "Extraction confidence only — not a clinical judgment")
- Show fhir_resource_type and history_type
- Show proposed_fields
- No diagnosis display. No risk score. No triage score.
- Show extraction_note on every card

### 4. Tests

`backend/tests/test_doctor_review_merge_foundation.py` (new — ≥60 tests):
- Merge route requires auth
- Merge creates patient_history_* entry
- Merge updates proposal_status to merged
- Cannot merge an already-rejected proposal
- Cannot merge with phi=true
- Reject route remains functional
- No auto-approval path exists

### 5. Docs

- `docs/architecture/DOCTOR_REVIEW_MERGE_FOUNDATION.md` (new)
- `docs/claude/CURRENT_STATE.md` — Module 154 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 155

## Constraints

- No auto-approval — staff/doctor must act on each proposal explicitly
- No diagnosis. No medical advice. No triage. No treatment recommendation.
- production_phi_enabled always False
- synthetic_demo always True
- All patient_history_* writes must be traceable to a proposal and a reviewer
- Full test suite must remain green
- Commit message:
  Sprint 20 / Module 154 — Doctor review and merge UI foundation
