"""
Anamnesis Template routes — PraxisMed Sprint 20 / Module 150.

Protected internal routes — require authenticated session.
No public access. No DELETE route. No patient answers. No history writes.
No diagnosis. No medical advice. No triage scoring. No real PHI.
Synthetic/fake staging only. production_phi_enabled always False.
Production PHI remains NO-GO.

POST   /clinics/{clinic_id}/anamnesis-templates
GET    /clinics/{clinic_id}/anamnesis-templates
GET    /anamnesis-templates/{template_id}
PATCH  /anamnesis-templates/{template_id}/status
POST   /anamnesis-templates/seed-demo
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories.anamnesis_template_repo import (
    AnamnesisTemplateRepoError,
    AnamnesisTemplateNotFoundError,
    InvalidAnamnesisTemplateError,
)
from backend.app.schemas.anamnesis_template import (
    AnamnesisTemplateCreate,
    AnamnesisTemplateStatusUpdate,
    AnamnesisTemplateResponse,
    AnamnesisTemplateListResponse,
)
from backend.app.services import anamnesis_template_engine as svc

logger = logging.getLogger(__name__)

router = APIRouter(tags=["anamnesis-templates"])


@router.post(
    "/clinics/{clinic_id}/anamnesis-templates",
    status_code=201,
    response_model=AnamnesisTemplateResponse,
)
async def create_anamnesis_template(
    clinic_id: str,
    body: AnamnesisTemplateCreate,
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> AnamnesisTemplateResponse:
    try:
        payload = {
            "clinic_id": clinic_id,
            "template_key": body.template_key,
            "display_name": body.display_name,
            "specialty": body.specialty,
            "template_schema": body.template_schema,
            "version": body.version,
            "primary_language": body.primary_language,
            "supported_languages": body.supported_languages,
            "escalation_keywords": body.escalation_keywords,
            "consent_purpose": body.consent_purpose,
            "synthetic_demo": body.synthetic_demo,
        }
        template = await svc.create_template(
            pool=pool,
            payload=payload,
            actor_user=current_user,
        )
        return AnamnesisTemplateResponse(ok=True, template=template)
    except InvalidAnamnesisTemplateError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except AnamnesisTemplateRepoError as exc:
        logger.error("create_anamnesis_template error: %s", exc)
        raise HTTPException(status_code=500, detail="Template creation failed")


@router.get(
    "/clinics/{clinic_id}/anamnesis-templates",
    response_model=AnamnesisTemplateListResponse,
)
async def list_anamnesis_templates(
    clinic_id: str,
    specialty: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> AnamnesisTemplateListResponse:
    templates = await svc.list_templates(
        pool=pool,
        clinic_id=clinic_id,
        specialty=specialty,
        status=status,
        limit=limit,
    )
    return AnamnesisTemplateListResponse(
        ok=True,
        templates=templates,
        total=len(templates),
    )


@router.get(
    "/anamnesis-templates/{template_id}",
    response_model=AnamnesisTemplateResponse,
)
async def get_anamnesis_template(
    template_id: str,
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> AnamnesisTemplateResponse:
    template = await svc.get_template(pool=pool, template_id=template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return AnamnesisTemplateResponse(ok=True, template=template)


@router.patch(
    "/anamnesis-templates/{template_id}/status",
    response_model=AnamnesisTemplateResponse,
)
async def update_anamnesis_template_status(
    template_id: str,
    body: AnamnesisTemplateStatusUpdate,
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> AnamnesisTemplateResponse:
    try:
        if body.status == "active":
            template = await svc.activate_template(
                pool=pool,
                template_id=template_id,
                updated_by_user_id=str(current_user.user_id),
            )
        else:
            template = await svc.archive_template(
                pool=pool,
                template_id=template_id,
                updated_by_user_id=str(current_user.user_id),
            )
        if template is None:
            raise HTTPException(status_code=404, detail="Template not found")
        return AnamnesisTemplateResponse(ok=True, template=template)
    except AnamnesisTemplateNotFoundError:
        raise HTTPException(status_code=404, detail="Template not found")
    except AnamnesisTemplateRepoError as exc:
        logger.error("update_anamnesis_template_status error: %s", exc)
        raise HTTPException(status_code=500, detail="Status update failed")


@router.post(
    "/anamnesis-templates/seed-demo",
    status_code=201,
    response_model=AnamnesisTemplateListResponse,
)
async def seed_demo_anamnesis_templates(
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> AnamnesisTemplateListResponse:
    templates = await svc.seed_demo_templates(pool=pool)
    return AnamnesisTemplateListResponse(
        ok=True,
        templates=templates,
        total=len(templates),
        production_phi_enabled=False,
    )
