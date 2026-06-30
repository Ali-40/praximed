# Sprint 2 / Module 29 — Consultation Session API Routes

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Module 24: patient schema contract committed.
- Sprint 2, Module 25: patient repository committed.
- Sprint 2, Module 26: patient API routes committed.
- Sprint 2, Module 27: consultation session schema contract committed.
- Sprint 2, Module 28: consultation session repository committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create API schemas and FastAPI routes for managing consultation sessions.

## Purpose
PraxisMed needs consultation session API routes before building audio upload, transcription, AI draft summaries, doctor approval, and patient timelines.

## Create or update only

1. `backend/app/schemas/consultations.py`
2. `backend/app/api/routes/consultations.py`
3. `backend/app/api/router.py`
4. `backend/tests/test_consultation_schemas.py`
5. `backend/tests/test_consultation_routes.py`
6. `docs/claude/CURRENT_STATE.md`
7. `docs/claude/NEXT_MODULE.md`

Do not create audio upload service yet.
Do not create transcription code yet.
Do not create AI summary generator yet.
Do not create patient timeline code yet.
Do not build frontend.
Do not build authentication.
Do not modify consultation_repo.py unless absolutely required by tests.
Do not use a real database in tests.

## Schemas

### ConsultationSessionCreate
- `clinic_id`: str (not empty)
- `patient_id`: str (not empty)
- `doctor_user_id`: str | None = None
- `source`: str = "manual" (manual, vapi, web, doctor_mobile, system)
- `status`: str = "created" (valid lifecycle status)
- `title`: str | None = None
- `reason_for_visit`: str | None = None
- `raw_payload`: dict | None = None

### ConsultationStatusUpdate
- `status`: str (valid)
- `approval_status`: str | None = None (not_ready, pending_review, approved, rejected)

### ConsultationAudioAttach
- `audio_file_path`: str (not empty)

### ConsultationTranscriptSave
- `transcript_text`: str (not empty)

### ConsultationDraftSummarySave
- `draft_summary`: dict (non-empty)

### ConsultationApprove
- `approved_summary`: dict (non-empty)
- `approved_by_user_id`: str (not empty)

### ConsultationReject
- `rejected_reason`: str (not empty)
- `rejected_by_user_id`: str | None = None

### ConsultationResponse / ConsultationListResponse

## Routes

1. `POST /consultations` → create_consultation_session → ConsultationResponse
2. `GET /consultations` → list_consultation_sessions (query: clinic_id, patient_id, doctor_user_id, status, approval_status, source, limit=50) → ConsultationListResponse
3. `GET /consultations/{session_id}` → get_consultation_session_by_id (query: clinic_id) → ConsultationResponse | 404
4. `PATCH /consultations/{session_id}/status` → update_consultation_status (query: clinic_id) → ConsultationResponse | 404
5. `POST /consultations/{session_id}/audio` → attach_audio_to_session → ConsultationResponse | 404
6. `POST /consultations/{session_id}/transcript` → save_transcript → ConsultationResponse | 404
7. `POST /consultations/{session_id}/draft-summary` → save_draft_summary → ConsultationResponse | 404
8. `POST /consultations/{session_id}/approve` → approve_consultation_summary → ConsultationResponse | 404
9. `POST /consultations/{session_id}/reject` → reject_consultation_summary → ConsultationResponse | 404
10. `POST /consultations/{session_id}/archive` → archive_consultation_session → ConsultationResponse | 404

### Error handling
- Missing db_pool → HTTP 503
- InvalidConsultationSessionError → HTTP 400
- Not found → HTTP 404
- Unexpected error → HTTP 500

## Tests

### test_consultation_schemas.py (16 tests)
1–5. ConsultationSessionCreate: valid, empty clinic_id, empty patient_id, invalid source, invalid status.
6–8. ConsultationStatusUpdate: valid, invalid status, invalid approval_status.
9–14. Field validation: audio_file_path, transcript_text, draft_summary, approved_summary, approved_by_user_id, rejected_reason.
15–16. ConsultationResponse, ConsultationListResponse.

### test_consultation_routes.py (19+ tests)
1–2. POST create: 200, calls repo.
3–4. GET list: 200, passes all filters.
5–6. GET by id: 200, 404.
7–8. PATCH status: 200, 404.
9. POST audio: 200.
10. POST transcript: 200.
11. POST draft-summary: 200.
12. POST approve: 200.
13. POST reject: 200.
14. POST archive: 200.
15–18. Error handling: 503, 422, 400, 500.
19. Existing routes still work.

## Run

```
pytest -v backend/tests/test_consultation_schemas.py
pytest -v backend/tests/test_consultation_routes.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 29 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Consultation API routes are mounted.
- No real audio upload yet.
- No transcription code yet.
- No AI summary generation yet.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 29 — Consultation session API routes`
