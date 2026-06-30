"""
Patient Timeline Report Service — PraxisMed Sprint 2 / Module 34

Builds a chronological patient timeline from existing consultation records.

Safety guarantees:
  - Never generates diagnosis or treatment advice.
  - Never promotes AI drafts to approved status.
  - Draft summaries are hidden by default.
  - Every entry retains doctor_review_required until approved.
  - AI/LLM calls: NONE.
  - External service calls: NONE.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.app.db.repositories import consultation_repo, patient_repo


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PatientTimelineError(RuntimeError):
    """Base class for patient timeline errors."""


class InvalidPatientTimelineInputError(PatientTimelineError):
    """Raised when timeline input is missing or invalid."""


class PatientNotFoundError(PatientTimelineError):
    """Raised when the requested patient does not exist."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TIMELINE_SCHEMA_VERSION = "patient_timeline_report.v1"

_PATIENT_REQUIRED_FIELDS = ("id", "clinic_id", "full_name")

_CONSULTATION_REQUIRED_FIELDS = ("id", "clinic_id", "patient_id", "status", "created_at")

_SAFETY_FLAGS = {
    "doctor_review_required_for_drafts": True,
    "drafts_hidden_by_default": True,
    "no_medical_content_generated": True,
    "no_diagnosis_generated": True,
    "no_treatment_advice_generated": True,
}

_TIMELINE_MESSAGE = "Patient timeline report generated from existing records only."


# ---------------------------------------------------------------------------
# 1. validate_timeline_request
# ---------------------------------------------------------------------------


def validate_timeline_request(
    clinic_id: str,
    patient_id: str,
    limit: int = 50,
    include_drafts: bool = False,
    language: str = "de-AT",
) -> Dict[str, Any]:
    if not clinic_id or not str(clinic_id).strip():
        raise InvalidPatientTimelineInputError("'clinic_id' must not be empty")
    if not patient_id or not str(patient_id).strip():
        raise InvalidPatientTimelineInputError("'patient_id' must not be empty")
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        raise InvalidPatientTimelineInputError("'limit' must be an integer between 1 and 100")
    if not isinstance(include_drafts, bool):
        raise InvalidPatientTimelineInputError("'include_drafts' must be a bool")
    if not language or not str(language).strip():
        raise InvalidPatientTimelineInputError("'language' must not be empty")

    return {
        "clinic_id": clinic_id,
        "patient_id": patient_id,
        "limit": limit,
        "include_drafts": include_drafts,
        "language": language,
    }


# ---------------------------------------------------------------------------
# 2. normalize_patient_record
# ---------------------------------------------------------------------------


def normalize_patient_record(patient: Any) -> Dict[str, Any]:
    if not isinstance(patient, dict):
        raise InvalidPatientTimelineInputError("'patient' must be a dict")

    for field in _PATIENT_REQUIRED_FIELDS:
        if field not in patient:
            raise InvalidPatientTimelineInputError(
                f"Patient record missing required field: '{field}'"
            )

    return {
        "id": patient.get("id"),
        "clinic_id": patient.get("clinic_id"),
        "external_patient_id": patient.get("external_patient_id"),
        "full_name": patient.get("full_name"),
        "date_of_birth": patient.get("date_of_birth"),
        "phone": patient.get("phone"),
        "email": patient.get("email"),
        "preferred_language": patient.get("preferred_language"),
        "status": patient.get("status"),
    }


# ---------------------------------------------------------------------------
# 3. detect_summary_status
# ---------------------------------------------------------------------------


def detect_summary_status(consultation: Dict[str, Any]) -> str:
    approval_status = consultation.get("approval_status")
    approved_summary = consultation.get("approved_summary")
    draft_summary = consultation.get("draft_summary")
    transcript_text = consultation.get("transcript_text")
    audio_file_path = consultation.get("audio_file_path")

    if approval_status == "approved" and approved_summary:
        return "approved"
    if draft_summary and approval_status != "approved":
        return "draft"
    if transcript_text and not draft_summary and not approved_summary:
        return "transcribed"
    if audio_file_path and not transcript_text:
        return "audio_only"
    return "created"


# ---------------------------------------------------------------------------
# 4. extract_summary_for_timeline
# ---------------------------------------------------------------------------


def extract_summary_for_timeline(
    consultation: Dict[str, Any],
    include_drafts: bool = False,
) -> Optional[Dict[str, Any]]:
    approval_status = consultation.get("approval_status")
    approved_summary = consultation.get("approved_summary")
    draft_summary = consultation.get("draft_summary")

    if approval_status == "approved" and approved_summary:
        return {
            "summary_type": "approved",
            "doctor_approved": True,
            "content": approved_summary,
            "warning": None,
        }

    if draft_summary:
        if include_drafts:
            return {
                "summary_type": "draft",
                "doctor_approved": False,
                "content": draft_summary,
                "warning": "Draft summary only. Doctor approval required.",
            }
        return None

    return None


# ---------------------------------------------------------------------------
# 5. build_timeline_entry
# ---------------------------------------------------------------------------


def build_timeline_entry(
    consultation: Dict[str, Any],
    include_drafts: bool = False,
) -> Dict[str, Any]:
    if not isinstance(consultation, dict):
        raise InvalidPatientTimelineInputError("'consultation' must be a dict")

    for field in _CONSULTATION_REQUIRED_FIELDS:
        if field not in consultation:
            raise InvalidPatientTimelineInputError(
                f"Consultation record missing required field: '{field}'"
            )

    summary_status = detect_summary_status(consultation)
    summary = extract_summary_for_timeline(consultation, include_drafts=include_drafts)

    doctor_review_required = summary_status != "approved"

    return {
        "consultation_id": consultation.get("id"),
        "clinic_id": consultation.get("clinic_id"),
        "patient_id": consultation.get("patient_id"),
        "doctor_user_id": consultation.get("doctor_user_id"),
        "created_at": consultation.get("created_at"),
        "updated_at": consultation.get("updated_at"),
        "source": consultation.get("source"),
        "status": consultation.get("status"),
        "approval_status": consultation.get("approval_status"),
        "title": consultation.get("title"),
        "reason_for_visit": consultation.get("reason_for_visit"),
        "summary_status": summary_status,
        "summary": summary,
        "has_audio": bool(consultation.get("audio_file_path")),
        "has_transcript": bool(consultation.get("transcript_text")),
        "doctor_review_required": doctor_review_required,
    }


# ---------------------------------------------------------------------------
# 6. sort_timeline_entries
# ---------------------------------------------------------------------------


def sort_timeline_entries(
    entries: List[Dict[str, Any]],
    newest_first: bool = True,
) -> List[Dict[str, Any]]:
    if not isinstance(entries, list):
        raise InvalidPatientTimelineInputError("'entries' must be a list")

    with_date = [e for e in entries if e.get("created_at") is not None]
    without_date = [e for e in entries if e.get("created_at") is None]

    sorted_dated = sorted(
        with_date,
        key=lambda e: str(e["created_at"]),
        reverse=newest_first,
    )
    return sorted_dated + without_date


# ---------------------------------------------------------------------------
# 7. build_patient_timeline_report
# ---------------------------------------------------------------------------


def build_patient_timeline_report(
    patient: Dict[str, Any],
    consultations: List[Dict[str, Any]],
    include_drafts: bool = False,
    language: str = "de-AT",
) -> Dict[str, Any]:
    normalized_patient = normalize_patient_record(patient)

    if not isinstance(consultations, list):
        raise InvalidPatientTimelineInputError("'consultations' must be a list")

    entries = [
        build_timeline_entry(c, include_drafts=include_drafts)
        for c in consultations
    ]
    timeline = sort_timeline_entries(entries, newest_first=True)

    approved_count = sum(1 for e in timeline if e["summary_status"] == "approved")
    draft_count = sum(1 for e in timeline if e["summary_status"] == "draft")
    transcribed_count = sum(1 for e in timeline if e["summary_status"] == "transcribed")
    audio_only_count = sum(1 for e in timeline if e["summary_status"] == "audio_only")
    review_required_count = sum(1 for e in timeline if e["doctor_review_required"])

    return {
        "schema_version": TIMELINE_SCHEMA_VERSION,
        "language": language,
        "patient": normalized_patient,
        "timeline": timeline,
        "totals": {
            "consultations": len(timeline),
            "approved_summaries": approved_count,
            "draft_summaries": draft_count,
            "transcribed_sessions": transcribed_count,
            "audio_only_sessions": audio_only_count,
            "doctor_review_required": review_required_count,
        },
        "safety": dict(_SAFETY_FLAGS),
        "message": _TIMELINE_MESSAGE,
    }


# ---------------------------------------------------------------------------
# 8. create_patient_timeline_report
# ---------------------------------------------------------------------------


async def create_patient_timeline_report(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    limit: int = 50,
    include_drafts: bool = False,
    language: str = "de-AT",
) -> Dict[str, Any]:
    validate_timeline_request(
        clinic_id=clinic_id,
        patient_id=patient_id,
        limit=limit,
        include_drafts=include_drafts,
        language=language,
    )

    try:
        patient = await patient_repo.get_patient_by_id(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
        )
    except InvalidPatientTimelineInputError:
        raise
    except Exception as exc:
        raise PatientTimelineError(
            f"Failed to fetch patient record: {exc}"
        ) from exc

    if patient is None:
        raise PatientNotFoundError(
            f"Patient '{patient_id}' not found in clinic '{clinic_id}'"
        )

    try:
        consultations = await consultation_repo.list_consultation_sessions(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            limit=limit,
        )
    except InvalidPatientTimelineInputError:
        raise
    except Exception as exc:
        raise PatientTimelineError(
            f"Failed to fetch consultation sessions: {exc}"
        ) from exc

    report = build_patient_timeline_report(
        patient=patient,
        consultations=consultations,
        include_drafts=include_drafts,
        language=language,
    )

    return {
        "ok": True,
        "report": report,
        "message": _TIMELINE_MESSAGE,
    }
