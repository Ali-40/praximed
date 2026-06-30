"""
Tests for audio_storage — PraxisMed Sprint 2 / Module 30.

No real database connection or file I/O is used.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.modules.audio.audio_storage import (
    AudioStorageError,
    InvalidAudioUploadError,
    MAX_AUDIO_BYTES,
    attach_audio_reference_to_consultation,
    build_audio_reference,
    build_consultation_audio_path,
    sanitize_audio_filename,
    validate_audio_upload_metadata,
)

REPO = "backend.app.modules.audio.audio_storage.consultation_repo"


# ---------------------------------------------------------------------------
# 1. validate_audio_upload_metadata accepts valid mp3
# ---------------------------------------------------------------------------


def test_validate_accepts_valid_mp3():
    meta = validate_audio_upload_metadata(
        file_name="recording.mp3",
        content_type="audio/mpeg",
        file_size_bytes=1024,
    )
    assert meta["extension"] == ".mp3"
    assert meta["content_type"] == "audio/mpeg"
    assert meta["file_size_bytes"] == 1024


# ---------------------------------------------------------------------------
# 2. validate_audio_upload_metadata accepts valid m4a
# ---------------------------------------------------------------------------


def test_validate_accepts_valid_m4a():
    meta = validate_audio_upload_metadata(
        file_name="session.m4a",
        content_type="audio/x-m4a",
        file_size_bytes=2048,
    )
    assert meta["extension"] == ".m4a"


# ---------------------------------------------------------------------------
# 3. validate_audio_upload_metadata rejects empty file_name
# ---------------------------------------------------------------------------


def test_validate_rejects_empty_file_name():
    with pytest.raises(InvalidAudioUploadError, match="file_name"):
        validate_audio_upload_metadata("", "audio/mpeg", 1024)


# ---------------------------------------------------------------------------
# 4. validate_audio_upload_metadata rejects unsupported content_type
# ---------------------------------------------------------------------------


def test_validate_rejects_unsupported_content_type():
    with pytest.raises(InvalidAudioUploadError, match="content_type"):
        validate_audio_upload_metadata("file.mp3", "video/mp4", 1024)


# ---------------------------------------------------------------------------
# 5. validate_audio_upload_metadata rejects unsupported extension
# ---------------------------------------------------------------------------


def test_validate_rejects_unsupported_extension():
    with pytest.raises(InvalidAudioUploadError, match="extension"):
        validate_audio_upload_metadata("file.flac", "audio/mpeg", 1024)


# ---------------------------------------------------------------------------
# 6. validate_audio_upload_metadata rejects zero file size
# ---------------------------------------------------------------------------


def test_validate_rejects_zero_file_size():
    with pytest.raises(InvalidAudioUploadError, match="file_size_bytes"):
        validate_audio_upload_metadata("file.mp3", "audio/mpeg", 0)


# ---------------------------------------------------------------------------
# 7. validate_audio_upload_metadata rejects file larger than MAX_AUDIO_BYTES
# ---------------------------------------------------------------------------


def test_validate_rejects_oversized_file():
    with pytest.raises(InvalidAudioUploadError, match="[Mm]aximum|exceed"):
        validate_audio_upload_metadata("file.mp3", "audio/mpeg", MAX_AUDIO_BYTES + 1)


# ---------------------------------------------------------------------------
# 8. sanitize_audio_filename removes path components
# ---------------------------------------------------------------------------


def test_sanitize_removes_path_components():
    result = sanitize_audio_filename("/some/path/recording.mp3")
    assert "/" not in result
    assert result.endswith(".mp3")


# ---------------------------------------------------------------------------
# 9. sanitize_audio_filename prevents path traversal
# ---------------------------------------------------------------------------


def test_sanitize_prevents_path_traversal():
    result = sanitize_audio_filename("../../etc/passwd.mp3")
    assert ".." not in result
    assert "/" not in result


# ---------------------------------------------------------------------------
# 10. sanitize_audio_filename replaces unsafe characters
# ---------------------------------------------------------------------------


def test_sanitize_replaces_unsafe_characters():
    result = sanitize_audio_filename("my file (1).mp3")
    assert " " not in result
    assert "(" not in result
    assert ")" not in result
    assert result.endswith(".mp3")


# ---------------------------------------------------------------------------
# 11. build_consultation_audio_path includes clinic_id and session_id
# ---------------------------------------------------------------------------


def test_build_path_includes_clinic_and_session():
    path = build_consultation_audio_path(
        clinic_id="clinic-1",
        session_id="sess-1",
        file_name="rec.mp3",
    )
    assert "clinic-1" in path
    assert "sess-1" in path
    assert path.endswith(".mp3")


# ---------------------------------------------------------------------------
# 12. build_consultation_audio_path rejects empty clinic_id
# ---------------------------------------------------------------------------


def test_build_path_rejects_empty_clinic_id():
    with pytest.raises(InvalidAudioUploadError, match="clinic_id"):
        build_consultation_audio_path("", "sess-1", "rec.mp3")


# ---------------------------------------------------------------------------
# 13. build_consultation_audio_path rejects empty session_id
# ---------------------------------------------------------------------------


def test_build_path_rejects_empty_session_id():
    with pytest.raises(InvalidAudioUploadError, match="session_id"):
        build_consultation_audio_path("clinic-1", "", "rec.mp3")


# ---------------------------------------------------------------------------
# 14. build_consultation_audio_path rejects empty storage_root
# ---------------------------------------------------------------------------


def test_build_path_rejects_empty_storage_root():
    with pytest.raises(InvalidAudioUploadError, match="storage_root"):
        build_consultation_audio_path("clinic-1", "sess-1", "rec.mp3", storage_root="")


# ---------------------------------------------------------------------------
# 15. build_consultation_audio_path never returns path containing ".."
# ---------------------------------------------------------------------------


def test_build_path_never_contains_traversal():
    path = build_consultation_audio_path("clinic-1", "sess-1", "../../evil.mp3")
    assert ".." not in path


# ---------------------------------------------------------------------------
# 16. build_audio_reference returns all expected fields
# ---------------------------------------------------------------------------


def test_build_audio_reference_returns_all_fields():
    ref = build_audio_reference(
        clinic_id="clinic-1",
        session_id="sess-1",
        file_name="rec.mp3",
        content_type="audio/mpeg",
        file_size_bytes=4096,
    )
    for field in (
        "clinic_id", "session_id", "audio_file_path",
        "original_file_name", "safe_file_name",
        "content_type", "extension", "file_size_bytes",
        "uploaded_by_user_id", "source", "raw_payload", "status",
    ):
        assert field in ref, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# 17. build_audio_reference sets status pending_upload
# ---------------------------------------------------------------------------


def test_build_audio_reference_status_pending_upload():
    ref = build_audio_reference(
        clinic_id="clinic-1",
        session_id="sess-1",
        file_name="rec.mp3",
        content_type="audio/mpeg",
        file_size_bytes=4096,
    )
    assert ref["status"] == "pending_upload"


# ---------------------------------------------------------------------------
# 18. build_audio_reference preserves raw_payload
# ---------------------------------------------------------------------------


def test_build_audio_reference_preserves_raw_payload():
    payload = {"device": "iPhone 15", "app_version": "2.1.0"}
    ref = build_audio_reference(
        clinic_id="clinic-1",
        session_id="sess-1",
        file_name="rec.mp3",
        content_type="audio/mpeg",
        file_size_bytes=4096,
        raw_payload=payload,
    )
    assert ref["raw_payload"] == payload


# ---------------------------------------------------------------------------
# 19. attach_audio_reference_to_consultation calls attach_audio_to_session
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_attach_calls_repo():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "audio_uploaded"}

    with patch(
        f"{REPO}.attach_audio_to_session",
        new=AsyncMock(return_value=fake_session),
    ) as mock:
        await attach_audio_reference_to_consultation(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            file_name="rec.mp3",
            content_type="audio/mpeg",
            file_size_bytes=4096,
        )
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 20. attach_audio_reference_to_consultation passes generated audio_file_path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_attach_passes_generated_path():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "audio_uploaded"}

    with patch(
        f"{REPO}.attach_audio_to_session",
        new=AsyncMock(return_value=fake_session),
    ) as mock:
        await attach_audio_reference_to_consultation(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            file_name="rec.mp3",
            content_type="audio/mpeg",
            file_size_bytes=4096,
        )
    called_path = mock.call_args.kwargs["audio_file_path"]
    assert "clinic-1" in called_path
    assert "sess-1" in called_path
    assert called_path.endswith(".mp3")


# ---------------------------------------------------------------------------
# 21. attach_audio_reference_to_consultation returns ok true
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_attach_returns_ok_true():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "audio_uploaded"}

    with patch(
        f"{REPO}.attach_audio_to_session",
        new=AsyncMock(return_value=fake_session),
    ):
        result = await attach_audio_reference_to_consultation(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            file_name="rec.mp3",
            content_type="audio/mpeg",
            file_size_bytes=4096,
        )
    assert result["ok"] is True
    assert result["consultation"] == fake_session
    assert "audio_reference" in result
    assert "Binary upload is not implemented yet" in result["message"]


# ---------------------------------------------------------------------------
# 22. attach maps unexpected repo error to AudioStorageError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_attach_maps_repo_error_to_audio_storage_error():
    pool = MagicMock()

    with patch(
        f"{REPO}.attach_audio_to_session",
        new=AsyncMock(side_effect=RuntimeError("db gone")),
    ):
        with pytest.raises(AudioStorageError):
            await attach_audio_reference_to_consultation(
                pool=pool,
                clinic_id="clinic-1",
                session_id="sess-1",
                file_name="rec.mp3",
                content_type="audio/mpeg",
                file_size_bytes=4096,
            )


# ---------------------------------------------------------------------------
# 23. No real database is used
# ---------------------------------------------------------------------------


def test_no_real_database_used():
    # All repo calls are patched in tests above; this test simply confirms
    # that the pure helper functions work without any pool argument.
    meta = validate_audio_upload_metadata("test.wav", "audio/wav", 512)
    assert meta["extension"] == ".wav"

    path = build_consultation_audio_path("c", "s", "test.wav")
    assert "test" in path
