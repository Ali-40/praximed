"""
n8n Calendar Sync Webhook Route — PraxisMed Sprint 1 / Module 8

Exposes one endpoint:

    POST /webhooks/n8n/calendar-sync

n8n calls this route whenever a clinic calendar changes.  The route
validates the HMAC-SHA256 webhook signature (Module 47) and the machine auth
context, then delegates all business logic to the calendar sync service
(Module 6) and contains no direct SQL.

Webhook security
----------------
Signature verification:  HMAC-SHA256 over the raw request body using
``N8N_WEBHOOK_SECRET``.

  • Missing or invalid ``X-N8N-Signature`` → HTTP 401.
  • ``N8N_WEBHOOK_SECRET`` not configured → HTTP 503.

Machine auth:  ``X-Service-Name``, ``X-Service-Clinic-Id``, ``X-Service-Scopes``
headers are validated by the machine auth dependency.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.api.dependencies.machine_auth import (
    get_machine_auth_context,
    require_n8n_calendar_sync_access,
)
from backend.app.api.dependencies.webhook_signature import (
    verify_n8n_webhook_signature_dependency,
)
from backend.app.api.deps import get_db_pool
from backend.app.core.machine_auth import MachineAuthContext
from backend.app.modules.audit import audit_logger
from backend.app.modules.calendar_sync.calendar_sync import (
    InvalidCalendarPayloadError,
    UnsupportedCalendarEventTypeError,
    process_calendar_sync_payload,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhooks"])


@router.post("/n8n/calendar-sync")
async def n8n_calendar_sync(
    payload: Dict[str, Any],
    pool: Any = Depends(get_db_pool),
    _sig: bool = Depends(verify_n8n_webhook_signature_dependency),
    machine_auth: MachineAuthContext = Depends(get_machine_auth_context),
) -> Dict[str, Any]:
    """
    Receive a calendar sync event from n8n and process it.

    n8n sends a JSON body describing what changed on the clinic's calendar.
    This route normalises the payload and hands it to
    ``process_calendar_sync_payload``, which upserts/deletes the relevant
    database records and writes a sync log entry.

    Error mapping
    -------------
    400  Invalid or missing payload fields.
    401  Missing/invalid n8n signature or missing machine auth.
    403  Machine service or scope not permitted.
    500  Unexpected error in the sync service.
    503  N8N_WEBHOOK_SECRET not configured or DB pool not initialised.
    """
    require_n8n_calendar_sync_access(
        requested_clinic_id=payload.get("clinic_id"),
        machine_context=machine_auth,
    )
    try:
        result = await process_calendar_sync_payload(pool, payload)
        await audit_logger.safe_record_audit_event(
            pool,
            audit_logger.build_machine_audit_event(
                machine_auth,
                action="n8n.calendar_sync",
                resource_type="calendar_sync",
                clinic_id=payload.get("clinic_id"),
                resource_id=result.get("sync_event_id"),
                severity="info",
                metadata={
                    "route": "n8n_calendar_sync",
                    "event_type": payload.get("event_type"),
                },
            ),
        )
        return result

    except (InvalidCalendarPayloadError, UnsupportedCalendarEventTypeError) as exc:
        logger.warning("Invalid calendar sync payload: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))

    except HTTPException:
        raise  # let FastAPI handle these as-is

    except Exception as exc:
        logger.exception("Unexpected error processing calendar sync payload")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error processing calendar sync event: {exc}",
        )
