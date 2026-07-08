"""
Patient History routes — PraxisMed Sprint 20 / Module 149.

Protected internal routes — require authenticated session.
No public access. No DELETE route. No diagnosis generated.
No medical advice. No triage scoring. No real patient PHI.
Synthetic/fake staging only. production_phi_enabled always False.
Production PHI remains NO-GO.

POST /clinics/{clinic_id}/patients/{patient_id}/history/{history_type}
GET  /clinics/{clinic_id}/patients/{patient_id}/history
GET  /clinics/{clinic_id}/patients/{patient_id}/history/{history_type}
GET  /patient-history/{history_type}/{entry_id}
PATCH /patient-history/{history_type}/{entry_id}/status

Supported history_type values:
  allergies, medications, conditions, procedures,
  immunizations, family-history, social-history
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories.patient_history_repo import (
    UnsupportedHistoryTypeError,
    InvalidPatientHistoryEntryError,
    PatientHistoryEntryNotFoundError,
)
from backend.app.schemas.patient_history import (
    HistoryEntryResponse,
    HistoryEntryListResponse,
    HistoryStatusUpdate,
    PatientHistoryTimelineResponse,
)
from backend.app.services import patient_history as patient_history_svc
from backend.app.services.patient_history import (
    PatientNotFoundError,
    AppointmentRequestNotFoundError,
    HistoryEntryNotFoundError,
)
from backend.app.services.consent_ledger import (
    ClinicNotFoundError,
    ConsentValidationError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["patient-history"])

_HISTORY_TYPES = frozenset({
    "allergies", "medications", "conditions", "procedures",
    "immunizations", "family-history", "social-history",
})


def _require_valid_history_type(history_type: str) -> None:
    if history_type not in _HISTORY_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported history_type {history_type!r}. "
                   f"Must be one of: {', '.join(sorted(_HISTORY_TYPES))}.",
        )


@router.post(
    "/clinics/{clinic_id}/patients/{patient_id}/history/{history_type}",
    response_model=HistoryEntryResponse,
    status_code=201,
)
async def create_history_entry(
    clinic_id: str,
    patient_id: str,
    history_type: str,
    body: dict,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> HistoryEntryResponse:
    """Protected — create a patient history entry. Requires valid consent event.

    Staff/doctor review required (status=unverified). No deletion.
    No diagnosis generated. No medical advice. No real patient PHI.
    Synthetic/fake staging only. production_phi_enabled always False.
    """
    _require_valid_history_type(history_type)
    body["patient_id"] = patient_id
    if "clinic_id" in body and body["clinic_id"] != clinic_id:
        raise HTTPException(
            status_code=400,
            detail="clinic_id in body does not match path parameter",
        )
    body["clinic_id"] = clinic_id

    try:
        row = await patient_history_svc.create_patient_history_entry(
            pool=pool,
            clinic_id=clinic_id,
            history_type=history_type,
            payload=body,
            actor_user=auth,
        )
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except (PatientNotFoundError, AppointmentRequestNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ConsentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except (UnsupportedHistoryTypeError, InvalidPatientHistoryEntryError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error creating history entry")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return HistoryEntryResponse(ok=True, entry=row, production_phi_enabled=False)


@router.get(
    "/clinics/{clinic_id}/patients/{patient_id}/history",
    response_model=PatientHistoryTimelineResponse,
)
async def get_patient_timeline(
    clinic_id: str,
    patient_id: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> PatientHistoryTimelineResponse:
    """Protected — list all history entries for a patient across all types (timeline)."""
    try:
        rows = await patient_history_svc.list_patient_history_timeline(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            actor_user=auth,
        )
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error fetching patient timeline")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return PatientHistoryTimelineResponse(
        ok=True,
        patient_id=patient_id,
        clinic_id=clinic_id,
        timeline=rows,
        total=len(rows),
        production_phi_enabled=False,
    )


@router.get(
    "/clinics/{clinic_id}/patients/{patient_id}/history/{history_type}",
    response_model=HistoryEntryListResponse,
)
async def list_history_by_type(
    clinic_id: str,
    patient_id: str,
    history_type: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> HistoryEntryListResponse:
    """Protected — list patient history entries for one FHIR resource type."""
    _require_valid_history_type(history_type)
    try:
        rows = await patient_history_svc.list_patient_history(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            history_type=history_type,
            actor_user=auth,
        )
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error listing history entries")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return HistoryEntryListResponse(
        ok=True,
        entries=rows,
        total=len(rows),
        history_type=history_type,
        production_phi_enabled=False,
    )


@router.get(
    "/patient-history/{history_type}/{entry_id}",
    response_model=HistoryEntryResponse,
)
async def get_history_entry(
    history_type: str,
    entry_id: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> HistoryEntryResponse:
    """Protected — get a single history entry by ID."""
    _require_valid_history_type(history_type)
    clinic_id = auth.clinic_id
    try:
        row = await patient_history_svc.get_patient_history_entry(
            pool=pool,
            clinic_id=clinic_id,
            history_type=history_type,
            entry_id=entry_id,
            actor_user=auth,
        )
    except Exception as exc:
        logger.exception("Unexpected error fetching history entry")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="History entry not found")

    return HistoryEntryResponse(ok=True, entry=row, production_phi_enabled=False)


@router.patch(
    "/patient-history/{history_type}/{entry_id}/status",
    response_model=HistoryEntryResponse,
)
async def update_history_status(
    history_type: str,
    entry_id: str,
    body: HistoryStatusUpdate,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> HistoryEntryResponse:
    """Protected — update the review status of a history entry.

    Staff/doctor review: approved / rejected / superseded.
    No deletion. Append-only ledger.
    """
    _require_valid_history_type(history_type)
    clinic_id = auth.clinic_id
    try:
        row = await patient_history_svc.update_patient_history_status(
            pool=pool,
            clinic_id=clinic_id,
            history_type=history_type,
            entry_id=entry_id,
            status=body.status,
            review_note=body.review_note,
            actor_user=auth,
        )
    except HistoryEntryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except InvalidPatientHistoryEntryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error updating history status")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return HistoryEntryResponse(
        ok=True,
        entry=row,
        message="History entry status updated.",
        production_phi_enabled=False,
    )
