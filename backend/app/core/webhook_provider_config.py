"""
Webhook provider header compatibility configuration — PraxisMed Sprint 6 / Module 53

Stores accepted signature header aliases per provider and provides helpers
to extract the signature from real request headers regardless of which
accepted alias the external service uses.

No FastAPI imports. No database usage. No real secrets stored here.
Safe to import in tests without side effects.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from backend.app.core.webhook_signature import (
    MissingWebhookSecretError,
    WebhookSignatureError,
    normalize_webhook_provider,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class WebhookProviderConfigError(RuntimeError):
    """Base class for webhook provider config errors."""


class InvalidWebhookProviderConfigError(WebhookProviderConfigError):
    """Raised when a WebhookProviderConfig has invalid field values, or when
    multiple accepted signature headers are found with conflicting values."""


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------


@dataclass
class WebhookProviderConfig:
    """Declarative config for a single webhook provider's signature convention.

    Fields:
        provider                  Validated provider name (vapi | n8n | internal).
        signature_header_names    Ordered tuple of accepted header aliases (first
                                  takes priority when multiple are present with the
                                  same value).
        signature_env_var         Name of the env var that holds the HMAC secret.
        algorithm                 Must be "hmac-sha256" (only supported value).
        accepted_signature_prefixes
                                  Must include "sha256=" or "" so at least one
                                  standard format is accepted.
    """

    provider: str
    signature_header_names: tuple[str, ...]
    signature_env_var: str
    algorithm: str = "hmac-sha256"
    accepted_signature_prefixes: tuple[str, ...] = ("sha256=", "")

    def __post_init__(self) -> None:
        # Validate and normalise provider
        try:
            self.provider = normalize_webhook_provider(self.provider)
        except WebhookSignatureError as exc:
            raise InvalidWebhookProviderConfigError(str(exc)) from exc

        # Normalise and validate signature_header_names
        if isinstance(self.signature_header_names, list):
            self.signature_header_names = tuple(self.signature_header_names)
        if not self.signature_header_names:
            raise InvalidWebhookProviderConfigError(
                "signature_header_names must not be empty"
            )
        for name in self.signature_header_names:
            if not name or not str(name).strip():
                raise InvalidWebhookProviderConfigError(
                    "signature_header_names must not contain empty strings"
                )

        # Validate signature_env_var
        if not self.signature_env_var or not str(self.signature_env_var).strip():
            raise InvalidWebhookProviderConfigError(
                "signature_env_var must not be empty"
            )

        # Validate algorithm
        if self.algorithm != "hmac-sha256":
            raise InvalidWebhookProviderConfigError(
                f"Unsupported algorithm {self.algorithm!r}. "
                "Only 'hmac-sha256' is supported."
            )

        # Normalise and validate accepted_signature_prefixes
        if isinstance(self.accepted_signature_prefixes, list):
            self.accepted_signature_prefixes = tuple(self.accepted_signature_prefixes)
        if (
            "sha256=" not in self.accepted_signature_prefixes
            and "" not in self.accepted_signature_prefixes
        ):
            raise InvalidWebhookProviderConfigError(
                "accepted_signature_prefixes must include 'sha256=' or ''"
            )


# ---------------------------------------------------------------------------
# Default provider configs
# ---------------------------------------------------------------------------

_DEFAULT_CONFIGS: dict[str, WebhookProviderConfig] = {
    "vapi": WebhookProviderConfig(
        provider="vapi",
        signature_env_var="VAPI_WEBHOOK_SECRET",
        signature_header_names=(
            "X-Vapi-Signature",
            "X-Vapi-Hmac-Sha256",
            "X-Signature",
        ),
    ),
    "n8n": WebhookProviderConfig(
        provider="n8n",
        signature_env_var="N8N_WEBHOOK_SECRET",
        signature_header_names=(
            "X-N8N-Signature",
            "X-N8n-Signature",
            "X-Signature",
        ),
    ),
    "internal": WebhookProviderConfig(
        provider="internal",
        signature_env_var="INTERNAL_WEBHOOK_SECRET",
        signature_header_names=(
            "X-Internal-Signature",
            "X-Signature",
        ),
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_default_provider_config(provider: str) -> WebhookProviderConfig:
    """Return the default WebhookProviderConfig for *provider*.

    Raises InvalidWebhookProviderConfigError for unknown providers.
    """
    try:
        normalised = normalize_webhook_provider(provider)
    except WebhookSignatureError as exc:
        raise InvalidWebhookProviderConfigError(str(exc)) from exc
    if normalised not in _DEFAULT_CONFIGS:
        raise InvalidWebhookProviderConfigError(
            f"No default config for provider {normalised!r}"
        )
    return _DEFAULT_CONFIGS[normalised]


def get_signature_header_names(provider: str) -> tuple[str, ...]:
    """Return the accepted signature header names for *provider*."""
    return get_default_provider_config(provider).signature_header_names


def get_signature_env_var(provider: str) -> str:
    """Return the env var name that holds the secret for *provider*."""
    return get_default_provider_config(provider).signature_env_var


def extract_signature_from_headers(headers, provider: str) -> Optional[str]:
    """Extract the webhook signature from *headers* for *provider*.

    Performs case-insensitive matching against the provider's accepted
    signature header names in priority order.

    Returns the signature string (with or without "sha256=" prefix), or
    None when no accepted header is present.

    Raises InvalidWebhookProviderConfigError when multiple accepted
    headers are present with conflicting (different) values.
    """
    config = get_default_provider_config(provider)

    # Map each accepted header name (lowercased) to its value in the request.
    found_values: dict[str, str] = {}
    for accepted_name in config.signature_header_names:
        accepted_lower = accepted_name.lower()
        if accepted_lower in found_values:
            # Already resolved (e.g. X-N8N-Signature and X-N8n-Signature share
            # the same lowercase form — they match the same request header).
            continue
        for key, value in headers.items():
            if key.lower() == accepted_lower and value:
                found_values[accepted_lower] = value
                break

    if not found_values:
        return None

    unique_values = set(found_values.values())
    if len(unique_values) > 1:
        raise InvalidWebhookProviderConfigError(
            f"Multiple accepted signature headers for provider {provider!r} "
            "were found with conflicting values. "
            "Send only one signature header per request."
        )

    # Return first match in priority order.
    for accepted_name in config.signature_header_names:
        accepted_lower = accepted_name.lower()
        if accepted_lower in found_values:
            return found_values[accepted_lower]

    return None  # unreachable


def get_provider_secret_from_env(provider: str) -> str:
    """Read the HMAC secret for *provider* from the environment.

    Uses the provider's configured signature_env_var.
    Raises MissingWebhookSecretError when the variable is absent or empty.
    """
    config = get_default_provider_config(provider)
    env_var = config.signature_env_var
    secret = os.environ.get(env_var, "")
    if not secret or not secret.strip():
        raise MissingWebhookSecretError(
            f"Webhook secret for provider {provider!r} is not configured. "
            f"Set the {env_var!r} environment variable."
        )
    return secret.strip()
