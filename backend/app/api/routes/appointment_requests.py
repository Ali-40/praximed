"""
Appointment Request API routes — PraxisMed Sprint 1 / Module 17
Updated: Sprint 3 / Module 38 — tenant guards applied (staff-level access)

Exposes seven endpoints under /appointment-requests for creating, listing,
fetching, updating, assigning, and archiving appointment requests.

Access policy: owner, admin, doctor, staff — clinic_id must match caller.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies.auth import get_auth_context, require_staff_clinic_access
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import appointment_request_repo
from backend.app.db.repositories.appointment_request_repo import InvalidAppointmentRequestError
from backend.app.schemas.appointment_requests import (
    AppointmentRequestAssign,
    AppointmentRequestCreate,
    AppointmentRequestListResponse,
    AppointmentRequestResponse,
    AppointmentRequestUpdateStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appointment-requests", tags=["appointment-requests"])


@router.post("", response_model=AppointmentRequestResponse)
async def create_appointment_request(
    body: AppointmentRequestCreate,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_auth_context),
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

    return AppointmentRequestResponse(ok=True, request=row)


@router.get("", response_model=AppointmentRequestListResponse)
async def list_appointment_requests(
    clinic_id: str = Query(...),
    status: Optional[str] = Query(None),
    action_required: Optional[bool] = Query(None),
    limit: int = Query(50),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_auth_context),
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
    auth: AuthContext = Depends(get_auth_context),
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


@router.patch("/{request_id}/status", response_model=AppointmentRequestResponse)
async def update_appointment_request_status(
    request_id: str,
    body: AppointmentRequestUpdateStatus,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_auth_context),
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

    return AppointmentRequestResponse(ok=True, request=row)


@router.patch("/{request_id}/assign", response_model=AppointmentRequestResponse)
async def assign_appointment_request(
    request_id: str,
    body: AppointmentRequestAssign,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_auth_context),
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

    return AppointmentRequestResponse(ok=True, request=row)


@router.post("/{request_id}/callback-needed", response_model=AppointmentRequestResponse)
async def mark_callback_needed(
    request_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_auth_context),
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

    return AppointmentRequestResponse(ok=True, request=row)


@router.post("/{request_id}/archive", response_model=AppointmentRequestResponse)
async def archive_appointment_request(
    request_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_auth_context),
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

    return AppointmentRequestResponse(ok=True, request=row)
