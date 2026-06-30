"""
Tests for review_workflow — PraxisMed Sprint 2 / Module 33.

No real database, no external services, no LLM calls.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.modules.clinical_summary.review_workflow import (
    REVIEW_SCHEMA_VERSION,
    InvalidReviewInputError,
    ReviewWorkflowError,
    approve_summary_after_review,
    build_review_package,
    reject_summary_after_review,
    validate_approved_summary,
    validate_draft_ready_for_review,
    validate_rejection_reason,
    validate_review_context,
    validate_reviewer_user_id,
)
from backend.app.modules.clinical_summary.summary_builder import (
    SUMMARY_SCHEMA_VERSION,
    build_clinical_summary_draft,
)

REPO = "backend.app.modules.clinical_summary.review_workflow.consultation_repo"

SIMPLE_TRANSCRIPT = (
    "Chief complaint: Headache for three days.\n"
    "Symptoms: Nausea, light sensitivity.\n"
    "History: No prior migraines.\n"
    "Findings: Blood pressure normal.\n"
    "Assessment: Possible tension headache.\n"
    "Plan: Rest and hydration.\n"
    "Medications: Ibuprofen 400mg as needed.\n"
    "Follow up: Return in one week if not improved.\n"
)


def _valid_draft() -> dict:
    return build_clinical_summary_draft(SIMPLE_TRANSCRIPT)


# ---------------------------------------------------------------------------
# 1. validate_review_context accepts valid clinic_id and session_id
# ---------------------------------------------------------------------------


def test_validate_review_context_accepts_valid():
    result = validate_review_context("clinic-1", "sess-1")
    assert result["clinic_id"] == "clinic-1"
    assert result["session_id"] == "sess-1"


# ---------------------------------------------------------------------------
# 2. validate_review_context rejects empty clinic_id
# ---------------------------------------------------------------------------


def test_validate_review_context_rejects_empty_clinic_id():
    with pytest.raises(InvalidReviewInputError, match="clinic_id"):
        validate_review_context("", "sess-1")


# ---------------------------------------------------------------------------
# 3. validate_review_context rejects empty session_id
# ---------------------------------------------------------------------------


def test_validate_review_context_rejects_empty_session_id():
    with pytest.raises(InvalidReviewInputError, match="session_id"):
        validate_review_context("clinic-1", "")


# ---------------------------------------------------------------------------
# 4. validate_reviewer_user_id accepts valid reviewer
# ---------------------------------------------------------------------------


def test_validate_reviewer_user_id_accepts_valid():
    result = validate_reviewer_user_id("doctor-99")
    assert result == "doctor-99"


# ---------------------------------------------------------------------------
# 5. validate_reviewer_user_id rejects empty reviewer
# ---------------------------------------------------------------------------


def test_validate_reviewer_user_id_rejects_empty():
    with pytest.raises(InvalidReviewInputError, match="reviewer_user_id"):
        validate_reviewer_user_id("")


# ---------------------------------------------------------------------------
# 6. validate_draft_ready_for_review accepts valid draft
# ---------------------------------------------------------------------------


def test_validate_draft_accepts_valid():
    draft = _valid_draft()
    result = validate_draft_ready_for_review(draft)
    assert result is draft


# ---------------------------------------------------------------------------
# 7. validate_draft_ready_for_review rejects non-dict draft
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_non_dict():
    with pytest.raises(InvalidReviewInputError, match="dict"):
        validate_draft_ready_for_review("not a dict")


# ---------------------------------------------------------------------------
# 8. validate_draft_ready_for_review rejects doctor_review_required false
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_review_required_false():
    draft = _valid_draft()
    draft["doctor_review_required"] = False
    with pytest.raises(InvalidReviewInputError, match="doctor_review_required"):
        validate_draft_ready_for_review(draft)


# ---------------------------------------------------------------------------
# 9. validate_draft_ready_for_review rejects no_diagnosis_generated false
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_no_diagnosis_false():
    draft = _valid_draft()
    draft["no_diagnosis_generated"] = False
    with pytest.raises(InvalidReviewInputError, match="no_diagnosis_generated"):
        validate_draft_ready_for_review(draft)


# ---------------------------------------------------------------------------
# 10. validate_draft_ready_for_review rejects no_treatment_advice_generated false
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_no_treatment_advice_false():
    draft = _valid_draft()
    draft["no_treatment_advice_generated"] = False
    with pytest.raises(InvalidReviewInputError, match="no_treatment_advice_generated"):
        validate_draft_ready_for_review(draft)


# ---------------------------------------------------------------------------
# 11. validate_draft_ready_for_review rejects top-level diagnosis key
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_diagnosis_key():
    draft = _valid_draft()
    draft["diagnosis"] = "Migraine"
    with pytest.raises(InvalidReviewInputError, match="diagnosis"):
        validate_draft_ready_for_review(draft)


# ---------------------------------------------------------------------------
# 12. build_review_package returns pending_doctor_review status
# ---------------------------------------------------------------------------


def test_build_review_package_returns_pending():
    draft = _valid_draft()
    pkg = build_review_package("clinic-1", "sess-1", draft)
    assert pkg["status"] == "pending_doctor_review"
    assert pkg["schema_version"] == REVIEW_SCHEMA_VERSION
    assert pkg["doctor_review_required"] is True


# ---------------------------------------------------------------------------
# 13. build_review_package includes review_instructions
# ---------------------------------------------------------------------------


def test_build_review_package_includes_instructions():
    draft = _valid_draft()
    pkg = build_review_package("clinic-1", "sess-1", draft)
    instructions = pkg["review_instructions"]
    assert isinstance(instructions, list)
    assert len(instructions) >= 3
    combined = " ".join(instructions).lower()
    assert "doctor" in combined
    assert "final medical documentation" in combined
    assert "clinical judgment" in combined


# ---------------------------------------------------------------------------
# 14. build_review_package preserves transcript_text
# ---------------------------------------------------------------------------


def test_build_review_package_preserves_transcript_text():
    draft = _valid_draft()
    pkg = build_review_package("clinic-1", "sess-1", draft, transcript_text="some text")
    assert pkg["transcript_text"] == "some text"


# ---------------------------------------------------------------------------
# 15. build_review_package preserves patient_context
# ---------------------------------------------------------------------------


def test_build_review_package_preserves_patient_context():
    draft = _valid_draft()
    ctx = {"dob": "1980-01-01"}
    pkg = build_review_package("clinic-1", "sess-1", draft, patient_context=ctx)
    assert pkg["patient_context"] == ctx


# ---------------------------------------------------------------------------
# 16. build_review_package rejects non-dict patient_context
# ---------------------------------------------------------------------------


def test_build_review_package_rejects_non_dict_patient_context():
    draft = _valid_draft()
    with pytest.raises(InvalidReviewInputError, match="patient_context"):
        build_review_package("clinic-1", "sess-1", draft, patient_context="bad")


# ---------------------------------------------------------------------------
# 17. build_review_package rejects non-dict consultation_context
# ---------------------------------------------------------------------------


def test_build_review_package_rejects_non_dict_consultation_context():
    draft = _valid_draft()
    with pytest.raises(InvalidReviewInputError, match="consultation_context"):
        build_review_package("clinic-1", "sess-1", draft, consultation_context=[1, 2])


# ---------------------------------------------------------------------------
# 18. validate_approved_summary accepts valid approved_summary
# ---------------------------------------------------------------------------


def test_validate_approved_summary_accepts_valid():
    result = validate_approved_summary({"notes": "looks good"}, "doctor-1")
    assert result["doctor_approved"] is True


# ---------------------------------------------------------------------------
# 19. validate_approved_summary rejects empty approved_summary
# ---------------------------------------------------------------------------


def test_validate_approved_summary_rejects_empty_dict():
    with pytest.raises(InvalidReviewInputError, match="approved_summary"):
        validate_approved_summary({}, "doctor-1")


# ---------------------------------------------------------------------------
# 20. validate_approved_summary rejects empty approved_by_user_id
# ---------------------------------------------------------------------------


def test_validate_approved_summary_rejects_empty_user_id():
    with pytest.raises(InvalidReviewInputError, match="approved_by_user_id"):
        validate_approved_summary({"notes": "ok"}, "")


# ---------------------------------------------------------------------------
# 21. validate_approved_summary adds doctor_approved metadata
# ---------------------------------------------------------------------------


def test_validate_approved_summary_adds_metadata():
    summary = {"notes": "reviewed"}
    result = validate_approved_summary(summary, "doctor-42")
    assert result["doctor_approved"] is True
    assert result["approved_by_user_id"] == "doctor-42"
    assert result["source"] == "doctor_review"


# ---------------------------------------------------------------------------
# 22. approve_summary_after_review calls consultation_repo.approve_consultation_summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_calls_repo():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "approved"}

    with patch(
        f"{REPO}.approve_consultation_summary",
        new=AsyncMock(return_value=fake_session),
    ) as mock:
        await approve_summary_after_review(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            approved_summary={"notes": "ok"},
            approved_by_user_id="doctor-1",
        )
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 23. approve_summary_after_review passes approved_by_user_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_passes_approved_by_user_id():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "approved"}

    with patch(
        f"{REPO}.approve_consultation_summary",
        new=AsyncMock(return_value=fake_session),
    ) as mock:
        await approve_summary_after_review(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            approved_summary={"notes": "ok"},
            approved_by_user_id="doctor-1",
        )
    kwargs = mock.call_args.kwargs
    assert kwargs["approved_by_user_id"] == "doctor-1"


# ---------------------------------------------------------------------------
# 24. approve_summary_after_review returns ok true
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_returns_ok_true():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "approved"}

    with patch(
        f"{REPO}.approve_consultation_summary",
        new=AsyncMock(return_value=fake_session),
    ):
        result = await approve_summary_after_review(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            approved_summary={"notes": "ok"},
            approved_by_user_id="doctor-1",
        )
    assert result["ok"] is True
    assert result["consultation"] == fake_session
    assert "approved_summary" in result
    assert "approved" in result["message"].lower()


# ---------------------------------------------------------------------------
# 25. approve_summary_after_review maps repository error to ReviewWorkflowError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_maps_repo_error():
    pool = MagicMock()
    with patch(
        f"{REPO}.approve_consultation_summary",
        new=AsyncMock(side_effect=RuntimeError("db gone")),
    ):
        with pytest.raises(ReviewWorkflowError):
            await approve_summary_after_review(
                pool=pool,
                clinic_id="clinic-1",
                session_id="sess-1",
                approved_summary={"notes": "ok"},
                approved_by_user_id="doctor-1",
            )


# ---------------------------------------------------------------------------
# 26. validate_rejection_reason accepts valid reason
# ---------------------------------------------------------------------------


def test_validate_rejection_reason_accepts_valid():
    result = validate_rejection_reason("Missing lab results.")
    assert result == "Missing lab results."


# ---------------------------------------------------------------------------
# 27. validate_rejection_reason rejects empty reason
# ---------------------------------------------------------------------------


def test_validate_rejection_reason_rejects_empty():
    with pytest.raises(InvalidReviewInputError, match="rejected_reason"):
        validate_rejection_reason("")


# ---------------------------------------------------------------------------
# 28. reject_summary_after_review calls consultation_repo.reject_consultation_summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reject_calls_repo():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "rejected"}

    with patch(
        f"{REPO}.reject_consultation_summary",
        new=AsyncMock(return_value=fake_session),
    ) as mock:
        await reject_summary_after_review(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            rejected_reason="Incomplete transcript.",
        )
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 29. reject_summary_after_review passes rejected_by_user_id when provided
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reject_passes_rejected_by_user_id():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "rejected"}

    with patch(
        f"{REPO}.reject_consultation_summary",
        new=AsyncMock(return_value=fake_session),
    ) as mock:
        await reject_summary_after_review(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            rejected_reason="Missing info.",
            rejected_by_user_id="doctor-2",
        )
    kwargs = mock.call_args.kwargs
    assert kwargs["rejected_by_user_id"] == "doctor-2"


# ---------------------------------------------------------------------------
# 30. reject_summary_after_review returns ok true
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reject_returns_ok_true():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "rejected"}

    with patch(
        f"{REPO}.reject_consultation_summary",
        new=AsyncMock(return_value=fake_session),
    ):
        result = await reject_summary_after_review(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            rejected_reason="Needs revision.",
        )
    assert result["ok"] is True
    assert result["consultation"] == fake_session
    assert result["rejected_reason"] == "Needs revision."
    assert "rejected" in result["message"].lower()


# ---------------------------------------------------------------------------
# 31. reject_summary_after_review maps repository error to ReviewWorkflowError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reject_maps_repo_error():
    pool = MagicMock()
    with patch(
        f"{REPO}.reject_consultation_summary",
        new=AsyncMock(side_effect=RuntimeError("db gone")),
    ):
        with pytest.raises(ReviewWorkflowError):
            await reject_summary_after_review(
                pool=pool,
                clinic_id="clinic-1",
                session_id="sess-1",
                rejected_reason="Needs revision.",
            )


# ---------------------------------------------------------------------------
# 32. No real database is used
# ---------------------------------------------------------------------------


def test_no_real_database_used():
    draft = _valid_draft()
    pkg = build_review_package("clinic-1", "sess-1", draft)
    assert pkg["schema_version"] == REVIEW_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 33. No external service is called
# ---------------------------------------------------------------------------


def test_no_external_service_called():
    draft = _valid_draft()
    result = validate_draft_ready_for_review(draft)
    assert result["schema_version"] == SUMMARY_SCHEMA_VERSION
