"""
Webhook signature FastAPI dependencies — PraxisMed Sprint 5 / Module 46
Updated: Sprint 6 / Module 53 — accept provider-specific signature header aliases

Provides FastAPI dependency functions that read the raw request body and
verify HMAC-SHA256 webhook signatures for each supported provider.

Header extraction is now alias-aware: each dependency accepts any of the
headers listed in the provider's WebhookProviderConfig.signature_header_names.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

from backend.app.core.webhook_provider_config import (
    InvalidWebhookProviderConfigError,
    extract_signature_from_headers,
    get_provider_secret_from_env,
)
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
) -> bool:
    """FastAPI dependency — verify a Vapi webhook HMAC-SHA256 signature.

    Accepted signature headers (in priority order):
      X-Vapi-Signature, X-Vapi-Hmac-Sha256, X-Signature

    HTTP 503  when VAPI_WEBHOOK_SECRET is not configured.
    HTTP 401  when the signature is missing, conflicting, or does not match.
    """
    body = await get_raw_request_body(request)
    try:
        signature = extract_signature_from_headers(request.headers, "vapi")
        secret = get_provider_secret_from_env("vapi")
        return verify_provider_webhook_signature(
            provider="vapi",
            payload_body=body,
            signature_header=signature,
            secret=secret,
        )
    except MissingWebhookSecretError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (
        InvalidWebhookProviderConfigError,
        InvalidWebhookSignatureError,
        WebhookSignatureError,
    ) as exc:
        raise HTTPException(status_code=401, detail=str(exc))


# ---------------------------------------------------------------------------
# 3. verify_n8n_webhook_signature_dependency
# ---------------------------------------------------------------------------


async def verify_n8n_webhook_signature_dependency(
    request: Request,
) -> bool:
    """FastAPI dependency — verify an n8n webhook HMAC-SHA256 signature.

    Accepted signature headers (in priority order):
      X-N8N-Signature, X-N8n-Signature, X-Signature

    HTTP 503  when N8N_WEBHOOK_SECRET is not configured.
    HTTP 401  when the signature is missing, conflicting, or does not match.
    """
    body = await get_raw_request_body(request)
    try:
        signature = extract_signature_from_headers(request.headers, "n8n")
        secret = get_provider_secret_from_env("n8n")
        return verify_provider_webhook_signature(
            provider="n8n",
            payload_body=body,
            signature_header=signature,
            secret=secret,
        )
    except MissingWebhookSecretError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (
        InvalidWebhookProviderConfigError,
        InvalidWebhookSignatureError,
        WebhookSignatureError,
    ) as exc:
        raise HTTPException(status_code=401, detail=str(exc))


# ---------------------------------------------------------------------------
# 4. verify_internal_webhook_signature_dependency
# ---------------------------------------------------------------------------


async def verify_internal_webhook_signature_dependency(
    request: Request,
) -> bool:
    """FastAPI dependency — verify an internal webhook HMAC-SHA256 signature.

    Accepted signature headers (in priority order):
      X-Internal-Signature, X-Signature

    HTTP 503  when INTERNAL_WEBHOOK_SECRET is not configured.
    HTTP 401  when the signature is missing, conflicting, or does not match.
    """
    body = await get_raw_request_body(request)
    try:
        signature = extract_signature_from_headers(request.headers, "internal")
        secret = get_provider_secret_from_env("internal")
        return verify_provider_webhook_signature(
            provider="internal",
            payload_body=body,
            signature_header=signature,
            secret=secret,
        )
    except MissingWebhookSecretError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (
        InvalidWebhookProviderConfigError,
        InvalidWebhookSignatureError,
        WebhookSignatureError,
    ) as exc:
        raise HTTPException(status_code=401, detail=str(exc))
