"""
Webhook signature FastAPI dependencies — PraxisMed Sprint 5 / Module 46

Provides FastAPI dependency functions that read the raw request body and
verify HMAC-SHA256 webhook signatures for each supported provider.

These dependencies are NOT yet applied to existing webhook routes.
Route-by-route enforcement is Module 47.
"""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request

from backend.app.core.webhook_signature import (
    InvalidWebhookSignatureError,
    MissingWebhookSecretError,
    WebhookSignatureError,
    verify_provider_webhook_signature,
)


# ---------------------------------------------------------------------------
# 1. get_raw_request_body
# ---------------------------------------------------------------------------


async def get_raw_request_body(request: Request) -> bytes:
    """FastAPI dependency — return the raw request body as bytes."""
    return await request.body()


# ---------------------------------------------------------------------------
# 2. verify_vapi_webhook_signature_dependency
# ---------------------------------------------------------------------------


async def verify_vapi_webhook_signature_dependency(
    request: Request,
    x_vapi_signature: str | None = Header(default=None, alias="X-Vapi-Signature"),
) -> bool:
    """FastAPI dependency — verify a Vapi webhook HMAC-SHA256 signature.

    HTTP 503  when the VAPI_WEBHOOK_SECRET env var is not configured.
    HTTP 401  when the signature is missing or does not match.
    """
    body = await get_raw_request_body(request)
    try:
        return verify_provider_webhook_signature(
            provider="vapi",
            payload_body=body,
            signature_header=x_vapi_signature,
        )
    except MissingWebhookSecretError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (InvalidWebhookSignatureError, WebhookSignatureError) as exc:
        raise HTTPException(status_code=401, detail=str(exc))


# ---------------------------------------------------------------------------
# 3. verify_n8n_webhook_signature_dependency
# ---------------------------------------------------------------------------


async def verify_n8n_webhook_signature_dependency(
    request: Request,
    x_n8n_signature: str | None = Header(default=None, alias="X-N8N-Signature"),
) -> bool:
    """FastAPI dependency — verify an n8n webhook HMAC-SHA256 signature.

    HTTP 503  when the N8N_WEBHOOK_SECRET env var is not configured.
    HTTP 401  when the signature is missing or does not match.
    """
    body = await get_raw_request_body(request)
    try:
        return verify_provider_webhook_signature(
            provider="n8n",
            payload_body=body,
            signature_header=x_n8n_signature,
        )
    except MissingWebhookSecretError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (InvalidWebhookSignatureError, WebhookSignatureError) as exc:
        raise HTTPException(status_code=401, detail=str(exc))


# ---------------------------------------------------------------------------
# 4. verify_internal_webhook_signature_dependency
# ---------------------------------------------------------------------------


async def verify_internal_webhook_signature_dependency(
    request: Request,
    x_internal_signature: str | None = Header(default=None, alias="X-Internal-Signature"),
) -> bool:
    """FastAPI dependency — verify an internal webhook HMAC-SHA256 signature.

    HTTP 503  when the INTERNAL_WEBHOOK_SECRET env var is not configured.
    HTTP 401  when the signature is missing or does not match.
    """
    body = await get_raw_request_body(request)
    try:
        return verify_provider_webhook_signature(
            provider="internal",
            payload_body=body,
            signature_header=x_internal_signature,
        )
    except MissingWebhookSecretError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (InvalidWebhookSignatureError, WebhookSignatureError) as exc:
        raise HTTPException(status_code=401, detail=str(exc))
