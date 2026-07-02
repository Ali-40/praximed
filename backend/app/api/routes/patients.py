"""
Patient API routes — PraxisMed Sprint 2 / Module 26
Updated: Sprint 3 / Module 37 — tenant guards applied (staff-level access)
Updated: Sprint 4 / Module 43 — audit logging for mutation routes
Updated: Sprint 7 / Module 61 — JWT current_user auth wired

Seven endpoints under /patients for creating, upserting, listing, fetching,
updating, and archiving clinic patient records.

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
from backend.app.db.repositories import patient_repo
from backend.app.db.repositories.patient_repo import InvalidPatientError
from backend.app.modules.audit import audit_logger
from backend.app.schemas.patients import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
    PatientUpsertByExternalId,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse)
async def create_patient(
    body: PatientCreate,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> PatientResponse:
    require_staff_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    try:
        row = await patient_repo.create_patient(
            pool=pool,
            clinic_id=body.clinic_id,
            full_name=body.full_name,
            external_patient_id=body.external_patient_id,
            date_of_birth=body.date_of_birth,
            phone=body.phone,
            email=body.email,
            preferred_language=body.preferred_language,
            status=body.status,
            notes=body.notes,
            raw_payload=body.raw_payload,
        )
    except InvalidPatientError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error creating patient")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="patient.create", resource_type="patients",
        resource_id=row.get("id"), metadata={"route": "create_patient"},
    ))
    return PatientResponse(ok=True, patient=row)


@router.post("/upsert-by-external-id", response_model=PatientResponse)
async def upsert_patient_by_external_id(
    body: PatientUpsertByExternalId,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> PatientResponse:
    require_staff_clinic_access(requested_clinic_id=body.clinic_id, auth_context=auth)
    try:
        row = await patient_repo.upsert_patient_by_external_id(
            pool=pool,
            clinic_id=body.clinic_id,
            external_patient_id=body.external_patient_id,
            full_name=body.full_name,
            date_of_birth=body.date_of_birth,
            phone=body.phone,
            email=body.email,
            preferred_language=body.preferred_language,
            status=body.status,
            notes=body.notes,
            raw_payload=body.raw_payload,
        )
    except InvalidPatientError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error upserting patient")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="patient.upsert_by_external_id", resource_type="patients",
        resource_id=row.get("id"), metadata={"route": "upsert_patient_by_external_id"},
    ))
    return PatientResponse(ok=True, patient=row)


@router.get("", response_model=PatientListResponse)
async def list_patients(
    clinic_id: str = Query(...),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> PatientListResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        rows = await patient_repo.list_patients(
            pool=pool,
            clinic_id=clinic_id,
            status=status,
            search=search,
            limit=limit,
        )
    except InvalidPatientError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error listing patients")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return PatientListResponse(ok=True, patients=rows)


# Declare /by-external-id/{...} before /{patient_id} to prevent path collision.
@router.get("/by-external-id/{external_patient_id}", response_model=PatientResponse)
async def get_patient_by_external_id(
    external_patient_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> PatientResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await patient_repo.get_patient_by_external_id(
            pool=pool,
            clinic_id=clinic_id,
            external_patient_id=external_patient_id,
        )
    except InvalidPatientError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error fetching patient by external id")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return PatientResponse(ok=True, patient=row)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient_by_id(
    patient_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> PatientResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await patient_repo.get_patient_by_id(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
        )
    except InvalidPatientError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error fetching patient")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return PatientResponse(ok=True, patient=row)


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    body: PatientUpdate,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> PatientResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await patient_repo.update_patient(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            full_name=body.full_name,
            date_of_birth=body.date_of_birth,
            phone=body.phone,
            email=body.email,
            preferred_language=body.preferred_language,
            status=body.status,
            notes=body.notes,
            raw_payload=body.raw_payload,
        )
    except InvalidPatientError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error updating patient")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="patient.update", resource_type="patients",
        resource_id=patient_id, metadata={"route": "update_patient"},
    ))
    return PatientResponse(ok=True, patient=row)


@router.post("/{patient_id}/archive", response_model=PatientResponse)
async def archive_patient(
    patient_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> PatientResponse:
    require_staff_clinic_access(requested_clinic_id=clinic_id, auth_context=auth)
    try:
        row = await patient_repo.archive_patient(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
        )
    except InvalidPatientError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error archiving patient")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    await audit_logger.safe_record_audit_event(pool, audit_logger.build_user_audit_event(
        auth, action="patient.archive", resource_type="patients",
        resource_id=patient_id, metadata={"route": "archive_patient"},
    ))
    return PatientResponse(ok=True, patient=row)
