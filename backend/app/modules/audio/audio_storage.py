"""
Audio Upload Placeholder Service — PraxisMed Sprint 2 / Module 30

Validates audio upload metadata, sanitizes filenames, builds safe storage
paths, and attaches audio references to consultation sessions.

This module does NOT:
  - upload binary audio data
  - write files to disk
  - call any external service (OpenAI, Whisper, Vapi, S3, etc.)
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional

from backend.app.db.repositories import consultation_repo


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class AudioStorageError(RuntimeError):
    """Base class for audio storage errors."""


class InvalidAudioUploadError(AudioStorageError):
    """Raised when upload metadata is invalid or the filename is unsafe."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_AUDIO_BYTES = 100 * 1024 * 1024  # 100 MB

_ALLOWED_CONTENT_TYPES = frozenset({
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/x-m4a",
    "audio/wav",
    "audio/webm",
    "audio/ogg",
    "audio/aac",
})

_ALLOWED_EXTENSIONS = frozenset({
    ".mp3", ".m4a", ".mp4", ".wav", ".webm", ".ogg", ".aac",
})

# Characters that are safe in a filename (alphanumeric, dot, dash, underscore)
_SAFE_FILENAME_RE = re.compile(r"[^\w.\-]")


# ---------------------------------------------------------------------------
# 1. validate_audio_upload_metadata
# ---------------------------------------------------------------------------


def validate_audio_upload_metadata(
    file_name: str,
    content_type: str,
    file_size_bytes: int,
) -> Dict[str, Any]:
    if not file_name or not file_name.strip():
        raise InvalidAudioUploadError("'file_name' must not be empty")

    if content_type not in _ALLOWED_CONTENT_TYPES:
        raise InvalidAudioUploadError(
            f"'content_type' must be one of {sorted(_ALLOWED_CONTENT_TYPES)!r}; "
            f"got {content_type!r}"
        )

    _, ext = os.path.splitext(file_name.lower())
    if ext not in _ALLOWED_EXTENSIONS:
        raise InvalidAudioUploadError(
            f"File extension must be one of {sorted(_ALLOWED_EXTENSIONS)!r}; "
            f"got {ext!r}"
        )

    if file_size_bytes <= 0:
        raise InvalidAudioUploadError("'file_size_bytes' must be greater than 0")

    if file_size_bytes > MAX_AUDIO_BYTES:
        raise InvalidAudioUploadError(
            f"File size {file_size_bytes} exceeds maximum {MAX_AUDIO_BYTES} bytes"
        )

    return {
        "file_name": file_name,
        "content_type": content_type,
        "extension": ext,
        "file_size_bytes": file_size_bytes,
    }


# ---------------------------------------------------------------------------
# 2. sanitize_audio_filename
# ---------------------------------------------------------------------------


def sanitize_audio_filename(file_name: str) -> str:
    if not file_name or not file_name.strip():
        raise InvalidAudioUploadError("'file_name' must not be empty")

    # Strip any directory components (path traversal prevention)
    base = os.path.basename(file_name)

    # Split stem and extension before sanitizing
    stem, ext = os.path.splitext(base)
    ext = ext.lower()

    if ext not in _ALLOWED_EXTENSIONS:
        raise InvalidAudioUploadError(
            f"File extension must be one of {sorted(_ALLOWED_EXTENSIONS)!r}; "
            f"got {ext!r}"
        )

    # Replace unsafe characters in the stem with underscores
    safe_stem = _SAFE_FILENAME_RE.sub("_", stem)

    # Collapse multiple underscores and strip leading/trailing underscores/dots
    safe_stem = re.sub(r"_+", "_", safe_stem).strip("_.")

    if not safe_stem:
        raise InvalidAudioUploadError(
            f"Sanitized filename stem is empty for input {file_name!r}"
        )

    result = safe_stem + ext

    # Final guard: no path separators, no traversal sequences
    if ".." in result or "/" in result or "\\" in result:
        raise InvalidAudioUploadError(
            f"Sanitized filename contains unsafe sequences: {result!r}"
        )

    return result


# ---------------------------------------------------------------------------
# 3. build_consultation_audio_path
# ---------------------------------------------------------------------------


def build_consultation_audio_path(
    clinic_id: str,
    session_id: str,
    file_name: str,
    storage_root: str = "consultation_audio",
) -> str:
    if not clinic_id or not clinic_id.strip():
        raise InvalidAudioUploadError("'clinic_id' must not be empty")
    if not session_id or not session_id.strip():
        raise InvalidAudioUploadError("'session_id' must not be empty")
    if not storage_root or not storage_root.strip():
        raise InvalidAudioUploadError("'storage_root' must not be empty")

    safe_name = sanitize_audio_filename(file_name)

    path = f"{storage_root}/{clinic_id}/consultations/{session_id}/{safe_name}"

    # Hard guards against path traversal
    if ".." in path:
        raise InvalidAudioUploadError(f"Path contains traversal sequence: {path!r}")
    if "\\" in path:
        raise InvalidAudioUploadError(f"Path contains backslash: {path!r}")
    if "//" in path:
        raise InvalidAudioUploadError(f"Path contains duplicate slashes: {path!r}")

    return path


# ---------------------------------------------------------------------------
# 4. build_audio_reference
# ---------------------------------------------------------------------------


def build_audio_reference(
    clinic_id: str,
    session_id: str,
    file_name: str,
    content_type: str,
    file_size_bytes: int,
    uploaded_by_user_id: Optional[str] = None,
    source: str = "doctor_mobile",
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not clinic_id or not clinic_id.strip():
        raise InvalidAudioUploadError("'clinic_id' must not be empty")
    if not session_id or not session_id.strip():
        raise InvalidAudioUploadError("'session_id' must not be empty")

    metadata = validate_audio_upload_metadata(file_name, content_type, file_size_bytes)
    safe_name = sanitize_audio_filename(file_name)
    audio_file_path = build_consultation_audio_path(clinic_id, session_id, file_name)

    return {
        "clinic_id": clinic_id,
        "session_id": session_id,
        "audio_file_path": audio_file_path,
        "original_file_name": file_name,
        "safe_file_name": safe_name,
        "content_type": metadata["content_type"],
        "extension": metadata["extension"],
        "file_size_bytes": metadata["file_size_bytes"],
        "uploaded_by_user_id": uploaded_by_user_id,
        "source": source,
        "raw_payload": raw_payload,
        "status": "pending_upload",
    }


# ---------------------------------------------------------------------------
# 5. attach_audio_reference_to_consultation
# ---------------------------------------------------------------------------


async def attach_audio_reference_to_consultation(
    pool: Any,
    clinic_id: str,
    session_id: str,
    file_name: str,
    content_type: str,
    file_size_bytes: int,
    uploaded_by_user_id: Optional[str] = None,
    source: str = "doctor_mobile",
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    try:
        audio_reference = build_audio_reference(
            clinic_id=clinic_id,
            session_id=session_id,
            file_name=file_name,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            uploaded_by_user_id=uploaded_by_user_id,
            source=source,
            raw_payload=raw_payload,
        )
    except InvalidAudioUploadError:
        raise

    try:
        consultation = await consultation_repo.attach_audio_to_session(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            audio_file_path=audio_reference["audio_file_path"],
        )
    except Exception as exc:
        raise AudioStorageError(
            f"Failed to attach audio reference to consultation session: {exc}"
        ) from exc

    return {
        "ok": True,
        "consultation": consultation,
        "audio_reference": audio_reference,
        "message": "Audio reference attached. Binary upload is not implemented yet.",
    }
