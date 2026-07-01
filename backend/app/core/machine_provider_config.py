"""
Machine auth provider header compatibility configuration — PraxisMed Sprint 6 / Module 54

Stores accepted machine auth header aliases per provider and provides helpers
to extract service_name, clinic_id, and scopes from real request headers
regardless of which accepted alias the external service uses.

No FastAPI imports. No database usage. No real secrets stored here.
Safe to import in tests without side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

ALLOWED_MACHINE_PROVIDERS = {"vapi", "n8n", "internal"}

_ALLOWED_FIELDS = {"service_name", "clinic_id", "scopes"}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class MachineProviderConfigError(RuntimeError):
    """Base class for machine provider config errors."""


class InvalidMachineProviderConfigError(MachineProviderConfigError):
    """Raised for invalid config values or conflicting header aliases."""


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------


@dataclass
class MachineProviderConfig:
    """Declarative config for a single provider's machine auth header aliases.

    Fields:
        provider                  Validated provider name (vapi | n8n | internal).
        service_name_header_names Ordered tuple of accepted service-name header aliases.
        clinic_id_header_names    Ordered tuple of accepted clinic-id header aliases.
        scopes_header_names       Ordered tuple of accepted scopes header aliases.
    """

    provider: str
    service_name_header_names: tuple[str, ...]
    clinic_id_header_names: tuple[str, ...]
    scopes_header_names: tuple[str, ...]

    def __post_init__(self) -> None:
        # Validate and normalise provider
        if not self.provider or not str(self.provider).strip():
            raise InvalidMachineProviderConfigError("provider must not be empty")
        normalised = self.provider.strip().lower()
        if normalised not in ALLOWED_MACHINE_PROVIDERS:
            raise InvalidMachineProviderConfigError(
                f"Unknown machine provider {normalised!r}. "
                f"Allowed: {sorted(ALLOWED_MACHINE_PROVIDERS)}"
            )
        self.provider = normalised

        # Normalise and validate each header names tuple
        for attr in (
            "service_name_header_names",
            "clinic_id_header_names",
            "scopes_header_names",
        ):
            val = getattr(self, attr)
            if isinstance(val, list):
                val = tuple(val)
                setattr(self, attr, val)
            if not val:
                raise InvalidMachineProviderConfigError(
                    f"{attr} must not be empty"
                )
            for name in val:
                if not name or not str(name).strip():
                    raise InvalidMachineProviderConfigError(
                        f"{attr} must not contain empty strings"
                    )


# ---------------------------------------------------------------------------
# Default provider configs
# ---------------------------------------------------------------------------

_DEFAULT_CONFIGS: dict[str, MachineProviderConfig] = {
    "vapi": MachineProviderConfig(
        provider="vapi",
        service_name_header_names=(
            "X-Service-Name",
            "X-Vapi-Service-Name",
            "X-Provider-Name",
        ),
        clinic_id_header_names=(
            "X-Service-Clinic-Id",
            "X-Vapi-Clinic-Id",
            "X-Clinic-Id",
        ),
        scopes_header_names=(
            "X-Service-Scopes",
            "X-Vapi-Scopes",
            "X-Provider-Scopes",
        ),
    ),
    "n8n": MachineProviderConfig(
        provider="n8n",
        service_name_header_names=(
            "X-Service-Name",
            "X-N8N-Service-Name",
            "X-N8n-Service-Name",
            "X-Provider-Name",
        ),
        clinic_id_header_names=(
            "X-Service-Clinic-Id",
            "X-N8N-Clinic-Id",
            "X-N8n-Clinic-Id",
            "X-Clinic-Id",
        ),
        scopes_header_names=(
            "X-Service-Scopes",
            "X-N8N-Scopes",
            "X-N8n-Scopes",
            "X-Provider-Scopes",
        ),
    ),
    "internal": MachineProviderConfig(
        provider="internal",
        service_name_header_names=(
            "X-Service-Name",
            "X-Internal-Service-Name",
            "X-Provider-Name",
        ),
        clinic_id_header_names=(
            "X-Service-Clinic-Id",
            "X-Internal-Clinic-Id",
            "X-Clinic-Id",
        ),
        scopes_header_names=(
            "X-Service-Scopes",
            "X-Internal-Scopes",
            "X-Provider-Scopes",
        ),
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalize_machine_provider(provider: str) -> str:
    """Validate and return a normalised machine provider name.

    Raises InvalidMachineProviderConfigError for unknown providers.
    """
    if not provider or not str(provider).strip():
        raise InvalidMachineProviderConfigError("provider must not be empty")
    normalised = provider.strip().lower()
    if normalised not in ALLOWED_MACHINE_PROVIDERS:
        raise InvalidMachineProviderConfigError(
            f"Unknown machine provider {normalised!r}. "
            f"Allowed: {sorted(ALLOWED_MACHINE_PROVIDERS)}"
        )
    return normalised


def get_default_machine_provider_config(provider: str) -> MachineProviderConfig:
    """Return the default MachineProviderConfig for *provider*.

    Raises InvalidMachineProviderConfigError for unknown providers.
    """
    normalised = normalize_machine_provider(provider)
    return _DEFAULT_CONFIGS[normalised]


def get_machine_header_names(provider: str, field: str) -> tuple[str, ...]:
    """Return the accepted header aliases for *field* of *provider*.

    *field* must be one of: service_name, clinic_id, scopes.
    Raises InvalidMachineProviderConfigError for invalid field names.
    """
    if field not in _ALLOWED_FIELDS:
        raise InvalidMachineProviderConfigError(
            f"Invalid field {field!r}. Allowed: {sorted(_ALLOWED_FIELDS)}"
        )
    config = get_default_machine_provider_config(provider)
    field_map = {
        "service_name": config.service_name_header_names,
        "clinic_id": config.clinic_id_header_names,
        "scopes": config.scopes_header_names,
    }
    return field_map[field]


def extract_machine_header_value(headers, provider: str, field: str) -> Optional[str]:
    """Extract the value of a single machine auth field from *headers*.

    Performs case-insensitive matching against the provider's accepted header
    aliases for *field*, in priority order.

    Returns the first matching non-empty value, or None if no alias is present.
    Raises InvalidMachineProviderConfigError when multiple accepted aliases are
    present with conflicting (different) values.
    """
    header_names = get_machine_header_names(provider, field)

    found_values: dict[str, str] = {}  # lower_header_name -> value
    for accepted_name in header_names:
        accepted_lower = accepted_name.lower()
        if accepted_lower in found_values:
            # Alias shares a lowercase form with a previously resolved alias
            # (e.g. X-N8N-Clinic-Id and X-N8n-Clinic-Id).
            continue
        for key, value in headers.items():
            if key.lower() == accepted_lower and value:
                found_values[accepted_lower] = value
                break

    if not found_values:
        return None

    unique_values = set(found_values.values())
    if len(unique_values) > 1:
        raise InvalidMachineProviderConfigError(
            f"Multiple accepted '{field}' headers for provider {provider!r} "
            "found with conflicting values. Send only one alias per field."
        )

    # Return first match in priority order.
    for accepted_name in header_names:
        accepted_lower = accepted_name.lower()
        if accepted_lower in found_values:
            return found_values[accepted_lower]

    return None  # unreachable


def extract_machine_auth_headers(headers, provider: str) -> dict[str, Optional[str]]:
    """Extract all three machine auth field values from *headers* for *provider*.

    Returns::

        {
            "service_name": str | None,
            "clinic_id":    str | None,
            "scopes":       str | None,
        }
    """
    return {
        "service_name": extract_machine_header_value(headers, provider, "service_name"),
        "clinic_id":    extract_machine_header_value(headers, provider, "clinic_id"),
        "scopes":       extract_machine_header_value(headers, provider, "scopes"),
    }
