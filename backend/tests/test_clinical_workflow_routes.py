"""
Tests for clinical workflow routes — PraxisMed Sprint 3 / Module 35.

Strategy:
- Use FastAPI TestClient; no real event loop or database.
- Override get_db_pool via app.dependency_overrides.
- Patch service functions at their usage site in the route module.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.api.deps import get_db_pool
from backend.app.main import app

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLINIC_ID = "11111111-1111-4111-8111-111111111111"
SESSION_ID = "22222222-2222-4222-8222-222222222222"
PATIENT_ID = "33333333-3333-4333-8333-333333333333"

BASE = "/clinical-workflows"
AUDIO_URL = f"{BASE}/consultations/{SESSION_ID}/audio-reference"
TRANSCRIPT_URL = f"{BASE}/consultations/{SESSION_ID}/manual-transcript"
DRAFT_URL = f"{BASE}/consultations/{SESSION_ID}/draft-summary"
REVIEW_URL = f"{BASE}/consultations/{SESSION_ID}/review-package"
APPROVE_URL = f"{BASE}/consultations/{SESSION_ID}/approve-summary"
REJECT_URL = f"{BASE}/consultations/{SESSION_ID}/reject-summary"
TIMELINE_URL = f"{BASE}/patients/{PATIENT_ID}/timeline"

SVC = "backend.app.api.routes.clinical_workflows"

FAKE_POOL = MagicMock()

FAKE_AUDIO_RESULT = {
    "ok": True,
    "consultation": {"id": SESSION_ID, "status": "audio_uploaded"},
    "audio_reference": {"file_name": "audio.mp3"},
    "message": "Audio reference attached. Upload not yet implemented.",
}

FAKE_TRANSCRIPT_RESULT = {
    "ok": True,
    "consultation": {"id": SESSION_ID, "status": "transcribed"},
    "transcription": {"transcript_text": "Chief complaint: Headache.", "segments": []},
    "message": "Transcription completed and saved.",
}

FAKE_DRAFT_RESULT = {
    "ok": True,
    "consultation": {"id": SESSION_ID, "status": "draft_ready"},
    "draft_summary": {"schema_version": "clinical_summary_draft.v1"},
    "message": "Clinical summary draft created and saved. Doctor review is required.",
}

FAKE_REVIEW_PACKAGE = {
    "schema_version": "doctor_review_workflow.v1",
    "clinic_id": CLINIC_ID,
    "session_id": SESSION_ID,
    "status": "pending_doctor_review",
    "doctor_review_required": True,
    "draft_summary": {},
    "review_instructions": ["Doctor must review and edit before approval."],
}

FAKE_APPROVE_RESULT = {
    "ok": True,
    "consultation": {"id": SESSION_ID, "status": "approved"},
    "approved_summary": {"doctor_approved": True},
    "message": "Clinical summary approved by doctor.",
}

FAKE_REJECT_RESULT = {
    "ok": True,
    "consultation": {"id": SESSION_ID, "status": "rejected"},
    "rejected_reason": "Missing lab results.",
    "message": "Clinical summary rejected. Revision is required.",
}

FAKE_TIMELINE_RESULT = {
    "ok": True,
    "report": {
        "schema_version": "patient_timeline_report.v1",
        "patient": {"id": PATIENT_ID, "full_name": "Maria Mustermann", "clinic_id": CLINIC_ID},
        "timeline": [],
        "totals": {"consultations": 0},
        "safety": {},
        "message": "Patient timeline report generated from existing records only.",
    },
    "message": "Patient timeline report generated from existing records only.",
}

VALID_DRAFT_SUMMARY = {
    "schema_version": "clinical_summary_draft.v1",
    "doctor_review_required": True,
    "no_diagnosis_generated": True,
    "no_treatment_advice_generated": True,
    "sections": {
        "chief_complaint": {"title": "Chief Complaint", "content": [], "source": "deterministic_placeholder", "confidence": None, "doctor_editable": True},
        "symptoms": {"title": "Symptoms", "content": [], "source": "deterministic_placeholder", "confidence": None, "doctor_editable": True},
        "relevant_history": {"title": "Relevant History", "content": [], "source": "deterministic_placeholder", "confidence": None, "doctor_editable": True},
        "findings": {"title": "Findings", "content": [], "source": "deterministic_placeholder", "confidence": None, "doctor_editable": True},
        "assessment": {"title": "Assessment", "content": [], "source": "deterministic_placeholder", "confidence": None, "doctor_editable": True, "draft_only": True},
        "plan": {"title": "Plan", "content": [], "source": "deterministic_placeholder", "confidence": None, "doctor_editable": True},
        "medications": {"title": "Medications", "content": [], "source": "deterministic_placeholder", "confidence": None, "doctor_editable": True},
        "follow_up": {"title": "Follow-Up", "content": [], "source": "deterministic_placeholder", "confidence": None, "doctor_editable": True},
        "missing_information": {"title": "Missing Information", "content": [], "source": "deterministic_placeholder", "confidence": None, "doctor_editable": True},
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)


@pytest.fixture()
def client_no_pool():
    app.dependency_overrides.pop(get_db_pool, None)
    yield TestClient(app)


# ---------------------------------------------------------------------------
# 1. POST audio-reference returns 200
# ---------------------------------------------------------------------------


def test_audio_reference_returns_200(client):
    with patch(f"{SVC}.attach_audio_reference_to_consultation", new=AsyncMock(return_value=FAKE_AUDIO_RESULT)):
        resp = client.post(AUDIO_URL, json={
            "clinic_id": CLINIC_ID,
            "file_name": "audio.mp3",
            "content_type": "audio/mpeg",
            "file_size_bytes": 1024,
        })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 2. POST audio-reference calls attach_audio_reference_to_consultation
# ---------------------------------------------------------------------------


def test_audio_reference_calls_service(client):
    with patch(f"{SVC}.attach_audio_reference_to_consultation", new=AsyncMock(return_value=FAKE_AUDIO_RESULT)) as mock:
        client.post(AUDIO_URL, json={
            "clinic_id": CLINIC_ID,
            "file_name": "audio.mp3",
            "content_type": "audio/mpeg",
            "file_size_bytes": 1024,
        })
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 3. POST manual-transcript returns 200
# ---------------------------------------------------------------------------


def test_manual_transcript_returns_200(client):
    with patch(f"{SVC}.transcribe_consultation_audio", new=AsyncMock(return_value=FAKE_TRANSCRIPT_RESULT)):
        resp = client.post(TRANSCRIPT_URL, json={
            "clinic_id": CLINIC_ID,
            "audio_file_path": "consultation_audio/clinic-1/sess-1/audio.mp3",
            "transcript_text": "Chief complaint: Headache.",
        })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 4. POST manual-transcript calls transcribe_consultation_audio
# ---------------------------------------------------------------------------


def test_manual_transcript_calls_service(client):
    with patch(f"{SVC}.transcribe_consultation_audio", new=AsyncMock(return_value=FAKE_TRANSCRIPT_RESULT)) as mock:
        client.post(TRANSCRIPT_URL, json={
            "clinic_id": CLINIC_ID,
            "audio_file_path": "consultation_audio/clinic-1/sess-1/audio.mp3",
            "transcript_text": "Chief complaint: Headache.",
        })
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 5. manual-transcript uses provider="manual"
# ---------------------------------------------------------------------------


def test_manual_transcript_uses_manual_provider(client):
    with patch(f"{SVC}.transcribe_consultation_audio", new=AsyncMock(return_value=FAKE_TRANSCRIPT_RESULT)) as mock:
        client.post(TRANSCRIPT_URL, json={
            "clinic_id": CLINIC_ID,
            "audio_file_path": "consultation_audio/clinic-1/sess-1/audio.mp3",
            "transcript_text": "Chief complaint: Headache.",
        })
    kwargs = mock.call_args.kwargs
    assert kwargs["provider"] == "manual"


# ---------------------------------------------------------------------------
# 6. POST draft-summary returns 200
# ---------------------------------------------------------------------------


def test_draft_summary_returns_200(client):
    with patch(f"{SVC}.create_and_save_clinical_summary_draft", new=AsyncMock(return_value=FAKE_DRAFT_RESULT)):
        resp = client.post(DRAFT_URL, json={
            "clinic_id": CLINIC_ID,
            "transcript_text": "Chief complaint: Headache.",
        })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 7. POST draft-summary calls create_and_save_clinical_summary_draft
# ---------------------------------------------------------------------------


def test_draft_summary_calls_service(client):
    with patch(f"{SVC}.create_and_save_clinical_summary_draft", new=AsyncMock(return_value=FAKE_DRAFT_RESULT)) as mock:
        client.post(DRAFT_URL, json={
            "clinic_id": CLINIC_ID,
            "transcript_text": "Chief complaint: Headache.",
        })
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 8. POST review-package returns 200
# ---------------------------------------------------------------------------


def test_review_package_returns_200(client):
    with patch(f"{SVC}.build_review_package", return_value=FAKE_REVIEW_PACKAGE):
        resp = client.post(REVIEW_URL, json={
            "clinic_id": CLINIC_ID,
            "draft_summary": VALID_DRAFT_SUMMARY,
        })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 9. POST review-package calls build_review_package
# ---------------------------------------------------------------------------


def test_review_package_calls_service(client):
    with patch(f"{SVC}.build_review_package", return_value=FAKE_REVIEW_PACKAGE) as mock:
        client.post(REVIEW_URL, json={
            "clinic_id": CLINIC_ID,
            "draft_summary": VALID_DRAFT_SUMMARY,
        })
    mock.assert_called_once()


# ---------------------------------------------------------------------------
# 10. POST approve-summary returns 200
# ---------------------------------------------------------------------------


def test_approve_summary_returns_200(client):
    with patch(f"{SVC}.approve_summary_after_review", new=AsyncMock(return_value=FAKE_APPROVE_RESULT)):
        resp = client.post(APPROVE_URL, json={
            "clinic_id": CLINIC_ID,
            "approved_summary": {"doctor_approved": True, "notes": "reviewed"},
            "approved_by_user_id": "doctor-1",
        })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 11. POST approve-summary calls approve_summary_after_review
# ---------------------------------------------------------------------------


def test_approve_summary_calls_service(client):
    with patch(f"{SVC}.approve_summary_after_review", new=AsyncMock(return_value=FAKE_APPROVE_RESULT)) as mock:
        client.post(APPROVE_URL, json={
            "clinic_id": CLINIC_ID,
            "approved_summary": {"doctor_approved": True, "notes": "reviewed"},
            "approved_by_user_id": "doctor-1",
        })
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 12. POST reject-summary returns 200
# ---------------------------------------------------------------------------


def test_reject_summary_returns_200(client):
    with patch(f"{SVC}.reject_summary_after_review", new=AsyncMock(return_value=FAKE_REJECT_RESULT)):
        resp = client.post(REJECT_URL, json={
            "clinic_id": CLINIC_ID,
            "rejected_reason": "Missing lab results.",
        })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 13. POST reject-summary calls reject_summary_after_review
# ---------------------------------------------------------------------------


def test_reject_summary_calls_service(client):
    with patch(f"{SVC}.reject_summary_after_review", new=AsyncMock(return_value=FAKE_REJECT_RESULT)) as mock:
        client.post(REJECT_URL, json={
            "clinic_id": CLINIC_ID,
            "rejected_reason": "Missing lab results.",
        })
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 14. GET patient timeline returns 200
# ---------------------------------------------------------------------------


def test_timeline_returns_200(client):
    with patch(f"{SVC}.create_patient_timeline_report", new=AsyncMock(return_value=FAKE_TIMELINE_RESULT)):
        resp = client.get(TIMELINE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 15. GET patient timeline calls create_patient_timeline_report
# ---------------------------------------------------------------------------


def test_timeline_calls_service(client):
    with patch(f"{SVC}.create_patient_timeline_report", new=AsyncMock(return_value=FAKE_TIMELINE_RESULT)) as mock:
        client.get(TIMELINE_URL, params={"clinic_id": CLINIC_ID})
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 16. Timeline route passes include_drafts default false
# ---------------------------------------------------------------------------


def test_timeline_include_drafts_default_false(client):
    with patch(f"{SVC}.create_patient_timeline_report", new=AsyncMock(return_value=FAKE_TIMELINE_RESULT)) as mock:
        client.get(TIMELINE_URL, params={"clinic_id": CLINIC_ID})
    kwargs = mock.call_args.kwargs
    assert kwargs["include_drafts"] is False


# ---------------------------------------------------------------------------
# 17. Timeline route passes limit
# ---------------------------------------------------------------------------


def test_timeline_passes_limit(client):
    with patch(f"{SVC}.create_patient_timeline_report", new=AsyncMock(return_value=FAKE_TIMELINE_RESULT)) as mock:
        client.get(TIMELINE_URL, params={"clinic_id": CLINIC_ID, "limit": 10})
    kwargs = mock.call_args.kwargs
    assert kwargs["limit"] == 10


# ---------------------------------------------------------------------------
# 18. Missing db_pool returns HTTP 503 for DB-backed routes
# ---------------------------------------------------------------------------


def test_audio_reference_503_when_no_pool(client_no_pool):
    resp = client_no_pool.post(AUDIO_URL, json={
        "clinic_id": CLINIC_ID,
        "file_name": "audio.mp3",
        "content_type": "audio/mpeg",
        "file_size_bytes": 1024,
    })
    assert resp.status_code == 503


# ---------------------------------------------------------------------------
# 19. Invalid request body returns HTTP 422
# ---------------------------------------------------------------------------


def test_audio_reference_422_on_missing_field(client):
    resp = client.post(AUDIO_URL, json={"clinic_id": CLINIC_ID})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 20. Missing db_pool returns 503 for transcript route
# ---------------------------------------------------------------------------


def test_transcript_503_when_no_pool(client_no_pool):
    resp = client_no_pool.post(TRANSCRIPT_URL, json={
        "clinic_id": CLINIC_ID,
        "audio_file_path": "some/path.mp3",
        "transcript_text": "Chief complaint: Headache.",
    })
    assert resp.status_code == 503


# ---------------------------------------------------------------------------
# 21. Invalid request body returns HTTP 422 for draft-summary
# ---------------------------------------------------------------------------


def test_draft_summary_422_on_missing_field(client):
    resp = client.post(DRAFT_URL, json={"clinic_id": CLINIC_ID})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 22. Service validation error maps to HTTP 400
# ---------------------------------------------------------------------------


def test_draft_summary_400_on_validation_error(client):
    from backend.app.modules.clinical_summary.summary_builder import InvalidClinicalSummaryInputError

    with patch(
        f"{SVC}.create_and_save_clinical_summary_draft",
        new=AsyncMock(side_effect=InvalidClinicalSummaryInputError("bad input")),
    ):
        resp = client.post(DRAFT_URL, json={
            "clinic_id": CLINIC_ID,
            "transcript_text": "Chief complaint: Headache.",
        })
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 23. PatientNotFoundError maps to HTTP 404
# ---------------------------------------------------------------------------


def test_timeline_404_on_patient_not_found(client):
    from backend.app.modules.patient_timeline.timeline_report import PatientNotFoundError

    with patch(
        f"{SVC}.create_patient_timeline_report",
        new=AsyncMock(side_effect=PatientNotFoundError("not found")),
    ):
        resp = client.get(TIMELINE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 24. Service internal error maps to HTTP 500
# ---------------------------------------------------------------------------


def test_approve_summary_500_on_service_error(client):
    from backend.app.modules.clinical_summary.review_workflow import ReviewWorkflowError

    with patch(
        f"{SVC}.approve_summary_after_review",
        new=AsyncMock(side_effect=ReviewWorkflowError("db gone")),
    ):
        resp = client.post(APPROVE_URL, json={
            "clinic_id": CLINIC_ID,
            "approved_summary": {"doctor_approved": True, "notes": "reviewed"},
            "approved_by_user_id": "doctor-1",
        })
    assert resp.status_code == 500


# ---------------------------------------------------------------------------
# 25. Existing routes still work after adding clinical_workflows router
# ---------------------------------------------------------------------------


def test_health_route_still_works(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_consultations_route_still_works(client):
    from backend.app.db.repositories import consultation_repo as cr

    with patch(
        "backend.app.api.routes.consultations.consultation_repo.list_consultation_sessions",
        new=AsyncMock(return_value=[]),
    ):
        resp = client.get("/consultations", params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200


def test_patients_route_still_works(client):
    with patch(
        "backend.app.api.routes.patients.patient_repo.list_patients",
        new=AsyncMock(return_value=[]),
    ):
        resp = client.get("/patients", params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 26. No external service is called
# ---------------------------------------------------------------------------


def test_no_external_service_called(client):
    with patch(f"{SVC}.create_and_save_clinical_summary_draft", new=AsyncMock(return_value=FAKE_DRAFT_RESULT)):
        resp = client.post(DRAFT_URL, json={
            "clinic_id": CLINIC_ID,
            "transcript_text": "Chief complaint: Headache.",
        })
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 27. No real database is used
# ---------------------------------------------------------------------------


def test_no_real_database_used(client):
    with patch(f"{SVC}.create_patient_timeline_report", new=AsyncMock(return_value=FAKE_TIMELINE_RESULT)):
        resp = client.get(TIMELINE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
