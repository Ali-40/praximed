"""
Tests for machine auth core — PraxisMed Sprint 3 / Module 39.

No real database. No external service calls.
"""

from __future__ import annotations

import pytest

from backend.app.core.machine_auth import (
    ALLOWED_SERVICE_SCOPES,
    DEFAULT_MACHINE_AUTH_SCHEME,
    InvalidMachineAuthHeaderError,
    MachineAccessDeniedError,
    MachineAuthContext,
    MachineAuthError,
    authorize_machine_access,
    build_machine_auth_context_from_headers,
    ensure_machine_clinic_access,
    ensure_machine_scope,
    ensure_machine_service_allowed,
    normalize_machine_header_value,
    parse_scope_header,
)

CLINIC_ID = "clinic-1"
OTHER_CLINIC_ID = "clinic-2"


# ---------------------------------------------------------------------------
# 1. MachineAuthContext accepts valid service_name
# ---------------------------------------------------------------------------


def test_machine_auth_context_valid_service_name():
    ctx = MachineAuthContext(service_name="vapi")
    assert ctx.service_name == "vapi"
    assert ctx.auth_scheme == DEFAULT_MACHINE_AUTH_SCHEME


# ---------------------------------------------------------------------------
# 2. MachineAuthContext accepts clinic_id
# ---------------------------------------------------------------------------


def test_machine_auth_context_accepts_clinic_id():
    ctx = MachineAuthContext(service_name="vapi", clinic_id=CLINIC_ID)
    assert ctx.clinic_id == CLINIC_ID


# ---------------------------------------------------------------------------
# 3. MachineAuthContext accepts valid scopes
# ---------------------------------------------------------------------------


def test_machine_auth_context_accepts_valid_scopes():
    ctx = MachineAuthContext(service_name="vapi", scopes={"vapi:tool", "availability:read"})
    assert "vapi:tool" in ctx.scopes
    assert "availability:read" in ctx.scopes


# ---------------------------------------------------------------------------
# 4. MachineAuthContext rejects empty service_name
# ---------------------------------------------------------------------------


def test_machine_auth_context_rejects_empty_service_name():
    with pytest.raises(InvalidMachineAuthHeaderError):
        MachineAuthContext(service_name="")


# ---------------------------------------------------------------------------
# 5. MachineAuthContext rejects invalid service_name
# ---------------------------------------------------------------------------


def test_machine_auth_context_rejects_invalid_service_name():
    with pytest.raises(InvalidMachineAuthHeaderError):
        MachineAuthContext(service_name="unknown-service")


# ---------------------------------------------------------------------------
# 6. MachineAuthContext rejects empty clinic_id when provided
# ---------------------------------------------------------------------------


def test_machine_auth_context_rejects_empty_clinic_id():
    with pytest.raises(InvalidMachineAuthHeaderError):
        MachineAuthContext(service_name="vapi", clinic_id="")


# ---------------------------------------------------------------------------
# 7. MachineAuthContext rejects non-set scopes
# ---------------------------------------------------------------------------


def test_machine_auth_context_rejects_non_set_scopes():
    with pytest.raises(InvalidMachineAuthHeaderError):
        MachineAuthContext(service_name="vapi", scopes=["vapi:tool"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 8. MachineAuthContext rejects unknown scope
# ---------------------------------------------------------------------------


def test_machine_auth_context_rejects_unknown_scope():
    with pytest.raises(InvalidMachineAuthHeaderError):
        MachineAuthContext(service_name="vapi", scopes={"not:a:real:scope"})


# ---------------------------------------------------------------------------
# 9. normalize_machine_header_value strips valid value
# ---------------------------------------------------------------------------


def test_normalize_machine_header_value_strips():
    result = normalize_machine_header_value("  vapi  ", "X-Service-Name")
    assert result == "vapi"


# ---------------------------------------------------------------------------
# 10. normalize_machine_header_value rejects None
# ---------------------------------------------------------------------------


def test_normalize_machine_header_value_rejects_none():
    with pytest.raises(InvalidMachineAuthHeaderError):
        normalize_machine_header_value(None, "X-Service-Name")


# ---------------------------------------------------------------------------
# 11. normalize_machine_header_value rejects empty string
# ---------------------------------------------------------------------------


def test_normalize_machine_header_value_rejects_empty():
    with pytest.raises(InvalidMachineAuthHeaderError):
        normalize_machine_header_value("   ", "X-Service-Name")


# ---------------------------------------------------------------------------
# 12. parse_scope_header returns empty set for None
# ---------------------------------------------------------------------------


def test_parse_scope_header_none_returns_empty_set():
    assert parse_scope_header(None) == set()


# ---------------------------------------------------------------------------
# 13. parse_scope_header parses comma-separated scopes
# ---------------------------------------------------------------------------


def test_parse_scope_header_parses_comma_separated():
    result = parse_scope_header("vapi:tool, availability:read")
    assert result == {"vapi:tool", "availability:read"}


# ---------------------------------------------------------------------------
# 14. parse_scope_header rejects unknown scope
# ---------------------------------------------------------------------------


def test_parse_scope_header_rejects_unknown():
    with pytest.raises(InvalidMachineAuthHeaderError):
        parse_scope_header("vapi:tool, not:known")


# ---------------------------------------------------------------------------
# 15. build_machine_auth_context_from_headers returns context
# ---------------------------------------------------------------------------


def test_build_machine_auth_context_from_headers_returns_context():
    ctx = build_machine_auth_context_from_headers(
        service_name="vapi",
        clinic_id=CLINIC_ID,
        scopes="vapi:tool",
    )
    assert ctx.service_name == "vapi"
    assert ctx.clinic_id == CLINIC_ID
    assert "vapi:tool" in ctx.scopes


# ---------------------------------------------------------------------------
# 16. build_machine_auth_context_from_headers rejects non-dict raw_claims
# ---------------------------------------------------------------------------


def test_build_machine_auth_context_rejects_non_dict_raw_claims():
    with pytest.raises(InvalidMachineAuthHeaderError):
        build_machine_auth_context_from_headers(
            service_name="vapi",
            raw_claims="not-a-dict",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# 17. ensure_machine_service_allowed passes allowed service
# ---------------------------------------------------------------------------


def test_ensure_machine_service_allowed_passes():
    ctx = MachineAuthContext(service_name="vapi", clinic_id=CLINIC_ID)
    ensure_machine_service_allowed(ctx, {"vapi", "internal"})  # should not raise


# ---------------------------------------------------------------------------
# 18. ensure_machine_service_allowed rejects disallowed service
# ---------------------------------------------------------------------------


def test_ensure_machine_service_allowed_rejects_disallowed():
    ctx = MachineAuthContext(service_name="n8n", clinic_id=CLINIC_ID)
    with pytest.raises(MachineAccessDeniedError):
        ensure_machine_service_allowed(ctx, {"vapi", "internal"})


# ---------------------------------------------------------------------------
# 19. ensure_machine_service_allowed rejects unknown allowed service
# ---------------------------------------------------------------------------


def test_ensure_machine_service_allowed_rejects_unknown_allowed():
    ctx = MachineAuthContext(service_name="vapi")
    with pytest.raises(MachineAuthError):
        ensure_machine_service_allowed(ctx, {"vapi", "unknown-svc"})


# ---------------------------------------------------------------------------
# 20. ensure_machine_scope passes existing scope
# ---------------------------------------------------------------------------


def test_ensure_machine_scope_passes():
    ctx = MachineAuthContext(service_name="vapi", scopes={"vapi:tool"})
    ensure_machine_scope(ctx, "vapi:tool")  # should not raise


# ---------------------------------------------------------------------------
# 21. ensure_machine_scope rejects missing scope
# ---------------------------------------------------------------------------


def test_ensure_machine_scope_rejects_missing():
    ctx = MachineAuthContext(service_name="vapi", scopes={"availability:read"})
    with pytest.raises(MachineAccessDeniedError):
        ensure_machine_scope(ctx, "vapi:tool")


# ---------------------------------------------------------------------------
# 22. ensure_machine_scope rejects unknown required scope
# ---------------------------------------------------------------------------


def test_ensure_machine_scope_rejects_unknown_required():
    ctx = MachineAuthContext(service_name="vapi", scopes={"vapi:tool"})
    with pytest.raises(MachineAuthError):
        ensure_machine_scope(ctx, "not:a:real:scope")


# ---------------------------------------------------------------------------
# 23. ensure_machine_clinic_access passes same clinic
# ---------------------------------------------------------------------------


def test_ensure_machine_clinic_access_passes_same_clinic():
    ctx = MachineAuthContext(service_name="vapi", clinic_id=CLINIC_ID)
    ensure_machine_clinic_access(ctx, CLINIC_ID)  # should not raise


# ---------------------------------------------------------------------------
# 24. ensure_machine_clinic_access rejects wrong clinic
# ---------------------------------------------------------------------------


def test_ensure_machine_clinic_access_rejects_wrong_clinic():
    ctx = MachineAuthContext(service_name="vapi", clinic_id=CLINIC_ID)
    with pytest.raises(MachineAccessDeniedError):
        ensure_machine_clinic_access(ctx, OTHER_CLINIC_ID)


# ---------------------------------------------------------------------------
# 25. ensure_machine_clinic_access allows missing clinic_id only with internal:admin
# ---------------------------------------------------------------------------


def test_ensure_machine_clinic_access_allows_no_clinic_with_admin_scope():
    ctx = MachineAuthContext(service_name="internal", scopes={"internal:admin"})
    ensure_machine_clinic_access(ctx, CLINIC_ID)  # should not raise


def test_ensure_machine_clinic_access_denies_no_clinic_without_admin_scope():
    ctx = MachineAuthContext(service_name="vapi", clinic_id=None, scopes={"vapi:tool"})
    with pytest.raises(MachineAccessDeniedError):
        ensure_machine_clinic_access(ctx, CLINIC_ID)


# ---------------------------------------------------------------------------
# 26. authorize_machine_access returns context on success
# ---------------------------------------------------------------------------


def test_authorize_machine_access_returns_context():
    ctx = MachineAuthContext(service_name="vapi", clinic_id=CLINIC_ID, scopes={"vapi:tool"})
    result = authorize_machine_access(
        machine_context=ctx,
        allowed_services={"vapi", "internal"},
        required_scope="vapi:tool",
        requested_clinic_id=CLINIC_ID,
    )
    assert result is ctx


# ---------------------------------------------------------------------------
# 27. authorize_machine_access rejects wrong service
# ---------------------------------------------------------------------------


def test_authorize_machine_access_rejects_wrong_service():
    ctx = MachineAuthContext(service_name="n8n", clinic_id=CLINIC_ID)
    with pytest.raises(MachineAccessDeniedError):
        authorize_machine_access(
            machine_context=ctx,
            allowed_services={"vapi", "internal"},
        )


# ---------------------------------------------------------------------------
# 28. authorize_machine_access rejects missing required scope
# ---------------------------------------------------------------------------


def test_authorize_machine_access_rejects_missing_scope():
    ctx = MachineAuthContext(service_name="vapi", clinic_id=CLINIC_ID, scopes={"availability:read"})
    with pytest.raises(MachineAccessDeniedError):
        authorize_machine_access(
            machine_context=ctx,
            allowed_services={"vapi"},
            required_scope="vapi:tool",
        )


# ---------------------------------------------------------------------------
# 29. authorize_machine_access rejects wrong clinic
# ---------------------------------------------------------------------------


def test_authorize_machine_access_rejects_wrong_clinic():
    ctx = MachineAuthContext(service_name="vapi", clinic_id=OTHER_CLINIC_ID, scopes={"vapi:tool"})
    with pytest.raises(MachineAccessDeniedError):
        authorize_machine_access(
            machine_context=ctx,
            allowed_services={"vapi"},
            required_scope="vapi:tool",
            requested_clinic_id=CLINIC_ID,
        )
