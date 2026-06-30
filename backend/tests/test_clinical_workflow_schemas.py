"""
Tests for clinical_workflows Pydantic schemas — PraxisMed Sprint 3 / Module 35.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.schemas.clinical_workflows import (
    ApproveSummaryRequest,
    AudioReferenceAttachRequest,
    ClinicalSummaryDraftRequest,
    ManualTranscriptRequest,
    RejectSummaryRequest,
    ReviewPackageRequest,
    TimelineReportResponse,
    WorkflowResponse,
)

VALID_DRAFT = {
    "schema_version": "clinical_summary_draft.v1",
    "doctor_review_required": True,
    "sections": {},
}

VALID_APPROVED = {
    "schema_version": "clinical_summary_draft.v1",
    "doctor_approved": True,
    "sections": {},
}


# ---------------------------------------------------------------------------
# 1. Valid AudioReferenceAttachRequest passes
# ---------------------------------------------------------------------------


def test_audio_reference_attach_request_valid():
    req = AudioReferenceAttachRequest(
        clinic_id="clinic-1",
        file_name="audio.mp3",
        content_type="audio/mpeg",
        file_size_bytes=1024,
    )
    assert req.clinic_id == "clinic-1"
    assert req.source == "doctor_mobile"


# ---------------------------------------------------------------------------
# 2. AudioReferenceAttachRequest rejects empty clinic_id
# ---------------------------------------------------------------------------


def test_audio_reference_attach_request_rejects_empty_clinic_id():
    with pytest.raises(ValidationError, match="clinic_id"):
        AudioReferenceAttachRequest(
            clinic_id="",
            file_name="audio.mp3",
            content_type="audio/mpeg",
            file_size_bytes=1024,
        )


# ---------------------------------------------------------------------------
# 3. AudioReferenceAttachRequest rejects empty file_name
# ---------------------------------------------------------------------------


def test_audio_reference_attach_request_rejects_empty_file_name():
    with pytest.raises(ValidationError, match="file_name"):
        AudioReferenceAttachRequest(
            clinic_id="clinic-1",
            file_name="",
            content_type="audio/mpeg",
            file_size_bytes=1024,
        )


# ---------------------------------------------------------------------------
# 4. AudioReferenceAttachRequest rejects zero file_size_bytes
# ---------------------------------------------------------------------------


def test_audio_reference_attach_request_rejects_zero_file_size():
    with pytest.raises(ValidationError, match="file_size_bytes"):
        AudioReferenceAttachRequest(
            clinic_id="clinic-1",
            file_name="audio.mp3",
            content_type="audio/mpeg",
            file_size_bytes=0,
        )


# ---------------------------------------------------------------------------
# 5. Valid ManualTranscriptRequest passes
# ---------------------------------------------------------------------------


def test_manual_transcript_request_valid():
    req = ManualTranscriptRequest(
        clinic_id="clinic-1",
        audio_file_path="consultation_audio/clinic-1/sess-1/audio.mp3",
        transcript_text="Chief complaint: Headache.",
    )
    assert req.language == "de-AT"


# ---------------------------------------------------------------------------
# 6. ManualTranscriptRequest rejects empty transcript_text
# ---------------------------------------------------------------------------


def test_manual_transcript_request_rejects_empty_transcript():
    with pytest.raises(ValidationError, match="transcript_text"):
        ManualTranscriptRequest(
            clinic_id="clinic-1",
            audio_file_path="some/path/audio.mp3",
            transcript_text="",
        )


# ---------------------------------------------------------------------------
# 7. ManualTranscriptRequest rejects empty audio_file_path
# ---------------------------------------------------------------------------


def test_manual_transcript_request_rejects_empty_path():
    with pytest.raises(ValidationError, match="audio_file_path"):
        ManualTranscriptRequest(
            clinic_id="clinic-1",
            audio_file_path="",
            transcript_text="Chief complaint: Headache.",
        )


# ---------------------------------------------------------------------------
# 8. Valid ClinicalSummaryDraftRequest passes
# ---------------------------------------------------------------------------


def test_clinical_summary_draft_request_valid():
    req = ClinicalSummaryDraftRequest(
        clinic_id="clinic-1",
        transcript_text="Chief complaint: Headache.",
    )
    assert req.language == "de-AT"
    assert req.patient_context is None


# ---------------------------------------------------------------------------
# 9. ClinicalSummaryDraftRequest rejects empty transcript_text
# ---------------------------------------------------------------------------


def test_clinical_summary_draft_request_rejects_empty_transcript():
    with pytest.raises(ValidationError, match="transcript_text"):
        ClinicalSummaryDraftRequest(
            clinic_id="clinic-1",
            transcript_text="",
        )


# ---------------------------------------------------------------------------
# 10. ClinicalSummaryDraftRequest rejects non-dict patient_context
# ---------------------------------------------------------------------------


def test_clinical_summary_draft_request_rejects_non_dict_patient_context():
    with pytest.raises(ValidationError, match="patient_context"):
        ClinicalSummaryDraftRequest(
            clinic_id="clinic-1",
            transcript_text="Some transcript.",
            patient_context="not a dict",
        )


# ---------------------------------------------------------------------------
# 11. Valid ReviewPackageRequest passes
# ---------------------------------------------------------------------------


def test_review_package_request_valid():
    req = ReviewPackageRequest(
        clinic_id="clinic-1",
        draft_summary=VALID_DRAFT,
    )
    assert req.transcript_text is None


# ---------------------------------------------------------------------------
# 12. ReviewPackageRequest rejects empty draft_summary
# ---------------------------------------------------------------------------


def test_review_package_request_rejects_empty_draft_summary():
    with pytest.raises(ValidationError, match="draft_summary"):
        ReviewPackageRequest(
            clinic_id="clinic-1",
            draft_summary={},
        )


# ---------------------------------------------------------------------------
# 13. Valid ApproveSummaryRequest passes
# ---------------------------------------------------------------------------


def test_approve_summary_request_valid():
    req = ApproveSummaryRequest(
        clinic_id="clinic-1",
        approved_summary=VALID_APPROVED,
        approved_by_user_id="doctor-1",
    )
    assert req.approved_by_user_id == "doctor-1"


# ---------------------------------------------------------------------------
# 14. ApproveSummaryRequest rejects empty approved_by_user_id
# ---------------------------------------------------------------------------


def test_approve_summary_request_rejects_empty_user_id():
    with pytest.raises(ValidationError, match="approved_by_user_id"):
        ApproveSummaryRequest(
            clinic_id="clinic-1",
            approved_summary=VALID_APPROVED,
            approved_by_user_id="",
        )


# ---------------------------------------------------------------------------
# 15. Valid RejectSummaryRequest passes
# ---------------------------------------------------------------------------


def test_reject_summary_request_valid():
    req = RejectSummaryRequest(
        clinic_id="clinic-1",
        rejected_reason="Missing lab results.",
    )
    assert req.rejected_by_user_id is None


# ---------------------------------------------------------------------------
# 16. RejectSummaryRequest rejects empty rejected_reason
# ---------------------------------------------------------------------------


def test_reject_summary_request_rejects_empty_reason():
    with pytest.raises(ValidationError, match="rejected_reason"):
        RejectSummaryRequest(
            clinic_id="clinic-1",
            rejected_reason="",
        )


# ---------------------------------------------------------------------------
# 17. WorkflowResponse accepts result dict
# ---------------------------------------------------------------------------


def test_workflow_response_accepts_result_dict():
    resp = WorkflowResponse(ok=True, result={"key": "value"}, message="Done.")
    assert resp.ok is True
    assert resp.result == {"key": "value"}


# ---------------------------------------------------------------------------
# 18. TimelineReportResponse accepts report dict
# ---------------------------------------------------------------------------


def test_timeline_report_response_accepts_report():
    resp = TimelineReportResponse(
        ok=True,
        report={"schema_version": "patient_timeline_report.v1", "timeline": []},
        message="Generated.",
    )
    assert resp.ok is True
    assert resp.report["schema_version"] == "patient_timeline_report.v1"
