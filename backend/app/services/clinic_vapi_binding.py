"""
Clinic Vapi Binding Service — PraxisMed Sprint 19 / Module 145.

Orchestrates creation and retrieval of Vapi binding metadata.
Secret reference names only — never resolves or stores actual secret values.
No live Vapi API calls. No PHI. production_phi_enabled always False.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import clinic_vapi_binding_repo
from backend.app.db.repositories.clinic_vapi_binding_repo import (
    InvalidClinicVapiBindingError,
    ClinicVapiBindingNotFoundError,
)
from backend.app.schemas.clinic_vapi_binding import ClinicVapiBindingCreate

logger = logging.getLogger(__name__)


class ClinicNotFoundError(RuntimeError):
    """Raised when the target clinic does not exist."""


async def _verify_clinic_exists(pool: Any, clinic_id: str) -> None:
    row = await pool.fetchrow(
        "SELECT id FROM clinics WHERE id = $1::uuid", clinic_id
    )
    if row is None:
        raise ClinicNotFoundError(f"Clinic not found: {clinic_id!r}")


async def create_vapi_binding_metadata(
    pool: Any,
    payload: ClinicVapiBindingCreate,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    await _verify_clinic_exists(pool, payload.clinic_id)

    row = await clinic_vapi_binding_repo.create_clinic_vapi_binding(
        pool=pool,
        clinic_id=payload.clinic_id,
        api_key_secret_ref=payload.api_key_secret_ref,
        webhook_secret_ref=payload.webhook_secret_ref,
        language_mode=payload.language_mode,
        created_by_user_id=actor_user.user_id if actor_user else None,
    )

    logger.info(
        "vapi_binding_created clinic_id=%s binding_id=%s language_mode=%s actor=%s",
        payload.clinic_id,
        row.get("id"),
        payload.language_mode,
        actor_user.user_id if actor_user else "anonymous",
    )

    row["production_phi_enabled"] = False
    return row


async def get_vapi_binding_metadata(
    pool: Any,
    clinic_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Optional[Dict[str, Any]]:
    await _verify_clinic_exists(pool, clinic_id)

    row = await clinic_vapi_binding_repo.get_clinic_vapi_binding_by_clinic_id(
        pool=pool,
        clinic_id=clinic_id,
    )
    if row is not None:
        row["production_phi_enabled"] = False
    return row


async def update_vapi_binding_status(
    pool: Any,
    binding_id: str,
    status: str,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    row = await clinic_vapi_binding_repo.update_clinic_vapi_binding_status(
        pool=pool,
        binding_id=binding_id,
        status=status,
    )

    if row is None:
        raise ClinicVapiBindingNotFoundError(f"Binding not found: {binding_id!r}")

    logger.info(
        "vapi_binding_status_updated binding_id=%s status=%s actor=%s",
        binding_id,
        status,
        actor_user.user_id if actor_user else "anonymous",
    )

    row["production_phi_enabled"] = False
    return row
