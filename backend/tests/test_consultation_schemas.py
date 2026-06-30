"""
Tests for backend/app/schemas/consultations.py — PraxisMed Sprint 2 / Module 29
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.schemas.consultations import (
    ConsultationApprove,
    ConsultationAudioAttach,
    ConsultationDraftSummarySave,
    ConsultationListResponse,
    ConsultationReject,
    ConsultationResponse,
    ConsultationSessionCreate,
    ConsultationStatusUpdate,
    ConsultationTranscriptSave,
)

CLINIC_ID  = "clinic-uuid-001"
PATIENT_ID = "patient-uuid-001"


def _create_body(**overrides) -> dict:
    base = {"clinic_id": CLINIC_ID, "patient_id": PATIENT_ID}
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. Valid ConsultationSessionCreate passes
# ---------------------------------------------------------------------------


def test_valid_consultation_create_passes():
    model = ConsultationSessionCreate(**_create_body())
    assert model.clinic_id == CLINIC_ID
    assert model.patient_id == PATIENT_ID
    assert model.source == "manual"
    assert model.status == "created"


# ---------------------------------------------------------------------------
# 2. Empty clinic_id fails
# ---------------------------------------------------------------------------


def test_empty_clinic_id_fails():
    with pytest.raises(ValidationError, match="clinic_id"):
        ConsultationSessionCreate(**_create_body(clinic_id=""))


# ---------------------------------------------------------------------------
# 3. Empty patient_id fails
# ---------------------------------------------------------------------------


def test_empty_patient_id_fails():
    with pytest.raises(ValidationError, match="patient_id"):
        ConsultationSessionCreate(**_create_body(patient_id=""))


# ---------------------------------------------------------------------------
# 4. Invalid source fails
# ---------------------------------------------------------------------------


def test_invalid_source_fails():
    with pytest.raises(ValidationError, match="source"):
        ConsultationSessionCreate(**_create_body(source="fax"))


# ---------------------------------------------------------------------------
# 5. Invalid status fails
# ---------------------------------------------------------------------------


def test_invalid_status_fails():
    with pytest.raises(ValidationError, match="status"):
        ConsultationSessionCreate(**_create_body(status="deleted"))


# ---------------------------------------------------------------------------
# 6. Valid ConsultationStatusUpdate passes
# ---------------------------------------------------------------------------


def test_valid_status_update_passes():
    model = ConsultationStatusUpdate(status="transcribing")
    assert model.status == "transcribing"
    assert model.approval_status is None


# ---------------------------------------------------------------------------
# 7. Invalid status update fails
# ---------------------------------------------------------------------------


def test_invalid_status_update_fails():
    with pytest.raises(ValidationError, match="status"):
        ConsultationStatusUpdate(status="bad_status")


# ---------------------------------------------------------------------------
# 8. Invalid approval_status fails
# ---------------------------------------------------------------------------


def test_invalid_approval_status_fails():
    with pytest.raises(ValidationError, match="approval_status"):
        ConsultationStatusUpdate(status="draft_ready", approval_status="bad_approval")


# ---------------------------------------------------------------------------
# 9. Empty audio_file_path fails
# ---------------------------------------------------------------------------


def test_empty_audio_file_path_fails():
    with pytest.raises(ValidationError, match="audio_file_path"):
        ConsultationAudioAttach(audio_file_path="")


# ---------------------------------------------------------------------------
# 10. Empty transcript_text fails
# ---------------------------------------------------------------------------


def test_empty_transcript_text_fails():
    with pytest.raises(ValidationError, match="transcript_text"):
        ConsultationTranscriptSave(transcript_text="")


# ---------------------------------------------------------------------------
# 11. Empty draft_summary fails
# ---------------------------------------------------------------------------


def test_empty_draft_summary_fails():
    with pytest.raises(ValidationError, match="draft_summary"):
        ConsultationDraftSummarySave(draft_summary={})


# ---------------------------------------------------------------------------
# 12. Empty approved_summary fails
# ---------------------------------------------------------------------------


def test_empty_approved_summary_fails():
    with pytest.raises(ValidationError, match="approved_summary"):
        ConsultationApprove(approved_summary={}, approved_by_user_id="doc-1")


# ---------------------------------------------------------------------------
# 13. Empty approved_by_user_id fails
# ---------------------------------------------------------------------------


def test_empty_approved_by_user_id_fails():
    with pytest.raises(ValidationError, match="approved_by_user_id"):
        ConsultationApprove(approved_summary={"key": "val"}, approved_by_user_id="")


# ---------------------------------------------------------------------------
# 14. Empty rejected_reason fails
# ---------------------------------------------------------------------------


def test_empty_rejected_reason_fails():
    with pytest.raises(ValidationError, match="rejected_reason"):
        ConsultationReject(rejected_reason="")


# ---------------------------------------------------------------------------
# 15. ConsultationResponse accepts consultation dict
# ---------------------------------------------------------------------------


def test_consultation_response_accepts_dict():
    resp = ConsultationResponse(ok=True, consultation={"id": "sess-1", "status": "created"})
    assert resp.ok is True
    assert resp.consultation["id"] == "sess-1"


# ---------------------------------------------------------------------------
# 16. ConsultationListResponse accepts list of dicts
# ---------------------------------------------------------------------------


def test_consultation_list_response_accepts_list():
    resp = ConsultationListResponse(
        ok=True,
        consultations=[{"id": "a"}, {"id": "b"}],
    )
    assert resp.ok is True
    assert len(resp.consultations) == 2
