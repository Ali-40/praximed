"""
Patient History Structuring routes — PraxisMed Sprint 20 / Module 153.

All routes are protected (authenticated session required).
Local deterministic demo extraction only. No external LLM.

Protected:
  POST   /clinics/{clinic_id}/intake-submissions/{submission_id}/structure
  GET    /clinics/{clinic_id}/history-proposals
  GET    /clinics/{clinic_id}/structuring-runs/{run_id}
  GET    /clinics/{clinic_id}/structuring-runs/{run_id}/proposals
  PATCH  /clinics/{clinic_id}/history-proposals/{proposal_id}/reject
  PATCH  /clinics/{clinic_id}/history-proposals/{proposal_id}/archive-demo

No DELETE. No approval route. No auto-approval. No diagnosis. No medical advice.
No triage scoring. No treatment recommendations. No patient_history_* writes.
production_phi_enabled always False. Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.schemas.patient_history_structuring import (
    StructuringRequest,
    StructuringResult,
    PatientHistoryProposalListResponse,
    PatientHistoryStructuringRunResponse,
    ProposalStatusUpdate,
    PatientHistoryProposalRead,
)
from backend.app.services import patient_history_structuring as svc

logger = logging.getLogger(__name__)

router = APIRouter(tags=["patient-history-structuring"])


@router.post(
    "/clinics/{clinic_id}/intake-submissions/{submission_id}/structure",
    status_code=201,
    response_model=StructuringResult,
)
async def trigger_structuring(
    clinic_id: str,
    submission_id: str,
    body: StructuringRequest = StructuringRequest(),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> StructuringResult:
    try:
        result = await svc.structure_intake_submission(
            pool=pool,
            submission_id=submission_id,
            clinic_id=clinic_id,
            actor_user=current_user,
        )
        return StructuringResult(**result)
    except svc.SubmissionNotFoundError:
        raise HTTPException(status_code=404, detail="Intake submission not found.")
    except svc.AlreadyStructuredError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("structuring_error clinic=%s submission=%s err=%r", clinic_id, submission_id, exc)
        raise HTTPException(status_code=500, detail="Structuring failed unexpectedly.")


@router.get(
    "/clinics/{clinic_id}/history-proposals",
    response_model=PatientHistoryProposalListResponse,
)
async def list_history_proposals(
    clinic_id: str,
    patient_id: Optional[str] = Query(default=None),
    proposal_status: Optional[str] = Query(default=None),
    history_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientHistoryProposalListResponse:
    proposals = await svc.list_patient_history_proposals(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
        proposal_status=proposal_status,
        history_type=history_type,
        limit=limit,
        actor_user=current_user,
    )
    return PatientHistoryProposalListResponse(
        ok=True,
        proposals=proposals,
        total=len(proposals),
        production_phi_enabled=False,
    )


@router.get(
    "/clinics/{clinic_id}/structuring-runs/{run_id}",
    response_model=PatientHistoryStructuringRunResponse,
)
async def get_structuring_run(
    clinic_id: str,
    run_id: str,
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientHistoryStructuringRunResponse:
    try:
        data = await svc.get_structuring_run(
            pool=pool,
            run_id=run_id,
            clinic_id=clinic_id,
            actor_user=current_user,
        )
        return PatientHistoryStructuringRunResponse(
            ok=True,
            run=data["run"],
            proposals=data["proposals"],
            production_phi_enabled=False,
        )
    except svc.StructuringRunNotFoundError:
        raise HTTPException(status_code=404, detail="Structuring run not found.")


@router.get(
    "/clinics/{clinic_id}/structuring-runs/{run_id}/proposals",
    response_model=PatientHistoryProposalListResponse,
)
async def list_run_proposals(
    clinic_id: str,
    run_id: str,
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientHistoryProposalListResponse:
    try:
        data = await svc.get_structuring_run(
            pool=pool,
            run_id=run_id,
            clinic_id=clinic_id,
            actor_user=current_user,
        )
    except svc.StructuringRunNotFoundError:
        raise HTTPException(status_code=404, detail="Structuring run not found.")
    proposals = data["proposals"]
    return PatientHistoryProposalListResponse(
        ok=True,
        proposals=proposals,
        total=len(proposals),
        production_phi_enabled=False,
    )


@router.patch(
    "/clinics/{clinic_id}/history-proposals/{proposal_id}/reject",
    response_model=PatientHistoryProposalRead,
)
async def reject_proposal(
    clinic_id: str,
    proposal_id: str,
    body: ProposalStatusUpdate,
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientHistoryProposalRead:
    try:
        updated = await svc.reject_history_proposal(
            pool=pool,
            proposal_id=proposal_id,
            clinic_id=clinic_id,
            reason=body.reason,
            actor_user=current_user,
        )
        return PatientHistoryProposalRead(**updated)
    except svc.ProposalNotFoundError:
        raise HTTPException(status_code=404, detail="Proposal not found.")


@router.patch(
    "/clinics/{clinic_id}/history-proposals/{proposal_id}/archive-demo",
    response_model=PatientHistoryProposalRead,
)
async def archive_demo_proposal(
    clinic_id: str,
    proposal_id: str,
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientHistoryProposalRead:
    try:
        updated = await svc.archive_demo_history_proposal(
            pool=pool,
            proposal_id=proposal_id,
            clinic_id=clinic_id,
            actor_user=current_user,
        )
        return PatientHistoryProposalRead(**updated)
    except svc.ProposalNotFoundError:
        raise HTTPException(status_code=404, detail="Proposal not found.")
