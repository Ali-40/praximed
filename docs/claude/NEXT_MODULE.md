# Sprint 2 / Module 28 — Consultation Session Repository

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Module 24: patient schema contract committed.
- Sprint 2, Module 25: patient repository committed.
- Sprint 2, Module 26: patient API routes committed.
- Sprint 2, Module 27: consultation session schema contract committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create the database repository layer for consultation_sessions.

## Purpose
PraxisMed needs a clean repository for consultation sessions before building consultation APIs, audio upload, transcription, AI draft summaries, doctor approval, and patient timelines.

## Create or update only

1. `backend/app/db/repositories/consultation_repo.py`
2. `backend/tests/test_consultation_repo.py`
3. `docs/claude/CURRENT_STATE.md`
4. `docs/claude/NEXT_MODULE.md`

Do not create API routes yet.
Do not create audio upload code yet.
Do not create transcription code.
Do not create AI summary code yet.
Do not create patient timeline code yet.
Do not build frontend.
Do not build authentication.
Do not use a real database in tests.

## Public async functions

### 1. `create_consultation_session(pool, clinic_id, patient_id, doctor_user_id=None, source="manual", status="created", title=None, reason_for_visit=None, raw_payload=None)`
- Validate `clinic_id` and `patient_id` not empty.
- Validate `source` and `status`.
- INSERT, RETURNING *.

### 2. `get_consultation_session_by_id(pool, clinic_id, session_id)`
- Return matching session or None. Filter by `clinic_id`.

### 3. `list_consultation_sessions(pool, clinic_id, patient_id=None, doctor_user_id=None, status=None, approval_status=None, source=None, limit=50)`
- Limit 1–100. Validate `status`, `approval_status`, `source` if provided.
- Optional filters: `patient_id`, `doctor_user_id`.

### 4. `update_consultation_status(pool, clinic_id, session_id, status, approval_status=None)`
- Validate `status` and `approval_status` if provided.

### 5. `attach_audio_to_session(pool, clinic_id, session_id, audio_file_path)`
- Validate `audio_file_path` not empty. Set `status='audio_uploaded'`.

### 6. `save_transcript(pool, clinic_id, session_id, transcript_text)`
- Validate `transcript_text` not empty. Set `status='transcribed'`.

### 7. `save_draft_summary(pool, clinic_id, session_id, draft_summary)`
- Validate `draft_summary` is non-empty dict. Set `status='draft_ready'`, `approval_status='pending_review'`.

### 8. `approve_consultation_summary(pool, clinic_id, session_id, approved_summary, approved_by_user_id)`
- Validate `approved_summary` non-empty dict and `approved_by_user_id` not empty.
- Set `approved_at=now()`, `status='approved'`, `approval_status='approved'`.

### 9. `reject_consultation_summary(pool, clinic_id, session_id, rejected_reason, rejected_by_user_id=None)`
- Validate `rejected_reason` not empty.
- Set `status='rejected'`, `approval_status='rejected'`.

### 10. `archive_consultation_session(pool, clinic_id, session_id)`
- Set `status='archived'`. Return updated row.

## Tests required (31 tests)

1–5. create_consultation_session: calls fetchrow, validates clinic_id, patient_id, source, status.
6. get_consultation_session_by_id calls fetchrow and filters by clinic_id.
7–13. list_consultation_sessions: calls fetch, validates limit, status, approval_status, source, patient_id filter, doctor_user_id filter.
14–16. update_consultation_status: calls fetchrow, validates status, validates approval_status.
17–18. attach_audio_to_session: calls fetchrow, validates empty path.
19–20. save_transcript: calls fetchrow, validates empty text.
21–22. save_draft_summary: calls fetchrow, validates empty summary.
23–25. approve_consultation_summary: calls fetchrow, validates empty summary, validates empty approver.
26–27. reject_consultation_summary: calls fetchrow, validates empty reason.
28. archive_consultation_session calls fetchrow.
29. SQL uses parameterized placeholders.
30. approve SQL sets approved_at=now().
31. save_draft_summary SQL sets approval_status='pending_review'.

## Run

```
pytest -v backend/tests/test_consultation_repo.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 28 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Only consultation_repo.py, its tests, and orchestration docs are changed.
- No API route yet.
- No audio/transcription/summary code yet.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 28 — Consultation session repository`
