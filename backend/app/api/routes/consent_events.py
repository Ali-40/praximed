"""
Consent Events routes — PraxisMed Sprint 20 / Module 148.

Protected internal routes — require authenticated session.

POST /clinics/{clinic_id}/consent-events              — record consent event
GET  /clinics/{clinic_id}/consent-events              — list consent events for clinic
GET  /consent-events/{consent_event_id}               — get single consent event
PATCH /consent-events/{consent_event_id}/revoke       — revoke consent event

Rules:
  - Authenticated session required on all routes.
  - No public access.
  - No real patient PHI stored or returned.
  - No diagnosis. No medical advice. No triage scoring.
  - No call recordings.
  - production_phi_enabled always False.
  - Consent events are append-only; revocation uses revoked_at marker.
  - No DELETE route exists.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories.consent_event_repo import (
    ConsentEventNotFoundError,
    InvalidConsentEventError,
)
from backend.app.schemas.consent_event import (
    ConsentEventCreate,
    ConsentEventListResponse,
    ConsentEventResponse,
    ConsentEventRevoke,
)
from backend.app.services import consent_ledger
from backend.app.services.consent_ledger import (
    AppointmentRequestNotFoundError,
    ClinicNotFoundError,
    ConsentValidationError,
    PatientNotFoundError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["consent-events"])


@router.post(
    "/clinics/{clinic_id}/consent-events",
    response_model=ConsentEventResponse,
    status_code=201,
)
async def create_consent_event(
    clinic_id: str,
    body: ConsentEventCreate,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsentEventResponse:
    """Protected — record a consent event for a clinic.

    No real patient PHI stored. production_phi_enabled always False.
    Synthetic/fake staging only. Production PHI remains NO-GO.
    """
    if body.clinic_id != clinic_id:
        raise HTTPException(
            status_code=400,
            detail="clinic_id in body does not match path parameter",
        )
    try:
        row = await consent_ledger.create_consent_event(
            pool=pool,
            payload=body,
            actor_user=auth,
        )
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except (PatientNotFoundError, AppointmentRequestNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except InvalidConsentEventError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error creating consent event")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ConsentEventResponse(ok=True, event=row, production_phi_enabled=False)


@router.get(
    "/clinics/{clinic_id}/consent-events",
    response_model=ConsentEventListResponse,
)
async def list_consent_events(
    clinic_id: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsentEventListResponse:
    """Protected — list consent events for a clinic (most recent first)."""
    try:
        rows = await consent_ledger.list_clinic_consent_events(
            pool=pool,
            clinic_id=clinic_id,
            actor_user=auth,
        )
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error listing consent events")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ConsentEventListResponse(
        ok=True,
        events=rows,
        total=len(rows),
        production_phi_enabled=False,
    )


@router.get(
    "/consent-events/{consent_event_id}",
    response_model=ConsentEventResponse,
)
async def get_consent_event(
    consent_event_id: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsentEventResponse:
    """Protected — get a single consent event by ID."""
    try:
        row = await consent_ledger.get_consent_event(
            pool=pool,
            event_id=consent_event_id,
            actor_user=auth,
        )
    except Exception as exc:
        logger.exception("Unexpected error fetching consent event")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Consent event not found")

    return ConsentEventResponse(ok=True, event=row, production_phi_enabled=False)


@router.patch(
    "/consent-events/{consent_event_id}/revoke",
    response_model=ConsentEventResponse,
)
async def revoke_consent_event(
    consent_event_id: str,
    body: ConsentEventRevoke,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ConsentEventResponse:
    """Protected — revoke a consent event. Marks revoked_at; does not delete the row.

    Consent events are append-only. Revocation is a marker, not a deletion.
    """
    try:
        row = await consent_ledger.revoke_consent_event(
            pool=pool,
            event_id=consent_event_id,
            payload=body,
            actor_user=auth,
        )
    except ConsentEventNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ConsentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error revoking consent event")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ConsentEventResponse(
        ok=True,
        event=row,
        message="Consent event revoked.",
        production_phi_enabled=False,
    )
