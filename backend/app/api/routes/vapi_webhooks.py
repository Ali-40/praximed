"""
Vapi call event webhook route — PraxisMed Sprint 1 / Module 14
Updated: Sprint 6 / Module 56 — real Vapi payload compatibility adapter

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

Payload adapter (Module 56)
---------------------------
The route accepts two payload shapes:

  • Internal/local shape: clinic_id, call_id, event_type at root.
  • Real Vapi server shape: {"message": {"type": ..., "call": {"id": ...}}}.

The adapter fills missing root fields from machine auth and request headers
before delegating to the event handler.  HMAC and machine auth enforcement
are unchanged.
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

# ---------------------------------------------------------------------------
# Real Vapi server message.type → internal event type mapping
# ---------------------------------------------------------------------------

_VAPI_MESSAGE_TYPE_MAP: Dict[str, str] = {
    "assistant-started":  "call.started",
    "end-of-call-report": "call.ended",
    "transcript":         "transcript.ready",
    "summary":            "summary.ready",
    "hang":               "call.ended",
}


def _adapt_vapi_payload(
    payload: Dict[str, Any],
    machine_auth: MachineAuthContext,
    request_headers: Any,
) -> Dict[str, Any]:
    """
    Normalize real Vapi server payloads to the internal shape expected by
    process_vapi_call_event.

    Real Vapi payloads use {"message": {"type": ..., "call": {"id": ...}}}
    and omit clinic_id, event_type, and call_id at the root.

    Fallback priority
    -----------------
    clinic_id  — body → machine auth context clinic_id
    event_type — body → message.type (mapped to internal name)
    call_id    — body → message.call.id → message.callId
                 → X-Call-Id header → "unknown-vapi-call"
    """
    message = payload.get("message") or {}
    call_obj = message.get("call") or {}

    clinic_id = payload.get("clinic_id") or machine_auth.clinic_id

    event_type = payload.get("event_type")
    if not event_type:
        raw_type = str(message.get("type") or "")
        event_type = _VAPI_MESSAGE_TYPE_MAP.get(raw_type, raw_type) if raw_type else None

    call_id = (
        payload.get("call_id")
        or call_obj.get("id")
        or message.get("callId")
        or request_headers.get("x-call-id")
        or "unknown-vapi-call"
    )

    return {**payload, "clinic_id": clinic_id, "event_type": event_type, "call_id": call_id}


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@router.post("/vapi/call-event")
async def vapi_call_event(
    request: Request,
    payload: Dict[str, Any],
    pool: Any = Depends(get_db_pool),
    _sig: bool = Depends(verify_vapi_webhook_signature_dependency),
    machine_auth: MachineAuthContext = Depends(get_machine_auth_context),
) -> Dict[str, Any]:
    """
    Receive a Vapi call event and persist it via the call event handler.

    Accepts both local/internal payload shapes and real Vapi server payloads.
    Missing root fields (clinic_id, event_type, call_id) are resolved via
    machine auth context and request headers before delegation.

    Error mapping
    -------------
    400  Invalid or unsupported payload.
    401  Missing/invalid Vapi signature or missing machine auth.
    403  Machine service or scope not permitted.
    500  Unexpected error in the event handler.
    503  VAPI_WEBHOOK_SECRET not configured or DB pool not initialised.
    """
    adapted = _adapt_vapi_payload(payload, machine_auth, request.headers)
    require_vapi_webhook_access(
        requested_clinic_id=adapted.get("clinic_id"),
        machine_context=machine_auth,
    )
    try:
        result = await process_vapi_call_event(pool, adapted)
        await audit_logger.safe_record_audit_event(
            pool,
            audit_logger.build_machine_audit_event(
                machine_auth,
                action="vapi.call_event",
                resource_type="clinic_call_logs",
                clinic_id=adapted.get("clinic_id"),
                resource_id=result.get("call_id"),
                severity="warning" if result.get("action_required") else "info",
                metadata={
                    "route": "vapi_call_event",
                    "event_type": adapted.get("event_type"),
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
