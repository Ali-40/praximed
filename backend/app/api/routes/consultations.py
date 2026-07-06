"""
Consultation session API routes — PraxisMed Sprint 2 / Module 29
Updated: Sprint 3 / Module 37 — tenant guards applied (clinical-level access)
Updated: Sprint 4 / Module 43 — audit logging for mutation routes
Updated: Sprint 7 / Module 62 — JWT current_user auth wired

Ten endpoints under /consultations covering the full session lifecycle:
create, list, fetch, status update, audio attach, transcript, draft summary,
approve, reject, and archive.

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
from backend.app.db.repositories import consultation_repo
from backend.app.modules.audit import audit_logger
from backend.app.db.repositories.consultation_repo import InvalidConsultationSessionError
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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/consultations",
    tags=["consultations"],
    dependencies=[Depends(enforce_phi_safeguard)],
)


@router.post("", response_model=ConsultationResponse)
async def create_consultation_session(
    body: ConsultationSessionCreate,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationResponse:
    require_clinical_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    try:
        row = await consultation_repo.create_consultation_session(
            pool=pool,
            clinic_id=body.clinic_id,
            patient_id=body.patient_id,
            doctor_user_id=body.doctor_user_id,
            source=body.source,
            status=body.status,
            title=body.title,
            reason_for_visit=body.reason_for_visit,
            raw_payload=body.raw_payload,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error creating consultation session")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="consultation.create", resource_type="consultation_sessions",
        resource_id=row.get("id"), metadata={"route": "create_consultation_session"},
    ))
    return ConsultationResponse(ok=True, consultation=row)


@router.get("", response_model=ConsultationListResponse)
async def list_consultation_sessions(
    clinic_id: str = Query(...),
    patient_id: Optional[str] = Query(None),
    doctor_user_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    approval_status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(50),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationListResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        rows = await consultation_repo.list_consultation_sessions(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            doctor_user_id=doctor_user_id,
            status=status,
            approval_status=approval_status,
            source=source,
            limit=limit,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error listing consultation sessions")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ConsultationListResponse(ok=True, consultations=rows)


@router.get("/{session_id}", response_model=ConsultationResponse)
async def get_consultation_session(
    session_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await consultation_repo.get_consultation_session_by_id(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error fetching consultation session")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    return ConsultationResponse(ok=True, consultation=row)


@router.patch("/{session_id}/status", response_model=ConsultationResponse)
async def update_consultation_status(
    session_id: str,
    body: ConsultationStatusUpdate,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await consultation_repo.update_consultation_status(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            status=body.status,
            approval_status=body.approval_status,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error updating consultation status")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="consultation.status_update", resource_type="consultation_sessions",
        resource_id=session_id, metadata={"route": "update_consultation_status", "status": body.status},
    ))
    return ConsultationResponse(ok=True, consultation=row)


@router.post("/{session_id}/audio", response_model=ConsultationResponse)
async def attach_audio(
    session_id: str,
    body: ConsultationAudioAttach,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await consultation_repo.attach_audio_to_session(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            audio_file_path=body.audio_file_path,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error attaching audio to session")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="consultation.audio_attach", resource_type="consultation_sessions",
        resource_id=session_id, metadata={"route": "attach_audio"},
    ))
    return ConsultationResponse(ok=True, consultation=row)


@router.post("/{session_id}/transcript", response_model=ConsultationResponse)
async def save_transcript(
    session_id: str,
    body: ConsultationTranscriptSave,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await consultation_repo.save_transcript(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            transcript_text=body.transcript_text,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error saving transcript")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="consultation.transcript_save", resource_type="consultation_sessions",
        resource_id=session_id, metadata={"route": "save_transcript"},
    ))
    return ConsultationResponse(ok=True, consultation=row)


@router.post("/{session_id}/draft-summary", response_model=ConsultationResponse)
async def save_draft_summary(
    session_id: str,
    body: ConsultationDraftSummarySave,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await consultation_repo.save_draft_summary(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            draft_summary=body.draft_summary,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error saving draft summary")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="consultation.draft_summary_save", resource_type="consultation_sessions",
        resource_id=session_id, metadata={"route": "save_draft_summary"},
    ))
    return ConsultationResponse(ok=True, consultation=row)


@router.post("/{session_id}/approve", response_model=ConsultationResponse)
async def approve_consultation(
    session_id: str,
    body: ConsultationApprove,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await consultation_repo.approve_consultation_summary(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            approved_summary=body.approved_summary,
            approved_by_user_id=body.approved_by_user_id,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error approving consultation summary")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="consultation.approve", resource_type="consultation_sessions",
        resource_id=session_id, severity="critical", metadata={"route": "approve_consultation"},
    ))
    return ConsultationResponse(ok=True, consultation=row)


@router.post("/{session_id}/reject", response_model=ConsultationResponse)
async def reject_consultation(
    session_id: str,
    body: ConsultationReject,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await consultation_repo.reject_consultation_summary(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            rejected_reason=body.rejected_reason,
            rejected_by_user_id=body.rejected_by_user_id,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error rejecting consultation summary")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="consultation.reject", resource_type="consultation_sessions",
        resource_id=session_id, severity="critical", metadata={"route": "reject_consultation"},
    ))
    return ConsultationResponse(ok=True, consultation=row)


@router.post("/{session_id}/archive", response_model=ConsultationResponse)
async def archive_consultation(
    session_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsultationResponse:
    require_clinical_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await consultation_repo.archive_consultation_session(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
        )
    except InvalidConsultationSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error archiving consultation session")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="consultation.archive", resource_type="consultation_sessions",
        resource_id=session_id, metadata={"route": "archive_consultation"},
    ))
    return ConsultationResponse(ok=True, consultation=row)
