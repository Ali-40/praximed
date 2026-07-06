"""
Clinical workflow API routes — PraxisMed Sprint 3 / Module 35
Updated: Sprint 3 / Module 37 — tenant guards applied (clinical-level access)
Updated: Sprint 4 / Module 43 — audit logging for mutation routes
Updated: Sprint 7 / Module 63 — JWT current_user auth wired

Seven endpoints that expose the clinical workflow service layer:
  - audio reference attachment
  - manual transcript entry
  - clinical summary draft generation
  - review package building
  - doctor approval
  - doctor rejection
  - patient timeline report

Routes call service modules, not repositories directly.
No LLM calls. No external transcription provider. No binary file upload.

Access policy: owner, admin, doctor — clinic_id must match caller.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies.auth import require_clinical_clinic_access
from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.core.compliance import enforce_phi_safeguard
from backend.app.modules.audit import audit_logger
from backend.app.modules.audio.audio_storage import (
    AudioStorageError,
    InvalidAudioUploadError,
    attach_audio_reference_to_consultation,
)
from backend.app.modules.clinical_summary.review_workflow import (
    InvalidReviewInputError,
    ReviewWorkflowError,
    approve_summary_after_review,
    build_review_package,
    reject_summary_after_review,
)
from backend.app.modules.clinical_summary.summary_builder import (
    ClinicalSummaryError,
    InvalidClinicalSummaryInputError,
    create_and_save_clinical_summary_draft,
)
from backend.app.modules.patient_timeline.timeline_report import (
    InvalidPatientTimelineInputError,
    PatientNotFoundError,
    PatientTimelineError,
    create_patient_timeline_report,
)
from backend.app.modules.transcription.transcription_service import (
    InvalidTranscriptionRequestError,
    TranscriptionProviderError,
    TranscriptionServiceError,
    transcribe_consultation_audio,
)
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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/clinical-workflows",
    tags=["clinical-workflows"],
    dependencies=[Depends(enforce_phi_safeguard)],
)


# ---------------------------------------------------------------------------
# Internal manual transcription adapter (no external calls)
# ---------------------------------------------------------------------------


class _ManualTranscriptAdapter:
    """Minimal TranscriptionAdapter that returns a caller-supplied transcript."""

    def __init__(self, transcript_text: str) -> None:
        self._transcript_text = transcript_text

    async def transcribe_audio_reference(
        self,
        audio_file_path: str,
        language: str = "de-AT",
        raw_payload: Any = None,
    ) -> dict:
        return {
            "transcript_text": self._transcript_text,
            "raw_payload": raw_payload,
        }


# ---------------------------------------------------------------------------
# 1. POST /clinical-workflows/consultations/{session_id}/audio-reference
# ---------------------------------------------------------------------------


@router.post(
    "/consultations/{session_id}/audio-reference",
    response_model=WorkflowResponse,
)
async def attach_audio_reference(
    session_id: str,
    body: AudioReferenceAttachRequest,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> WorkflowResponse:
    require_clinical_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    try:
        result = await attach_audio_reference_to_consultation(
            pool=pool,
            clinic_id=body.clinic_id,
            session_id=session_id,
            file_name=body.file_name,
            content_type=body.content_type,
            file_size_bytes=body.file_size_bytes,
            uploaded_by_user_id=body.uploaded_by_user_id,
            source=body.source,
            raw_payload=body.raw_payload,
        )
    except InvalidAudioUploadError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except AudioStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error attaching audio reference")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="clinical_workflow.audio_reference_attach",
        resource_type="consultation_sessions", resource_id=session_id,
        metadata={"route": "attach_audio_reference"},
    ))
    return WorkflowResponse(ok=True, result=result, message=result.get("message"))


# ---------------------------------------------------------------------------
# 2. POST /clinical-workflows/consultations/{session_id}/manual-transcript
# ---------------------------------------------------------------------------


@router.post(
    "/consultations/{session_id}/manual-transcript",
    response_model=WorkflowResponse,
)
async def save_manual_transcript(
    session_id: str,
    body: ManualTranscriptRequest,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> WorkflowResponse:
    require_clinical_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    adapter = _ManualTranscriptAdapter(transcript_text=body.transcript_text)

    try:
        result = await transcribe_consultation_audio(
            pool=pool,
            adapter=adapter,
            clinic_id=body.clinic_id,
            session_id=session_id,
            audio_file_path=body.audio_file_path,
            language=body.language,
            provider="manual",
            raw_payload=body.raw_payload,
        )
    except InvalidTranscriptionRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except TranscriptionProviderError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except TranscriptionServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error saving manual transcript")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="clinical_workflow.manual_transcript_save",
        resource_type="consultation_sessions", resource_id=session_id,
        metadata={"route": "save_manual_transcript"},
    ))
    return WorkflowResponse(ok=True, result=result, message=result.get("message"))


# ---------------------------------------------------------------------------
# 3. POST /clinical-workflows/consultations/{session_id}/draft-summary
# ---------------------------------------------------------------------------


@router.post(
    "/consultations/{session_id}/draft-summary",
    response_model=WorkflowResponse,
)
async def generate_draft_summary(
    session_id: str,
    body: ClinicalSummaryDraftRequest,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> WorkflowResponse:
    require_clinical_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    try:
        result = await create_and_save_clinical_summary_draft(
            pool=pool,
            clinic_id=body.clinic_id,
            session_id=session_id,
            transcript_text=body.transcript_text,
            language=body.language,
            patient_context=body.patient_context,
            consultation_context=body.consultation_context,
            raw_payload=body.raw_payload,
        )
    except InvalidClinicalSummaryInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ClinicalSummaryError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error generating draft summary")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="clinical_workflow.draft_summary_create",
        resource_type="consultation_sessions", resource_id=session_id,
        metadata={"route": "generate_draft_summary"},
    ))
    return WorkflowResponse(ok=True, result=result, message=result.get("message"))


# ---------------------------------------------------------------------------
# 4. POST /clinical-workflows/consultations/{session_id}/review-package
# ---------------------------------------------------------------------------


@router.post(
    "/consultations/{session_id}/review-package",
    response_model=WorkflowResponse,
)
async def get_review_package(
    session_id: str,
    body: ReviewPackageRequest,
    auth: AuthContext = Depends(get_current_user),
) -> WorkflowResponse:
    require_clinical_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    try:
        package = build_review_package(
            clinic_id=body.clinic_id,
            session_id=session_id,
            draft_summary=body.draft_summary,
            transcript_text=body.transcript_text,
            patient_context=body.patient_context,
            consultation_context=body.consultation_context,
        )
    except InvalidReviewInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ReviewWorkflowError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error building review package")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return WorkflowResponse(
        ok=True,
        result=package,
        message="Review package created. Doctor review is required.",
    )


# ---------------------------------------------------------------------------
# 5. POST /clinical-workflows/consultations/{session_id}/approve-summary
# ---------------------------------------------------------------------------


@router.post(
    "/consultations/{session_id}/approve-summary",
    response_model=WorkflowResponse,
)
async def approve_summary(
    session_id: str,
    body: ApproveSummaryRequest,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> WorkflowResponse:
    require_clinical_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    try:
        result = await approve_summary_after_review(
            pool=pool,
            clinic_id=body.clinic_id,
            session_id=session_id,
            approved_summary=body.approved_summary,
            approved_by_user_id=body.approved_by_user_id,
        )
    except InvalidReviewInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ReviewWorkflowError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error approving summary")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="clinical_workflow.summary_approve",
        resource_type="consultation_sessions", resource_id=session_id,
        severity="critical", metadata={"route": "approve_summary"},
    ))
    return WorkflowResponse(ok=True, result=result, message=result.get("message"))


# ---------------------------------------------------------------------------
# 6. POST /clinical-workflows/consultations/{session_id}/reject-summary
# ---------------------------------------------------------------------------


@router.post(
    "/consultations/{session_id}/reject-summary",
    response_model=WorkflowResponse,
)
async def reject_summary(
    session_id: str,
    body: RejectSummaryRequest,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> WorkflowResponse:
    require_clinical_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    try:
        result = await reject_summary_after_review(
            pool=pool,
            clinic_id=body.clinic_id,
            session_id=session_id,
            rejected_reason=body.rejected_reason,
            rejected_by_user_id=body.rejected_by_user_id,
        )
    except InvalidReviewInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ReviewWorkflowError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error rejecting summary")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="clinical_workflow.summary_reject",
        resource_type="consultation_sessions", resource_id=session_id,
        severity="critical", metadata={"route": "reject_summary"},
    ))
    return WorkflowResponse(ok=True, result=result, message=result.get("message"))


# ---------------------------------------------------------------------------
# 7. GET /clinical-workflows/patients/{patient_id}/timeline
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{patient_id}/timeline",
    response_model=TimelineReportResponse,
)
async def get_patient_timeline(
    patient_id: str,
    clinic_id: str = Query(...),
    limit: int = Query(50),
    include_drafts: bool = Query(False),
    language: str = Query("de-AT"),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> TimelineReportResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        result = await create_patient_timeline_report(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            limit=limit,
            include_drafts=include_drafts,
            language=language,
        )
    except InvalidPatientTimelineInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PatientTimelineError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error building patient timeline")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return TimelineReportResponse(
        ok=True,
        report=result.get("report"),
        message=result.get("message"),
    )
