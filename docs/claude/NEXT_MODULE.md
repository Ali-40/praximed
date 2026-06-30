# Sprint 2 / Module 33 — Doctor Review and Approval Workflow

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–32: all committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create a doctor review workflow service for clinical summary drafts.

## Purpose
PraxisMed must keep AI-generated clinical summaries in draft state until a human doctor reviews and approves them. This service will:

- validate draft summaries before review
- build a review package
- approve doctor-edited summaries
- reject draft summaries with a reason
- call consultation_repo approval/rejection functions
- never auto-approve AI output

This module does not create API routes.
This module does not create frontend.
This module does not call OpenAI or any LLM.
This module does not generate diagnosis or treatment advice.
This module does not modify schema.

## Create or update only

1. `backend/app/modules/clinical_summary/review_workflow.py`
2. `backend/app/modules/clinical_summary/__init__.py`
3. `backend/tests/test_review_workflow.py`
4. `docs/claude/CURRENT_STATE.md`
5. `docs/claude/NEXT_MODULE.md`

Do not create API routes yet.
Do not modify consultation routes.
Do not modify `consultation_repo.py` unless absolutely required by tests.
Do not modify `summary_builder.py` unless absolutely required by tests.
Do not create real LLM integration.
Do not build frontend.
Do not build authentication.
Do not use a real database in tests.

## Service requirements

### Exceptions
- `ReviewWorkflowError`
- `InvalidReviewInputError`

### Constants
- `REVIEW_SCHEMA_VERSION = "doctor_review_workflow.v1"`

### Public functions

1. `validate_review_context(clinic_id, session_id)` → dict
2. `validate_reviewer_user_id(reviewer_user_id)` → str
3. `validate_draft_ready_for_review(draft_summary)` → dict
4. `build_review_package(clinic_id, session_id, draft_summary, transcript_text, patient_context, consultation_context)` → dict
5. `validate_approved_summary(approved_summary, approved_by_user_id)` → dict
6. `approve_summary_after_review(pool, clinic_id, session_id, approved_summary, approved_by_user_id)` → dict (async)
7. `validate_rejection_reason(rejected_reason)` → str
8. `reject_summary_after_review(pool, clinic_id, session_id, rejected_reason, rejected_by_user_id)` → dict (async)

## Tests (33 tests)

1–3. validate_review_context: valid, empty clinic_id, empty session_id.
4–5. validate_reviewer_user_id: valid, empty.
6–11. validate_draft_ready_for_review: valid, non-dict, doctor_review_required=False, no_diagnosis_generated=False, no_treatment_advice_generated=False, top-level diagnosis key.
12–17. build_review_package: returns pending_doctor_review, includes review_instructions, preserves transcript_text, preserves patient_context, rejects non-dict patient_context, rejects non-dict consultation_context.
18–21. validate_approved_summary: valid, empty dict, empty approved_by_user_id, adds doctor_approved metadata.
22–25. approve_summary_after_review: calls repo, passes approved_by_user_id, ok true, maps repo error.
26–27. validate_rejection_reason: valid, empty.
28–31. reject_summary_after_review: calls repo, passes rejected_by_user_id, ok true, maps repo error.
32–33. No real database, no external service.

## Acceptance criteria

- All Module 33 tests pass.
- All previous tests still pass.
- No real database connection is used.
- No external services are called.
- No LLM call is made.
- No diagnosis or treatment advice generation exists.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 33 — Doctor review workflow`
