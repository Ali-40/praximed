# Sprint 2 / Module 33 — Doctor Review and Approval Workflow

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–32: all committed.

Do not modify completed modules unless absolutely required.

## Task scope
Implement the doctor review and approval workflow service for clinical summary drafts.

## Purpose
After a clinical summary draft is generated (Module 32), a doctor must review and either approve or reject it. This module provides the service layer that orchestrates the approval/rejection flow, enforces role-based safety constraints, and persists the outcome via the consultation repository.

## Create or update only

1. `backend/app/modules/clinical_summary/review_workflow.py`
2. `backend/tests/test_review_workflow.py`
3. `docs/claude/CURRENT_STATE.md`
4. `docs/claude/NEXT_MODULE.md`

## Key design

- No LLM calls, no external services.
- Approval is only allowed when `draft_summary` is present and `approval_status` is `pending_review`.
- Rejection requires a non-empty `rejected_reason`.
- Every approval must supply a non-empty `approved_by_user_id`.
- Approved summary must retain `doctor_review_required=True` and `schema_version`.
- Exceptions: `ReviewWorkflowError` (base), `InvalidReviewInputError`, `ReviewStateError`.

## Public functions

1. `validate_review_request(clinic_id, session_id, approved_by_user_id)` → dict
2. `validate_rejection_request(clinic_id, session_id, approved_by_user_id, rejected_reason)` → dict
3. `validate_draft_summary_for_approval(draft_summary)` → dict  — checks schema_version, doctor_review_required, required sections
4. `build_approved_summary(draft_summary, approved_by_user_id)` → dict  — stamps reviewer, approval timestamp marker
5. `approve_clinical_summary(pool, clinic_id, session_id, approved_by_user_id, draft_summary)` → dict (async)
   - Calls `consultation_repo.approve_consultation_summary`
   - Returns `{"ok": True, "consultation": ..., "approved_summary": ..., "message": "..."}`
6. `reject_clinical_summary(pool, clinic_id, session_id, approved_by_user_id, rejected_reason)` → dict (async)
   - Calls `consultation_repo.reject_consultation_summary`
   - Returns `{"ok": True, "consultation": ..., "message": "..."}`

## Tests (35 tests)

1–3. validate_review_request: valid, empty clinic_id, empty session_id.
4–6. validate_review_request: empty approved_by_user_id.
7–9. validate_rejection_request: valid, empty rejected_reason, whitespace-only rejected_reason.
10–13. validate_draft_summary_for_approval: valid draft, missing schema_version, doctor_review_required=False, missing required section.
14–16. build_approved_summary: returns dict with schema_version, retains doctor_review_required=True, stamps reviewed_by.
17–20. approve_clinical_summary: calls repo, passes approved_summary, ok true, includes approved_summary.
21–23. approve_clinical_summary: message mentions approved, maps repo RuntimeError to ReviewWorkflowError, validates empty clinic_id.
24–27. reject_clinical_summary: calls repo, ok true, message mentions rejected, maps repo RuntimeError to ReviewWorkflowError.
28–30. reject_clinical_summary: validates empty clinic_id, validates empty session_id, validates empty rejected_reason.
31–32. ReviewStateError raised when draft_summary fails validation in approve flow.
33–35. No real database, no external service, no LLM call.

## Acceptance criteria

- All Module 33 tests pass.
- All previous tests still pass.
- No real database connection is used.
- No external services are called.
- No LLM call is made.
- No diagnosis or treatment advice generation exists.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 33 — Doctor review and approval workflow`
