"""
Tests for auth_context — PraxisMed Sprint 3 / Module 36.

No real database, no external services.
"""

from __future__ import annotations

import pytest

from backend.app.core.auth_context import (
    ALLOWED_ROLES,
    CLINICAL_ROLES,
    STAFF_ROLES,
    AuthContext,
    AuthContextError,
    InvalidAuthHeaderError,
    TenantAccessDeniedError,
    authorize_clinic_access,
    build_auth_context_from_headers,
    ensure_clinical_access,
    ensure_role_allowed,
    ensure_same_clinic,
    ensure_staff_access,
    normalize_header_value,
    parse_role_header,
)


def _make_ctx(role: str = "doctor", clinic_id: str = "clinic-1") -> AuthContext:
    return AuthContext(user_id="user-1", clinic_id=clinic_id, role=role)


# ---------------------------------------------------------------------------
# 1. AuthContext accepts valid fields
# ---------------------------------------------------------------------------


def test_auth_context_accepts_valid():
    ctx = AuthContext(user_id="u-1", clinic_id="c-1", role="doctor")
    assert ctx.user_id == "u-1"
    assert ctx.clinic_id == "c-1"
    assert ctx.role == "doctor"


# ---------------------------------------------------------------------------
# 2. AuthContext rejects empty user_id
# ---------------------------------------------------------------------------


def test_auth_context_rejects_empty_user_id():
    with pytest.raises(AuthContextError, match="user_id"):
        AuthContext(user_id="", clinic_id="c-1", role="doctor")


# ---------------------------------------------------------------------------
# 3. AuthContext rejects empty clinic_id
# ---------------------------------------------------------------------------


def test_auth_context_rejects_empty_clinic_id():
    with pytest.raises(AuthContextError, match="clinic_id"):
        AuthContext(user_id="u-1", clinic_id="", role="doctor")


# ---------------------------------------------------------------------------
# 4. AuthContext rejects invalid role
# ---------------------------------------------------------------------------


def test_auth_context_rejects_invalid_role():
    with pytest.raises(AuthContextError, match="superuser"):
        AuthContext(user_id="u-1", clinic_id="c-1", role="superuser")


# ---------------------------------------------------------------------------
# 5. normalize_header_value accepts and strips valid value
# ---------------------------------------------------------------------------


def test_normalize_header_value_strips_whitespace():
    result = normalize_header_value("  user-1  ", "X-User-Id")
    assert result == "user-1"


# ---------------------------------------------------------------------------
# 6. normalize_header_value rejects None
# ---------------------------------------------------------------------------


def test_normalize_header_value_rejects_none():
    with pytest.raises(InvalidAuthHeaderError, match="X-User-Id"):
        normalize_header_value(None, "X-User-Id")


# ---------------------------------------------------------------------------
# 7. normalize_header_value rejects empty string
# ---------------------------------------------------------------------------


def test_normalize_header_value_rejects_empty_string():
    with pytest.raises(InvalidAuthHeaderError, match="X-User-Role"):
        normalize_header_value("   ", "X-User-Role")


# ---------------------------------------------------------------------------
# 8. parse_role_header lowercases role
# ---------------------------------------------------------------------------


def test_parse_role_header_lowercases():
    result = parse_role_header("DOCTOR")
    assert result == "doctor"


# ---------------------------------------------------------------------------
# 9. parse_role_header rejects invalid role
# ---------------------------------------------------------------------------


def test_parse_role_header_rejects_invalid():
    with pytest.raises(InvalidAuthHeaderError, match="superuser"):
        parse_role_header("superuser")


# ---------------------------------------------------------------------------
# 10. build_auth_context_from_headers returns AuthContext
# ---------------------------------------------------------------------------


def test_build_auth_context_from_headers_returns_context():
    ctx = build_auth_context_from_headers(
        user_id="u-1", clinic_id="c-1", role="staff"
    )
    assert isinstance(ctx, AuthContext)
    assert ctx.role == "staff"
    assert ctx.user_id == "u-1"


# ---------------------------------------------------------------------------
# 11. build_auth_context_from_headers rejects non-dict raw_claims
# ---------------------------------------------------------------------------


def test_build_auth_context_rejects_non_dict_raw_claims():
    with pytest.raises(InvalidAuthHeaderError, match="raw_claims"):
        build_auth_context_from_headers(
            user_id="u-1", clinic_id="c-1", role="doctor",
            raw_claims="not a dict",
        )


# ---------------------------------------------------------------------------
# 12. ensure_same_clinic passes for same clinic
# ---------------------------------------------------------------------------


def test_ensure_same_clinic_passes():
    ctx = _make_ctx(clinic_id="clinic-1")
    ensure_same_clinic(ctx, "clinic-1")  # no exception


# ---------------------------------------------------------------------------
# 13. ensure_same_clinic rejects different clinic
# ---------------------------------------------------------------------------


def test_ensure_same_clinic_rejects_different():
    ctx = _make_ctx(clinic_id="clinic-1")
    with pytest.raises(TenantAccessDeniedError, match="clinic-2"):
        ensure_same_clinic(ctx, "clinic-2")


# ---------------------------------------------------------------------------
# 14. ensure_role_allowed passes allowed role
# ---------------------------------------------------------------------------


def test_ensure_role_allowed_passes():
    ctx = _make_ctx(role="doctor")
    ensure_role_allowed(ctx, {"doctor", "admin"})  # no exception


# ---------------------------------------------------------------------------
# 15. ensure_role_allowed rejects disallowed role
# ---------------------------------------------------------------------------


def test_ensure_role_allowed_rejects_disallowed():
    ctx = _make_ctx(role="viewer")
    with pytest.raises(TenantAccessDeniedError, match="viewer"):
        ensure_role_allowed(ctx, {"doctor", "admin"})


# ---------------------------------------------------------------------------
# 16. ensure_role_allowed rejects unknown allowed role in set
# ---------------------------------------------------------------------------


def test_ensure_role_allowed_rejects_unknown_role_in_set():
    ctx = _make_ctx(role="doctor")
    with pytest.raises(AuthContextError, match="superuser"):
        ensure_role_allowed(ctx, {"doctor", "superuser"})


# ---------------------------------------------------------------------------
# 17. ensure_staff_access allows staff
# ---------------------------------------------------------------------------


def test_ensure_staff_access_allows_staff():
    ctx = _make_ctx(role="staff")
    ensure_staff_access(ctx)  # no exception


# ---------------------------------------------------------------------------
# 18. ensure_staff_access rejects viewer
# ---------------------------------------------------------------------------


def test_ensure_staff_access_rejects_viewer():
    ctx = _make_ctx(role="viewer")
    with pytest.raises(TenantAccessDeniedError):
        ensure_staff_access(ctx)


# ---------------------------------------------------------------------------
# 19. ensure_clinical_access allows doctor
# ---------------------------------------------------------------------------


def test_ensure_clinical_access_allows_doctor():
    ctx = _make_ctx(role="doctor")
    ensure_clinical_access(ctx)  # no exception


# ---------------------------------------------------------------------------
# 20. ensure_clinical_access rejects staff
# ---------------------------------------------------------------------------


def test_ensure_clinical_access_rejects_staff():
    ctx = _make_ctx(role="staff")
    with pytest.raises(TenantAccessDeniedError):
        ensure_clinical_access(ctx)


# ---------------------------------------------------------------------------
# 21. authorize_clinic_access returns auth context on success
# ---------------------------------------------------------------------------


def test_authorize_clinic_access_returns_context():
    ctx = _make_ctx(role="doctor", clinic_id="clinic-1")
    result = authorize_clinic_access(ctx, "clinic-1")
    assert result is ctx


# ---------------------------------------------------------------------------
# 22. authorize_clinic_access rejects wrong clinic
# ---------------------------------------------------------------------------


def test_authorize_clinic_access_rejects_wrong_clinic():
    ctx = _make_ctx(clinic_id="clinic-1")
    with pytest.raises(TenantAccessDeniedError):
        authorize_clinic_access(ctx, "clinic-2")


# ---------------------------------------------------------------------------
# 23. authorize_clinic_access rejects wrong role
# ---------------------------------------------------------------------------


def test_authorize_clinic_access_rejects_wrong_role():
    ctx = _make_ctx(role="viewer", clinic_id="clinic-1")
    with pytest.raises(TenantAccessDeniedError):
        authorize_clinic_access(ctx, "clinic-1", allowed_roles=CLINICAL_ROLES)
