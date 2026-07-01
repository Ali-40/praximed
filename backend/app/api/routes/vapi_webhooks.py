"""
Vapi call event webhook route — PraxisMed Sprint 1 / Module 14

Exposes one endpoint:

    POST /webhooks/vapi/call-event

Vapi posts a JSON body whenever a call event occurs (call started, ended,
transcript ready, human handoff required, etc.).  The route validates the
HMAC-SHA256 webhook signature (Module 47) and the machine auth context, then
delegates to the event handler and returns the service result as JSON.

Webhook security
----------------
Signature verification:  HMAC-SHA256 over the raw request body using
``VAPI_WEBHOOK_SECRET``.

  • Missing or invalid ``X-Vapi-Signature`` → HTTP 401.
  • ``VAPI_WEBHOOK_SECRET`` not configured → HTTP 503.

Machine auth:  ``X-Service-Name``, ``X-Service-Clinic-Id``, ``X-Service-Scopes``
headers are validated by the machine auth dependency.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.api.dependencies.machine_auth import (
    get_machine_auth_context,
    require_vapi_webhook_access,
)
from backend.app.api.dependencies.webhook_signature import (
    verify_vapi_webhook_signature_dependency,
)
from backend.app.api.deps import get_db_pool
from backend.app.core.machine_auth import MachineAuthContext
from backend.app.modules.audit import audit_logger
from backend.app.modules.vapi.vapi_event_handler import (
    InvalidVapiEventPayloadError,
    UnsupportedVapiEventTypeError,
    process_vapi_call_event,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["vapi-webhooks"])


@router.post("/vapi/call-event")
async def vapi_call_event(
    payload: Dict[str, Any],
    pool: Any = Depends(get_db_pool),
    _sig: bool = Depends(verify_vapi_webhook_signature_dependency),
    machine_auth: MachineAuthContext = Depends(get_machine_auth_context),
) -> Dict[str, Any]:
    """
    Receive a Vapi call event and persist it via the call event handler.

    Error mapping
    -------------
    400  Invalid or unsupported payload.
    401  Missing/invalid Vapi signature or missing machine auth.
    403  Machine service or scope not permitted.
    500  Unexpected error in the event handler.
    503  VAPI_WEBHOOK_SECRET not configured or DB pool not initialised.
    """
    require_vapi_webhook_access(
        requested_clinic_id=payload.get("clinic_id"),
        machine_context=machine_auth,
    )
    try:
        result = await process_vapi_call_event(pool, payload)
        await audit_logger.safe_record_audit_event(
            pool,
            audit_logger.build_machine_audit_event(
                machine_auth,
                action="vapi.call_event",
                resource_type="clinic_call_logs",
                clinic_id=payload.get("clinic_id"),
                resource_id=result.get("call_id"),
                severity="warning" if result.get("action_required") else "info",
                metadata={
                    "route": "vapi_call_event",
                    "event_type": payload.get("event_type"),
                },
            ),
        )
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
