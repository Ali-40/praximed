"""
Transcription Adapter Interface — PraxisMed Sprint 2 / Module 31

Provider-agnostic transcription service. Validates requests, normalizes
provider output, and persists transcripts via consultation_repo.

This module does NOT:
  - call OpenAI, Whisper, Vapi, or any external service
  - read or write audio files from disk
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from backend.app.db.repositories import consultation_repo


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class TranscriptionServiceError(RuntimeError):
    """Base class for transcription service errors."""


class InvalidTranscriptionRequestError(TranscriptionServiceError):
    """Raised when the transcription request is missing or invalid."""


class TranscriptionProviderError(TranscriptionServiceError):
    """Raised when a transcription adapter fails."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VALID_PROVIDERS = frozenset({"mock", "openai", "whisper", "vapi", "manual"})


# ---------------------------------------------------------------------------
# Adapter interface (Protocol)
# ---------------------------------------------------------------------------


@runtime_checkable
class TranscriptionAdapter(Protocol):
    async def transcribe_audio_reference(
        self,
        audio_file_path: str,
        language: str = "de-AT",
        raw_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ...


# ---------------------------------------------------------------------------
# 1. validate_transcription_request
# ---------------------------------------------------------------------------


def validate_transcription_request(
    clinic_id: str,
    session_id: str,
    audio_file_path: str,
    language: str = "de-AT",
) -> Dict[str, Any]:
    if not clinic_id or not clinic_id.strip():
        raise InvalidTranscriptionRequestError("'clinic_id' must not be empty")
    if not session_id or not session_id.strip():
        raise InvalidTranscriptionRequestError("'session_id' must not be empty")
    if not audio_file_path or not audio_file_path.strip():
        raise InvalidTranscriptionRequestError("'audio_file_path' must not be empty")
    if ".." in audio_file_path:
        raise InvalidTranscriptionRequestError(
            f"'audio_file_path' contains path traversal sequence: {audio_file_path!r}"
        )
    if "\\" in audio_file_path:
        raise InvalidTranscriptionRequestError(
            f"'audio_file_path' contains backslash: {audio_file_path!r}"
        )
    if not language or not language.strip():
        raise InvalidTranscriptionRequestError("'language' must not be empty")

    return {
        "clinic_id": clinic_id,
        "session_id": session_id,
        "audio_file_path": audio_file_path,
        "language": language,
    }


# ---------------------------------------------------------------------------
# 2. validate_provider_name
# ---------------------------------------------------------------------------


def validate_provider_name(provider: str) -> str:
    if not provider or not provider.strip():
        raise InvalidTranscriptionRequestError("'provider' must not be empty")
    if provider not in _VALID_PROVIDERS:
        raise InvalidTranscriptionRequestError(
            f"'provider' must be one of {sorted(_VALID_PROVIDERS)!r}; got {provider!r}"
        )
    return provider


# ---------------------------------------------------------------------------
# 3. normalize_transcription_result
# ---------------------------------------------------------------------------


def normalize_transcription_result(
    provider_result: Any,
    provider: str = "mock",
    language: str = "de-AT",
) -> Dict[str, Any]:
    validate_provider_name(provider)

    if not isinstance(provider_result, dict):
        raise InvalidTranscriptionRequestError(
            f"'provider_result' must be a dict; got {type(provider_result).__name__!r}"
        )

    transcript_text = provider_result.get("transcript_text")
    if transcript_text is None:
        raise InvalidTranscriptionRequestError(
            "'provider_result' must contain 'transcript_text'"
        )
    if not isinstance(transcript_text, str) or not transcript_text.strip():
        raise InvalidTranscriptionRequestError(
            "'transcript_text' must be a non-empty string"
        )

    segments = provider_result.get("segments")
    if segments is not None and not isinstance(segments, list):
        raise InvalidTranscriptionRequestError(
            "'segments', if provided, must be a list"
        )

    return {
        "provider": provider,
        "language": language,
        "transcript_text": transcript_text,
        "confidence": provider_result.get("confidence"),
        "duration_seconds": provider_result.get("duration_seconds"),
        "segments": segments,
        "raw_payload": provider_result.get("raw_payload"),
    }


# ---------------------------------------------------------------------------
# 4. run_transcription_adapter
# ---------------------------------------------------------------------------


async def run_transcription_adapter(
    adapter: Any,
    audio_file_path: str,
    language: str = "de-AT",
    raw_payload: Optional[Dict[str, Any]] = None,
    provider: str = "mock",
) -> Dict[str, Any]:
    validate_provider_name(provider)

    if not hasattr(adapter, "transcribe_audio_reference"):
        raise InvalidTranscriptionRequestError(
            "Adapter must implement 'transcribe_audio_reference'"
        )

    try:
        provider_result = await adapter.transcribe_audio_reference(
            audio_file_path=audio_file_path,
            language=language,
            raw_payload=raw_payload,
        )
    except TranscriptionProviderError:
        raise
    except Exception as exc:
        raise TranscriptionProviderError(
            f"Transcription adapter raised an unexpected error: {exc}"
        ) from exc

    return normalize_transcription_result(provider_result, provider=provider, language=language)


# ---------------------------------------------------------------------------
# 5. transcribe_consultation_audio
# ---------------------------------------------------------------------------


async def transcribe_consultation_audio(
    pool: Any,
    adapter: Any,
    clinic_id: str,
    session_id: str,
    audio_file_path: str,
    language: str = "de-AT",
    provider: str = "mock",
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    validate_transcription_request(
        clinic_id=clinic_id,
        session_id=session_id,
        audio_file_path=audio_file_path,
        language=language,
    )

    normalized = await run_transcription_adapter(
        adapter=adapter,
        audio_file_path=audio_file_path,
        language=language,
        raw_payload=raw_payload,
        provider=provider,
    )

    try:
        consultation = await consultation_repo.save_transcript(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            transcript_text=normalized["transcript_text"],
        )
    except (InvalidTranscriptionRequestError, TranscriptionProviderError):
        raise
    except Exception as exc:
        raise TranscriptionServiceError(
            f"Failed to save transcript to consultation session: {exc}"
        ) from exc

    return {
        "ok": True,
        "consultation": consultation,
        "transcription": normalized,
        "message": "Transcription completed and saved.",
    }
