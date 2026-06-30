"""
Vapi tool routes — PraxisMed Sprint 1 / Module 12

Exposes two endpoints for the Vapi voice agent to call during a phone session:

    POST /vapi/tools/check-availability  — is a specific slot bookable?
    POST /vapi/tools/suggest-slots       — suggest available slots for a date
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import get_config_loader, get_db_pool
from backend.app.core.config_loader import ConfigNotFoundError, ConfigValidationError
from backend.app.db.repositories.appointment_request_repo import InvalidAppointmentRequestError
from backend.app.modules.calendar_sync import availability_engine
from backend.app.modules.calendar_sync.availability_engine import (
    InvalidAvailabilityRangeError,
)
from backend.app.modules.vapi import vapi_appointment_capture
from backend.app.modules.vapi.vapi_appointment_capture import (
    InvalidVapiAppointmentCaptureError,
)
from backend.app.schemas.vapi import (
    VapiAppointmentCaptureRequest,
    VapiAppointmentCaptureResponse,
    VapiAvailabilityCheckRequest,
    VapiAvailabilityCheckResponse,
    VapiSlotSuggestionRequest,
    VapiSlotSuggestionResponse,
    VapiSuggestedSlot,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["vapi"])


@router.post(
    "/vapi/tools/check-availability",
    response_model=VapiAvailabilityCheckResponse,
)
async def vapi_check_availability(
    body: VapiAvailabilityCheckRequest,
    pool: Any = Depends(get_db_pool),
    config_loader: Any = Depends(get_config_loader),
) -> VapiAvailabilityCheckResponse:
    """
    Check whether a specific time slot is bookable for the given clinic.

    Returns a Vapi-friendly response with a plain-language ``message`` the
    voice agent can read directly to the caller.
    """
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
        logger.exception("Unexpected error in vapi_check_availability")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error checking availability: {exc}",
        )

    if available:
        message = (
            f"Der gewünschte Termin von {body.starts_at.strftime('%H:%M')} bis "
            f"{body.ends_at.strftime('%H:%M')} scheint verfügbar zu sein."
        )
    else:
        message = (
            f"Der gewünschte Termin von {body.starts_at.strftime('%H:%M')} bis "
            f"{body.ends_at.strftime('%H:%M')} ist leider nicht verfügbar. "
            "Bitte schlage dem Anrufer alternative Zeiten vor."
        )

    return VapiAvailabilityCheckResponse(
        ok=True,
        available=available,
        message=message,
        starts_at=body.starts_at,
        ends_at=body.ends_at,
    )


@router.post(
    "/vapi/tools/suggest-slots",
    response_model=VapiSlotSuggestionResponse,
)
async def vapi_suggest_slots(
    body: VapiSlotSuggestionRequest,
    pool: Any = Depends(get_db_pool),
    config_loader: Any = Depends(get_config_loader),
) -> VapiSlotSuggestionResponse:
    """
    Suggest available time slots for the given clinic on a specific date.

    Returns a Vapi-friendly response.  When no slots are found the message
    instructs the agent to offer a callback instead.
    """
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
        logger.exception("Unexpected error in vapi_suggest_slots")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error suggesting slots: {exc}",
        )

    slots = [
        VapiSuggestedSlot(starts_at=s["starts_at"], ends_at=s["ends_at"])
        for s in raw_slots
    ]

    if slots:
        message = (
            f"Es gibt {len(slots)} verfügbare Termin(e) am {body.date.isoformat()}. "
            "Bitte präsentiere dem Anrufer die Optionen."
        )
    else:
        message = (
            f"Am {body.date.isoformat()} sind leider keine freien Termine verfügbar. "
            "Biete dem Anrufer einen Rückruf an."
        )

    return VapiSlotSuggestionResponse(ok=True, message=message, slots=slots)


@router.post(
    "/vapi/tools/capture-appointment-request",
    response_model=VapiAppointmentCaptureResponse,
)
async def vapi_capture_appointment_request(
    body: VapiAppointmentCaptureRequest,
    pool: Any = Depends(get_db_pool),
    config_loader: Any = Depends(get_config_loader),
) -> VapiAppointmentCaptureResponse:
    """
    Capture an appointment request from a completed Vapi phone session.

    The appointment is NOT booked automatically.  A row is created with
    status='new' and action_required=True so clinic staff can review and
    confirm before the appointment is considered booked.
    """
    try:
        result = await vapi_appointment_capture.capture_vapi_appointment_request(
            pool=pool,
            config_loader=config_loader,
            clinic_ref=body.clinic_ref,
            call_id=body.call_id,
            patient_name=body.patient_name,
            caller_phone=body.caller_phone,
            patient_email=body.patient_email,
            date_of_birth=body.date_of_birth,
            reason=body.reason,
            preferred_starts_at=body.preferred_starts_at,
            preferred_ends_at=body.preferred_ends_at,
            urgency_level=body.urgency_level,
            raw_payload=body.raw_payload,
        )
    except (InvalidVapiAppointmentCaptureError, InvalidAppointmentRequestError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ConfigNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Clinic config not found for ref: {body.clinic_ref!r}",
        )
    except ConfigValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in vapi_capture_appointment_request")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error capturing appointment request: {exc}",
        )

    return VapiAppointmentCaptureResponse(
        ok=result["ok"],
        message=result["message"],
        request=result["request"],
    )
