"""
Tests for timeline_report — PraxisMed Sprint 2 / Module 34.

No real database, no external services, no LLM calls.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.modules.patient_timeline.timeline_report import (
    TIMELINE_SCHEMA_VERSION,
    InvalidPatientTimelineInputError,
    PatientNotFoundError,
    PatientTimelineError,
    build_patient_timeline_report,
    build_timeline_entry,
    create_patient_timeline_report,
    detect_summary_status,
    extract_summary_for_timeline,
    normalize_patient_record,
    sort_timeline_entries,
    validate_timeline_request,
)

PATIENT_REPO = "backend.app.modules.patient_timeline.timeline_report.patient_repo"
CONSULTATION_REPO = "backend.app.modules.patient_timeline.timeline_report.consultation_repo"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_patient(**kwargs) -> dict:
    base = {
        "id": "patient-1",
        "clinic_id": "clinic-1",
        "full_name": "Maria Mustermann",
        "external_patient_id": "ext-001",
        "date_of_birth": "1980-05-15",
        "phone": "+43123456789",
        "email": "maria@example.com",
        "preferred_language": "de-AT",
        "status": "active",
        "notes": "sensitive clinical notes",
        "raw_payload": {"source": "import"},
    }
    base.update(kwargs)
    return base


def _fake_consultation(**kwargs) -> dict:
    base = {
        "id": "sess-1",
        "clinic_id": "clinic-1",
        "patient_id": "patient-1",
        "doctor_user_id": "doctor-1",
        "created_at": "2024-03-01T10:00:00Z",
        "updated_at": "2024-03-01T11:00:00Z",
        "source": "manual",
        "status": "draft_ready",
        "approval_status": "pending_review",
        "title": "Routine checkup",
        "reason_for_visit": "Headache",
        "audio_file_path": None,
        "transcript_text": None,
        "draft_summary": None,
        "approved_summary": None,
    }
    base.update(kwargs)
    return base


def _fake_draft_summary() -> dict:
    return {
        "schema_version": "clinical_summary_draft.v1",
        "doctor_review_required": True,
        "no_diagnosis_generated": True,
        "no_treatment_advice_generated": True,
        "sections": {},
    }


def _fake_approved_summary() -> dict:
    return {
        "schema_version": "clinical_summary_draft.v1",
        "doctor_approved": True,
        "sections": {},
    }


# ---------------------------------------------------------------------------
# 1. validate_timeline_request accepts valid request
# ---------------------------------------------------------------------------


def test_validate_timeline_request_accepts_valid():
    result = validate_timeline_request(
        clinic_id="clinic-1", patient_id="patient-1", limit=20, include_drafts=False
    )
    assert result["clinic_id"] == "clinic-1"
    assert result["patient_id"] == "patient-1"
    assert result["limit"] == 20
    assert result["include_drafts"] is False


# ---------------------------------------------------------------------------
# 2. validate_timeline_request rejects empty clinic_id
# ---------------------------------------------------------------------------


def test_validate_timeline_request_rejects_empty_clinic_id():
    with pytest.raises(InvalidPatientTimelineInputError, match="clinic_id"):
        validate_timeline_request(clinic_id="", patient_id="patient-1")


# ---------------------------------------------------------------------------
# 3. validate_timeline_request rejects empty patient_id
# ---------------------------------------------------------------------------


def test_validate_timeline_request_rejects_empty_patient_id():
    with pytest.raises(InvalidPatientTimelineInputError, match="patient_id"):
        validate_timeline_request(clinic_id="clinic-1", patient_id="")


# ---------------------------------------------------------------------------
# 4. validate_timeline_request rejects limit below 1
# ---------------------------------------------------------------------------


def test_validate_timeline_request_rejects_limit_below_1():
    with pytest.raises(InvalidPatientTimelineInputError, match="limit"):
        validate_timeline_request(clinic_id="clinic-1", patient_id="p-1", limit=0)


# ---------------------------------------------------------------------------
# 5. validate_timeline_request rejects limit above 100
# ---------------------------------------------------------------------------


def test_validate_timeline_request_rejects_limit_above_100():
    with pytest.raises(InvalidPatientTimelineInputError, match="limit"):
        validate_timeline_request(clinic_id="clinic-1", patient_id="p-1", limit=101)


# ---------------------------------------------------------------------------
# 6. validate_timeline_request rejects non-bool include_drafts
# ---------------------------------------------------------------------------


def test_validate_timeline_request_rejects_non_bool_include_drafts():
    with pytest.raises(InvalidPatientTimelineInputError, match="include_drafts"):
        validate_timeline_request(
            clinic_id="clinic-1", patient_id="p-1", include_drafts="yes"
        )


# ---------------------------------------------------------------------------
# 7. validate_timeline_request rejects empty language
# ---------------------------------------------------------------------------


def test_validate_timeline_request_rejects_empty_language():
    with pytest.raises(InvalidPatientTimelineInputError, match="language"):
        validate_timeline_request(
            clinic_id="clinic-1", patient_id="p-1", language=""
        )


# ---------------------------------------------------------------------------
# 8. normalize_patient_record accepts valid patient
# ---------------------------------------------------------------------------


def test_normalize_patient_record_accepts_valid():
    result = normalize_patient_record(_fake_patient())
    assert result["id"] == "patient-1"
    assert result["full_name"] == "Maria Mustermann"
    assert result["clinic_id"] == "clinic-1"


# ---------------------------------------------------------------------------
# 9. normalize_patient_record rejects non-dict patient
# ---------------------------------------------------------------------------


def test_normalize_patient_record_rejects_non_dict():
    with pytest.raises(InvalidPatientTimelineInputError, match="dict"):
        normalize_patient_record("not a dict")


# ---------------------------------------------------------------------------
# 10. normalize_patient_record rejects missing id
# ---------------------------------------------------------------------------


def test_normalize_patient_record_rejects_missing_id():
    patient = _fake_patient()
    del patient["id"]
    with pytest.raises(InvalidPatientTimelineInputError, match="id"):
        normalize_patient_record(patient)


# ---------------------------------------------------------------------------
# 11. normalize_patient_record does not expose notes
# ---------------------------------------------------------------------------


def test_normalize_patient_record_does_not_expose_notes():
    result = normalize_patient_record(_fake_patient())
    assert "notes" not in result


# ---------------------------------------------------------------------------
# 12. normalize_patient_record does not expose raw_payload
# ---------------------------------------------------------------------------


def test_normalize_patient_record_does_not_expose_raw_payload():
    result = normalize_patient_record(_fake_patient())
    assert "raw_payload" not in result


# ---------------------------------------------------------------------------
# 13. detect_summary_status returns approved for approved summary
# ---------------------------------------------------------------------------


def test_detect_summary_status_approved():
    c = _fake_consultation(
        approval_status="approved",
        approved_summary=_fake_approved_summary(),
    )
    assert detect_summary_status(c) == "approved"


# ---------------------------------------------------------------------------
# 14. detect_summary_status returns draft for draft summary
# ---------------------------------------------------------------------------


def test_detect_summary_status_draft():
    c = _fake_consultation(
        approval_status="pending_review",
        draft_summary=_fake_draft_summary(),
    )
    assert detect_summary_status(c) == "draft"


# ---------------------------------------------------------------------------
# 15. detect_summary_status returns transcribed for transcript only
# ---------------------------------------------------------------------------


def test_detect_summary_status_transcribed():
    c = _fake_consultation(transcript_text="Doctor reviewed patient.")
    assert detect_summary_status(c) == "transcribed"


# ---------------------------------------------------------------------------
# 16. detect_summary_status returns audio_only for audio only
# ---------------------------------------------------------------------------


def test_detect_summary_status_audio_only():
    c = _fake_consultation(audio_file_path="consultation_audio/clinic-1/sess-1/audio.mp3")
    assert detect_summary_status(c) == "audio_only"


# ---------------------------------------------------------------------------
# 17. detect_summary_status returns created otherwise
# ---------------------------------------------------------------------------


def test_detect_summary_status_created():
    c = _fake_consultation()
    assert detect_summary_status(c) == "created"


# ---------------------------------------------------------------------------
# 18. extract_summary_for_timeline returns approved summary
# ---------------------------------------------------------------------------


def test_extract_summary_returns_approved():
    c = _fake_consultation(
        approval_status="approved",
        approved_summary=_fake_approved_summary(),
    )
    result = extract_summary_for_timeline(c)
    assert result is not None
    assert result["summary_type"] == "approved"
    assert result["doctor_approved"] is True
    assert result["warning"] is None


# ---------------------------------------------------------------------------
# 19. extract_summary_for_timeline hides draft by default
# ---------------------------------------------------------------------------


def test_extract_summary_hides_draft_by_default():
    c = _fake_consultation(
        approval_status="pending_review",
        draft_summary=_fake_draft_summary(),
    )
    result = extract_summary_for_timeline(c, include_drafts=False)
    assert result is None


# ---------------------------------------------------------------------------
# 20. extract_summary_for_timeline returns draft when include_drafts true
# ---------------------------------------------------------------------------


def test_extract_summary_returns_draft_when_enabled():
    c = _fake_consultation(
        approval_status="pending_review",
        draft_summary=_fake_draft_summary(),
    )
    result = extract_summary_for_timeline(c, include_drafts=True)
    assert result is not None
    assert result["summary_type"] == "draft"
    assert result["doctor_approved"] is False
    assert "Doctor approval required" in result["warning"]


# ---------------------------------------------------------------------------
# 21. build_timeline_entry returns required fields
# ---------------------------------------------------------------------------


def test_build_timeline_entry_returns_required_fields():
    c = _fake_consultation()
    entry = build_timeline_entry(c)
    for field in (
        "consultation_id", "clinic_id", "patient_id", "created_at",
        "status", "summary_status", "has_audio", "has_transcript",
        "doctor_review_required",
    ):
        assert field in entry, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# 22. build_timeline_entry sets has_audio true when audio_file_path exists
# ---------------------------------------------------------------------------


def test_build_timeline_entry_has_audio_true():
    c = _fake_consultation(audio_file_path="consultation_audio/clinic/sess/audio.mp3")
    entry = build_timeline_entry(c)
    assert entry["has_audio"] is True


# ---------------------------------------------------------------------------
# 23. build_timeline_entry sets has_transcript true when transcript_text exists
# ---------------------------------------------------------------------------


def test_build_timeline_entry_has_transcript_true():
    c = _fake_consultation(transcript_text="Chief complaint: pain.")
    entry = build_timeline_entry(c)
    assert entry["has_transcript"] is True


# ---------------------------------------------------------------------------
# 24. build_timeline_entry sets doctor_review_required false for approved summary
# ---------------------------------------------------------------------------


def test_build_timeline_entry_review_required_false_for_approved():
    c = _fake_consultation(
        approval_status="approved",
        approved_summary=_fake_approved_summary(),
    )
    entry = build_timeline_entry(c)
    assert entry["doctor_review_required"] is False


# ---------------------------------------------------------------------------
# 25. build_timeline_entry sets doctor_review_required true for draft summary
# ---------------------------------------------------------------------------


def test_build_timeline_entry_review_required_true_for_draft():
    c = _fake_consultation(
        approval_status="pending_review",
        draft_summary=_fake_draft_summary(),
    )
    entry = build_timeline_entry(c)
    assert entry["doctor_review_required"] is True


# ---------------------------------------------------------------------------
# 26. sort_timeline_entries sorts newest first
# ---------------------------------------------------------------------------


def test_sort_timeline_entries_newest_first():
    entries = [
        {"created_at": "2024-01-01T00:00:00Z"},
        {"created_at": "2024-03-01T00:00:00Z"},
        {"created_at": "2024-02-01T00:00:00Z"},
    ]
    sorted_entries = sort_timeline_entries(entries, newest_first=True)
    dates = [e["created_at"] for e in sorted_entries]
    assert dates == [
        "2024-03-01T00:00:00Z",
        "2024-02-01T00:00:00Z",
        "2024-01-01T00:00:00Z",
    ]


# ---------------------------------------------------------------------------
# 27. sort_timeline_entries sorts oldest first
# ---------------------------------------------------------------------------


def test_sort_timeline_entries_oldest_first():
    entries = [
        {"created_at": "2024-03-01T00:00:00Z"},
        {"created_at": "2024-01-01T00:00:00Z"},
    ]
    sorted_entries = sort_timeline_entries(entries, newest_first=False)
    assert sorted_entries[0]["created_at"] == "2024-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# 28. sort_timeline_entries handles missing created_at
# ---------------------------------------------------------------------------


def test_sort_timeline_entries_handles_missing_created_at():
    entries = [
        {"created_at": None},
        {"created_at": "2024-03-01T00:00:00Z"},
        {},
    ]
    sorted_entries = sort_timeline_entries(entries, newest_first=True)
    # Entries with missing/None created_at should appear last
    assert sorted_entries[0]["created_at"] == "2024-03-01T00:00:00Z"


# ---------------------------------------------------------------------------
# 29. build_patient_timeline_report returns schema_version
# ---------------------------------------------------------------------------


def test_build_report_returns_schema_version():
    report = build_patient_timeline_report(_fake_patient(), [])
    assert report["schema_version"] == TIMELINE_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 30. build_patient_timeline_report includes normalized patient
# ---------------------------------------------------------------------------


def test_build_report_includes_normalized_patient():
    report = build_patient_timeline_report(_fake_patient(), [])
    assert report["patient"]["id"] == "patient-1"
    assert report["patient"]["full_name"] == "Maria Mustermann"
    assert "notes" not in report["patient"]


# ---------------------------------------------------------------------------
# 31. build_patient_timeline_report hides draft summaries by default
# ---------------------------------------------------------------------------


def test_build_report_hides_drafts_by_default():
    c = _fake_consultation(
        approval_status="pending_review",
        draft_summary=_fake_draft_summary(),
    )
    report = build_patient_timeline_report(_fake_patient(), [c], include_drafts=False)
    entry = report["timeline"][0]
    assert entry["summary"] is None


# ---------------------------------------------------------------------------
# 32. build_patient_timeline_report includes drafts when include_drafts true
# ---------------------------------------------------------------------------


def test_build_report_includes_drafts_when_enabled():
    c = _fake_consultation(
        approval_status="pending_review",
        draft_summary=_fake_draft_summary(),
    )
    report = build_patient_timeline_report(_fake_patient(), [c], include_drafts=True)
    entry = report["timeline"][0]
    assert entry["summary"] is not None
    assert entry["summary"]["summary_type"] == "draft"


# ---------------------------------------------------------------------------
# 33. build_patient_timeline_report calculates totals
# ---------------------------------------------------------------------------


def test_build_report_calculates_totals():
    c_approved = _fake_consultation(
        id="sess-a",
        approval_status="approved",
        approved_summary=_fake_approved_summary(),
    )
    c_draft = _fake_consultation(
        id="sess-b",
        approval_status="pending_review",
        draft_summary=_fake_draft_summary(),
    )
    report = build_patient_timeline_report(_fake_patient(), [c_approved, c_draft])
    totals = report["totals"]
    assert totals["consultations"] == 2
    assert totals["approved_summaries"] == 1
    assert totals["draft_summaries"] == 1


# ---------------------------------------------------------------------------
# 34. build_patient_timeline_report includes safety flags
# ---------------------------------------------------------------------------


def test_build_report_includes_safety_flags():
    report = build_patient_timeline_report(_fake_patient(), [])
    safety = report["safety"]
    assert safety["no_diagnosis_generated"] is True
    assert safety["no_treatment_advice_generated"] is True
    assert safety["drafts_hidden_by_default"] is True
    assert safety["doctor_review_required_for_drafts"] is True


# ---------------------------------------------------------------------------
# 35. build_patient_timeline_report says no medical content generated
# ---------------------------------------------------------------------------


def test_build_report_message_no_medical_content():
    report = build_patient_timeline_report(_fake_patient(), [])
    assert "existing records only" in report["message"].lower()
    assert report["safety"]["no_medical_content_generated"] is True


# ---------------------------------------------------------------------------
# 36. create_patient_timeline_report calls patient_repo.get_patient_by_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_calls_patient_repo():
    pool = MagicMock()
    fake_patient = _fake_patient()

    with patch(f"{PATIENT_REPO}.get_patient_by_id", new=AsyncMock(return_value=fake_patient)) as mock_p, \
         patch(f"{CONSULTATION_REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])):
        await create_patient_timeline_report(
            pool=pool, clinic_id="clinic-1", patient_id="patient-1"
        )
    mock_p.assert_awaited_once()


# ---------------------------------------------------------------------------
# 37. create_patient_timeline_report calls consultation_repo.list_consultation_sessions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_calls_consultation_repo():
    pool = MagicMock()
    fake_patient = _fake_patient()

    with patch(f"{PATIENT_REPO}.get_patient_by_id", new=AsyncMock(return_value=fake_patient)), \
         patch(f"{CONSULTATION_REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])) as mock_c:
        await create_patient_timeline_report(
            pool=pool, clinic_id="clinic-1", patient_id="patient-1"
        )
    mock_c.assert_awaited_once()


# ---------------------------------------------------------------------------
# 38. create_patient_timeline_report passes patient_id filter to consultation repo
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_passes_patient_id_filter():
    pool = MagicMock()
    fake_patient = _fake_patient()

    with patch(f"{PATIENT_REPO}.get_patient_by_id", new=AsyncMock(return_value=fake_patient)), \
         patch(f"{CONSULTATION_REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])) as mock_c:
        await create_patient_timeline_report(
            pool=pool, clinic_id="clinic-1", patient_id="patient-1"
        )
    kwargs = mock_c.call_args.kwargs
    assert kwargs["patient_id"] == "patient-1"


# ---------------------------------------------------------------------------
# 39. create_patient_timeline_report returns ok true
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_returns_ok_true():
    pool = MagicMock()
    fake_patient = _fake_patient()

    with patch(f"{PATIENT_REPO}.get_patient_by_id", new=AsyncMock(return_value=fake_patient)), \
         patch(f"{CONSULTATION_REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])):
        result = await create_patient_timeline_report(
            pool=pool, clinic_id="clinic-1", patient_id="patient-1"
        )
    assert result["ok"] is True
    assert "report" in result
    assert result["report"]["schema_version"] == TIMELINE_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 40. create_patient_timeline_report raises PatientNotFoundError when patient is None
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_raises_patient_not_found():
    pool = MagicMock()

    with patch(f"{PATIENT_REPO}.get_patient_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(PatientNotFoundError):
            await create_patient_timeline_report(
                pool=pool, clinic_id="clinic-1", patient_id="patient-missing"
            )


# ---------------------------------------------------------------------------
# 41. create_patient_timeline_report maps repository error to PatientTimelineError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_maps_repo_error():
    pool = MagicMock()

    with patch(
        f"{PATIENT_REPO}.get_patient_by_id",
        new=AsyncMock(side_effect=RuntimeError("db gone")),
    ):
        with pytest.raises(PatientTimelineError):
            await create_patient_timeline_report(
                pool=pool, clinic_id="clinic-1", patient_id="patient-1"
            )


# ---------------------------------------------------------------------------
# 42. No real database is used
# ---------------------------------------------------------------------------


def test_no_real_database_used():
    report = build_patient_timeline_report(_fake_patient(), [])
    assert report["schema_version"] == TIMELINE_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 43. No external service is called
# ---------------------------------------------------------------------------


def test_no_external_service_called():
    c = _fake_consultation()
    entry = build_timeline_entry(c)
    assert entry["summary_status"] == "created"
