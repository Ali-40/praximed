"""
n8n Calendar Sync Webhook Route — PraxisMed Sprint 1 / Module 8

Exposes one endpoint:

    POST /webhooks/n8n/calendar-sync

n8n calls this route whenever a clinic calendar changes.  The route
delegates all business logic to the calendar sync service (Module 6) and
contains no direct SQL.

Webhook security
----------------
Read the expected secret from the environment variable
``PRAXIMED_N8N_WEBHOOK_SECRET``.

  • If the variable is set, the incoming request MUST carry a matching
    ``X-PraxisMed-Webhook-Secret`` header, otherwise HTTP 401 is returned.
  • If the variable is not set (local / CI environments), all requests are
    accepted so that tests run without extra configuration.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.api.dependencies.machine_auth import (
    get_machine_auth_context,
    require_n8n_calendar_sync_access,
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

_SECRET_ENV_VAR    = "PRAXIMED_N8N_WEBHOOK_SECRET"
_SECRET_HEADER_KEY = "x-praxismed-webhook-secret"   # ASGI lowercases all header names


def _verify_webhook_secret(request: Request) -> None:
    """
    FastAPI dependency that validates the webhook secret header.

    Reads the expected secret from ``PRAXIMED_N8N_WEBHOOK_SECRET``.
    No-op when the variable is not set (local / CI environments).
    Raises HTTP 401 when the header is missing or does not match.

    We read the header directly from ``request.headers`` instead of using
    FastAPI's ``Header()`` injection to avoid any ambiguity in how FastAPI
    converts the mixed-case header name ``X-PraxisMed-Webhook-Secret`` to a
    Python parameter name.
    """
    expected = os.environ.get(_SECRET_ENV_VAR)
    if not expected:
        return  # secret check disabled in this environment

    provided = request.headers.get(_SECRET_HEADER_KEY)
    if provided != expected:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing webhook secret.",
        )


@router.post("/n8n/calendar-sync")
async def n8n_calendar_sync(
    payload: Dict[str, Any],
    pool: Any = Depends(get_db_pool),
    _secret: None = Depends(_verify_webhook_secret),
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
    401  Webhook secret mismatch or missing machine auth.
    403  Machine service or scope not permitted.
    500  Unexpected error in the sync service.
    503  Database pool not yet initialised (returned by ``get_db_pool``).
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
