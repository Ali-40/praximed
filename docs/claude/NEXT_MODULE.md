# Sprint 2 / Module 30 — Audio Upload Placeholder Service

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–29: all committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create a safe placeholder service for consultation audio upload references.

## Purpose
PraxisMed will later support doctor consultation recordings. This module:
- Validates audio upload metadata
- Sanitizes file names
- Builds safe storage paths
- Attaches an audio reference path to a consultation session

This module does NOT upload binary audio, write files to disk, or call external services.

## Create or update only

1. `backend/app/modules/audio/__init__.py`
2. `backend/app/modules/audio/audio_storage.py`
3. `backend/tests/test_audio_storage.py`
4. `docs/claude/CURRENT_STATE.md`
5. `docs/claude/NEXT_MODULE.md`

## Public functions

### `validate_audio_upload_metadata(file_name, content_type, file_size_bytes) -> dict`
- Validates file_name, content_type, extension, file_size_bytes.
- Allowed types: audio/mpeg, audio/mp3, audio/mp4, audio/x-m4a, audio/wav, audio/webm, audio/ogg, audio/aac
- Allowed extensions: .mp3, .m4a, .mp4, .wav, .webm, .ogg, .aac
- MAX_AUDIO_BYTES = 100 MB

### `sanitize_audio_filename(file_name) -> str`
- Strips path components, prevents traversal, replaces unsafe chars.

### `build_consultation_audio_path(clinic_id, session_id, file_name, storage_root="consultation_audio") -> str`
- Returns: `consultation_audio/{clinic_id}/consultations/{session_id}/{safe_filename}`
- No "..", no backslashes, no duplicate slashes.

### `build_audio_reference(clinic_id, session_id, file_name, content_type, file_size_bytes, ...) -> dict`
- Returns full reference dict including `status: "pending_upload"`.

### `attach_audio_reference_to_consultation(pool, clinic_id, session_id, file_name, ...) -> dict`
- Calls `consultation_repo.attach_audio_to_session`.
- Returns `{ok: True, consultation, audio_reference, message}`.

## Tests (23 tests)

1–7. validate_audio_upload_metadata: valid mp3, valid m4a, empty name, bad content_type, bad extension, zero size, oversized.
8–10. sanitize_audio_filename: removes paths, prevents traversal, replaces unsafe chars.
11–15. build_consultation_audio_path: includes ids, rejects empties, no traversal.
16–18. build_audio_reference: all fields, pending_upload status, raw_payload preserved.
19–22. attach_audio_reference_to_consultation: calls repo, passes path, returns ok, maps error.
23. No real database used.

## Acceptance criteria

- All Module 30 tests pass.
- All previous tests still pass.
- No real database, no binary upload, no disk writes, no external calls.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 30 — Audio upload placeholder service`
