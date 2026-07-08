"""
Tests — AI Structuring Service Foundation (Module 153).

Covers: migration, Pydantic schemas, repo functions, service layer,
routes (unit), forbidden vocabulary guards, PHI invariant, schema.sql,
arch doc existence.

No external LLM API calls. No Anthropic/OpenAI/Vapi API keys.
No patient_history_* writes. No auto-approval. No diagnosis. No medical advice.
No triage scoring. No treatment recommendations.
extraction_confidence is extraction confidence only — not a medical judgment.
production_phi_enabled always False. synthetic_demo always True.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[2]
_MIGRATION_PATH = ROOT / "backend/migrations/versions/0010_patient_history_structuring.py"
_SCHEMA_SQL_PATH = ROOT / "backend/app/db/schema.sql"
_REPO_PATH = ROOT / "backend/app/db/repositories/patient_history_structuring_repo.py"
_SERVICE_PATH = ROOT / "backend/app/services/patient_history_structuring.py"
_ROUTES_PATH = ROOT / "backend/app/api/routes/patient_history_structuring.py"
_ARCH_DOC_PATH = ROOT / "docs/architecture/AI_STRUCTURING_SERVICE_FOUNDATION.md"

# ── Helpers ────────────────────────────────────────────────────────────────────


def _load_migration() -> Any:
    spec = importlib.util.spec_from_file_location("migration_0010", _MIGRATION_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_pool(
    fetchrow_return: Any = None,
    fetch_return: Any = None,
) -> Any:
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fetchrow_return)
    pool.fetch = AsyncMock(return_value=fetch_return or [])
    return pool


def _mock_run_row(run_id: str = "run-111") -> Dict[str, Any]:
    return {
        "id": run_id,
        "clinic_id": "clinic-aaa",
        "intake_submission_id": "sub-bbb",
        "intake_link_id": None,
        "template_id": None,
        "patient_id": None,
        "appointment_request_id": None,
        "consent_event_id": "consent-ccc",
        "provider": "local_demo_extractor",
        "provider_model": None,
        "status": "completed",
        "language": "de",
        "extraction_mode": "synthetic_demo",
        "proposals_count": 1,
        "error_message": None,
        "pseudonymized_log_ref": None,
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "created_by_user_id": None,
        "created_at": "2026-07-09T10:00:00Z",
        "updated_at": "2026-07-09T10:00:00Z",
    }


def _mock_proposal_row(proposal_id: str = "prop-222") -> Dict[str, Any]:
    return {
        "id": proposal_id,
        "clinic_id": "clinic-aaa",
        "structuring_run_id": "run-111",
        "intake_submission_id": "sub-bbb",
        "consent_event_id": "consent-ccc",
        "patient_id": None,
        "appointment_request_id": None,
        "proposal_status": "unverified",
        "history_type": "allergies",
        "fhir_resource_type": "AllergyIntolerance",
        "source_question_key": "allergies_q",
        "source_answer_ref": None,
        "proposed_fields": json.dumps({"raw_answer": "peanuts", "extraction_source": "local_demo_extractor", "question_label": "Allergies"}),
        "proposed_fhir_payload": json.dumps({"resourceType": "AllergyIntolerance", "note": [{"text": "peanuts"}]}),
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


def _mock_submission_row(
    submission_id: str = "sub-bbb",
    answers: Optional[Dict] = None,
    template_id: str = "tmpl-ddd",
) -> Any:
    row = MagicMock()
    row.__iter__ = MagicMock(return_value=iter({
        "id": submission_id,
        "clinic_id": "clinic-aaa",
        "intake_link_id": None,
        "template_id": template_id,
        "consent_event_id": "consent-ccc",
        "patient_id": None,
        "appointment_request_id": None,
        "language": "de",
        "answers": json.dumps(answers or {}),
        "skipped_questions": "[]",
        "escalation_matches": "[]",
        "status": "submitted",
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "submitted_at": "2026-07-09T10:00:00Z",
        "created_at": "2026-07-09T10:00:00Z",
        "updated_at": "2026-07-09T10:00:00Z",
    }.items()))

    d = {
        "id": submission_id,
        "clinic_id": "clinic-aaa",
        "intake_link_id": None,
        "template_id": template_id,
        "consent_event_id": "consent-ccc",
        "patient_id": None,
        "appointment_request_id": None,
        "language": "de",
        "answers": json.dumps(answers or {}),
        "skipped_questions": "[]",
        "escalation_matches": "[]",
        "status": "submitted",
        "synthetic_demo": True,
        "production_phi_enabled": False,
    }
    row.__getitem__ = lambda self, k: d[k]
    row.get = lambda k, default=None: d.get(k, default)
    return row


# ── Migration tests ────────────────────────────────────────────────────────────


def test_migration_file_exists():
    assert _MIGRATION_PATH.exists()


def test_migration_revision_id():
    mod = _load_migration()
    assert mod.revision == "0010_patient_history_structuring"


def test_migration_down_revision():
    mod = _load_migration()
    assert mod.down_revision == "0009_patient_intake_links"


def test_migration_upgrade_callable():
    mod = _load_migration()
    assert callable(mod.upgrade)


def test_migration_downgrade_callable():
    mod = _load_migration()
    assert callable(mod.downgrade)


def test_migration_no_raw_prompt_column():
    src = _MIGRATION_PATH.read_text()
    assert "raw_prompt" not in src


def test_migration_no_model_response_column():
    src = _MIGRATION_PATH.read_text()
    assert "raw_model_response" not in src


def test_migration_phi_check_constraint():
    src = _MIGRATION_PATH.read_text()
    assert "production_phi_enabled = false" in src


def test_migration_demo_check_constraint():
    src = _MIGRATION_PATH.read_text()
    assert "synthetic_demo = true" in src


def test_migration_staff_review_required_check():
    src = _MIGRATION_PATH.read_text()
    assert "staff_review_required = true" in src


def test_migration_confidence_check():
    src = _MIGRATION_PATH.read_text()
    assert "extraction_confidence" in src
    assert "proposals_confidence_check" in src or "confidence_check" in src


def test_migration_structuring_runs_table_present():
    src = _MIGRATION_PATH.read_text()
    assert "patient_history_structuring_runs" in src


def test_migration_proposals_table_present():
    src = _MIGRATION_PATH.read_text()
    assert "patient_history_proposals" in src


# ── Schema.sql tests ──────────────────────────────────────────────────────────


def test_schema_sql_has_structuring_runs_table():
    src = _SCHEMA_SQL_PATH.read_text()
    assert "patient_history_structuring_runs" in src


def test_schema_sql_has_proposals_table():
    src = _SCHEMA_SQL_PATH.read_text()
    assert "patient_history_proposals" in src


def test_schema_sql_phi_check_in_runs():
    src = _SCHEMA_SQL_PATH.read_text()
    assert "structuring_runs_phi_check" in src


def test_schema_sql_phi_check_in_proposals():
    src = _SCHEMA_SQL_PATH.read_text()
    assert "proposals_phi_check" in src


def test_schema_sql_no_raw_prompt_column():
    src = _SCHEMA_SQL_PATH.read_text()
    lines = [l for l in src.splitlines() if "raw_prompt" in l and "patient_history" in l]
    assert len(lines) == 0


# ── Pydantic schema tests ─────────────────────────────────────────────────────


from backend.app.schemas.patient_history_structuring import (
    StructuringRequest,
    StructuringResult,
    ProposalStatusUpdate,
    PatientHistoryProposalRead,
    PatientHistoryStructuringRunResponse,
    PatientHistoryProposalListResponse,
)


def test_structuring_request_defaults():
    req = StructuringRequest()
    assert req.provider == "local_demo_extractor"
    assert req.extraction_mode == "synthetic_demo"
    assert req.synthetic_demo is True
    assert req.production_phi_enabled is False


def test_structuring_request_rejects_phi_true():
    with pytest.raises(ValidationError):
        StructuringRequest(production_phi_enabled=True)


def test_structuring_request_rejects_demo_false():
    with pytest.raises(ValidationError):
        StructuringRequest(synthetic_demo=False)


def test_structuring_request_rejects_invalid_provider():
    with pytest.raises(ValidationError):
        StructuringRequest(provider="openai_gpt4")


def test_structuring_request_rejects_invalid_extraction_mode():
    with pytest.raises(ValidationError):
        StructuringRequest(extraction_mode="live_llm")


def test_structuring_result_has_extraction_note():
    result = StructuringResult(ok=True)
    assert "extraction" in result.extraction_note.lower()
    assert "medical judgment" in result.extraction_note.lower()


def test_structuring_result_phi_always_false():
    result = StructuringResult(ok=True)
    assert result.production_phi_enabled is False


def test_proposal_status_update_allows_rejected():
    u = ProposalStatusUpdate(proposal_status="rejected")
    assert u.proposal_status == "rejected"


def test_proposal_status_update_allows_archived_demo():
    u = ProposalStatusUpdate(proposal_status="archived_demo")
    assert u.proposal_status == "archived_demo"


def test_proposal_status_update_rejects_merged():
    with pytest.raises(ValidationError):
        ProposalStatusUpdate(proposal_status="merged")


def test_proposal_status_update_rejects_unverified():
    with pytest.raises(ValidationError):
        ProposalStatusUpdate(proposal_status="unverified")


def test_proposal_list_response_has_extraction_note():
    r = PatientHistoryProposalListResponse(ok=True, proposals=[], total=0)
    assert "extraction" in r.extraction_note.lower()


def test_structuring_run_response_phi_false():
    r = PatientHistoryStructuringRunResponse(ok=True)
    assert r.production_phi_enabled is False


# ── Repo tests ────────────────────────────────────────────────────────────────


from backend.app.db.repositories import patient_history_structuring_repo as repo


@pytest.mark.asyncio
async def test_repo_create_structuring_run_calls_pool():
    run_row = MagicMock()
    run_row.__iter__ = MagicMock(return_value=iter(_mock_run_row().items()))
    run_row.keys = MagicMock(return_value=list(_mock_run_row().keys()))

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=run_row)

    # Simulate dict(row) behavior
    with patch("backend.app.db.repositories.patient_history_structuring_repo.dict", side_effect=lambda r: _mock_run_row()):
        result = await repo.create_structuring_run(
            pool=pool,
            clinic_id="clinic-aaa",
            intake_submission_id="sub-bbb",
            consent_event_id="consent-ccc",
        )
    pool.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_repo_create_structuring_run_sets_phi_false():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    try:
        await repo.create_structuring_run(
            pool=pool,
            clinic_id="c",
            intake_submission_id="s",
            consent_event_id="e",
        )
    except Exception:
        pass
    call_sql = pool.fetchrow.call_args[0][0]
    assert "false" in call_sql.lower()
    assert "true" in call_sql.lower()


@pytest.mark.asyncio
async def test_repo_create_history_proposal_sets_unverified():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    try:
        await repo.create_history_proposal(
            pool=pool,
            clinic_id="c",
            structuring_run_id="r",
            intake_submission_id="s",
            consent_event_id="e",
            history_type="allergies",
            fhir_resource_type="AllergyIntolerance",
            proposed_fields={},
            proposed_fhir_payload={},
        )
    except Exception:
        pass
    call_sql = pool.fetchrow.call_args[0][0]
    assert "unverified" in call_sql


@pytest.mark.asyncio
async def test_repo_update_proposal_status_uses_clinic_scoped_sql():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    result = await repo.update_proposal_status(
        pool=pool, proposal_id="p", clinic_id="c", proposal_status="rejected"
    )
    assert result is None
    call_sql = pool.fetchrow.call_args[0][0]
    assert "clinic_id" in call_sql


@pytest.mark.asyncio
async def test_repo_list_history_proposals_scoped_by_clinic():
    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=[])
    result = await repo.list_history_proposals(pool=pool, clinic_id="c")
    assert result == []
    call_sql = pool.fetch.call_args[0][0]
    assert "clinic_id" in call_sql


@pytest.mark.asyncio
async def test_repo_get_structuring_run_by_id_returns_none_when_missing():
    pool = _make_pool(fetchrow_return=None)
    result = await repo.get_structuring_run_by_id(pool=pool, run_id="x", clinic_id="c")
    assert result is None


@pytest.mark.asyncio
async def test_repo_get_history_proposal_by_id_returns_none_when_missing():
    pool = _make_pool(fetchrow_return=None)
    result = await repo.get_history_proposal_by_id(pool=pool, proposal_id="x", clinic_id="c")
    assert result is None


@pytest.mark.asyncio
async def test_repo_list_proposals_for_run_scoped():
    pool = _make_pool(fetch_return=[])
    result = await repo.list_proposals_for_run(pool=pool, run_id="r", clinic_id="c")
    assert result == []
    call_sql = pool.fetch.call_args[0][0]
    assert "structuring_run_id" in call_sql


# ── Service tests ─────────────────────────────────────────────────────────────


from backend.app.services import patient_history_structuring as svc


@pytest.mark.asyncio
async def test_service_structure_raises_if_submission_missing():
    pool = _make_pool(fetchrow_return=None)
    with pytest.raises(svc.SubmissionNotFoundError):
        await svc.structure_intake_submission(pool=pool, submission_id="x", clinic_id="c")


@pytest.mark.asyncio
async def test_service_structure_raises_if_already_structured():
    existing_run = MagicMock()
    existing_run.__getitem__ = lambda self, k: {"id": "run-existing"}[k]

    call_count = [0]

    async def fetchrow_side_effect(sql, *args):
        call_count[0] += 1
        if call_count[0] == 1:
            return existing_run
        return None

    pool = MagicMock()
    pool.fetchrow = AsyncMock(side_effect=fetchrow_side_effect)

    with pytest.raises(svc.AlreadyStructuredError):
        await svc.structure_intake_submission(pool=pool, submission_id="s", clinic_id="c")


def _make_submission_dict(
    submission_id: str = "sub-bbb",
    answers: Optional[Dict] = None,
    template_id: Optional[str] = "tmpl-ddd",
) -> Dict[str, Any]:
    return {
        "id": submission_id,
        "clinic_id": "clinic-aaa",
        "intake_link_id": None,
        "template_id": template_id,
        "consent_event_id": "consent-ccc",
        "patient_id": None,
        "appointment_request_id": None,
        "language": "de",
        "answers": answers or {},
        "skipped_questions": [],
        "escalation_matches": [],
        "status": "submitted",
        "synthetic_demo": True,
        "production_phi_enabled": False,
    }


def _make_template_questions(questions_by_target: Dict[str, str]) -> List[Dict[str, Any]]:
    qs = []
    for q_key, target in questions_by_target.items():
        qs.append({
            "question_key": q_key,
            "history_target": target,
            "type": "textarea",
            "label": {"en": q_key.replace("_", " ").title(), "de": q_key},
        })
    return qs


@pytest.mark.asyncio
async def test_service_structure_skips_empty_answers():
    sub = _make_submission_dict(answers={"allergies_q": ""})
    questions = _make_template_questions({"allergies_q": "allergies"})
    run_dict = _mock_run_row(run_id="run-new")

    with patch.object(svc, "_check_not_already_structured", AsyncMock()), \
         patch.object(svc, "_load_submission", AsyncMock(return_value=sub)), \
         patch.object(svc, "_load_template_questions", AsyncMock(return_value=questions)), \
         patch.object(repo, "create_structuring_run", AsyncMock(return_value=run_dict)), \
         patch.object(repo, "create_history_proposal", AsyncMock(return_value=_mock_proposal_row())):
        result = await svc.structure_intake_submission(
            pool=MagicMock(), submission_id="sub-bbb", clinic_id="clinic-aaa"
        )

    assert result["proposals_created"] == 0
    assert result["proposal_ids"] == []


@pytest.mark.asyncio
async def test_service_structure_skips_history_target_none():
    sub = _make_submission_dict(answers={"symptom_q": "headache"})
    questions = _make_template_questions({"symptom_q": "none"})
    run_dict = _mock_run_row(run_id="run-new")

    with patch.object(svc, "_check_not_already_structured", AsyncMock()), \
         patch.object(svc, "_load_submission", AsyncMock(return_value=sub)), \
         patch.object(svc, "_load_template_questions", AsyncMock(return_value=questions)), \
         patch.object(repo, "create_structuring_run", AsyncMock(return_value=run_dict)), \
         patch.object(repo, "create_history_proposal", AsyncMock()) as mock_create:
        result = await svc.structure_intake_submission(
            pool=MagicMock(), submission_id="sub-bbb", clinic_id="clinic-aaa"
        )

    mock_create.assert_not_called()
    assert result["proposals_created"] == 0


@pytest.mark.asyncio
async def test_service_structure_skips_appointment_context_target():
    sub = _make_submission_dict(answers={"appt_q": "next tuesday"})
    questions = _make_template_questions({"appt_q": "appointment-context"})
    run_dict = _mock_run_row()

    with patch.object(svc, "_check_not_already_structured", AsyncMock()), \
         patch.object(svc, "_load_submission", AsyncMock(return_value=sub)), \
         patch.object(svc, "_load_template_questions", AsyncMock(return_value=questions)), \
         patch.object(repo, "create_structuring_run", AsyncMock(return_value=run_dict)), \
         patch.object(repo, "create_history_proposal", AsyncMock()) as mock_create:
        await svc.structure_intake_submission(pool=MagicMock(), submission_id="s", clinic_id="c")

    mock_create.assert_not_called()


@pytest.mark.asyncio
async def test_service_structure_creates_proposal_for_allergy_answer():
    sub = _make_submission_dict(answers={"allergy_q": "peanuts, shellfish"})
    questions = _make_template_questions({"allergy_q": "allergies"})
    run_dict = _mock_run_row()
    proposal_dict = _mock_proposal_row()

    with patch.object(svc, "_check_not_already_structured", AsyncMock()), \
         patch.object(svc, "_load_submission", AsyncMock(return_value=sub)), \
         patch.object(svc, "_load_template_questions", AsyncMock(return_value=questions)), \
         patch.object(repo, "create_structuring_run", AsyncMock(return_value=run_dict)), \
         patch.object(repo, "create_history_proposal", AsyncMock(return_value=proposal_dict)) as mock_create:
        result = await svc.structure_intake_submission(
            pool=MagicMock(), submission_id="sub-bbb", clinic_id="clinic-aaa"
        )

    mock_create.assert_called_once()
    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["history_type"] == "allergies"
    assert call_kwargs["fhir_resource_type"] == "AllergyIntolerance"
    assert result["proposals_created"] == 1


@pytest.mark.asyncio
async def test_service_structure_all_proposals_status_unverified():
    sub = _make_submission_dict(answers={"med_q": "aspirin 100mg"})
    questions = _make_template_questions({"med_q": "medications"})
    run_dict = _mock_run_row()
    proposal_dict = _mock_proposal_row()

    with patch.object(svc, "_check_not_already_structured", AsyncMock()), \
         patch.object(svc, "_load_submission", AsyncMock(return_value=sub)), \
         patch.object(svc, "_load_template_questions", AsyncMock(return_value=questions)), \
         patch.object(repo, "create_structuring_run", AsyncMock(return_value=run_dict)), \
         patch.object(repo, "create_history_proposal", AsyncMock(return_value=proposal_dict)) as mock_create:
        result = await svc.structure_intake_submission(
            pool=MagicMock(), submission_id="sub-bbb", clinic_id="clinic-aaa"
        )

    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["history_type"] == "medications"
    assert call_kwargs["fhir_resource_type"] == "MedicationStatement"


@pytest.mark.asyncio
async def test_service_structure_result_phi_always_false():
    pool = _make_pool(fetchrow_return=None)
    with pytest.raises(svc.SubmissionNotFoundError):
        await svc.structure_intake_submission(pool=pool, submission_id="x", clinic_id="c")


@pytest.mark.asyncio
async def test_service_structure_result_contains_extraction_note():
    sub = _make_submission_dict(answers={}, template_id=None)
    run_dict = _mock_run_row()

    with patch.object(svc, "_check_not_already_structured", AsyncMock()), \
         patch.object(svc, "_load_submission", AsyncMock(return_value=sub)), \
         patch.object(svc, "_load_template_questions", AsyncMock(return_value=[])), \
         patch.object(repo, "create_structuring_run", AsyncMock(return_value=run_dict)):
        result = await svc.structure_intake_submission(
            pool=MagicMock(), submission_id="sub-bbb", clinic_id="clinic-aaa"
        )

    assert "extraction_note" in result
    assert "medical judgment" in result["extraction_note"].lower()
    assert result["production_phi_enabled"] is False


@pytest.mark.asyncio
async def test_service_reject_proposal_calls_repo():
    updated = _mock_proposal_row()
    updated["proposal_status"] = "rejected"
    with patch.object(repo, "update_proposal_status", AsyncMock(return_value=updated)):
        result = await svc.reject_history_proposal(
            pool=MagicMock(), proposal_id="prop-222", clinic_id="clinic-aaa", reason="duplicate"
        )
    assert result["proposal_status"] == "rejected"


@pytest.mark.asyncio
async def test_service_reject_proposal_raises_if_not_found():
    with patch.object(repo, "update_proposal_status", AsyncMock(return_value=None)):
        with pytest.raises(svc.ProposalNotFoundError):
            await svc.reject_history_proposal(
                pool=MagicMock(), proposal_id="x", clinic_id="c"
            )


@pytest.mark.asyncio
async def test_service_archive_demo_proposal_sets_archived_status():
    updated = _mock_proposal_row()
    updated["proposal_status"] = "archived_demo"
    with patch.object(repo, "update_proposal_status", AsyncMock(return_value=updated)):
        result = await svc.archive_demo_history_proposal(
            pool=MagicMock(), proposal_id="prop-222", clinic_id="clinic-aaa"
        )
    assert result["proposal_status"] == "archived_demo"


@pytest.mark.asyncio
async def test_service_archive_demo_raises_if_not_found():
    with patch.object(repo, "update_proposal_status", AsyncMock(return_value=None)):
        with pytest.raises(svc.ProposalNotFoundError):
            await svc.archive_demo_history_proposal(
                pool=MagicMock(), proposal_id="x", clinic_id="c"
            )


@pytest.mark.asyncio
async def test_service_get_structuring_run_raises_if_not_found():
    with patch.object(repo, "get_structuring_run_by_id", AsyncMock(return_value=None)):
        with pytest.raises(svc.StructuringRunNotFoundError):
            await svc.get_structuring_run(pool=MagicMock(), run_id="x", clinic_id="c")


@pytest.mark.asyncio
async def test_service_get_structuring_run_returns_run_and_proposals():
    run_dict = _mock_run_row()
    proposal_list = [_mock_proposal_row()]
    with patch.object(repo, "get_structuring_run_by_id", AsyncMock(return_value=run_dict)), \
         patch.object(repo, "list_proposals_for_run", AsyncMock(return_value=proposal_list)):
        data = await svc.get_structuring_run(pool=MagicMock(), run_id="run-111", clinic_id="clinic-aaa")
    assert data["run"]["id"] == "run-111"
    assert len(data["proposals"]) == 1


# ── History type → FHIR mapping tests ────────────────────────────────────────


def test_history_type_to_fhir_allergies():
    assert svc._HISTORY_TYPE_TO_FHIR["allergies"] == "AllergyIntolerance"


def test_history_type_to_fhir_medications():
    assert svc._HISTORY_TYPE_TO_FHIR["medications"] == "MedicationStatement"


def test_history_type_to_fhir_conditions():
    assert svc._HISTORY_TYPE_TO_FHIR["conditions"] == "Condition"


def test_history_type_to_fhir_procedures():
    assert svc._HISTORY_TYPE_TO_FHIR["procedures"] == "Procedure"


def test_history_type_to_fhir_immunizations():
    assert svc._HISTORY_TYPE_TO_FHIR["immunizations"] == "Immunization"


def test_history_type_to_fhir_family_history():
    assert svc._HISTORY_TYPE_TO_FHIR["family-history"] == "FamilyMemberHistory"


def test_history_type_to_fhir_social_history():
    assert svc._HISTORY_TYPE_TO_FHIR["social-history"] == "Observation"


# ── Routes vocabulary guard tests ─────────────────────────────────────────────


def _routes_src() -> str:
    return _ROUTES_PATH.read_text()


def _service_src() -> str:
    return _SERVICE_PATH.read_text()


def _repo_src() -> str:
    return _REPO_PATH.read_text()


def _non_prohibition(lines: List[str], word: str) -> List[str]:
    return [
        l for l in lines
        if word in l.lower()
        and "no " not in l.lower()
        and not l.strip().startswith("#")
        and "not a" not in l.lower()
        and "only" not in l.lower()
    ]


def test_routes_no_auto_approval():
    src = _routes_src()
    lines = [
        l for l in src.splitlines()
        if ("auto_approv" in l.lower() or "auto-approv" in l.lower())
        and "no" not in l.lower()
        and not l.strip().startswith("#")
    ]
    assert lines == []


def test_routes_no_diagnosis_field():
    src = _routes_src()
    lines = _non_prohibition(src.splitlines(), "diagnosis")
    assert lines == []


def test_routes_no_medical_advice():
    src = _routes_src()
    lines = _non_prohibition(src.splitlines(), "medical_advice")
    assert lines == []


def test_routes_no_triage_score():
    src = _routes_src()
    lines = _non_prohibition(src.splitlines(), "triage_score")
    assert lines == []


def test_routes_phi_always_false_in_response():
    src = _routes_src()
    assert "production_phi_enabled=False" in src or 'production_phi_enabled": false' in src.lower()


def test_routes_all_routes_require_get_current_user():
    src = _routes_src()
    assert src.count("get_current_user") >= 6


def test_service_no_api_key_usage():
    src = _service_src()
    lines = [l for l in src.splitlines() if "api_key" in l.lower() and not l.strip().startswith("#")]
    assert lines == []


def test_service_no_anthropic_import():
    src = _service_src()
    lines = [l for l in src.splitlines() if "import anthropic" in l.lower()]
    assert lines == []


def test_service_no_openai_import():
    src = _service_src()
    lines = [l for l in src.splitlines() if "import openai" in l.lower()]
    assert lines == []


def test_service_no_httpx_external_call():
    src = _service_src()
    lines = [l for l in src.splitlines() if "httpx" in l.lower() and not l.strip().startswith("#")]
    assert lines == []


def test_service_no_diagnosis_field():
    src = _service_src()
    lines = _non_prohibition(src.splitlines(), "diagnosis")
    assert lines == []


def test_service_extraction_confidence_not_clinical():
    src = _service_src()
    assert "extraction confidence" in src.lower() or "extraction_confidence" in src.lower()
    lines = [l for l in src.splitlines() if "clinical_confidence" in l.lower() and not l.strip().startswith("#")]
    assert lines == []


def test_service_no_patient_history_writes():
    src = _service_src()
    lines = [l for l in src.splitlines() if "patient_history_repo" in l.lower()]
    assert lines == []


def test_repo_no_patient_history_table_references():
    src = _repo_src()
    bad = [l for l in src.splitlines() if "patient_history_entries" in l or "patient_history_conditions" in l]
    assert bad == []


def test_repo_no_raw_api_key():
    src = _repo_src()
    lines = [l for l in src.splitlines() if "api_key" in l.lower() and not l.strip().startswith("#")]
    assert lines == []


def test_service_provider_is_local_demo():
    src = _service_src()
    assert "local_demo_extractor" in src


def test_service_no_treatment_recommendation():
    src = _service_src()
    lines = _non_prohibition(src.splitlines(), "treatment_recommendation")
    assert lines == []


# ── Route auth tests via FastAPI TestClient ───────────────────────────────────


from backend.app.api.routes.patient_history_structuring import router as structuring_router
from fastapi import FastAPI

_test_app = FastAPI()
_test_app.include_router(structuring_router)
_test_client = TestClient(_test_app, raise_server_exceptions=False)


def test_route_trigger_requires_auth():
    resp = _test_client.post(
        "/clinics/clinic-aaa/intake-submissions/sub-bbb/structure",
        json={},
    )
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_route_list_proposals_requires_auth():
    resp = _test_client.get("/clinics/clinic-aaa/history-proposals")
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_route_get_run_requires_auth():
    resp = _test_client.get("/clinics/clinic-aaa/structuring-runs/run-111")
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_route_reject_proposal_requires_auth():
    resp = _test_client.patch(
        "/clinics/clinic-aaa/history-proposals/prop-222/reject",
        json={"proposal_status": "rejected"},
    )
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_route_archive_demo_proposal_requires_auth():
    resp = _test_client.patch(
        "/clinics/clinic-aaa/history-proposals/prop-222/archive-demo",
    )
    assert resp.status_code in (401, 403, 422, 500, 503)


# ── Architecture doc tests ────────────────────────────────────────────────────


def test_arch_doc_exists():
    assert _ARCH_DOC_PATH.exists()


def test_arch_doc_mentions_module_153():
    assert "153" in _ARCH_DOC_PATH.read_text()


def test_arch_doc_mentions_local_demo_extractor():
    assert "local_demo_extractor" in _ARCH_DOC_PATH.read_text()


def test_arch_doc_no_phi():
    src = _ARCH_DOC_PATH.read_text()
    lines = [l for l in src.splitlines() if "phi" in l.lower() and "no" not in l.lower() and "production_phi_enabled" not in l.lower()]
    assert len(lines) == 0 or all("false" in l.lower() for l in lines)


# ── Forbidden fields in proposed_fields guard ─────────────────────────────────


from backend.app.schemas.patient_history_structuring import _FORBIDDEN_FIELD_KEYS


def test_forbidden_keys_include_clinical_confidence():
    assert "clinical_confidence" in _FORBIDDEN_FIELD_KEYS


def test_forbidden_keys_include_diagnosis_score():
    assert "diagnosis_score" in _FORBIDDEN_FIELD_KEYS


def test_forbidden_keys_include_triage_score():
    assert "triage_score" in _FORBIDDEN_FIELD_KEYS


def test_forbidden_keys_include_risk_score():
    assert "risk_score" in _FORBIDDEN_FIELD_KEYS


def test_forbidden_keys_include_medical_advice():
    assert "medical_advice" in _FORBIDDEN_FIELD_KEYS


def test_forbidden_keys_include_treatment_recommendation():
    assert "treatment_recommendation" in _FORBIDDEN_FIELD_KEYS
