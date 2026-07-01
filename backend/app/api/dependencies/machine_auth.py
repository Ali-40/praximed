"""
Machine/internal auth FastAPI dependencies — PraxisMed Sprint 3 / Module 39
Updated: Sprint 6 / Module 54 — accept provider-specific machine auth header aliases

Provides get_machine_auth_context and require_* helpers for machine-to-machine
route protection.

Header extraction is now alias-aware: get_machine_auth_context reads the service
name from any configured alias across all providers, then uses that provider's
config to extract clinic_id and scopes.

Original canonical headers remain fully supported:
  X-Service-Name, X-Service-Clinic-Id, X-Service-Scopes
"""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, Request

from backend.app.core.machine_auth import (
    InvalidMachineAuthHeaderError,
    MachineAccessDeniedError,
    MachineAuthContext,
    MachineAuthError,
    authorize_machine_access,
    build_machine_auth_context_from_headers,
)
from backend.app.core.machine_provider_config import (
    ALLOWED_MACHINE_PROVIDERS,
    InvalidMachineProviderConfigError,
    extract_machine_auth_headers,
    get_default_machine_provider_config,
    normalize_machine_provider,
)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _get_header_case_insensitive(headers, name: str) -> Optional[str]:
    """Return the first non-empty value for *name* (case-insensitive) or None."""
    name_lower = name.lower()
    for key, value in headers.items():
        if key.lower() == name_lower and value:
            return value
    return None


def _extract_service_name_universal(headers) -> Optional[str]:
    """Search every provider's service_name aliases to find the service name.

    Returns the service name string, or None if no alias is present.
    Raises InvalidMachineProviderConfigError when multiple aliases are present
    with conflicting (different) values.
    """
    # Collect the deduplicated union of all service_name aliases across providers.
    all_aliases_lower: dict[str, str] = {}  # lower_alias -> canonical alias
    for provider_name in sorted(ALLOWED_MACHINE_PROVIDERS):
        config = get_default_machine_provider_config(provider_name)
        for alias in config.service_name_header_names:
            alias_lower = alias.lower()
            if alias_lower not in all_aliases_lower:
                all_aliases_lower[alias_lower] = alias

    # Scan request headers for any of the collected aliases.
    found_values: dict[str, str] = {}  # lower_alias -> value
    for key, value in headers.items():
        key_lower = key.lower()
        if key_lower in all_aliases_lower and value:
            found_values[key_lower] = value

    if not found_values:
        return None

    unique_values = set(found_values.values())
    if len(unique_values) > 1:
        raise InvalidMachineProviderConfigError(
            "Multiple service name headers found with conflicting values. "
            "Send only one service name header per request."
        )
    return next(iter(found_values.values()))


# ---------------------------------------------------------------------------
# 1. get_machine_auth_context
# ---------------------------------------------------------------------------


async def get_machine_auth_context(request: Request) -> MachineAuthContext:
    """FastAPI dependency — build MachineAuthContext from alias-aware headers.

    Accepted service-name headers (checked across all providers):
      X-Service-Name, X-Vapi-Service-Name, X-N8N-Service-Name,
      X-Internal-Service-Name, X-Provider-Name

    For recognised providers (vapi, n8n, internal) the full set of clinic_id
    and scopes aliases is also accepted.  For service names outside the alias
    config (e.g. "system", "dashboard") the canonical headers are used as
    fallback.

    HTTP 401  for missing/invalid/conflicting machine auth headers.
    """
    headers = request.headers
    try:
        # Step 1: Find service name from any provider alias.
        service_name_raw = _extract_service_name_universal(headers)
        if service_name_raw is None:
            raise InvalidMachineAuthHeaderError(
                "Missing required header: 'X-Service-Name' or equivalent alias"
            )

        # Step 2: Attempt to resolve provider-specific aliases for clinic/scopes.
        try:
            provider = normalize_machine_provider(service_name_raw)
        except InvalidMachineProviderConfigError:
            # Service name is valid in machine_auth (e.g. "system", "dashboard")
            # but has no alias config.  Fall back to canonical headers.
            provider = None

        if provider is not None:
            extracted = extract_machine_auth_headers(headers, provider)
            clinic_id  = extracted["clinic_id"]
            scopes_str = extracted["scopes"]
        else:
            clinic_id  = _get_header_case_insensitive(headers, "X-Service-Clinic-Id")
            scopes_str = _get_header_case_insensitive(headers, "X-Service-Scopes")

        return build_machine_auth_context_from_headers(
            service_name=service_name_raw.strip(),
            clinic_id=clinic_id,
            scopes=scopes_str,
        )

    except InvalidMachineProviderConfigError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except (InvalidMachineAuthHeaderError, MachineAuthError) as exc:
        raise HTTPException(status_code=401, detail=str(exc))


# ---------------------------------------------------------------------------
# 2. require_machine_access
# ---------------------------------------------------------------------------


def require_machine_access(
    machine_context: MachineAuthContext,
    allowed_services: set,
    required_scope: Optional[str] = None,
    requested_clinic_id: Optional[str] = None,
) -> MachineAuthContext:
    try:
        return authorize_machine_access(
            machine_context=machine_context,
            allowed_services=allowed_services,
            required_scope=required_scope,
            requested_clinic_id=requested_clinic_id,
        )
    except MachineAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


# ---------------------------------------------------------------------------
# 3. require_vapi_tool_access
# ---------------------------------------------------------------------------


def require_vapi_tool_access(
    requested_clinic_id: str,
    machine_context: MachineAuthContext,
) -> MachineAuthContext:
    return require_machine_access(
        machine_context=machine_context,
        allowed_services={"vapi", "internal", "system"},
        required_scope="vapi:tool",
        requested_clinic_id=requested_clinic_id,
    )


# ---------------------------------------------------------------------------
# 4. require_vapi_webhook_access
# ---------------------------------------------------------------------------


def require_vapi_webhook_access(
    requested_clinic_id: Optional[str],
    machine_context: MachineAuthContext,
) -> MachineAuthContext:
    return require_machine_access(
        machine_context=machine_context,
        allowed_services={"vapi", "internal", "system"},
        required_scope="vapi:webhook",
        requested_clinic_id=requested_clinic_id,
    )


# ---------------------------------------------------------------------------
# 5. require_n8n_calendar_sync_access
# ---------------------------------------------------------------------------


def require_n8n_calendar_sync_access(
    requested_clinic_id: str,
    machine_context: MachineAuthContext,
) -> MachineAuthContext:
    return require_machine_access(
        machine_context=machine_context,
        allowed_services={"n8n", "internal", "system"},
        required_scope="calendar:sync",
        requested_clinic_id=requested_clinic_id,
    )


# ---------------------------------------------------------------------------
# 6. require_availability_read_access
# ---------------------------------------------------------------------------


def require_availability_read_access(
    requested_clinic_id: str,
    machine_context: MachineAuthContext,
) -> MachineAuthContext:
    return require_machine_access(
        machine_context=machine_context,
        allowed_services={"vapi", "internal", "system", "dashboard"},
        required_scope="availability:read",
        requested_clinic_id=requested_clinic_id,
    )
