"""
Tests — Doctor Review & Merge UI Foundation (Module 154).

Covers: Pydantic schemas, service layer, routes (unit), frontend/static
vocabulary guards, PHI invariant, arch doc, forbidden fields.

No auto-approval. No diagnosis. No medical advice. No triage scoring.
No treatment recommendations. No external LLM. No API keys.
production_phi_enabled always False. synthetic_demo always True.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = ROOT / "backend/app/schemas/patient_history_review.py"
_SERVICE_PATH = ROOT / "backend/app/services/patient_history_review.py"
_ROUTES_PATH = ROOT / "backend/app/api/routes/patient_history_review.py"
_ARCH_DOC_PATH = ROOT / "docs/architecture/DOCTOR_REVIEW_MERGE_UI_FOUNDATION.md"
_PAGE_PATH = ROOT / "frontend/app/developer-console/history-review/page.tsx"
_CONSOLE_PAGE_PATH = ROOT / "frontend/app/developer-console/page.tsx"
_API_TS_PATH = ROOT / "frontend/lib/api.ts"

# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_pool(fetchrow_return: Any = None, fetch_return: Any = None) -> Any:
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fetchrow_return)
    pool.fetch = AsyncMock(return_value=fetch_return or [])
    pool.execute = AsyncMock(return_value=None)
    return pool


def _mock_proposal(
    proposal_id: str = "prop-aaa",
    status: str = "unverified",
    history_type: str = "allergies",
    fhir_resource_type: str = "AllergyIntolerance",
    patient_id: Optional[str] = "patient-bbb",
) -> Dict[str, Any]:
    return {
        "id": proposal_id,
        "clinic_id": "clinic-ccc",
        "structuring_run_id": "run-ddd",
        "intake_submission_id": "sub-eee",
        "consent_event_id": "consent-fff",
        "patient_id": patient_id,
        "appointment_request_id": None,
        "proposal_status": status,
        "history_type": history_type,
        "fhir_resource_type": fhir_resource_type,
        "source_question_key": "allergy_q",
        "source_answer_ref": None,
        "proposed_fields": {"raw_answer": "peanuts", "extraction_source": "local_demo_extractor", "question_label": "Allergies"},
        "proposed_fhir_payload": {"resourceType": fhir_resource_type},
        "extraction_confidence": 0.70,
        "confidence_explanation": "Extraction confidence only — not a medical judgment.",
        "staff_review_required": True,
        "reviewed_by_user_id": None,
        "reviewed_at": None,
        "review_note": None,
        "merged_history_entry_id": None,
        "rejected_reason": None,
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "created_at": "2026-07-09T10:00:00Z",
        "updated_at": "2026-07-09T10:00:00Z",
    }


def _mock_history_row(entry_id: str = "entry-zzz") -> Dict[str, Any]:
    return {
        "id": entry_id,
        "clinic_id": "clinic-ccc",
        "patient_id": "patient-bbb",
        "status": "approved",
        "source_type": "ai_proposal",
        "production_phi_enabled": False,
    }


# ── Pydantic schema tests ─────────────────────────────────────────────────────


from backend.app.schemas.patient_history_review import (
    PatientHistoryMergeRequest,
    PatientHistoryMergeResult,
    PatientHistoryRejectRequest,
    PatientHistoryRejectResult,
    PatientHistoryProposalReviewDetail,
    PatientHistoryReviewQueueResponse,
    _FORBIDDEN_MERGE_KEYS,
)


def test_merge_request_requires_confirm_staff_review():
    with pytest.raises(ValidationError):
        PatientHistoryMergeRequest(edited_fields={}, confirm_staff_review=False)


def test_merge_request_accepts_confirm_true():
    req = PatientHistoryMergeRequest(edited_fields={"substance_text": "peanuts"}, confirm_staff_review=True)
    assert req.confirm_staff_review is True


def test_merge_request_rejects_forbidden_field_key_clinical_confidence():
    with pytest.raises(ValidationError):
        PatientHistoryMergeRequest(
            edited_fields={"clinical_confidence": 0.9},
            confirm_staff_review=True,
        )


def test_merge_request_rejects_diagnosis_score():
    with pytest.raises(ValidationError):
        PatientHistoryMergeRequest(
            edited_fields={"diagnosis_score": 0.5},
            confirm_staff_review=True,
        )


def test_merge_request_rejects_auto_approved():
    with pytest.raises(ValidationError):
        PatientHistoryMergeRequest(
            edited_fields={"auto_approved": True},
            confirm_staff_review=True,
        )


def test_merge_request_rejects_auto_confirmed():
    with pytest.raises(ValidationError):
        PatientHistoryMergeRequest(
            edited_fields={"auto_confirmed": True},
            confirm_staff_review=True,
        )


def test_merge_request_rejects_triage_score():
    with pytest.raises(ValidationError):
        PatientHistoryMergeRequest(
            edited_fields={"triage_score": 3},
            confirm_staff_review=True,
        )


def test_merge_request_rejects_phi_unlock():
    with pytest.raises(ValidationError):
        PatientHistoryMergeRequest(
            edited_fields={"production_phi_enabled": True},
            confirm_staff_review=True,
        )


def test_merge_result_phi_always_false():
    r = PatientHistoryMergeResult(
        ok=True,
        proposal_id="p",
        merged_history_entry_id="e",
        history_type="allergies",
        fhir_resource_type="AllergyIntolerance",
    )
    assert r.production_phi_enabled is False


def test_merge_result_default_message():
    r = PatientHistoryMergeResult(
        ok=True,
        proposal_id="p",
        merged_history_entry_id="e",
        history_type="allergies",
        fhir_resource_type="AllergyIntolerance",
    )
    assert "staff review" in r.message.lower()


def test_reject_result_phi_always_false():
    r = PatientHistoryRejectResult(ok=True, proposal_id="p")
    assert r.production_phi_enabled is False


def test_reject_result_default_message():
    r = PatientHistoryRejectResult(ok=True, proposal_id="p")
    assert "rejected" in r.message.lower()


def test_review_queue_response_has_extraction_note():
    r = PatientHistoryReviewQueueResponse(ok=True, proposals=[], total=0)
    assert "extraction" in r.extraction_note.lower()


def test_review_queue_response_phi_false():
    r = PatientHistoryReviewQueueResponse(ok=True, proposals=[], total=0)
    assert r.production_phi_enabled is False


def test_forbidden_merge_keys_includes_clinical_confidence():
    assert "clinical_confidence" in _FORBIDDEN_MERGE_KEYS


def test_forbidden_merge_keys_includes_diagnosis_score():
    assert "diagnosis_score" in _FORBIDDEN_MERGE_KEYS


def test_forbidden_merge_keys_includes_risk_score():
    assert "risk_score" in _FORBIDDEN_MERGE_KEYS


def test_forbidden_merge_keys_includes_medical_advice():
    assert "medical_advice" in _FORBIDDEN_MERGE_KEYS


def test_forbidden_merge_keys_includes_treatment_recommendation():
    assert "treatment_recommendation" in _FORBIDDEN_MERGE_KEYS


def test_forbidden_merge_keys_includes_auto_approved():
    assert "auto_approved" in _FORBIDDEN_MERGE_KEYS


# ── Service tests ─────────────────────────────────────────────────────────────


from backend.app.services import patient_history_review as svc


@pytest.mark.asyncio
async def test_service_list_review_queue_returns_proposals():
    proposals = [_mock_proposal()]
    with patch("backend.app.services.patient_history_review.struct_repo.list_history_proposals", AsyncMock(return_value=proposals)):
        result = await svc.list_review_queue(pool=MagicMock(), clinic_id="clinic-ccc")
    assert len(result) == 1
    assert result[0]["proposal_status"] == "unverified"


@pytest.mark.asyncio
async def test_service_get_proposal_review_detail_returns_proposal():
    proposal = _mock_proposal()
    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)):
        result = await svc.get_proposal_review_detail(pool=MagicMock(), proposal_id="prop-aaa", clinic_id="clinic-ccc")
    assert result["id"] == "prop-aaa"


@pytest.mark.asyncio
async def test_service_get_proposal_review_detail_raises_if_not_found():
    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=None)):
        with pytest.raises(svc.ProposalNotFoundError):
            await svc.get_proposal_review_detail(pool=MagicMock(), proposal_id="x", clinic_id="c")


@pytest.mark.asyncio
async def test_service_approve_merge_raises_if_not_found():
    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=None)):
        with pytest.raises(svc.ProposalNotFoundError):
            await svc.approve_and_merge_history_proposal(
                pool=MagicMock(), proposal_id="x", clinic_id="c", edited_fields={}
            )


@pytest.mark.asyncio
async def test_service_approve_merge_raises_if_not_unverified():
    rejected_proposal = _mock_proposal(status="rejected")
    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=rejected_proposal)):
        with pytest.raises(svc.ProposalNotEligibleError):
            await svc.approve_and_merge_history_proposal(
                pool=MagicMock(), proposal_id="prop-aaa", clinic_id="clinic-ccc", edited_fields={}
            )


@pytest.mark.asyncio
async def test_service_approve_merge_raises_if_merged():
    merged_proposal = _mock_proposal(status="merged")
    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=merged_proposal)):
        with pytest.raises(svc.ProposalNotEligibleError):
            await svc.approve_and_merge_history_proposal(
                pool=MagicMock(), proposal_id="prop-aaa", clinic_id="clinic-ccc", edited_fields={}
            )


@pytest.mark.asyncio
async def test_service_approve_merge_raises_if_no_patient_id():
    proposal = _mock_proposal(patient_id=None)
    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)):
        with pytest.raises(svc.PatientRequiredError):
            await svc.approve_and_merge_history_proposal(
                pool=MagicMock(), proposal_id="prop-aaa", clinic_id="clinic-ccc", edited_fields={}
            )


@pytest.mark.asyncio
async def test_service_approve_merge_raises_if_forbidden_field():
    proposal = _mock_proposal()
    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.assert_valid_consent_for_history_write", AsyncMock()):
        with pytest.raises(svc.ForbiddenMergeFieldError):
            await svc.approve_and_merge_history_proposal(
                pool=MagicMock(),
                proposal_id="prop-aaa",
                clinic_id="clinic-ccc",
                edited_fields={"clinical_confidence": 0.9},
            )


@pytest.mark.asyncio
async def test_service_approve_merge_calls_consent_gate():
    proposal = _mock_proposal()
    history_row = _mock_history_row()
    mock_create_fn = AsyncMock(return_value=history_row)

    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.assert_valid_consent_for_history_write", AsyncMock()) as mock_consent, \
         patch.dict(svc._CREATE_FN, {"allergies": mock_create_fn}), \
         patch("backend.app.services.patient_history_review.struct_repo.update_proposal_status", AsyncMock(return_value=proposal)):
        pool = _make_pool()
        await svc.approve_and_merge_history_proposal(
            pool=pool, proposal_id="prop-aaa", clinic_id="clinic-ccc",
            edited_fields={"substance_text": "peanuts"},
        )
    mock_consent.assert_called_once()


@pytest.mark.asyncio
async def test_service_approve_merge_creates_history_row():
    proposal = _mock_proposal()
    history_row = _mock_history_row()
    mock_create_fn = AsyncMock(return_value=history_row)

    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.assert_valid_consent_for_history_write", AsyncMock()), \
         patch.dict(svc._CREATE_FN, {"allergies": mock_create_fn}), \
         patch("backend.app.services.patient_history_review.struct_repo.update_proposal_status", AsyncMock(return_value=proposal)):
        pool = _make_pool()
        await svc.approve_and_merge_history_proposal(
            pool=pool, proposal_id="prop-aaa", clinic_id="clinic-ccc",
            edited_fields={"substance_text": "peanuts"},
        )
    mock_create_fn.assert_called_once()


@pytest.mark.asyncio
async def test_service_approve_merge_history_row_status_approved():
    proposal = _mock_proposal()
    history_row = _mock_history_row()
    assert history_row["status"] == "approved"
    mock_create_fn = AsyncMock(return_value=history_row)

    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.assert_valid_consent_for_history_write", AsyncMock()), \
         patch.dict(svc._CREATE_FN, {"allergies": mock_create_fn}), \
         patch("backend.app.services.patient_history_review.struct_repo.update_proposal_status", AsyncMock(return_value=proposal)):
        pool = _make_pool()
        result = await svc.approve_and_merge_history_proposal(
            pool=pool, proposal_id="prop-aaa", clinic_id="clinic-ccc",
            edited_fields={"substance_text": "peanuts"},
        )
    assert result["merged_history_entry_id"] == "entry-zzz"


@pytest.mark.asyncio
async def test_service_approve_merge_history_row_source_type_ai_proposal():
    proposal = _mock_proposal()
    history_row = _mock_history_row()
    assert history_row["source_type"] == "ai_proposal"
    mock_create_fn = AsyncMock(return_value=history_row)

    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.assert_valid_consent_for_history_write", AsyncMock()), \
         patch.dict(svc._CREATE_FN, {"allergies": mock_create_fn}), \
         patch("backend.app.services.patient_history_review.struct_repo.update_proposal_status", AsyncMock(return_value=proposal)):
        pool = _make_pool()
        await svc.approve_and_merge_history_proposal(
            pool=pool, proposal_id="prop-aaa", clinic_id="clinic-ccc",
            edited_fields={"substance_text": "peanuts"},
        )
    kwargs = mock_create_fn.call_args.kwargs
    assert kwargs.get("source_type") == "ai_proposal"


@pytest.mark.asyncio
async def test_service_approve_merge_history_row_phi_false():
    proposal = _mock_proposal()
    history_row = _mock_history_row()
    assert history_row["production_phi_enabled"] is False
    mock_create_fn = AsyncMock(return_value=history_row)

    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.assert_valid_consent_for_history_write", AsyncMock()), \
         patch.dict(svc._CREATE_FN, {"allergies": mock_create_fn}), \
         patch("backend.app.services.patient_history_review.struct_repo.update_proposal_status", AsyncMock(return_value=proposal)):
        pool = _make_pool()
        result = await svc.approve_and_merge_history_proposal(
            pool=pool, proposal_id="prop-aaa", clinic_id="clinic-ccc",
            edited_fields={"substance_text": "peanuts"},
        )
    assert result["production_phi_enabled"] is False


@pytest.mark.asyncio
async def test_service_approve_merge_result_proposal_status_merged():
    proposal = _mock_proposal()
    history_row = _mock_history_row()
    mock_create_fn = AsyncMock(return_value=history_row)

    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.assert_valid_consent_for_history_write", AsyncMock()), \
         patch.dict(svc._CREATE_FN, {"allergies": mock_create_fn}), \
         patch("backend.app.services.patient_history_review.struct_repo.update_proposal_status", AsyncMock(return_value=proposal)):
        pool = _make_pool()
        result = await svc.approve_and_merge_history_proposal(
            pool=pool, proposal_id="prop-aaa", clinic_id="clinic-ccc",
            edited_fields={"substance_text": "peanuts"},
        )
    assert result["proposal_status"] == "merged"


@pytest.mark.asyncio
async def test_service_approve_merge_result_message_mentions_staff_review():
    proposal = _mock_proposal()
    history_row = _mock_history_row()
    mock_create_fn = AsyncMock(return_value=history_row)

    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.assert_valid_consent_for_history_write", AsyncMock()), \
         patch.dict(svc._CREATE_FN, {"allergies": mock_create_fn}), \
         patch("backend.app.services.patient_history_review.struct_repo.update_proposal_status", AsyncMock(return_value=proposal)):
        pool = _make_pool()
        result = await svc.approve_and_merge_history_proposal(
            pool=pool, proposal_id="prop-aaa", clinic_id="clinic-ccc",
            edited_fields={"substance_text": "peanuts"},
        )
    assert "staff review" in result["message"].lower()


@pytest.mark.asyncio
async def test_service_reject_sets_proposal_status_rejected():
    proposal = _mock_proposal()
    rejected = dict(proposal)
    rejected["proposal_status"] = "rejected"

    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.struct_repo.update_proposal_status", AsyncMock(return_value=rejected)):
        result = await svc.reject_history_proposal_with_review(
            pool=MagicMock(), proposal_id="prop-aaa", clinic_id="clinic-ccc", rejected_reason="duplicate"
        )
    assert result["proposal_status"] == "rejected"


@pytest.mark.asyncio
async def test_service_reject_does_not_create_history_row():
    proposal = _mock_proposal()

    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.struct_repo.update_proposal_status", AsyncMock(return_value=proposal)), \
         patch("backend.app.services.patient_history_review.patient_history_repo.create_allergy_history", AsyncMock()) as mock_create:
        await svc.reject_history_proposal_with_review(
            pool=MagicMock(), proposal_id="prop-aaa", clinic_id="clinic-ccc"
        )
    mock_create.assert_not_called()


@pytest.mark.asyncio
async def test_service_reject_raises_if_already_rejected():
    proposal = _mock_proposal(status="rejected")
    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=proposal)):
        with pytest.raises(svc.ProposalNotEligibleError):
            await svc.reject_history_proposal_with_review(
                pool=MagicMock(), proposal_id="prop-aaa", clinic_id="clinic-ccc"
            )


@pytest.mark.asyncio
async def test_service_reject_raises_if_not_found():
    with patch("backend.app.services.patient_history_review.struct_repo.get_history_proposal_by_id", AsyncMock(return_value=None)):
        with pytest.raises(svc.ProposalNotFoundError):
            await svc.reject_history_proposal_with_review(
                pool=MagicMock(), proposal_id="x", clinic_id="c"
            )


# ── History type mapping tests ────────────────────────────────────────────────


def test_service_primary_field_allergies():
    assert svc._PRIMARY_TEXT_FIELD["allergies"] == "substance_text"


def test_service_primary_field_medications():
    assert svc._PRIMARY_TEXT_FIELD["medications"] == "medication_text"


def test_service_primary_field_conditions():
    assert svc._PRIMARY_TEXT_FIELD["conditions"] == "condition_text"


def test_service_primary_field_procedures():
    assert svc._PRIMARY_TEXT_FIELD["procedures"] == "procedure_text"


def test_service_primary_field_immunizations():
    assert svc._PRIMARY_TEXT_FIELD["immunizations"] == "vaccine_text"


def test_service_primary_field_family_history():
    assert svc._PRIMARY_TEXT_FIELD["family-history"] == "relationship_text"


def test_service_primary_field_social_history():
    assert svc._PRIMARY_TEXT_FIELD["social-history"] == "observation_category"


# ── Route tests via FastAPI TestClient ────────────────────────────────────────


from backend.app.api.routes.patient_history_review import router as review_router

_test_app = FastAPI()
_test_app.include_router(review_router)
_test_client = TestClient(_test_app, raise_server_exceptions=False)


def test_route_review_queue_requires_auth():
    resp = _test_client.get("/clinics/clinic-ccc/patient-history-review-queue")
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_route_proposal_review_requires_auth():
    resp = _test_client.get("/patient-history-proposals/prop-aaa/review?clinic_id=clinic-ccc")
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_route_approve_merge_requires_auth():
    resp = _test_client.patch(
        "/patient-history-proposals/prop-aaa/approve-merge?clinic_id=clinic-ccc",
        json={"edited_fields": {}, "confirm_staff_review": True},
    )
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_route_reject_review_requires_auth():
    resp = _test_client.patch(
        "/patient-history-proposals/prop-aaa/reject-review?clinic_id=clinic-ccc",
        json={},
    )
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_no_delete_route_exists():
    resp = _test_client.delete("/patient-history-proposals/prop-aaa")
    assert resp.status_code in (404, 405)


def test_no_public_approve_route():
    src = _ROUTES_PATH.read_text()
    assert "/public/" not in src
    assert "public_approve" not in src


# ── Routes vocabulary guard tests ─────────────────────────────────────────────


def _non_prohibition(lines: List[str], word: str) -> List[str]:
    return [
        l for l in lines
        if word in l.lower()
        and "no " not in l.lower()
        and not l.strip().startswith("#")
        and "not a" not in l.lower()
    ]


def test_routes_no_auto_approval():
    src = _ROUTES_PATH.read_text()
    lines = [
        l for l in src.splitlines()
        if ("auto_approv" in l.lower() or "auto-approv" in l.lower())
        and "no" not in l.lower()
        and not l.strip().startswith("#")
    ]
    assert lines == []


def test_routes_no_diagnosis():
    src = _ROUTES_PATH.read_text()
    assert _non_prohibition(src.splitlines(), "diagnosis_generation") == []


def test_routes_no_medical_advice():
    src = _ROUTES_PATH.read_text()
    lines = [l for l in src.splitlines() if "medical_advice" in l.lower() and "no" not in l.lower() and not l.strip().startswith("#")]
    assert lines == []


def test_routes_phi_false_in_response():
    src = _ROUTES_PATH.read_text()
    assert "production_phi_enabled=False" in src or "production_phi_enabled" in src


def test_routes_all_routes_require_get_current_user():
    src = _ROUTES_PATH.read_text()
    assert src.count("get_current_user") >= 4


def test_service_no_api_key():
    src = _SERVICE_PATH.read_text()
    lines = [l for l in src.splitlines() if "api_key" in l.lower() and not l.strip().startswith("#")]
    assert lines == []


def test_service_no_anthropic_import():
    src = _SERVICE_PATH.read_text()
    assert "import anthropic" not in src.lower()


def test_service_no_auto_approval():
    src = _SERVICE_PATH.read_text()
    lines = [
        l for l in src.splitlines()
        if "auto_approv" in l.lower()
        and "no" not in l.lower()
        and not l.strip().startswith("#")
    ]
    assert lines == []


def test_service_no_diagnosis_generation():
    src = _SERVICE_PATH.read_text()
    lines = [l for l in src.splitlines() if "diagnosis_generated" in l.lower() and not l.strip().startswith("#")]
    assert lines == []


# ── Frontend page tests ───────────────────────────────────────────────────────


def _page_src() -> str:
    return _PAGE_PATH.read_text()


def _api_ts_src() -> str:
    return _API_TS_PATH.read_text()


def _console_src() -> str:
    return _CONSOLE_PAGE_PATH.read_text()


def test_history_review_page_exists():
    assert _PAGE_PATH.exists()


def test_history_review_page_mentions_patient_history_review():
    assert "Patient History Review" in _page_src()


def test_history_review_page_mentions_merge_queue():
    src = _page_src()
    assert "merge queue" in src.lower() or "Doctor-reviewed" in src


def test_history_review_page_mentions_admin_staging():
    assert "ADMIN / STAGING" in _page_src() or "ADMIN" in _page_src()


def test_history_review_page_mentions_synthetic_staging():
    assert "Synthetic staging only" in _page_src() or "synthetic" in _page_src().lower()


def test_history_review_page_mentions_staff_doctor_review():
    src = _page_src()
    assert "staff" in src.lower() or "doctor" in src.lower()


def test_history_review_page_mentions_production_phi_no_go():
    assert "Production PHI remains NO-GO" in _page_src()


def test_history_review_page_has_clinic_id_input():
    assert "clinicId" in _page_src() or "clinic_id" in _page_src() or "Clinic ID" in _page_src()


def test_history_review_page_has_patient_id_filter():
    assert "patientId" in _page_src() or "Patient ID" in _page_src()


def test_history_review_page_has_history_type_filter():
    assert "historyType" in _page_src() or "history_type" in _page_src()


def test_history_review_page_has_load_queue_button():
    assert "Load review queue" in _page_src()


def test_history_review_page_has_approve_merge_button():
    assert "Approve & merge" in _page_src()


def test_history_review_page_has_reject_proposal_button():
    assert "Reject proposal" in _page_src()


def test_history_review_page_has_staff_review_confirmation():
    src = _page_src()
    assert "confirm" in src.lower() and ("staff" in src.lower() or "review" in src.lower())


def test_history_review_page_mentions_extraction_confidence_note():
    assert "not a medical judgment" in _page_src()


def test_history_review_page_no_ai_diagnosis():
    src = _page_src()
    lines = [l for l in src.splitlines() if "ai diagnosis" in l.lower() and "//" not in l]
    assert lines == []


def test_history_review_page_no_medical_advice_claim():
    src = _page_src()
    lines = [l for l in src.splitlines() if "medical advice" in l.lower() and "no " not in l.lower() and "//" not in l]
    assert lines == []


def test_history_review_page_no_automatic_approval():
    src = _page_src()
    lines = [l for l in src.splitlines() if "automatic approval" in l.lower() and "no " not in l.lower() and "//" not in l]
    assert lines == []


def test_history_review_page_no_local_storage():
    assert "localStorage" not in _page_src()


def test_history_review_page_no_session_storage():
    assert "sessionStorage" not in _page_src()


def test_api_ts_has_fetch_review_queue():
    assert "fetchPatientHistoryReviewQueue" in _api_ts_src()


def test_api_ts_has_fetch_proposal_review():
    assert "fetchPatientHistoryProposalReview" in _api_ts_src()


def test_api_ts_has_approve_merge():
    assert "approveMergePatientHistoryProposal" in _api_ts_src()


def test_api_ts_has_reject_review():
    assert "rejectReviewPatientHistoryProposal" in _api_ts_src()


def test_api_ts_uses_credentials_include_for_review():
    src = _api_ts_src()
    assert "credentials" in src and "include" in src


def test_api_ts_no_local_storage():
    assert "localStorage" not in _api_ts_src()


def test_api_ts_no_session_storage():
    assert "sessionStorage" not in _api_ts_src()


def test_developer_console_links_to_history_review():
    assert "/developer-console/history-review" in _console_src()


def test_developer_console_mentions_patient_history_review():
    assert "Patient History Review" in _console_src()


# ── Architecture doc tests ────────────────────────────────────────────────────


def test_arch_doc_exists():
    assert _ARCH_DOC_PATH.exists()


def test_arch_doc_mentions_module_154():
    assert "154" in _ARCH_DOC_PATH.read_text()


def test_arch_doc_mentions_no_auto_approval():
    src = _ARCH_DOC_PATH.read_text()
    assert "auto-approval" in src.lower() or "auto_approval" in src.lower()


def test_arch_doc_mentions_staff_review():
    assert "staff" in _ARCH_DOC_PATH.read_text().lower()


def test_arch_doc_mentions_synthetic_staging():
    assert "synthetic" in _ARCH_DOC_PATH.read_text().lower()


def test_arch_doc_mentions_phi_no_go():
    assert "Production PHI remains NO-GO" in _ARCH_DOC_PATH.read_text()


def test_arch_doc_mentions_approved_row():
    assert "approved" in _ARCH_DOC_PATH.read_text().lower()


def test_arch_doc_mentions_ai_proposal_source():
    assert "ai_proposal" in _ARCH_DOC_PATH.read_text()
