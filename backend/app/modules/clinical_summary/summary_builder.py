"""
Clinical Summary Draft Generator — PraxisMed Sprint 2 / Module 32

Deterministic placeholder summary builder for consultation transcripts.

Safety guarantees:
  - Never generates diagnosis.
  - Never produces treatment advice.
  - Never invents information not present in the transcript.
  - Every draft is marked doctor_review_required=True.
  - AI/LLM calls: NONE.
  - External service calls: NONE.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from backend.app.db.repositories import consultation_repo


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ClinicalSummaryError(RuntimeError):
    """Base class for clinical summary errors."""


class InvalidClinicalSummaryInputError(ClinicalSummaryError):
    """Raised when summary input is missing or invalid."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUMMARY_SCHEMA_VERSION = "clinical_summary_draft.v1"
DEFAULT_GENERATOR = "deterministic_placeholder"

_REQUIRED_SECTIONS = [
    "chief_complaint",
    "symptoms",
    "relevant_history",
    "findings",
    "assessment",
    "plan",
    "medications",
    "follow_up",
    "missing_information",
]

# Mapping: lowercased marker prefix → canonical section name
_MARKER_MAP = {
    "chief complaint":    "chief_complaint",
    "complaint":          "chief_complaint",
    "symptoms":           "symptoms",
    "history":            "relevant_history",
    "relevant history":   "relevant_history",
    "findings":           "findings",
    "examination":        "findings",
    "assessment":         "assessment",
    "plan":               "plan",
    "medication":         "medications",
    "medications":        "medications",
    "follow up":          "follow_up",
    "follow-up":          "follow_up",
    "missing information":"missing_information",
}

# Pre-compiled pattern: lines starting with a known marker followed by ":"
_MARKER_PATTERN = re.compile(
    r"^("
    + "|".join(re.escape(k) for k in sorted(_MARKER_MAP, key=len, reverse=True))
    + r")\s*:\s*(.*)",
    re.IGNORECASE | re.MULTILINE,
)


# ---------------------------------------------------------------------------
# 1. validate_summary_input
# ---------------------------------------------------------------------------


def validate_summary_input(
    transcript_text: str,
    language: str = "de-AT",
    patient_context: Optional[Dict[str, Any]] = None,
    consultation_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not transcript_text or not isinstance(transcript_text, str) or not transcript_text.strip():
        raise InvalidClinicalSummaryInputError("'transcript_text' must be a non-empty string")
    if not language or not language.strip():
        raise InvalidClinicalSummaryInputError("'language' must not be empty")
    if patient_context is not None and not isinstance(patient_context, dict):
        raise InvalidClinicalSummaryInputError("'patient_context' must be a dict if provided")
    if consultation_context is not None and not isinstance(consultation_context, dict):
        raise InvalidClinicalSummaryInputError("'consultation_context' must be a dict if provided")

    return {
        "transcript_text": transcript_text,
        "language": language,
        "patient_context": patient_context,
        "consultation_context": consultation_context,
    }


# ---------------------------------------------------------------------------
# 2. create_empty_summary_template
# ---------------------------------------------------------------------------


def _make_section(title: str, *, draft_only: bool = False) -> Dict[str, Any]:
    section: Dict[str, Any] = {
        "title": title,
        "content": [],
        "source": DEFAULT_GENERATOR,
        "confidence": None,
        "doctor_editable": True,
    }
    if draft_only:
        section["draft_only"] = True
    return section


def create_empty_summary_template(
    language: str = "de-AT",
    source: str = DEFAULT_GENERATOR,
) -> Dict[str, Any]:
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "language": language,
        "source": source,
        "generator": DEFAULT_GENERATOR,
        "doctor_review_required": True,
        "no_diagnosis_generated": True,
        "no_treatment_advice_generated": True,
        "sections": {
            "chief_complaint":    _make_section("Chief Complaint"),
            "symptoms":           _make_section("Symptoms"),
            "relevant_history":   _make_section("Relevant History"),
            "findings":           _make_section("Findings"),
            "assessment":         _make_section("Assessment", draft_only=True),
            "plan":               _make_section("Plan"),
            "medications":        _make_section("Medications"),
            "follow_up":          _make_section("Follow-Up"),
            "missing_information": _make_section("Missing Information"),
        },
    }


# ---------------------------------------------------------------------------
# 3. parse_structured_transcript_markers
# ---------------------------------------------------------------------------


def parse_structured_transcript_markers(transcript_text: str) -> Dict[str, List[str]]:
    found: Dict[str, List[str]] = {}
    for match in _MARKER_PATTERN.finditer(transcript_text):
        marker_key = match.group(1).strip().lower()
        value = match.group(2).strip()
        if not value:
            continue
        section = _MARKER_MAP.get(marker_key)
        if section is None:
            continue
        found.setdefault(section, []).append(value)
    return found


# ---------------------------------------------------------------------------
# 4. build_clinical_summary_draft
# ---------------------------------------------------------------------------


def build_clinical_summary_draft(
    transcript_text: str,
    language: str = "de-AT",
    patient_context: Optional[Dict[str, Any]] = None,
    consultation_context: Optional[Dict[str, Any]] = None,
    source: str = DEFAULT_GENERATOR,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    validate_summary_input(
        transcript_text=transcript_text,
        language=language,
        patient_context=patient_context,
        consultation_context=consultation_context,
    )

    draft = create_empty_summary_template(language=language, source=source)

    markers = parse_structured_transcript_markers(transcript_text)

    for section_name, lines in markers.items():
        if section_name in draft["sections"]:
            draft["sections"][section_name]["content"] = lines

    if not markers:
        draft["sections"]["missing_information"]["content"] = [
            "No structured markers were detected in the transcript. "
            "Doctor must review the full transcript directly."
        ]

    if patient_context:
        draft["patient_context"] = patient_context
    if consultation_context:
        draft["consultation_context"] = consultation_context
    if raw_payload is not None:
        draft["raw_payload"] = raw_payload

    draft["transcript_metadata"] = {
        "transcript_available": True,
        "transcript_character_count": len(transcript_text),
        "structured_markers_found": len(markers),
    }

    draft["safety_note"] = (
        "Draft generated from transcript markers only. "
        "Doctor review and approval required."
    )

    return draft


# ---------------------------------------------------------------------------
# 5. validate_clinical_summary_draft
# ---------------------------------------------------------------------------


def validate_clinical_summary_draft(draft_summary: Any) -> Dict[str, Any]:
    if not isinstance(draft_summary, dict):
        raise InvalidClinicalSummaryInputError("'draft_summary' must be a dict")

    if "schema_version" not in draft_summary:
        raise InvalidClinicalSummaryInputError(
            "'draft_summary' must contain 'schema_version'"
        )

    if not draft_summary.get("doctor_review_required"):
        raise InvalidClinicalSummaryInputError(
            "'doctor_review_required' must be True in draft_summary"
        )

    sections = draft_summary.get("sections", {})
    for required in _REQUIRED_SECTIONS:
        if required not in sections:
            raise InvalidClinicalSummaryInputError(
                f"Required section '{required}' missing from draft_summary"
            )

    if "diagnosis" in draft_summary:
        raise InvalidClinicalSummaryInputError(
            "draft_summary must not contain a top-level 'diagnosis' key"
        )

    return draft_summary


# ---------------------------------------------------------------------------
# 6. create_and_save_clinical_summary_draft
# ---------------------------------------------------------------------------


async def create_and_save_clinical_summary_draft(
    pool: Any,
    clinic_id: str,
    session_id: str,
    transcript_text: str,
    language: str = "de-AT",
    patient_context: Optional[Dict[str, Any]] = None,
    consultation_context: Optional[Dict[str, Any]] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not clinic_id or not clinic_id.strip():
        raise InvalidClinicalSummaryInputError("'clinic_id' must not be empty")
    if not session_id or not session_id.strip():
        raise InvalidClinicalSummaryInputError("'session_id' must not be empty")

    draft_summary = build_clinical_summary_draft(
        transcript_text=transcript_text,
        language=language,
        patient_context=patient_context,
        consultation_context=consultation_context,
        raw_payload=raw_payload,
    )
    validate_clinical_summary_draft(draft_summary)

    try:
        consultation = await consultation_repo.save_draft_summary(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            draft_summary=draft_summary,
        )
    except InvalidClinicalSummaryInputError:
        raise
    except Exception as exc:
        raise ClinicalSummaryError(
            f"Failed to save clinical summary draft to consultation session: {exc}"
        ) from exc

    return {
        "ok": True,
        "consultation": consultation,
        "draft_summary": draft_summary,
        "message": "Clinical summary draft created and saved. Doctor review is required.",
    }
