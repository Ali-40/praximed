"""
Tests for consultation_repo — PraxisMed Sprint 2 / Module 28.

All tests use a MagicMock pool with AsyncMock fetchrow/fetch.
No real database connection is used.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.db.repositories.consultation_repo import (
    InvalidConsultationSessionError,
    approve_consultation_summary,
    archive_consultation_session,
    attach_audio_to_session,
    create_consultation_session,
    get_consultation_session_by_id,
    list_consultation_sessions,
    reject_consultation_summary,
    save_draft_summary,
    save_transcript,
    update_consultation_status,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pool(row=None, rows=None):
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row)
    pool.fetch = AsyncMock(return_value=rows or [])
    return pool


def _fake_row(**kwargs):
    defaults = {
        "id":                  "sess-1",
        "clinic_id":           "clinic-1",
        "patient_id":          "pat-1",
        "doctor_user_id":      None,
        "source":              "manual",
        "status":              "created",
        "title":               None,
        "reason_for_visit":    None,
        "audio_file_path":     None,
        "transcript_text":     None,
        "draft_summary":       None,
        "approved_summary":    None,
        "approval_status":     "not_ready",
        "approved_by_user_id": None,
        "approved_at":         None,
        "rejected_reason":     None,
        "raw_payload":         None,
        "created_at":          "2024-06-01T10:00:00+00:00",
        "updated_at":          "2024-06-01T10:00:00+00:00",
    }
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# 1. create_consultation_session calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_consultation_session_calls_fetchrow():
    pool = _make_pool(row=_fake_row())
    result = await create_consultation_session(
        pool, clinic_id="clinic-1", patient_id="pat-1"
    )
    pool.fetchrow.assert_awaited_once()
    assert result["clinic_id"] == "clinic-1"


# ---------------------------------------------------------------------------
# 2. create raises InvalidConsultationSessionError for empty clinic_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_raises_for_empty_clinic_id():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="clinic_id"):
        await create_consultation_session(pool, clinic_id="", patient_id="pat-1")


# ---------------------------------------------------------------------------
# 3. create raises InvalidConsultationSessionError for empty patient_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_raises_for_empty_patient_id():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="patient_id"):
        await create_consultation_session(pool, clinic_id="clinic-1", patient_id="")


# ---------------------------------------------------------------------------
# 4. create validates invalid source
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_validates_invalid_source():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="source"):
        await create_consultation_session(
            pool, clinic_id="clinic-1", patient_id="pat-1", source="fax"
        )


# ---------------------------------------------------------------------------
# 5. create validates invalid status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_validates_invalid_status():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="status"):
        await create_consultation_session(
            pool, clinic_id="clinic-1", patient_id="pat-1", status="deleted"
        )


# ---------------------------------------------------------------------------
# 6. get_consultation_session_by_id calls fetchrow and filters by clinic_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_by_id_calls_fetchrow_and_filters_clinic():
    pool = _make_pool(row=_fake_row())
    result = await get_consultation_session_by_id(
        pool, clinic_id="clinic-1", session_id="sess-1"
    )
    pool.fetchrow.assert_awaited_once()
    sql_arg, *bind_args = pool.fetchrow.call_args[0]
    assert "clinic_id" in sql_arg.lower()
    assert "clinic-1" in bind_args


# ---------------------------------------------------------------------------
# 7. list_consultation_sessions calls fetch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_calls_fetch():
    pool = _make_pool(rows=[_fake_row()])
    result = await list_consultation_sessions(pool, clinic_id="clinic-1")
    pool.fetch.assert_awaited_once()
    assert len(result) == 1


# ---------------------------------------------------------------------------
# 8. list validates limit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_invalid_limit_zero():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="limit"):
        await list_consultation_sessions(pool, clinic_id="clinic-1", limit=0)


@pytest.mark.asyncio
async def test_list_invalid_limit_over_100():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="limit"):
        await list_consultation_sessions(pool, clinic_id="clinic-1", limit=101)


# ---------------------------------------------------------------------------
# 9. list validates status filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_validates_status_filter():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="status"):
        await list_consultation_sessions(
            pool, clinic_id="clinic-1", status="invalid_status"
        )


# ---------------------------------------------------------------------------
# 10. list validates approval_status filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_validates_approval_status_filter():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="approval_status"):
        await list_consultation_sessions(
            pool, clinic_id="clinic-1", approval_status="bad_approval"
        )


# ---------------------------------------------------------------------------
# 11. list validates source filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_validates_source_filter():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="source"):
        await list_consultation_sessions(
            pool, clinic_id="clinic-1", source="fax"
        )


# ---------------------------------------------------------------------------
# 12. list supports patient_id filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_supports_patient_id_filter():
    pool = _make_pool(rows=[])
    await list_consultation_sessions(pool, clinic_id="clinic-1", patient_id="pat-99")
    _, *bind_args = pool.fetch.call_args[0]
    assert "pat-99" in bind_args


# ---------------------------------------------------------------------------
# 13. list supports doctor_user_id filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_supports_doctor_user_id_filter():
    pool = _make_pool(rows=[])
    await list_consultation_sessions(
        pool, clinic_id="clinic-1", doctor_user_id="doc-42"
    )
    _, *bind_args = pool.fetch.call_args[0]
    assert "doc-42" in bind_args


# ---------------------------------------------------------------------------
# 14. update_consultation_status calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_status_calls_fetchrow():
    pool = _make_pool(row=_fake_row(status="transcribing"))
    result = await update_consultation_status(
        pool, clinic_id="clinic-1", session_id="sess-1", status="transcribing"
    )
    pool.fetchrow.assert_awaited_once()
    assert result["status"] == "transcribing"


# ---------------------------------------------------------------------------
# 15. update_consultation_status validates invalid status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_status_validates_invalid_status():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="status"):
        await update_consultation_status(
            pool, clinic_id="clinic-1", session_id="sess-1", status="bad_status"
        )


# ---------------------------------------------------------------------------
# 16. update_consultation_status validates invalid approval_status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_status_validates_invalid_approval_status():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="approval_status"):
        await update_consultation_status(
            pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            status="draft_ready",
            approval_status="bad_approval",
        )


# ---------------------------------------------------------------------------
# 17. attach_audio_to_session calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_attach_audio_calls_fetchrow():
    pool = _make_pool(row=_fake_row(audio_file_path="/audio/rec.mp3", status="audio_uploaded"))
    result = await attach_audio_to_session(
        pool, clinic_id="clinic-1", session_id="sess-1", audio_file_path="/audio/rec.mp3"
    )
    pool.fetchrow.assert_awaited_once()
    assert result["audio_file_path"] == "/audio/rec.mp3"


# ---------------------------------------------------------------------------
# 18. attach_audio_to_session validates empty audio_file_path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_attach_audio_validates_empty_path():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="audio_file_path"):
        await attach_audio_to_session(
            pool, clinic_id="clinic-1", session_id="sess-1", audio_file_path=""
        )


# ---------------------------------------------------------------------------
# 19. save_transcript calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_transcript_calls_fetchrow():
    pool = _make_pool(row=_fake_row(transcript_text="Patient has a cough.", status="transcribed"))
    result = await save_transcript(
        pool, clinic_id="clinic-1", session_id="sess-1",
        transcript_text="Patient has a cough."
    )
    pool.fetchrow.assert_awaited_once()
    assert result["transcript_text"] == "Patient has a cough."


# ---------------------------------------------------------------------------
# 20. save_transcript validates empty transcript_text
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_transcript_validates_empty_text():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="transcript_text"):
        await save_transcript(
            pool, clinic_id="clinic-1", session_id="sess-1", transcript_text=""
        )


# ---------------------------------------------------------------------------
# 21. save_draft_summary calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_summary_calls_fetchrow():
    pool = _make_pool(row=_fake_row(status="draft_ready", approval_status="pending_review"))
    result = await save_draft_summary(
        pool,
        clinic_id="clinic-1",
        session_id="sess-1",
        draft_summary={"diagnosis": "Flu"},
    )
    pool.fetchrow.assert_awaited_once()
    assert result["status"] == "draft_ready"


# ---------------------------------------------------------------------------
# 22. save_draft_summary validates empty draft_summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_summary_validates_empty():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="draft_summary"):
        await save_draft_summary(
            pool, clinic_id="clinic-1", session_id="sess-1", draft_summary={}
        )


# ---------------------------------------------------------------------------
# 23. approve_consultation_summary calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_summary_calls_fetchrow():
    pool = _make_pool(row=_fake_row(status="approved", approval_status="approved"))
    result = await approve_consultation_summary(
        pool,
        clinic_id="clinic-1",
        session_id="sess-1",
        approved_summary={"final": "All clear"},
        approved_by_user_id="doc-1",
    )
    pool.fetchrow.assert_awaited_once()
    assert result["status"] == "approved"


# ---------------------------------------------------------------------------
# 24. approve_consultation_summary validates empty approved_summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_summary_validates_empty_summary():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="approved_summary"):
        await approve_consultation_summary(
            pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            approved_summary={},
            approved_by_user_id="doc-1",
        )


# ---------------------------------------------------------------------------
# 25. approve_consultation_summary validates empty approved_by_user_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_summary_validates_empty_approver():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="approved_by_user_id"):
        await approve_consultation_summary(
            pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            approved_summary={"final": "All clear"},
            approved_by_user_id="",
        )


# ---------------------------------------------------------------------------
# 26. reject_consultation_summary calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reject_summary_calls_fetchrow():
    pool = _make_pool(row=_fake_row(status="rejected", approval_status="rejected"))
    result = await reject_consultation_summary(
        pool,
        clinic_id="clinic-1",
        session_id="sess-1",
        rejected_reason="Incomplete notes",
    )
    pool.fetchrow.assert_awaited_once()
    assert result["status"] == "rejected"


# ---------------------------------------------------------------------------
# 27. reject_consultation_summary validates empty rejected_reason
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reject_summary_validates_empty_reason():
    pool = _make_pool()
    with pytest.raises(InvalidConsultationSessionError, match="rejected_reason"):
        await reject_consultation_summary(
            pool, clinic_id="clinic-1", session_id="sess-1", rejected_reason=""
        )


# ---------------------------------------------------------------------------
# 28. archive_consultation_session calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_archive_session_calls_fetchrow():
    pool = _make_pool(row=_fake_row(status="archived"))
    result = await archive_consultation_session(
        pool, clinic_id="clinic-1", session_id="sess-1"
    )
    pool.fetchrow.assert_awaited_once()
    assert result["status"] == "archived"


# ---------------------------------------------------------------------------
# 29. SQL uses parameterized placeholders, not string formatting
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sql_uses_parameterised_placeholders():
    pool = _make_pool(row=_fake_row())
    await create_consultation_session(pool, clinic_id="clinic-1", patient_id="pat-1")
    sql = pool.fetchrow.call_args[0][0]
    assert "$1" in sql
    assert "%" not in sql
    assert "{" not in sql


# ---------------------------------------------------------------------------
# 30. approve_consultation_summary SQL sets approved_at=now()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_summary_sql_sets_approved_at():
    pool = _make_pool(row=_fake_row())
    await approve_consultation_summary(
        pool,
        clinic_id="clinic-1",
        session_id="sess-1",
        approved_summary={"final": "ok"},
        approved_by_user_id="doc-1",
    )
    sql = pool.fetchrow.call_args[0][0].lower()
    assert "approved_at" in sql
    assert "now()" in sql


# ---------------------------------------------------------------------------
# 31. save_draft_summary SQL sets approval_status='pending_review'
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_summary_sql_sets_pending_review():
    pool = _make_pool(row=_fake_row())
    await save_draft_summary(
        pool,
        clinic_id="clinic-1",
        session_id="sess-1",
        draft_summary={"section": "notes"},
    )
    sql = pool.fetchrow.call_args[0][0].lower()
    assert "pending_review" in sql
