"""
Clinic Vapi Binding routes — PraxisMed Sprint 19 / Module 145.

Protected internal routes — require authenticated session.

POST /clinics/{clinic_id}/vapi-bindings       — create binding metadata record
GET  /clinics/{clinic_id}/vapi-bindings        — get binding metadata for clinic
PATCH /clinic-vapi-bindings/{binding_id}/status — update binding status

Rules:
  - Authenticated session required on all routes.
  - No actual secret values accepted or returned (reference names only).
  - No live Vapi API calls.
  - No PHI. No patient data. No call recordings.
  - production_phi_enabled always False.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.schemas.clinic_vapi_binding import (
    ClinicVapiBindingCreate,
    ClinicVapiBindingResponse,
    ClinicVapiBindingUpdateStatus,
)
from backend.app.services import clinic_vapi_binding as binding_service
from backend.app.services.clinic_vapi_binding import ClinicNotFoundError
from backend.app.db.repositories.clinic_vapi_binding_repo import (
    InvalidClinicVapiBindingError,
    ClinicVapiBindingNotFoundError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["clinic-vapi-bindings"])


@router.post(
    "/clinics/{clinic_id}/vapi-bindings",
    response_model=ClinicVapiBindingResponse,
    status_code=201,
)
async def create_clinic_vapi_binding(
    clinic_id: str,
    body: ClinicVapiBindingCreate,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ClinicVapiBindingResponse:
    """Protected — create Vapi binding metadata for a clinic.

    Stores secret reference names only. No VAPI_API_KEY value accepted.
    No live Vapi API call made. No PHI. production_phi_enabled always False.
    """
    if body.clinic_id != clinic_id:
        raise HTTPException(
            status_code=400,
            detail="clinic_id in body does not match path parameter",
        )
    try:
        row = await binding_service.create_vapi_binding_metadata(
            pool=pool,
            payload=body,
            actor_user=auth,
        )
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except InvalidClinicVapiBindingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error creating Vapi binding metadata")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ClinicVapiBindingResponse(ok=True, binding=row, production_phi_enabled=False)


@router.get(
    "/clinics/{clinic_id}/vapi-bindings",
    response_model=ClinicVapiBindingResponse,
)
async def get_clinic_vapi_binding(
    clinic_id: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ClinicVapiBindingResponse:
    """Protected — get the latest Vapi binding metadata for a clinic.

    Returns reference names only — no actual secret values returned.
    """
    try:
        row = await binding_service.get_vapi_binding_metadata(
            pool=pool,
            clinic_id=clinic_id,
            actor_user=auth,
        )
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error fetching Vapi binding metadata")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="No Vapi binding found for this clinic")

    return ClinicVapiBindingResponse(ok=True, binding=row, production_phi_enabled=False)


@router.patch(
    "/clinic-vapi-bindings/{binding_id}/status",
    response_model=ClinicVapiBindingResponse,
)
async def update_clinic_vapi_binding_status(
    binding_id: str,
    body: ClinicVapiBindingUpdateStatus,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ClinicVapiBindingResponse:
    """Protected — update the status of a Vapi binding (draft/configured/disabled/revoked)."""
    try:
        row = await binding_service.update_vapi_binding_status(
            pool=pool,
            binding_id=binding_id,
            status=body.status,
            actor_user=auth,
        )
    except ClinicVapiBindingNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except InvalidClinicVapiBindingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error updating Vapi binding status")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ClinicVapiBindingResponse(ok=True, binding=row, production_phi_enabled=False)
