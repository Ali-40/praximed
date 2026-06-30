# Sprint 2 / Module 34 — Patient Timeline Report Service

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–33: all committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create a patient timeline report service.

## Purpose
PraxisMed needs a safe patient timeline before building doctor dashboard views, exports, or search. This service fetches a patient record and their consultation sessions, builds a chronological timeline, distinguishes approved summaries from drafts, and returns a structured report object.

This module does not create API routes.
This module does not create PDF/Excel export.
This module does not create frontend.
This module does not call OpenAI or any LLM.
This module does not generate medical content.
This module does not modify schema.

## Create or update only

1. `backend/app/modules/patient_timeline/__init__.py`
2. `backend/app/modules/patient_timeline/timeline_report.py`
3. `backend/tests/test_patient_timeline_report.py`
4. `docs/claude/CURRENT_STATE.md`
5. `docs/claude/NEXT_MODULE.md`

## Tests (43 tests)

1–7. validate_timeline_request: valid, empty clinic_id, empty patient_id, limit<1, limit>100, non-bool include_drafts, empty language.
8–12. normalize_patient_record: valid, non-dict, missing id, does not expose notes, does not expose raw_payload.
13–17. detect_summary_status: approved, draft, transcribed, audio_only, created.
18–20. extract_summary_for_timeline: approved, hides draft by default, returns draft when include_drafts=True.
21–25. build_timeline_entry: required fields, has_audio, has_transcript, doctor_review_required=False for approved, doctor_review_required=True for draft.
26–28. sort_timeline_entries: newest first, oldest first, handles missing created_at.
29–35. build_patient_timeline_report: schema_version, normalized patient, hides drafts by default, includes drafts, calculates totals, safety flags, no medical content message.
36–41. create_patient_timeline_report: calls patient_repo, calls consultation_repo, passes patient_id filter, returns ok true, raises PatientNotFoundError, maps repo error.
42–43. No real database, no external service.

## Acceptance criteria

- All Module 34 tests pass.
- All previous tests still pass.
- No real database connection is used.
- No external services are called.
- No LLM call is made.
- No diagnosis or treatment advice generation exists.
- Draft summaries are hidden by default.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 34 — Patient timeline report service`
