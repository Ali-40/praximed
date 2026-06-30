# Sprint 3 / Module 35 — Clinical Workflow API Routes

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–34: all committed.
- Architecture Checkpoint 02: committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create FastAPI routes that expose the clinical workflow service layer.

## Purpose
Modules 30–34 created service-layer workflows for audio reference attachment, transcription, clinical summary draft generation, doctor review/approval, and patient timeline reports. These workflows are not exposed through API routes yet. This module creates clean internal API endpoints that call the service modules, not repositories directly.

## Create or update only

1. `backend/app/schemas/clinical_workflows.py`
2. `backend/app/api/routes/clinical_workflows.py`
3. `backend/app/api/router.py`
4. `backend/tests/test_clinical_workflow_schemas.py`
5. `backend/tests/test_clinical_workflow_routes.py`
6. `docs/claude/CURRENT_STATE.md`
7. `docs/claude/NEXT_MODULE.md`

## Routes (prefix: /clinical-workflows)

1. POST `/clinical-workflows/consultations/{session_id}/audio-reference`
2. POST `/clinical-workflows/consultations/{session_id}/manual-transcript`
3. POST `/clinical-workflows/consultations/{session_id}/draft-summary`
4. POST `/clinical-workflows/consultations/{session_id}/review-package`
5. POST `/clinical-workflows/consultations/{session_id}/approve-summary`
6. POST `/clinical-workflows/consultations/{session_id}/reject-summary`
7. GET  `/clinical-workflows/patients/{patient_id}/timeline`

## Tests (schema: 18, routes: 27 = 45 total)

## Acceptance criteria

- All Module 35 tests pass.
- All previous tests still pass.
- Routes call service-layer modules, not repositories directly.
- No external transcription or LLM provider called.
- No binary file upload.
- No diagnosis or treatment advice.
- Commit all changes only if tests pass.

## Commit message

`Sprint 3 / Module 35 — Clinical workflow API routes`
