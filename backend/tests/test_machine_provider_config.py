"""
Unit tests for machine provider config — PraxisMed Sprint 6 / Module 54

Strategy:
- No FastAPI imports.
- No database connection.
- No external service calls.
"""

from __future__ import annotations

import pytest

from backend.app.core.machine_provider_config import (
    InvalidMachineProviderConfigError,
    MachineProviderConfig,
    extract_machine_auth_headers,
    extract_machine_header_value,
    get_default_machine_provider_config,
    get_machine_header_names,
    normalize_machine_provider,
)


# ===========================================================================
# MachineProviderConfig validation (tests 1–7)
# ===========================================================================


def test_config_accepts_valid_vapi_config():
    """Test 1 — Valid vapi config is created without errors."""
    cfg = MachineProviderConfig(
        provider="vapi",
        service_name_header_names=("X-Service-Name",),
        clinic_id_header_names=("X-Service-Clinic-Id",),
        scopes_header_names=("X-Service-Scopes",),
    )
    assert cfg.provider == "vapi"


def test_config_rejects_empty_provider():
    """Test 2 — Empty provider raises InvalidMachineProviderConfigError."""
    with pytest.raises(InvalidMachineProviderConfigError):
        MachineProviderConfig(
            provider="",
            service_name_header_names=("X-Service-Name",),
            clinic_id_header_names=("X-Service-Clinic-Id",),
            scopes_header_names=("X-Service-Scopes",),
        )


def test_config_rejects_invalid_provider():
    """Test 3 — Unknown provider raises InvalidMachineProviderConfigError."""
    with pytest.raises(InvalidMachineProviderConfigError):
        MachineProviderConfig(
            provider="bogus-provider",
            service_name_header_names=("X-Service-Name",),
            clinic_id_header_names=("X-Service-Clinic-Id",),
            scopes_header_names=("X-Service-Scopes",),
        )


def test_config_rejects_empty_service_name_header_names():
    """Test 4 — Empty service_name_header_names raises InvalidMachineProviderConfigError."""
    with pytest.raises(InvalidMachineProviderConfigError):
        MachineProviderConfig(
            provider="vapi",
            service_name_header_names=(),
            clinic_id_header_names=("X-Service-Clinic-Id",),
            scopes_header_names=("X-Service-Scopes",),
        )


def test_config_rejects_empty_clinic_id_header_names():
    """Test 5 — Empty clinic_id_header_names raises InvalidMachineProviderConfigError."""
    with pytest.raises(InvalidMachineProviderConfigError):
        MachineProviderConfig(
            provider="vapi",
            service_name_header_names=("X-Service-Name",),
            clinic_id_header_names=(),
            scopes_header_names=("X-Service-Scopes",),
        )


def test_config_rejects_empty_scopes_header_names():
    """Test 6 — Empty scopes_header_names raises InvalidMachineProviderConfigError."""
    with pytest.raises(InvalidMachineProviderConfigError):
        MachineProviderConfig(
            provider="vapi",
            service_name_header_names=("X-Service-Name",),
            clinic_id_header_names=("X-Service-Clinic-Id",),
            scopes_header_names=(),
        )


def test_config_rejects_empty_string_header_name():
    """Test 7 — Empty string inside any header names tuple raises InvalidMachineProviderConfigError."""
    with pytest.raises(InvalidMachineProviderConfigError):
        MachineProviderConfig(
            provider="vapi",
            service_name_header_names=("X-Service-Name", ""),
            clinic_id_header_names=("X-Service-Clinic-Id",),
            scopes_header_names=("X-Service-Scopes",),
        )


# ===========================================================================
# normalize_machine_provider (tests 8–9)
# ===========================================================================


def test_normalize_machine_provider_trims_and_lowercases():
    """Test 8 — normalize_machine_provider strips and lowercases the input."""
    assert normalize_machine_provider("  VAPI  ") == "vapi"
    assert normalize_machine_provider("N8N") == "n8n"
    assert normalize_machine_provider("Internal") == "internal"


def test_normalize_machine_provider_rejects_unknown():
    """Test 9 — normalize_machine_provider raises for unknown provider."""
    with pytest.raises(InvalidMachineProviderConfigError):
        normalize_machine_provider("unknown")


# ===========================================================================
# get_default_machine_provider_config (tests 10–12)
# ===========================================================================


def test_get_default_machine_provider_config_returns_vapi():
    """Test 10 — Default vapi config has correct provider and env alias headers."""
    cfg = get_default_machine_provider_config("vapi")
    assert cfg.provider == "vapi"
    assert "X-Service-Name" in cfg.service_name_header_names
    assert "X-Vapi-Service-Name" in cfg.service_name_header_names
    assert "X-Service-Clinic-Id" in cfg.clinic_id_header_names
    assert "X-Vapi-Clinic-Id" in cfg.clinic_id_header_names


def test_get_default_machine_provider_config_returns_n8n():
    """Test 11 — Default n8n config has correct headers."""
    cfg = get_default_machine_provider_config("n8n")
    assert cfg.provider == "n8n"
    assert "X-Service-Name" in cfg.service_name_header_names
    assert "X-N8N-Service-Name" in cfg.service_name_header_names
    assert "X-N8N-Clinic-Id" in cfg.clinic_id_header_names


def test_get_default_machine_provider_config_returns_internal():
    """Test 12 — Default internal config has correct headers."""
    cfg = get_default_machine_provider_config("internal")
    assert cfg.provider == "internal"
    assert "X-Service-Name" in cfg.service_name_header_names
    assert "X-Internal-Service-Name" in cfg.service_name_header_names
    assert "X-Internal-Clinic-Id" in cfg.clinic_id_header_names


# ===========================================================================
# get_machine_header_names (tests 13–16)
# ===========================================================================


def test_get_machine_header_names_returns_service_name_aliases():
    """Test 13 — get_machine_header_names returns service_name aliases for vapi."""
    names = get_machine_header_names("vapi", "service_name")
    assert isinstance(names, tuple)
    assert "X-Service-Name" in names
    assert "X-Vapi-Service-Name" in names


def test_get_machine_header_names_returns_clinic_id_aliases():
    """Test 14 — get_machine_header_names returns clinic_id aliases for vapi."""
    names = get_machine_header_names("vapi", "clinic_id")
    assert isinstance(names, tuple)
    assert "X-Service-Clinic-Id" in names
    assert "X-Vapi-Clinic-Id" in names


def test_get_machine_header_names_returns_scopes_aliases():
    """Test 15 — get_machine_header_names returns scopes aliases for vapi."""
    names = get_machine_header_names("vapi", "scopes")
    assert isinstance(names, tuple)
    assert "X-Service-Scopes" in names
    assert "X-Vapi-Scopes" in names


def test_get_machine_header_names_rejects_invalid_field():
    """Test 16 — get_machine_header_names raises for unknown field name."""
    with pytest.raises(InvalidMachineProviderConfigError):
        get_machine_header_names("vapi", "password")


# ===========================================================================
# extract_machine_header_value (tests 17–22)
# ===========================================================================


def test_extract_reads_primary_header():
    """Test 17 — extract_machine_header_value reads X-Service-Name."""
    headers = {"X-Service-Name": "vapi"}
    assert extract_machine_header_value(headers, "vapi", "service_name") == "vapi"


def test_extract_reads_alias_header():
    """Test 18 — extract_machine_header_value reads X-Vapi-Clinic-Id alias."""
    headers = {"X-Vapi-Clinic-Id": "clinic-abc"}
    assert extract_machine_header_value(headers, "vapi", "clinic_id") == "clinic-abc"


def test_extract_is_case_insensitive():
    """Test 19 — extract_machine_header_value matches header names case-insensitively."""
    headers = {"x-service-name": "vapi"}
    assert extract_machine_header_value(headers, "vapi", "service_name") == "vapi"


def test_extract_returns_none_when_missing():
    """Test 20 — extract_machine_header_value returns None when no alias present."""
    headers = {"Authorization": "Bearer token"}
    assert extract_machine_header_value(headers, "vapi", "clinic_id") is None


def test_extract_allows_duplicate_same_value_aliases():
    """Test 21 — Two accepted aliases with identical value → returns that value."""
    headers = {
        "X-Service-Clinic-Id": "clinic-1",
        "X-Vapi-Clinic-Id": "clinic-1",
    }
    result = extract_machine_header_value(headers, "vapi", "clinic_id")
    assert result == "clinic-1"


def test_extract_rejects_duplicate_different_value_aliases():
    """Test 22 — Two accepted aliases with different values → raises."""
    headers = {
        "X-Service-Clinic-Id": "clinic-1",
        "X-Vapi-Clinic-Id": "clinic-2",
    }
    with pytest.raises(InvalidMachineProviderConfigError):
        extract_machine_header_value(headers, "vapi", "clinic_id")


# ===========================================================================
# extract_machine_auth_headers (test 23)
# ===========================================================================


def test_extract_machine_auth_headers_returns_full_dict():
    """Test 23 — extract_machine_auth_headers returns service_name/clinic_id/scopes dict."""
    headers = {
        "X-Service-Name": "vapi",
        "X-Service-Clinic-Id": "clinic-x",
        "X-Service-Scopes": "vapi:tool",
    }
    result = extract_machine_auth_headers(headers, "vapi")
    assert result["service_name"] == "vapi"
    assert result["clinic_id"] == "clinic-x"
    assert result["scopes"] == "vapi:tool"


# ===========================================================================
# Safety (test 24)
# ===========================================================================


def test_config_module_does_not_contain_secrets():
    """Test 24 — Config module source does not contain hardcoded secrets."""
    import backend.app.core.machine_provider_config as mod

    content = open(mod.__file__).read()
    for marker in ("sk-", "Bearer ", "password", "prod-secret", "real-secret"):
        assert marker not in content, (
            f"Possible secret marker {marker!r} found in machine_provider_config.py"
        )
