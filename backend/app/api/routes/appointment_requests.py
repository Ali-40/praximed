"""
Appointment Request API routes — PraxisMed Sprint 1 / Module 17
Updated: Sprint 3 / Module 38 — tenant guards applied (staff-level access)
Updated: Sprint 4 / Module 43 — audit logging for mutation routes
Updated: Sprint 7 / Module 64 — JWT current_user auth wired

Exposes seven endpoints under /appointment-requests for creating, listing,
fetching, updating, assigning, and archiving appointment requests.

Access policy: owner, admin, doctor, staff — clinic_id must match caller.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies.auth import require_staff_clinic_access
from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.core.compliance import enforce_phi_safeguard
from backend.app.db.repositories import appointment_request_repo
from backend.app.db.repositories import patient_repo
from backend.app.modules.audit import audit_logger
from backend.app.db.repositories.appointment_request_repo import InvalidAppointmentRequestError
from backend.app.services.pre_appointment_summary import build_pre_appointment_summary
from backend.app.schemas.appointment_requests import (
    AppointmentRequestAssign,
    AppointmentRequestCreate,
    AppointmentRequestListResponse,
    AppointmentRequestResponse,
    AppointmentRequestUpdateStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/appointment-requests",
    tags=["appointment-requests"],
    dependencies=[Depends(enforce_phi_safeguard)],
)


@router.post("", response_model=AppointmentRequestResponse)
async def create_appointment_request(
    body: AppointmentRequestCreate,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> AppointmentRequestResponse:
    require_staff_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    try:
        row = await appointment_request_repo.create_appointment_request(
            pool=pool,
            clinic_id=body.clinic_id,
            source=body.source,
            patient_name=body.patient_name,
            source_ref=body.source_ref,
            patient_phone=body.patient_phone,
            patient_email=body.patient_email,
            date_of_birth=body.date_of_birth,
            reason=body.reason,
            preferred_starts_at=body.preferred_starts_at,
            preferred_ends_at=body.preferred_ends_at,
            urgency_level=body.urgency_level,
            raw_payload=body.raw_payload,
        )
    except InvalidAppointmentRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error creating appointment request")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="appointment_request.create", resource_type="appointment_requests",
        resource_id=row.get("id"), metadata={"route": "create_appointment_request"},
    ))
    return AppointmentRequestResponse(ok=True, request=row)


@router.get("", response_model=AppointmentRequestListResponse)
async def list_appointment_requests(
    clinic_id: str = Query(...),
    status: Optional[str] = Query(None),
    action_required: Optional[bool] = Query(None),
    limit: int = Query(50),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> AppointmentRequestListResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        rows = await appointment_request_repo.list_appointment_requests(
            pool=pool,
            clinic_id=clinic_id,
            status=status,
            action_required=action_required,
            limit=limit,
        )
    except InvalidAppointmentRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error listing appointment requests")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return AppointmentRequestListResponse(ok=True, requests=rows)


@router.get("/{request_id}", response_model=AppointmentRequestResponse)
async def get_appointment_request(
    request_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> AppointmentRequestResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await appointment_request_repo.get_appointment_request_by_id(
            pool=pool,
            clinic_id=clinic_id,
            request_id=request_id,
        )
    except InvalidAppointmentRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error fetching appointment request")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Appointment request not found")

    return AppointmentRequestResponse(ok=True, request=row)


@router.get("/{request_id}/pre-appointment-summary")
async def get_pre_appointment_summary(
    request_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> dict:
    """Return a structured pre-appointment brief for a linked appointment request.

    Tenant isolation: clinic_id from the query param is validated against the
    caller's auth context — cross-clinic access returns HTTP 403.
    No diagnosis or medical advice is included in the response.
    """
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await appointment_request_repo.get_appointment_request_by_id(
            pool=pool,
            clinic_id=clinic_id,
            request_id=request_id,
        )
    except Exception as exc:
        logger.exception("Unexpected error fetching appointment request for summary")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Appointment request not found")

    linked_patient = None
    previous_request_count = 0
    patient_id = row.get("patient_id")

    if patient_id:
        try:
            linked_patient = await patient_repo.get_patient_by_id(
                pool=pool,
                clinic_id=clinic_id,
                patient_id=str(patient_id),
            )
            previous_request_count = await appointment_request_repo.count_requests_for_patient(
                pool=pool,
                clinic_id=clinic_id,
                patient_id=str(patient_id),
                exclude_request_id=request_id,
            )
        except Exception as exc:
            logger.exception("Unexpected error fetching patient for summary")
            raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    summary = build_pre_appointment_summary(
        appointment_request=row,
        patient=linked_patient,
        previous_request_count=previous_request_count,
    )
    return {"ok": True, "summary": summary}


@router.patch("/{request_id}/status", response_model=AppointmentRequestResponse)
async def update_appointment_request_status(
    request_id: str,
    body: AppointmentRequestUpdateStatus,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> AppointmentRequestResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await appointment_request_repo.update_appointment_request_status(
            pool=pool,
            clinic_id=clinic_id,
            request_id=request_id,
            status=body.status,
            action_required=body.action_required,
        )
    except InvalidAppointmentRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error updating appointment request status")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Appointment request not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="appointment_request.status_update", resource_type="appointment_requests",
        resource_id=request_id, metadata={"route": "update_appointment_request_status", "status": body.status},
    ))
    return AppointmentRequestResponse(ok=True, request=row)


@router.patch("/{request_id}/assign", response_model=AppointmentRequestResponse)
async def assign_appointment_request(
    request_id: str,
    body: AppointmentRequestAssign,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> AppointmentRequestResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await appointment_request_repo.assign_appointment_request(
            pool=pool,
            clinic_id=clinic_id,
            request_id=request_id,
            assigned_user_id=body.assigned_user_id,
        )
    except InvalidAppointmentRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error assigning appointment request")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Appointment request not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="appointment_request.assign", resource_type="appointment_requests",
        resource_id=request_id, metadata={"route": "assign_appointment_request"},
    ))
    return AppointmentRequestResponse(ok=True, request=row)


@router.post("/{request_id}/callback-needed", response_model=AppointmentRequestResponse)
async def mark_callback_needed(
    request_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> AppointmentRequestResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await appointment_request_repo.mark_callback_needed(
            pool=pool,
            clinic_id=clinic_id,
            request_id=request_id,
        )
    except InvalidAppointmentRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error marking callback needed")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Appointment request not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="appointment_request.callback_needed", resource_type="appointment_requests",
        resource_id=request_id, severity="warning", metadata={"route": "mark_callback_needed"},
    ))
    return AppointmentRequestResponse(ok=True, request=row)


@router.post("/{request_id}/archive", response_model=AppointmentRequestResponse)
async def archive_appointment_request(
    request_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> AppointmentRequestResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await appointment_request_repo.archive_appointment_request(
            pool=pool,
            clinic_id=clinic_id,
            request_id=request_id,
        )
    except InvalidAppointmentRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error archiving appointment request")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Appointment request not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="appointment_request.archive", resource_type="appointment_requests",
        resource_id=request_id, metadata={"route": "archive_appointment_request"},
    ))
    return AppointmentRequestResponse(ok=True, request=row)
