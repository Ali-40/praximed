"""
Vapi Assistant Config Pack route — PraxisMed Sprint 19 / Module 141.

Protected:
  GET /clinics/{clinic_id}/vapi-assistant-config-pack

No PHI. No secrets. No Vapi credentials. No live Vapi binding.
production_phi_enabled is always False in the response.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.schemas.vapi_assistant_config import VapiAssistantConfigPack
from backend.app.services.clinic_language_settings import ClinicNotFoundError
from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/clinics",
    tags=["vapi-assistant-config"],
)


@router.get(
    "/{clinic_id}/vapi-assistant-config-pack",
    response_model=VapiAssistantConfigPack,
)
async def get_vapi_assistant_config_pack(
    clinic_id: str,
    pool: Any = Depends(get_db_pool),
    auth: AuthContext = Depends(get_current_user),
) -> VapiAssistantConfigPack:
    """Protected — return a safe Vapi assistant config pack for a clinic.

    Derives the pack from clinic language settings and tenant config.
    No PHI. No secrets. No live Vapi binding. production_phi_enabled is always False.
    """
    try:
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id=clinic_id,
            actor_user=auth,
        )
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error building Vapi assistant config pack")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return VapiAssistantConfigPack(**pack)
