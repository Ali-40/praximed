"""
Availability API routes — PraxisMed Sprint 1 / Module 10
Updated: Sprint 3 / Module 40 — machine access guards applied (availability:read)

Exposes two endpoints under /calendar/availability:

    POST /calendar/availability/check   — is a specific slot bookable?
    POST /calendar/availability/suggest — suggest available slots for a date

Access policy: vapi, internal, system, dashboard — availability:read scope required.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.dependencies.machine_auth import (
    get_machine_auth_context,
    require_availability_read_access,
)
from backend.app.api.deps import get_config_loader, get_db_pool
from backend.app.core.config_loader import (
    ConfigNotFoundError,
    ConfigValidationError,
)
from backend.app.core.machine_auth import MachineAuthContext
from backend.app.modules.calendar_sync import availability_engine
from backend.app.modules.calendar_sync.availability_engine import (
    InvalidAvailabilityRangeError,
)
from backend.app.schemas.availability import (
    AvailabilityCheckRequest,
    AvailabilityCheckResponse,
    SuggestedSlot,
    SuggestedSlotsRequest,
    SuggestedSlotsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["availability"])


@router.post("/calendar/availability/check", response_model=AvailabilityCheckResponse)
async def check_availability(
    body: AvailabilityCheckRequest,
    pool: Any = Depends(get_db_pool),
    config_loader: Any = Depends(get_config_loader),
    machine_auth: MachineAuthContext = Depends(get_machine_auth_context),
) -> AvailabilityCheckResponse:
    """
    Check whether a specific time slot is bookable for the given clinic.

    Returns ``available: true`` when the slot falls within opening hours and
    has no overlapping calendar blocks; ``available: false`` otherwise.
    """
    require_availability_read_access(
        requested_clinic_id=body.clinic_ref, machine_context=machine_auth
    )
    try:
        config = await config_loader.load(body.clinic_ref)
    except ConfigNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Clinic config not found for ref: {body.clinic_ref!r}",
        )
    except ConfigValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        available = await availability_engine.is_slot_bookable(
            pool, config, body.starts_at, body.ends_at
        )
    except InvalidAvailabilityRangeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in check_availability")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error checking availability: {exc}",
        )

    return AvailabilityCheckResponse(
        ok=True,
        clinic_id=config.tenant_id,
        available=available,
        starts_at=body.starts_at,
        ends_at=body.ends_at,
    )


@router.post("/calendar/availability/suggest", response_model=SuggestedSlotsResponse)
async def suggest_slots(
    body: SuggestedSlotsRequest,
    pool: Any = Depends(get_db_pool),
    config_loader: Any = Depends(get_config_loader),
    machine_auth: MachineAuthContext = Depends(get_machine_auth_context),
) -> SuggestedSlotsResponse:
    """
    Suggest available time slots for the given clinic on a specific date.
    """
    require_availability_read_access(
        requested_clinic_id=body.clinic_ref, machine_context=machine_auth
    )
    try:
        config = await config_loader.load(body.clinic_ref)
    except ConfigNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Clinic config not found for ref: {body.clinic_ref!r}",
        )
    except ConfigValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        raw_slots = await availability_engine.suggest_available_slots(
            pool, config, body.date, body.limit
        )
    except InvalidAvailabilityRangeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in suggest_slots")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error suggesting slots: {exc}",
        )

    slots = [SuggestedSlot(starts_at=s["starts_at"], ends_at=s["ends_at"]) for s in raw_slots]

    return SuggestedSlotsResponse(
        ok=True,
        clinic_id=config.tenant_id,
        slots=slots,
    )
