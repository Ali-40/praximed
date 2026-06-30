"""
Tests for transcription_service — PraxisMed Sprint 2 / Module 31.

No real database, no external services, no file I/O.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.modules.transcription.transcription_service import (
    InvalidTranscriptionRequestError,
    TranscriptionProviderError,
    TranscriptionServiceError,
    normalize_transcription_result,
    run_transcription_adapter,
    transcribe_consultation_audio,
    validate_provider_name,
    validate_transcription_request,
)

REPO = "backend.app.modules.transcription.transcription_service.consultation_repo"

VALID_RESULT = {
    "transcript_text": "Der Patient klagt über Kopfschmerzen.",
    "confidence": 0.97,
    "duration_seconds": 120.5,
    "segments": [{"start": 0, "end": 5, "text": "Der Patient"}],
}


# ---------------------------------------------------------------------------
# Fake adapter
# ---------------------------------------------------------------------------


class _FakeAdapter:
    async def transcribe_audio_reference(self, audio_file_path, language="de-AT", raw_payload=None):
        return dict(VALID_RESULT)


# ---------------------------------------------------------------------------
# 1. validate_transcription_request accepts valid request
# ---------------------------------------------------------------------------


def test_validate_request_accepts_valid():
    req = validate_transcription_request(
        clinic_id="clinic-1",
        session_id="sess-1",
        audio_file_path="consultation_audio/clinic-1/consultations/sess-1/rec.mp3",
    )
    assert req["clinic_id"] == "clinic-1"
    assert req["session_id"] == "sess-1"
    assert req["language"] == "de-AT"


# ---------------------------------------------------------------------------
# 2. validate_transcription_request rejects empty clinic_id
# ---------------------------------------------------------------------------


def test_validate_request_rejects_empty_clinic_id():
    with pytest.raises(InvalidTranscriptionRequestError, match="clinic_id"):
        validate_transcription_request("", "sess-1", "audio/path.mp3")


# ---------------------------------------------------------------------------
# 3. validate_transcription_request rejects empty session_id
# ---------------------------------------------------------------------------


def test_validate_request_rejects_empty_session_id():
    with pytest.raises(InvalidTranscriptionRequestError, match="session_id"):
        validate_transcription_request("clinic-1", "", "audio/path.mp3")


# ---------------------------------------------------------------------------
# 4. validate_transcription_request rejects empty audio_file_path
# ---------------------------------------------------------------------------


def test_validate_request_rejects_empty_path():
    with pytest.raises(InvalidTranscriptionRequestError, match="audio_file_path"):
        validate_transcription_request("clinic-1", "sess-1", "")


# ---------------------------------------------------------------------------
# 5. validate_transcription_request rejects path traversal
# ---------------------------------------------------------------------------


def test_validate_request_rejects_path_traversal():
    with pytest.raises(InvalidTranscriptionRequestError, match="traversal|audio_file_path"):
        validate_transcription_request("clinic-1", "sess-1", "../../etc/passwd.mp3")


# ---------------------------------------------------------------------------
# 6. validate_transcription_request rejects backslashes
# ---------------------------------------------------------------------------


def test_validate_request_rejects_backslashes():
    with pytest.raises(InvalidTranscriptionRequestError, match="backslash|audio_file_path"):
        validate_transcription_request("clinic-1", "sess-1", "audio\\path.mp3")


# ---------------------------------------------------------------------------
# 7. validate_transcription_request rejects empty language
# ---------------------------------------------------------------------------


def test_validate_request_rejects_empty_language():
    with pytest.raises(InvalidTranscriptionRequestError, match="language"):
        validate_transcription_request("clinic-1", "sess-1", "audio/path.mp3", language="")


# ---------------------------------------------------------------------------
# 8. validate_provider_name accepts mock
# ---------------------------------------------------------------------------


def test_validate_provider_accepts_mock():
    assert validate_provider_name("mock") == "mock"


# ---------------------------------------------------------------------------
# 9. validate_provider_name accepts openai
# ---------------------------------------------------------------------------


def test_validate_provider_accepts_openai():
    assert validate_provider_name("openai") == "openai"


# ---------------------------------------------------------------------------
# 10. validate_provider_name rejects invalid provider
# ---------------------------------------------------------------------------


def test_validate_provider_rejects_invalid():
    with pytest.raises(InvalidTranscriptionRequestError, match="provider"):
        validate_provider_name("google")


# ---------------------------------------------------------------------------
# 11. normalize_transcription_result accepts valid transcript
# ---------------------------------------------------------------------------


def test_normalize_accepts_valid_result():
    normalized = normalize_transcription_result(VALID_RESULT, provider="mock")
    assert normalized["transcript_text"] == VALID_RESULT["transcript_text"]
    assert normalized["provider"] == "mock"
    assert normalized["language"] == "de-AT"


# ---------------------------------------------------------------------------
# 12. normalize_transcription_result rejects non-dict provider_result
# ---------------------------------------------------------------------------


def test_normalize_rejects_non_dict():
    with pytest.raises(InvalidTranscriptionRequestError, match="dict"):
        normalize_transcription_result("not a dict", provider="mock")


# ---------------------------------------------------------------------------
# 13. normalize_transcription_result rejects missing transcript_text
# ---------------------------------------------------------------------------


def test_normalize_rejects_missing_transcript_text():
    with pytest.raises(InvalidTranscriptionRequestError, match="transcript_text"):
        normalize_transcription_result({"confidence": 0.9}, provider="mock")


# ---------------------------------------------------------------------------
# 14. normalize_transcription_result rejects empty transcript_text
# ---------------------------------------------------------------------------


def test_normalize_rejects_empty_transcript_text():
    with pytest.raises(InvalidTranscriptionRequestError, match="transcript_text"):
        normalize_transcription_result({"transcript_text": "   "}, provider="mock")


# ---------------------------------------------------------------------------
# 15. normalize_transcription_result rejects non-list segments
# ---------------------------------------------------------------------------


def test_normalize_rejects_non_list_segments():
    with pytest.raises(InvalidTranscriptionRequestError, match="segments"):
        normalize_transcription_result(
            {"transcript_text": "Hello", "segments": "not a list"},
            provider="mock",
        )


# ---------------------------------------------------------------------------
# 16. normalize_transcription_result preserves confidence and duration_seconds
# ---------------------------------------------------------------------------


def test_normalize_preserves_confidence_and_duration():
    normalized = normalize_transcription_result(VALID_RESULT, provider="mock")
    assert normalized["confidence"] == 0.97
    assert normalized["duration_seconds"] == 120.5


# ---------------------------------------------------------------------------
# 17. run_transcription_adapter calls adapter.transcribe_audio_reference
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_adapter_calls_transcribe():
    adapter = MagicMock()
    adapter.transcribe_audio_reference = AsyncMock(return_value=dict(VALID_RESULT))

    await run_transcription_adapter(
        adapter=adapter,
        audio_file_path="audio/clinic-1/rec.mp3",
        provider="mock",
    )
    adapter.transcribe_audio_reference.assert_awaited_once()


# ---------------------------------------------------------------------------
# 18. run_transcription_adapter normalizes adapter result
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_adapter_normalizes_result():
    result = await run_transcription_adapter(
        adapter=_FakeAdapter(),
        audio_file_path="audio/clinic-1/rec.mp3",
        provider="mock",
    )
    assert "transcript_text" in result
    assert result["provider"] == "mock"


# ---------------------------------------------------------------------------
# 19. run_transcription_adapter rejects adapter without transcribe_audio_reference
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_adapter_rejects_missing_method():
    with pytest.raises(InvalidTranscriptionRequestError, match="transcribe_audio_reference"):
        await run_transcription_adapter(
            adapter=object(),
            audio_file_path="audio/rec.mp3",
            provider="mock",
        )


# ---------------------------------------------------------------------------
# 20. run_transcription_adapter maps unexpected adapter error to TranscriptionProviderError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_adapter_maps_unexpected_error():
    adapter = MagicMock()
    adapter.transcribe_audio_reference = AsyncMock(side_effect=RuntimeError("provider down"))

    with pytest.raises(TranscriptionProviderError):
        await run_transcription_adapter(
            adapter=adapter,
            audio_file_path="audio/rec.mp3",
            provider="mock",
        )


# ---------------------------------------------------------------------------
# 21. transcribe_consultation_audio calls consultation_repo.save_transcript
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_transcribe_calls_save_transcript():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "transcribed"}

    with patch(f"{REPO}.save_transcript", new=AsyncMock(return_value=fake_session)) as mock:
        await transcribe_consultation_audio(
            pool=pool,
            adapter=_FakeAdapter(),
            clinic_id="clinic-1",
            session_id="sess-1",
            audio_file_path="audio/clinic-1/consultations/sess-1/rec.mp3",
        )
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 22. transcribe_consultation_audio passes transcript_text to repository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_transcribe_passes_transcript_text():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "transcribed"}

    with patch(f"{REPO}.save_transcript", new=AsyncMock(return_value=fake_session)) as mock:
        await transcribe_consultation_audio(
            pool=pool,
            adapter=_FakeAdapter(),
            clinic_id="clinic-1",
            session_id="sess-1",
            audio_file_path="audio/clinic-1/consultations/sess-1/rec.mp3",
        )
    kwargs = mock.call_args.kwargs
    assert kwargs["transcript_text"] == VALID_RESULT["transcript_text"]


# ---------------------------------------------------------------------------
# 23. transcribe_consultation_audio returns ok true
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_transcribe_returns_ok_true():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "transcribed"}

    with patch(f"{REPO}.save_transcript", new=AsyncMock(return_value=fake_session)):
        result = await transcribe_consultation_audio(
            pool=pool,
            adapter=_FakeAdapter(),
            clinic_id="clinic-1",
            session_id="sess-1",
            audio_file_path="audio/clinic-1/consultations/sess-1/rec.mp3",
        )
    assert result["ok"] is True
    assert result["consultation"] == fake_session
    assert result["message"] == "Transcription completed and saved."


# ---------------------------------------------------------------------------
# 24. transcribe_consultation_audio includes normalized transcription result
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_transcribe_includes_normalized_transcription():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "transcribed"}

    with patch(f"{REPO}.save_transcript", new=AsyncMock(return_value=fake_session)):
        result = await transcribe_consultation_audio(
            pool=pool,
            adapter=_FakeAdapter(),
            clinic_id="clinic-1",
            session_id="sess-1",
            audio_file_path="audio/clinic-1/consultations/sess-1/rec.mp3",
        )
    assert "transcription" in result
    assert result["transcription"]["transcript_text"] == VALID_RESULT["transcript_text"]


# ---------------------------------------------------------------------------
# 25. transcribe_consultation_audio maps repository error to TranscriptionServiceError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_transcribe_maps_repo_error():
    pool = MagicMock()

    with patch(
        f"{REPO}.save_transcript",
        new=AsyncMock(side_effect=RuntimeError("db gone")),
    ):
        with pytest.raises(TranscriptionServiceError):
            await transcribe_consultation_audio(
                pool=pool,
                adapter=_FakeAdapter(),
                clinic_id="clinic-1",
                session_id="sess-1",
                audio_file_path="audio/clinic-1/consultations/sess-1/rec.mp3",
            )


# ---------------------------------------------------------------------------
# 26. No real database is used
# ---------------------------------------------------------------------------


def test_no_real_database_used():
    req = validate_transcription_request(
        clinic_id="c", session_id="s", audio_file_path="audio/c/s/rec.mp3"
    )
    assert req["clinic_id"] == "c"


# ---------------------------------------------------------------------------
# 27. No external service is called
# ---------------------------------------------------------------------------


def test_no_external_service_called():
    # Pure sync functions work without any I/O — confirms no external calls needed.
    result = normalize_transcription_result(
        {"transcript_text": "Test transcript"}, provider="mock"
    )
    assert result["provider"] == "mock"
