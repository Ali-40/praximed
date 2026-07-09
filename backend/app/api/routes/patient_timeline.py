"""
Patient Timeline routes — PraxisMed Sprint 20 / Module 156.

Protected internal routes — require authenticated session.
Longitudinal patient timeline aggregator: approved history, unverified proposals,
intake submissions, consent events, structuring runs, and appointment requests.

  GET /clinics/{clinic_id}/patients/{patient_id}/timeline
  GET /clinics/{clinic_id}/patients/{patient_id}/timeline/delta
  GET /clinics/{clinic_id}/patients/{patient_id}/timeline/delta-since

No DELETE. No POST/write routes. No public access.
No diagnosis. No medical advice. No triage scoring. No treatment recommendations.
No external LLM. production_phi_enabled always False. Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.schemas.patient_timeline import (
    PatientTimelineDeltaResponse,
    PatientTimelineResponse,
)
from backend.app.services import patient_timeline as svc

logger = logging.getLogger(__name__)

router = APIRouter(tags=["patient-timeline"])


@router.get(
    "/clinics/{clinic_id}/patients/{patient_id}/timeline",
    response_model=PatientTimelineResponse,
)
async def get_patient_timeline(
    clinic_id: str,
    patient_id: str,
    include_unverified: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=300),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientTimelineResponse:
    try:
        result = await svc.get_patient_timeline(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            include_unverified=include_unverified,
            limit=limit,
            actor_user=current_user,
        )
        return PatientTimelineResponse(**result)
    except svc.PatientTimelineClinicError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except svc.PatientTimelineAccessError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("timeline_error clinic=%s patient=%s err=%r", clinic_id, patient_id, exc)
        raise HTTPException(status_code=500, detail="Patient timeline could not be loaded.")


@router.get(
    "/clinics/{clinic_id}/patients/{patient_id}/timeline/delta",
    response_model=PatientTimelineDeltaResponse,
)
async def get_patient_timeline_delta(
    clinic_id: str,
    patient_id: str,
    include_unverified: bool = Query(default=True),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientTimelineDeltaResponse:
    try:
        result = await svc.get_patient_delta_since_last_visit(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            include_unverified=include_unverified,
            actor_user=current_user,
        )
        return PatientTimelineDeltaResponse(**result)
    except svc.PatientTimelineClinicError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except svc.PatientTimelineAccessError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("delta_error clinic=%s patient=%s err=%r", clinic_id, patient_id, exc)
        raise HTTPException(status_code=500, detail="Delta view could not be loaded.")


@router.get(
    "/clinics/{clinic_id}/patients/{patient_id}/timeline/delta-since",
    response_model=PatientTimelineDeltaResponse,
)
async def get_patient_timeline_delta_since(
    clinic_id: str,
    patient_id: str,
    since: str = Query(..., description="ISO datetime string"),
    include_unverified: bool = Query(default=True),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientTimelineDeltaResponse:
    try:
        since_dt = datetime.fromisoformat(since)
    except ValueError:
        raise HTTPException(status_code=422, detail="'since' must be a valid ISO datetime string.")

    try:
        result = await svc.get_patient_delta_since(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            since_datetime=since_dt,
            include_unverified=include_unverified,
            actor_user=current_user,
        )
        return PatientTimelineDeltaResponse(**result)
    except svc.PatientTimelineClinicError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except svc.PatientTimelineAccessError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("delta_since_error clinic=%s patient=%s since=%s err=%r", clinic_id, patient_id, since, exc)
        raise HTTPException(status_code=500, detail="Delta view could not be loaded.")
