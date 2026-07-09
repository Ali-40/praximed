"""
Sales Demo routes — PraxisMed Sprint 21 / Module 158

Staging-only endpoints for the one-click sales demo flow.
Creates synthetic appointment requests and resets demo data.

Safety constraints:
- No real patient data. No PHI. No Vapi live calls. No audio.
- Administrative scheduling only. Staff review required before any clinical decision.
- No patient_history_* writes.
- production_phi_enabled is always False in all created records.
- Demo records identified by source_ref LIKE 'sales-demo-call-%'.
- Reset archives demo records (status → archived) — no records removed.
- Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
import os
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import appointment_request_repo

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/demo/sales-mvp",
    tags=["sales-demo"],
)

_STAGING_ENVIRONMENTS = frozenset({"local", "staging"})


def _require_staging() -> None:
    env = os.environ.get("ENVIRONMENT", "local").lower()
    if env not in _STAGING_ENVIRONMENTS:
        raise HTTPException(status_code=403, detail="Demo endpoints are staging-only.")


@router.post("/create-call")
async def create_sales_demo_call(
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> dict:
    """
    Creates a synthetic sales-demo appointment request.

    No real patient data. No PHI. No Vapi. No audio.
    Administrative scheduling only. production_phi_enabled = False.
    Staging-only — blocked in production environments.
    """
    _require_staging()

    clinic_id = current_user.clinic_id
    demo_ref = f"sales-demo-call-{secrets.token_hex(6)}"

    row = await appointment_request_repo.create_appointment_request(
        pool=pool,
        clinic_id=clinic_id,
        source="staff",
        source_ref=demo_ref,
        patient_name="Mag. Klaus Hofer",
        patient_phone="+43 660 000 0000",
        reason="Rückenschmerzen seit 3 Tagen, Termin erbeten",
        status="callback_needed",
        urgency_level="normal",
        action_required=True,
        raw_payload={
            "sales_demo": True,
            "synthetic_demo": True,
            "production_phi_enabled": False,
            "preferred_time_label": "Morgen Vormittag",
            "demo_note": "Synthetische Demo-Anfrage — kein echter Patient. Keine PHI.",
        },
    )

    logger.info("Sales demo call created: clinic=%s ref=%s", clinic_id, demo_ref)

    return {
        "ok": True,
        "request_id": str(row["id"]),
        "message": "Demo-Anfrage wurde der Warteschlange hinzugefügt.",
        "synthetic_demo": True,
        "production_phi_enabled": False,
    }


@router.post("/reset")
async def reset_sales_demo_data(
    pool: Any = Depends(get_db_pool),
    current_user: AuthContext = Depends(get_current_user),
) -> dict:
    """
    Archives all synthetic demo appointment requests for the clinic.

    Identifies demo records by source_ref LIKE 'sales-demo-call-%'.
    Archives (status → archived) — never deletes real records.
    No PHI. No real patient data. Staging-only.
    """
    _require_staging()

    clinic_id = current_user.clinic_id

    sql = """
        UPDATE appointment_requests
        SET status = 'archived'
        WHERE clinic_id = $1
          AND source_ref LIKE 'sales-demo-call-%'
          AND status != 'archived'
        RETURNING id
    """
    rows = await pool.fetch(sql, clinic_id)
    archived_count = len(rows)

    logger.info("Sales demo reset: clinic=%s archived=%d", clinic_id, archived_count)

    return {
        "ok": True,
        "archived_count": archived_count,
        "message": f"Demo zurückgesetzt. {archived_count} Demo-Anfrage(n) archiviert.",
        "synthetic_demo": True,
        "production_phi_enabled": False,
    }
