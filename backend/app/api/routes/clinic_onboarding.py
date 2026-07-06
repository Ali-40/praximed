"""
Clinic Onboarding Request routes — PraxisMed Sprint 19 / Module 132.

Public:
  POST /clinic-onboarding-requests   — submit pilot/onboarding request (no auth)

Protected (existing current_user auth):
  GET  /clinic-onboarding-requests                   — list (admin/staff)
  GET  /clinic-onboarding-requests/{request_id}      — get single (admin/staff)
  PATCH /clinic-onboarding-requests/{request_id}/status — update status (admin/staff)

No enforce_phi_safeguard applied — this endpoint does not process patient PHI.
No automatic tenant creation. production_phi_enabled always false.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import clinic_onboarding_repo
from backend.app.db.repositories.clinic_onboarding_repo import InvalidClinicOnboardingRequestError
from backend.app.schemas.clinic_onboarding import (
    ClinicOnboardingRequestCreate,
    ClinicOnboardingRequestListResponse,
    ClinicOnboardingRequestResponse,
    ClinicOnboardingRequestStatusUpdate,
)
from backend.app.services import tenant_provisioning
from backend.app.services.tenant_provisioning import (
    ProvisioningBlockedError,
    ProvisioningNotFoundError,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/clinic-onboarding-requests",
    tags=["clinic-onboarding"],
)


@router.post("", response_model=ClinicOnboardingRequestResponse, status_code=201)
async def submit_clinic_onboarding_request(
    body: ClinicOnboardingRequestCreate,
    pool: Any = Depends(get_db_pool),
) -> ClinicOnboardingRequestResponse:
    """Public endpoint — accept a clinic pilot/onboarding request.

    No auth required. Does not create a production tenant.
    production_phi_enabled is always false. No patient PHI accepted.
    """
    try:
        row = await clinic_onboarding_repo.create_clinic_onboarding_request(
            pool=pool,
            clinic_name=body.clinic_name,
            doctor_name=body.doctor_name,
            contact_email=body.contact_email,
            consent_pilot_contact=body.consent_pilot_contact,
            acknowledges_no_phi=body.acknowledges_no_phi,
            clinic_type=body.clinic_type,
            specialty=body.specialty,
            city=body.city,
            address=body.address,
            website=body.website,
            contact_phone=body.contact_phone,
            preferred_language=body.preferred_language,
            fallback_language=body.fallback_language,
            supported_languages=body.supported_languages,
            workflow_notes=body.workflow_notes,
            estimated_call_volume=body.estimated_call_volume,
            current_booking_system=body.current_booking_system,
            wants_ai_phone_intake=body.wants_ai_phone_intake,
            wants_dashboard=body.wants_dashboard,
            wants_notifications=body.wants_notifications,
            pilot_interest_level=body.pilot_interest_level,
            source=body.source,
        )
    except InvalidClinicOnboardingRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error creating clinic onboarding request")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ClinicOnboardingRequestResponse(ok=True, request=row)


@router.get("", response_model=ClinicOnboardingRequestListResponse)
async def list_clinic_onboarding_requests(
    status: Optional[str] = Query(None),
    limit: int = Query(50),
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ClinicOnboardingRequestListResponse:
    """Protected — list onboarding requests (staff/admin review)."""
    try:
        rows = await clinic_onboarding_repo.list_clinic_onboarding_requests(
            pool=pool,
            status=status,
            limit=limit,
        )
    except InvalidClinicOnboardingRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error listing clinic onboarding requests")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ClinicOnboardingRequestListResponse(ok=True, requests=rows, total=len(rows))


@router.get("/{request_id}", response_model=ClinicOnboardingRequestResponse)
async def get_clinic_onboarding_request(
    request_id: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ClinicOnboardingRequestResponse:
    """Protected — get a single onboarding request by ID."""
    try:
        row = await clinic_onboarding_repo.get_clinic_onboarding_request_by_id(
            pool=pool,
            request_id=request_id,
        )
    except Exception as exc:
        logger.exception("Unexpected error fetching clinic onboarding request")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Onboarding request not found")

    return ClinicOnboardingRequestResponse(ok=True, request=row)


@router.patch("/{request_id}/status", response_model=ClinicOnboardingRequestResponse)
async def update_clinic_onboarding_request_status(
    request_id: str,
    body: ClinicOnboardingRequestStatusUpdate,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ClinicOnboardingRequestResponse:
    """Protected — update the review status of an onboarding request."""
    try:
        row = await clinic_onboarding_repo.update_clinic_onboarding_status(
            pool=pool,
            request_id=request_id,
            status=body.status,
            reviewer_notes=body.reviewer_notes,
        )
    except InvalidClinicOnboardingRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error updating clinic onboarding status")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Onboarding request not found")

    return ClinicOnboardingRequestResponse(ok=True, request=row)


@router.post("/{request_id}/provision-clinic-shell")
async def provision_clinic_shell(
    request_id: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> dict:
    """Protected internal endpoint — create a safe clinic shell from a
    pilot_approved onboarding request.

    Safety:
      - Requires authenticated session.
      - Only works when request status is pilot_approved.
      - Does NOT activate production PHI.
      - Does NOT store Vapi credentials.
      - Does NOT create patient records.
      - Does NOT auto-provision from public onboarding submission.
      - Records immutable audit event.
      - Idempotent: returns existing clinic info if already provisioned.
    """
    try:
        result = await tenant_provisioning.provision_clinic_shell_from_onboarding_request(
            pool=pool,
            request_id=request_id,
            actor_user_id=auth.user_id,
        )
    except ProvisioningNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ProvisioningBlockedError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error during clinic shell provisioning")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return {"ok": True, **result}
