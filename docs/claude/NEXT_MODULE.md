# Sprint 2 / Module 31 — Transcription Adapter Interface

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–30: all committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create a provider-agnostic transcription service interface for consultation audio.

## Purpose
PraxisMed will later use OpenAI/Whisper or another transcription provider. This module provides a clean internal abstraction layer before wiring any real provider.

## Create or update only

1. `backend/app/modules/transcription/__init__.py`
2. `backend/app/modules/transcription/transcription_service.py`
3. `backend/tests/test_transcription_service.py`
4. `docs/claude/CURRENT_STATE.md`
5. `docs/claude/NEXT_MODULE.md`

## Key design

- `TranscriptionAdapter` — runtime_checkable Protocol with `transcribe_audio_reference`
- Valid providers: mock, openai, whisper, vapi, manual
- Exceptions: `TranscriptionServiceError`, `InvalidTranscriptionRequestError`, `TranscriptionProviderError`

## Public functions

1. `validate_transcription_request(clinic_id, session_id, audio_file_path, language)` → dict
2. `validate_provider_name(provider)` → str
3. `normalize_transcription_result(provider_result, provider, language)` → dict
4. `run_transcription_adapter(adapter, audio_file_path, language, raw_payload, provider)` → dict (async)
5. `transcribe_consultation_audio(pool, adapter, clinic_id, session_id, audio_file_path, language, provider, raw_payload)` → dict (async)

## Tests (27 tests)

1–7. validate_transcription_request: valid, empty clinic_id, empty session_id, empty path, path traversal, backslashes, empty language.
8–10. validate_provider_name: mock, openai, invalid.
11–16. normalize_transcription_result: valid, non-dict, missing text, empty text, non-list segments, preserves confidence/duration.
17–20. run_transcription_adapter: calls adapter, normalizes, rejects missing method, maps errors.
21–25. transcribe_consultation_audio: calls repo, passes text, ok true, includes transcription, maps repo error.
26–27. No real database, no external service.

## Acceptance criteria

- All Module 31 tests pass.
- All previous tests still pass.
- No real database, no external calls, no file I/O.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 31 — Transcription adapter interface`
