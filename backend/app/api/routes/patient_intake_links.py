"""
Patient Intake Link routes — PraxisMed Sprint 20 / Module 151.

Protected internal routes — require authenticated session.
Public demo-token routes — no login required but demo/synthetic only.

Protected:
  POST   /clinics/{clinic_id}/patient-intake-links
  GET    /clinics/{clinic_id}/patient-intake-links
  GET    /clinics/{clinic_id}/patient-intake-submissions
  PATCH  /patient-intake-links/{link_id}/revoke

Public (demo token):
  GET    /intake/{token}
  POST   /intake/{token}/submit

No DELETE. No real patient data. No PHI. No diagnosis. No medical advice.
No history writes. No AI structuring. No triage scoring.
production_phi_enabled always False. Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.schemas.patient_intake_link import (
    PatientIntakeLinkCreate,
    PatientIntakeSubmissionCreate,
    PatientIntakeLinkRevoke,
    PatientIntakeLinkCreateResponse,
    PatientIntakeLinkListResponse,
    PatientIntakePublicResponse,
    PatientIntakeSubmitResponse,
    PatientIntakeSubmissionListResponse,
    PatientIntakeLinkRead,
    PatientIntakePublicTemplateRead,
)
from backend.app.services import patient_intake_link as svc

logger = logging.getLogger(__name__)

router = APIRouter(tags=["patient-intake-links"])


# ── Protected admin routes ────────────────────────────────────────────────────


@router.post(
    "/clinics/{clinic_id}/patient-intake-links",
    status_code=201,
    response_model=PatientIntakeLinkCreateResponse,
)
async def create_patient_intake_link(
    clinic_id: str,
    body: PatientIntakeLinkCreate,
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientIntakeLinkCreateResponse:
    try:
        result = await svc.create_demo_intake_link(
            pool=pool,
            clinic_id=clinic_id,
            payload={
                "template_id": body.template_id,
                "language": body.language,
                "purpose": body.purpose,
                "expires_at": body.expires_at,
                "patient_id": body.patient_id,
                "appointment_request_id": body.appointment_request_id,
                "max_submissions": body.max_submissions,
            },
            actor_user=current_user,
        )
        link_data = result["link"]
        link_read = PatientIntakeLinkRead(
            id=str(link_data["id"]),
            clinic_id=str(link_data["clinic_id"]),
            patient_id=str(link_data["patient_id"]) if link_data.get("patient_id") else None,
            appointment_request_id=str(link_data["appointment_request_id"]) if link_data.get("appointment_request_id") else None,
            template_id=str(link_data["template_id"]),
            token_prefix=link_data["token_prefix"],
            status=link_data["status"],
            purpose=link_data["purpose"],
            language=link_data["language"],
            expires_at=link_data["expires_at"],
            max_submissions=link_data["max_submissions"],
            submission_count=link_data["submission_count"],
            synthetic_demo=link_data["synthetic_demo"],
            production_phi_enabled=False,
            created_by_user_id=str(link_data["created_by_user_id"]) if link_data.get("created_by_user_id") else None,
            created_at=link_data["created_at"],
            updated_at=link_data["updated_at"],
        )
        return PatientIntakeLinkCreateResponse(
            ok=True,
            link=link_read,
            intake_url=result["intake_url"],
            raw_token_shown_once=True,
        )
    except svc.ClinicNotFoundError:
        raise HTTPException(status_code=404, detail="Clinic not found")
    except svc.TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("create_patient_intake_link error: %s", exc)
        raise HTTPException(status_code=500, detail="Intake link creation failed")


@router.get(
    "/clinics/{clinic_id}/patient-intake-links",
    response_model=PatientIntakeLinkListResponse,
)
async def list_patient_intake_links(
    clinic_id: str,
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientIntakeLinkListResponse:
    links = await svc.list_clinic_intake_links(
        pool=pool, clinic_id=clinic_id, status=status, limit=limit
    )
    return PatientIntakeLinkListResponse(ok=True, links=links, total=len(links))


@router.get(
    "/clinics/{clinic_id}/patient-intake-submissions",
    response_model=PatientIntakeSubmissionListResponse,
)
async def list_patient_intake_submissions(
    clinic_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientIntakeSubmissionListResponse:
    submissions = await svc.list_clinic_intake_submissions(
        pool=pool, clinic_id=clinic_id, limit=limit
    )
    return PatientIntakeSubmissionListResponse(
        ok=True, submissions=submissions, total=len(submissions)
    )


@router.patch(
    "/patient-intake-links/{link_id}/revoke",
    response_model=PatientIntakeLinkCreateResponse,
)
async def revoke_patient_intake_link(
    link_id: str,
    body: PatientIntakeLinkRevoke,
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> PatientIntakeLinkCreateResponse:
    try:
        clinic_id = str(current_user.clinic_id)
        await svc.revoke_intake_link(
            pool=pool,
            link_id=link_id,
            clinic_id=clinic_id,
            actor_user=current_user,
        )
        return PatientIntakeLinkCreateResponse(ok=True, message="Intake link revoked.")
    except svc.IntakeLinkNotFoundError:
        raise HTTPException(status_code=404, detail="Intake link not found")
    except Exception as exc:
        logger.error("revoke_patient_intake_link error: %s", exc)
        raise HTTPException(status_code=500, detail="Revoke failed")


# ── Public demo-token routes ──────────────────────────────────────────────────


@router.get(
    "/intake/{token}",
    response_model=PatientIntakePublicResponse,
)
async def get_public_intake_template(
    token: str,
    pool: Any = Depends(get_db_pool),
) -> PatientIntakePublicResponse:
    try:
        data = await svc.get_public_intake_template(pool=pool, raw_token=token)
        template_read = PatientIntakePublicTemplateRead(**data)
        return PatientIntakePublicResponse(ok=True, template=template_read)
    except svc.IntakeLinkNotFoundError:
        raise HTTPException(status_code=404, detail="Intake link not found or invalid.")
    except (svc.IntakeLinkExpiredError, svc.IntakeLinkRevokedError, svc.IntakeLinkSubmittedError) as exc:
        raise HTTPException(status_code=410, detail=str(exc))
    except svc.TemplateNotFoundError:
        raise HTTPException(status_code=404, detail="Template not found.")
    except Exception as exc:
        logger.error("get_public_intake_template error: %s", exc)
        raise HTTPException(status_code=500, detail="Could not load intake.")


@router.post(
    "/intake/{token}/submit",
    status_code=201,
    response_model=PatientIntakeSubmitResponse,
)
async def submit_public_intake(
    token: str,
    body: PatientIntakeSubmissionCreate,
    pool: Any = Depends(get_db_pool),
) -> PatientIntakeSubmitResponse:
    try:
        result = await svc.submit_public_intake(
            pool=pool,
            raw_token=token,
            payload={
                "language": body.language,
                "answers": body.answers,
                "skipped_questions": body.skipped_questions,
                "consent_text_version": body.consent_text_version,
                "consent_text_snapshot": body.consent_text_snapshot,
            },
        )
        return PatientIntakeSubmitResponse(
            ok=True,
            submission_id=result["submission_id"],
            consent_event_id=result["consent_event_id"],
            escalation_matches=result["escalation_matches"],
            status="submitted",
            production_phi_enabled=False,
            message="Intake submitted for staff review.",
        )
    except svc.IntakeLinkNotFoundError:
        raise HTTPException(status_code=404, detail="Intake link not found or invalid.")
    except (svc.IntakeLinkExpiredError, svc.IntakeLinkRevokedError, svc.IntakeLinkSubmittedError) as exc:
        raise HTTPException(status_code=410, detail=str(exc))
    except Exception as exc:
        logger.error("submit_public_intake error: %s", exc)
        raise HTTPException(status_code=500, detail="Could not submit intake.")
