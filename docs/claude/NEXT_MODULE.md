# Sprint 20 / Module 155 — Live Doctor Review & Merge Smoke Evidence

Status: pending.

## Context

Module 154 complete (Doctor Review & Merge UI Foundation):
- Review queue, proposal detail, approve-merge, and reject routes implemented (all auth-protected).
- Frontend review UI at /developer-console/history-review with mandatory staff-confirmation checkbox.
- All proposals remain status=unverified until explicit staff merge action.
- No auto-approval. No auto-merge. No external LLM. No PHI.
- 4925/4925 backend tests passing. Frontend build clean.
- Production PHI remains NO-GO.

## Goal

Produce live end-to-end smoke evidence that the full intake → structure → review → merge pipeline
works in the deployed staging environment. No new backend code. Docs-only module.

## What Module 155 must produce

### 1. Evidence document

`docs/runtime/LIVE_DOCTOR_REVIEW_MERGE_SMOKE_EVIDENCE.md` (new):

Record each step of the pipeline with observed responses:

1. Create intake link → GET /developer-console/intake-links
2. Fill intake form with synthetic patient answers
3. Trigger structuring → POST /clinics/{clinic_id}/intake-submissions/{submission_id}/structure
4. List proposals → GET /clinics/{clinic_id}/history-proposals → observe status=unverified
5. Load review queue → GET /clinics/{clinic_id}/patient-history-review-queue
6. Load proposal detail → GET /patient-history-proposals/{proposal_id}/review
7. Approve-merge (with confirm_staff_review=true) → PATCH /patient-history-proposals/{proposal_id}/approve-merge
   → observe merged_history_entry_id, proposal_status=merged
8. Verify proposal in queue no longer appears as unverified
9. Reject a second proposal → PATCH /patient-history-proposals/{proposal_id}/reject-review
   → observe proposal_status=rejected

### 2. Constraints on evidence

- All data must be synthetic/demo (synthetic_demo=true, production_phi_enabled=false)
- No real patient names, DOBs, or health data
- No auto-approval — confirm_staff_review=true must be present in the approve-merge step
- No external LLM calls — structuring uses local deterministic extraction only
- extraction_confidence labeled as "Extraction confidence only — not a medical judgment." in evidence
- production_phi_enabled=false confirmed in all responses documented
- Production PHI remains NO-GO

### 3. Tests

`backend/tests/test_live_doctor_review_merge_smoke_evidence.py` (new — ≥20 tests):

Static evidence validation tests (no live API calls):
- Evidence doc exists
- Evidence doc mentions Module 155
- Evidence doc mentions merged_history_entry_id (merge confirmed)
- Evidence doc mentions proposal_status=merged
- Evidence doc mentions proposal_status=rejected
- Evidence doc mentions synthetic_demo or synthetic
- Evidence doc mentions production_phi_enabled=false
- Evidence doc mentions staff review confirmed or confirm_staff_review
- Evidence doc mentions extraction confidence labeled correctly
- Evidence doc mentions no auto-approval
- Evidence doc does not mention real patient names (no "John", "Jane", "Patient Name")
- Evidence doc does not mention production PHI
- Evidence doc has structuring step
- Evidence doc has review queue step
- Evidence doc has approve-merge step
- Evidence doc has reject step
- No DATABASE_URL, no JWT_SECRET, no sk- keys in evidence doc
- Evidence doc mentions no external LLM or local extraction

### 4. Docs updates

- docs/claude/CURRENT_STATE.md — Module 155 entry
- docs/claude/NEXT_MODULE.md — updated to Module 156

## Constraints

- No new backend code — docs/tests only
- All evidence must be synthetic staging — no real PHI
- No diagnosis, no medical advice, no triage scoring in evidence
- production_phi_enabled=False confirmed in all documented responses
- Full test suite must remain green
- Frontend build must remain clean
- Commit message:
  Sprint 20 / Module 155 — Live doctor review and merge smoke evidence
