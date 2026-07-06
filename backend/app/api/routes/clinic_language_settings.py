"""
Clinic Language Settings routes — PraxisMed Sprint 19 / Module 138.

Protected (existing current_user auth):
  GET  /clinics/{clinic_id}/language-settings  — read language settings
  PATCH /clinics/{clinic_id}/language-settings — update language settings

No PHI. No secrets. No Vapi credentials. Production PHI remains NO-GO.
German-first defaults for Austrian clinics.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.schemas.clinic_language_settings import (
    ClinicLanguageSettingsRead,
    ClinicLanguageSettingsUpdate,
)
from backend.app.services.clinic_language_settings import (
    ClinicNotFoundError,
    LanguageSettingsValidationError,
    get_clinic_language_settings,
    update_clinic_language_settings,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/clinics",
    tags=["clinic-language-settings"],
)


@router.get("/{clinic_id}/language-settings", response_model=ClinicLanguageSettingsRead)
async def read_clinic_language_settings(
    clinic_id: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ClinicLanguageSettingsRead:
    """Protected — return language settings for a clinic.

    Returns German-first defaults when no explicit settings are stored.
    No PHI. No secrets. No Vapi credentials.
    """
    try:
        settings = await get_clinic_language_settings(pool=pool, clinic_id=clinic_id)
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error reading clinic language settings")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ClinicLanguageSettingsRead(ok=True, **settings)


@router.patch("/{clinic_id}/language-settings", response_model=ClinicLanguageSettingsRead)
async def patch_clinic_language_settings(
    clinic_id: str,
    body: ClinicLanguageSettingsUpdate,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> ClinicLanguageSettingsRead:
    """Protected — partially update language settings for a clinic.

    Updates clinics.locale in the database and writes language_config to
    the tenant JSON config file. No PHI, secrets, or Vapi credentials accepted.
    """
    try:
        updated = await update_clinic_language_settings(
            pool=pool,
            clinic_id=clinic_id,
            update=body.model_dump(exclude_none=True),
            actor_user_id=auth.user_id,
        )
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except LanguageSettingsValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error updating clinic language settings")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return ClinicLanguageSettingsRead(ok=True, **updated)
