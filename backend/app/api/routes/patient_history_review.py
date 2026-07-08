"""
Patient History Review routes — PraxisMed Sprint 20 / Module 154.

Protected internal routes — require authenticated session.
Staff/doctor review workflow for unverified patient history proposals.

Protected:
  GET    /clinics/{clinic_id}/patient-history-review-queue
  GET    /patient-history-proposals/{proposal_id}/review
  PATCH  /patient-history-proposals/{proposal_id}/approve-merge
  PATCH  /patient-history-proposals/{proposal_id}/reject-review

No DELETE. No public access. No auto-approval. No diagnosis. No medical advice.
No triage scoring. No treatment recommendations. No external LLM.
production_phi_enabled always False. Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.schemas.patient_history_review import (
    PatientHistoryMergeRequest,
    PatientHistoryMergeResult,
    PatientHistoryRejectRequest,
    PatientHistoryRejectResult,
    PatientHistoryProposalReviewDetail,
    PatientHistoryReviewQueueResponse,
)
from backend.app.services import patient_history_review as svc

logger = logging.getLogger(__name__)

router = APIRouter(tags=["patient-history-review"])


@router.get(
    "/clinics/{clinic_id}/patient-history-review-queue",
    response_model=PatientHistoryReviewQueueResponse,
)
async def get_review_queue(
    clinic_id: str,
    patient_id: Optional[str] = Query(default=None),
    history_type: Optional[str] = Query(default=None),
    status: str = Query(default="unverified"),
    limit: int = Query(default=50, ge=1, le=200),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientHistoryReviewQueueResponse:
    proposals = await svc.list_review_queue(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
        history_type=history_type,
        status=status,
        limit=limit,
        actor_user=current_user,
    )
    return PatientHistoryReviewQueueResponse(
        ok=True,
        proposals=proposals,
        total=len(proposals),
        production_phi_enabled=False,
    )


@router.get(
    "/patient-history-proposals/{proposal_id}/review",
    response_model=PatientHistoryProposalReviewDetail,
)
async def get_proposal_review_detail(
    proposal_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientHistoryProposalReviewDetail:
    try:
        detail = await svc.get_proposal_review_detail(
            pool=pool,
            proposal_id=proposal_id,
            clinic_id=clinic_id,
            actor_user=current_user,
        )
        return PatientHistoryProposalReviewDetail(**detail)
    except svc.ProposalNotFoundError:
        raise HTTPException(status_code=404, detail="Proposal not found.")


@router.patch(
    "/patient-history-proposals/{proposal_id}/approve-merge",
    status_code=201,
    response_model=PatientHistoryMergeResult,
)
async def approve_merge_proposal(
    proposal_id: str,
    body: PatientHistoryMergeRequest,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientHistoryMergeResult:
    try:
        result = await svc.approve_and_merge_history_proposal(
            pool=pool,
            proposal_id=proposal_id,
            clinic_id=clinic_id,
            edited_fields=body.edited_fields,
            edited_fhir_payload=body.edited_fhir_payload,
            review_note=body.review_note,
            actor_user=current_user,
        )
        return PatientHistoryMergeResult(**result)
    except svc.ProposalNotFoundError:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    except svc.ProposalNotEligibleError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except svc.PatientRequiredError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except svc.ForbiddenMergeFieldError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except svc.PhiGuardError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("approve_merge_error proposal=%s clinic=%s err=%r", proposal_id, clinic_id, exc)
        raise HTTPException(status_code=500, detail="Could not merge proposal.")


@router.patch(
    "/patient-history-proposals/{proposal_id}/reject-review",
    response_model=PatientHistoryRejectResult,
)
async def reject_proposal_review(
    proposal_id: str,
    body: PatientHistoryRejectRequest,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientHistoryRejectResult:
    try:
        result = await svc.reject_history_proposal_with_review(
            pool=pool,
            proposal_id=proposal_id,
            clinic_id=clinic_id,
            rejected_reason=body.rejected_reason,
            review_note=body.review_note,
            actor_user=current_user,
        )
        return PatientHistoryRejectResult(**result)
    except svc.ProposalNotFoundError:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    except svc.ProposalNotEligibleError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("reject_review_error proposal=%s clinic=%s err=%r", proposal_id, clinic_id, exc)
        raise HTTPException(status_code=500, detail="Could not reject proposal.")
