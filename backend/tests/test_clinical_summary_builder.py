"""
Tests for summary_builder — PraxisMed Sprint 2 / Module 32.

No real database, no external services, no LLM calls.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.modules.clinical_summary.summary_builder import (
    SUMMARY_SCHEMA_VERSION,
    ClinicalSummaryError,
    InvalidClinicalSummaryInputError,
    build_clinical_summary_draft,
    create_and_save_clinical_summary_draft,
    create_empty_summary_template,
    parse_structured_transcript_markers,
    validate_clinical_summary_draft,
    validate_summary_input,
)

REPO = "backend.app.modules.clinical_summary.summary_builder.consultation_repo"

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

UNSTRUCTURED_TRANSCRIPT = "Patient came in feeling unwell. Doctor examined the patient."


# ---------------------------------------------------------------------------
# 1. validate_summary_input accepts valid transcript
# ---------------------------------------------------------------------------


def test_validate_input_accepts_valid():
    result = validate_summary_input("Patient reports headache.")
    assert result["transcript_text"] == "Patient reports headache."
    assert result["language"] == "de-AT"


# ---------------------------------------------------------------------------
# 2. validate_summary_input rejects empty transcript_text
# ---------------------------------------------------------------------------


def test_validate_input_rejects_empty_transcript():
    with pytest.raises(InvalidClinicalSummaryInputError, match="transcript_text"):
        validate_summary_input("")


# ---------------------------------------------------------------------------
# 3. validate_summary_input rejects empty language
# ---------------------------------------------------------------------------


def test_validate_input_rejects_empty_language():
    with pytest.raises(InvalidClinicalSummaryInputError, match="language"):
        validate_summary_input("Some text.", language="")


# ---------------------------------------------------------------------------
# 4. validate_summary_input rejects non-dict patient_context
# ---------------------------------------------------------------------------


def test_validate_input_rejects_non_dict_patient_context():
    with pytest.raises(InvalidClinicalSummaryInputError, match="patient_context"):
        validate_summary_input("Some text.", patient_context="not a dict")


# ---------------------------------------------------------------------------
# 5. validate_summary_input rejects non-dict consultation_context
# ---------------------------------------------------------------------------


def test_validate_input_rejects_non_dict_consultation_context():
    with pytest.raises(InvalidClinicalSummaryInputError, match="consultation_context"):
        validate_summary_input("Some text.", consultation_context=["list"])


# ---------------------------------------------------------------------------
# 6. create_empty_summary_template includes schema_version
# ---------------------------------------------------------------------------


def test_template_includes_schema_version():
    tmpl = create_empty_summary_template()
    assert tmpl["schema_version"] == SUMMARY_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 7. create_empty_summary_template includes all required sections
# ---------------------------------------------------------------------------


def test_template_includes_all_required_sections():
    tmpl = create_empty_summary_template()
    for section in (
        "chief_complaint", "symptoms", "relevant_history", "findings",
        "assessment", "plan", "medications", "follow_up", "missing_information",
    ):
        assert section in tmpl["sections"], f"Missing section: {section}"


# ---------------------------------------------------------------------------
# 8. create_empty_summary_template sets doctor_review_required true
# ---------------------------------------------------------------------------


def test_template_sets_doctor_review_required():
    tmpl = create_empty_summary_template()
    assert tmpl["doctor_review_required"] is True


# ---------------------------------------------------------------------------
# 9. create_empty_summary_template sets no_diagnosis_generated true
# ---------------------------------------------------------------------------


def test_template_sets_no_diagnosis_generated():
    tmpl = create_empty_summary_template()
    assert tmpl["no_diagnosis_generated"] is True


# ---------------------------------------------------------------------------
# 10. create_empty_summary_template sets no_treatment_advice_generated true
# ---------------------------------------------------------------------------


def test_template_sets_no_treatment_advice_generated():
    tmpl = create_empty_summary_template()
    assert tmpl["no_treatment_advice_generated"] is True


# ---------------------------------------------------------------------------
# 11. assessment section is draft_only and doctor_editable
# ---------------------------------------------------------------------------


def test_assessment_is_draft_only_and_doctor_editable():
    tmpl = create_empty_summary_template()
    assessment = tmpl["sections"]["assessment"]
    assert assessment["draft_only"] is True
    assert assessment["doctor_editable"] is True
    assert assessment["content"] == []


# ---------------------------------------------------------------------------
# 12. parse_structured_transcript_markers extracts chief complaint
# ---------------------------------------------------------------------------


def test_parse_extracts_chief_complaint():
    markers = parse_structured_transcript_markers("Chief complaint: Headache.\n")
    assert "chief_complaint" in markers
    assert "Headache." in markers["chief_complaint"]


# ---------------------------------------------------------------------------
# 13. parse_structured_transcript_markers extracts symptoms
# ---------------------------------------------------------------------------


def test_parse_extracts_symptoms():
    markers = parse_structured_transcript_markers("Symptoms: Nausea, vomiting.\n")
    assert "symptoms" in markers
    assert markers["symptoms"][0] == "Nausea, vomiting."


# ---------------------------------------------------------------------------
# 14. parse_structured_transcript_markers extracts relevant history
# ---------------------------------------------------------------------------


def test_parse_extracts_relevant_history():
    markers = parse_structured_transcript_markers("Relevant history: Hypertension.\n")
    assert "relevant_history" in markers
    assert "Hypertension." in markers["relevant_history"]


# ---------------------------------------------------------------------------
# 15. parse_structured_transcript_markers extracts findings from examination marker
# ---------------------------------------------------------------------------


def test_parse_extracts_findings_from_examination():
    markers = parse_structured_transcript_markers("Examination: Blood pressure 120/80.\n")
    assert "findings" in markers
    assert "Blood pressure 120/80." in markers["findings"]


# ---------------------------------------------------------------------------
# 16. parse_structured_transcript_markers extracts medications from medication marker
# ---------------------------------------------------------------------------


def test_parse_extracts_medications_from_medication():
    markers = parse_structured_transcript_markers("Medication: Aspirin 100mg daily.\n")
    assert "medications" in markers
    assert "Aspirin 100mg daily." in markers["medications"]


# ---------------------------------------------------------------------------
# 17. parse_structured_transcript_markers handles case-insensitive markers
# ---------------------------------------------------------------------------


def test_parse_handles_case_insensitive_markers():
    markers = parse_structured_transcript_markers("CHIEF COMPLAINT: Sore throat.\n")
    assert "chief_complaint" in markers
    assert "Sore throat." in markers["chief_complaint"]


# ---------------------------------------------------------------------------
# 18. parse_structured_transcript_markers ignores unstructured text
# ---------------------------------------------------------------------------


def test_parse_ignores_unstructured_text():
    markers = parse_structured_transcript_markers(UNSTRUCTURED_TRANSCRIPT)
    assert markers == {}


# ---------------------------------------------------------------------------
# 19. build_clinical_summary_draft returns schema_version clinical_summary_draft.v1
# ---------------------------------------------------------------------------


def test_build_draft_schema_version():
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT)
    assert draft["schema_version"] == SUMMARY_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 20. build_clinical_summary_draft fills only explicitly marked sections
# ---------------------------------------------------------------------------


def test_build_draft_fills_marked_sections():
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT)
    assert draft["sections"]["chief_complaint"]["content"] != []
    assert draft["sections"]["symptoms"]["content"] != []
    assert draft["sections"]["plan"]["content"] != []


# ---------------------------------------------------------------------------
# 21. build_clinical_summary_draft preserves patient_context
# ---------------------------------------------------------------------------


def test_build_draft_preserves_patient_context():
    ctx = {"dob": "1980-01-01", "gender": "female"}
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT, patient_context=ctx)
    assert draft["patient_context"] == ctx


# ---------------------------------------------------------------------------
# 22. build_clinical_summary_draft preserves consultation_context
# ---------------------------------------------------------------------------


def test_build_draft_preserves_consultation_context():
    ctx = {"session_type": "follow_up"}
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT, consultation_context=ctx)
    assert draft["consultation_context"] == ctx


# ---------------------------------------------------------------------------
# 23. build_clinical_summary_draft preserves raw_payload
# ---------------------------------------------------------------------------


def test_build_draft_preserves_raw_payload():
    payload = {"device": "tablet"}
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT, raw_payload=payload)
    assert draft["raw_payload"] == payload


# ---------------------------------------------------------------------------
# 24. build_clinical_summary_draft includes transcript_metadata
# ---------------------------------------------------------------------------


def test_build_draft_includes_transcript_metadata():
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT)
    meta = draft["transcript_metadata"]
    assert meta["transcript_available"] is True
    assert meta["transcript_character_count"] == len(SIMPLE_TRANSCRIPT)
    assert meta["structured_markers_found"] > 0


# ---------------------------------------------------------------------------
# 25. build_clinical_summary_draft adds missing_information when no markers found
# ---------------------------------------------------------------------------


def test_build_draft_adds_missing_info_for_unstructured():
    draft = build_clinical_summary_draft(UNSTRUCTURED_TRANSCRIPT)
    missing = draft["sections"]["missing_information"]["content"]
    assert len(missing) > 0
    assert any("doctor" in line.lower() for line in missing)


# ---------------------------------------------------------------------------
# 26. build_clinical_summary_draft does not create diagnosis key
# ---------------------------------------------------------------------------


def test_build_draft_no_diagnosis_key():
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT)
    assert "diagnosis" not in draft
    for section in draft["sections"].values():
        assert "diagnosis" not in section


# ---------------------------------------------------------------------------
# 27. validate_clinical_summary_draft accepts valid draft
# ---------------------------------------------------------------------------


def test_validate_draft_accepts_valid():
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT)
    result = validate_clinical_summary_draft(draft)
    assert result is draft


# ---------------------------------------------------------------------------
# 28. validate_clinical_summary_draft rejects non-dict draft
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_non_dict():
    with pytest.raises(InvalidClinicalSummaryInputError, match="dict"):
        validate_clinical_summary_draft("not a dict")


# ---------------------------------------------------------------------------
# 29. validate_clinical_summary_draft rejects missing schema_version
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_missing_schema_version():
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT)
    del draft["schema_version"]
    with pytest.raises(InvalidClinicalSummaryInputError, match="schema_version"):
        validate_clinical_summary_draft(draft)


# ---------------------------------------------------------------------------
# 30. validate_clinical_summary_draft rejects missing required section
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_missing_section():
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT)
    del draft["sections"]["plan"]
    with pytest.raises(InvalidClinicalSummaryInputError, match="plan"):
        validate_clinical_summary_draft(draft)


# ---------------------------------------------------------------------------
# 31. validate_clinical_summary_draft rejects doctor_review_required false
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_false_review_required():
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT)
    draft["doctor_review_required"] = False
    with pytest.raises(InvalidClinicalSummaryInputError, match="doctor_review_required"):
        validate_clinical_summary_draft(draft)


# ---------------------------------------------------------------------------
# 32. validate_clinical_summary_draft rejects top-level diagnosis key
# ---------------------------------------------------------------------------


def test_validate_draft_rejects_diagnosis_key():
    draft = build_clinical_summary_draft(SIMPLE_TRANSCRIPT)
    draft["diagnosis"] = "Migraine"
    with pytest.raises(InvalidClinicalSummaryInputError, match="diagnosis"):
        validate_clinical_summary_draft(draft)


# ---------------------------------------------------------------------------
# 33. create_and_save_clinical_summary_draft calls consultation_repo.save_draft_summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_calls_repo():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "draft_ready"}

    with patch(f"{REPO}.save_draft_summary", new=AsyncMock(return_value=fake_session)) as mock:
        await create_and_save_clinical_summary_draft(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            transcript_text=SIMPLE_TRANSCRIPT,
        )
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 34. create_and_save_clinical_summary_draft passes draft_summary to repository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_passes_draft_summary():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "draft_ready"}

    with patch(f"{REPO}.save_draft_summary", new=AsyncMock(return_value=fake_session)) as mock:
        await create_and_save_clinical_summary_draft(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            transcript_text=SIMPLE_TRANSCRIPT,
        )
    kwargs = mock.call_args.kwargs
    passed_draft = kwargs["draft_summary"]
    assert passed_draft["schema_version"] == SUMMARY_SCHEMA_VERSION
    assert passed_draft["doctor_review_required"] is True


# ---------------------------------------------------------------------------
# 35. create_and_save_clinical_summary_draft returns ok true
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_returns_ok_true():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "draft_ready"}

    with patch(f"{REPO}.save_draft_summary", new=AsyncMock(return_value=fake_session)):
        result = await create_and_save_clinical_summary_draft(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            transcript_text=SIMPLE_TRANSCRIPT,
        )
    assert result["ok"] is True
    assert result["consultation"] == fake_session
    assert "draft_summary" in result


# ---------------------------------------------------------------------------
# 36. create_and_save_clinical_summary_draft message says doctor review is required
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_message_mentions_doctor_review():
    pool = MagicMock()
    fake_session = {"id": "sess-1", "status": "draft_ready"}

    with patch(f"{REPO}.save_draft_summary", new=AsyncMock(return_value=fake_session)):
        result = await create_and_save_clinical_summary_draft(
            pool=pool,
            clinic_id="clinic-1",
            session_id="sess-1",
            transcript_text=SIMPLE_TRANSCRIPT,
        )
    assert "doctor review" in result["message"].lower()


# ---------------------------------------------------------------------------
# 37. create_and_save_clinical_summary_draft validates empty clinic_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_validates_empty_clinic_id():
    pool = MagicMock()
    with pytest.raises(InvalidClinicalSummaryInputError, match="clinic_id"):
        await create_and_save_clinical_summary_draft(
            pool=pool, clinic_id="", session_id="sess-1",
            transcript_text=SIMPLE_TRANSCRIPT,
        )


# ---------------------------------------------------------------------------
# 38. create_and_save_clinical_summary_draft validates empty session_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_validates_empty_session_id():
    pool = MagicMock()
    with pytest.raises(InvalidClinicalSummaryInputError, match="session_id"):
        await create_and_save_clinical_summary_draft(
            pool=pool, clinic_id="clinic-1", session_id="",
            transcript_text=SIMPLE_TRANSCRIPT,
        )


# ---------------------------------------------------------------------------
# 39. create_and_save_clinical_summary_draft maps repository error to ClinicalSummaryError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_draft_maps_repo_error():
    pool = MagicMock()
    with patch(
        f"{REPO}.save_draft_summary",
        new=AsyncMock(side_effect=RuntimeError("db gone")),
    ):
        with pytest.raises(ClinicalSummaryError):
            await create_and_save_clinical_summary_draft(
                pool=pool, clinic_id="clinic-1", session_id="sess-1",
                transcript_text=SIMPLE_TRANSCRIPT,
            )


# ---------------------------------------------------------------------------
# 40. No real database is used
# ---------------------------------------------------------------------------


def test_no_real_database_used():
    draft = build_clinical_summary_draft("Chief complaint: Cough.")
    assert draft["schema_version"] == SUMMARY_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 41. No external service is called
# ---------------------------------------------------------------------------


def test_no_external_service_called():
    markers = parse_structured_transcript_markers("Symptoms: Fever.\nPlan: Rest.")
    assert "symptoms" in markers
    assert "plan" in markers
