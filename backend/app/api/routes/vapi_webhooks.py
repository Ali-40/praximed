"""
Vapi call event webhook route — PraxisMed Sprint 1 / Module 14

Exposes one endpoint:

    POST /webhooks/vapi/call-event

Vapi posts a JSON body whenever a call event occurs (call started, ended,
transcript ready, human handoff required, etc.).  The route validates the
optional webhook secret, delegates to the event handler, and returns the
service result as JSON.

Webhook security
----------------
Read the expected secret from the environment variable
``PRAXIMED_VAPI_WEBHOOK_SECRET``.

  • If the variable is set the request MUST carry a matching
    ``X-PraxisMed-Vapi-Secret`` header, otherwise HTTP 401 is returned.
  • If the variable is not set (local / CI environments) all requests
    are accepted so that tests run without extra configuration.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.api.dependencies.machine_auth import (
    get_machine_auth_context,
    require_vapi_webhook_access,
)
from backend.app.api.deps import get_db_pool
from backend.app.core.machine_auth import MachineAuthContext
from backend.app.modules.vapi.vapi_event_handler import (
    InvalidVapiEventPayloadError,
    UnsupportedVapiEventTypeError,
    process_vapi_call_event,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["vapi-webhooks"])

_SECRET_ENV_VAR    = "PRAXIMED_VAPI_WEBHOOK_SECRET"
_SECRET_HEADER_KEY = "x-praxismed-vapi-secret"   # lowercase of X-PraxisMed-Vapi-Secret


def _verify_vapi_secret(request: Request) -> None:
    """
    FastAPI dependency that validates the Vapi webhook secret header.

    No-op when the environment variable is not set (local / CI environments).
    Raises HTTP 401 when the header is missing or does not match.
    """
    expected = os.environ.get(_SECRET_ENV_VAR)
    if not expected:
        return

    provided = request.headers.get(_SECRET_HEADER_KEY)
    if provided != expected:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing Vapi webhook secret.",
        )


@router.post("/vapi/call-event")
async def vapi_call_event(
    payload: Dict[str, Any],
    pool: Any = Depends(get_db_pool),
    _secret: None = Depends(_verify_vapi_secret),
    machine_auth: MachineAuthContext = Depends(get_machine_auth_context),
) -> Dict[str, Any]:
    """
    Receive a Vapi call event and persist it via the call event handler.

    Error mapping
    -------------
    400  Invalid or unsupported payload.
    401  Webhook secret mismatch or missing machine auth.
    403  Machine service or scope not permitted.
    500  Unexpected error in the event handler.
    503  Database pool not yet initialised.
    """
    require_vapi_webhook_access(
        requested_clinic_id=payload.get("clinic_id"),
        machine_context=machine_auth,
    )
    try:
        result = await process_vapi_call_event(pool, payload)
        return result

    except (InvalidVapiEventPayloadError, UnsupportedVapiEventTypeError) as exc:
        logger.warning("Invalid Vapi call event payload: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Unexpected error processing Vapi call event")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error processing Vapi call event: {exc}",
        )
