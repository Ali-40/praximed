"""
Auth context and tenant access primitives — PraxisMed Sprint 3 / Module 36

Provides header-based auth context construction and tenant ownership
enforcement helpers. No external auth provider. No database calls.
Route-by-route enforcement applied in Module 37.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class AuthContextError(RuntimeError):
    """Base class for auth context errors."""


class InvalidAuthHeaderError(AuthContextError):
    """Raised when a required auth header is missing or malformed."""


class TenantAccessDeniedError(AuthContextError):
    """Raised when clinic_id or role check fails."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_AUTH_SCHEME = "internal_header"

ALLOWED_ROLES: Set[str] = {"owner", "admin", "doctor", "staff", "viewer", "system"}
CLINICAL_ROLES: Set[str] = {"owner", "admin", "doctor"}
STAFF_ROLES: Set[str] = {"owner", "admin", "doctor", "staff"}


# ---------------------------------------------------------------------------
# AuthContext dataclass
# ---------------------------------------------------------------------------


@dataclass
class AuthContext:
    user_id: str
    clinic_id: str
    role: str
    auth_scheme: str = DEFAULT_AUTH_SCHEME
    raw_claims: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self) -> None:
        if not self.user_id or not str(self.user_id).strip():
            raise AuthContextError("'user_id' must not be empty")
        if not self.clinic_id or not str(self.clinic_id).strip():
            raise AuthContextError("'clinic_id' must not be empty")
        if self.role not in ALLOWED_ROLES:
            raise AuthContextError(
                f"'{self.role}' is not a valid role. Allowed: {sorted(ALLOWED_ROLES)}"
            )


# ---------------------------------------------------------------------------
# 1. normalize_header_value
# ---------------------------------------------------------------------------


def normalize_header_value(value: Optional[str], header_name: str) -> str:
    if value is None:
        raise InvalidAuthHeaderError(
            f"Required header '{header_name}' is missing"
        )
    stripped = value.strip()
    if not stripped:
        raise InvalidAuthHeaderError(
            f"Required header '{header_name}' must not be empty"
        )
    return stripped


# ---------------------------------------------------------------------------
# 2. parse_role_header
# ---------------------------------------------------------------------------


def parse_role_header(value: Optional[str]) -> str:
    raw = normalize_header_value(value, "X-User-Role")
    role = raw.lower()
    if role not in ALLOWED_ROLES:
        raise InvalidAuthHeaderError(
            f"'{role}' is not a valid role. Allowed: {sorted(ALLOWED_ROLES)}"
        )
    return role


# ---------------------------------------------------------------------------
# 3. build_auth_context_from_headers
# ---------------------------------------------------------------------------


def build_auth_context_from_headers(
    user_id: Optional[str],
    clinic_id: Optional[str],
    role: Optional[str],
    auth_scheme: str = DEFAULT_AUTH_SCHEME,
    raw_claims: Optional[Dict[str, Any]] = None,
) -> AuthContext:
    norm_user_id = normalize_header_value(user_id, "X-User-Id")
    norm_clinic_id = normalize_header_value(clinic_id, "X-Clinic-Id")
    norm_role = parse_role_header(role)

    if raw_claims is not None and not isinstance(raw_claims, dict):
        raise InvalidAuthHeaderError("'raw_claims' must be a dict if provided")

    return AuthContext(
        user_id=norm_user_id,
        clinic_id=norm_clinic_id,
        role=norm_role,
        auth_scheme=auth_scheme,
        raw_claims=raw_claims,
    )


# ---------------------------------------------------------------------------
# 4. ensure_same_clinic
# ---------------------------------------------------------------------------


def ensure_same_clinic(auth_context: AuthContext, requested_clinic_id: str) -> None:
    if not requested_clinic_id or not str(requested_clinic_id).strip():
        raise TenantAccessDeniedError("'requested_clinic_id' must not be empty")
    if auth_context.clinic_id != requested_clinic_id:
        raise TenantAccessDeniedError(
            f"Access denied: caller belongs to clinic '{auth_context.clinic_id}', "
            f"not '{requested_clinic_id}'"
        )


# ---------------------------------------------------------------------------
# 5. ensure_role_allowed
# ---------------------------------------------------------------------------


def ensure_role_allowed(auth_context: AuthContext, allowed_roles: Set[str]) -> None:
    if not allowed_roles:
        raise AuthContextError("'allowed_roles' must be a non-empty set")
    unknown = allowed_roles - ALLOWED_ROLES
    if unknown:
        raise AuthContextError(
            f"Unknown roles in allowed_roles: {sorted(unknown)}"
        )
    if auth_context.role not in allowed_roles:
        raise TenantAccessDeniedError(
            f"Role '{auth_context.role}' is not permitted. "
            f"Required one of: {sorted(allowed_roles)}"
        )


# ---------------------------------------------------------------------------
# 6. ensure_staff_access
# ---------------------------------------------------------------------------


def ensure_staff_access(auth_context: AuthContext) -> None:
    ensure_role_allowed(auth_context, STAFF_ROLES)


# ---------------------------------------------------------------------------
# 7. ensure_clinical_access
# ---------------------------------------------------------------------------


def ensure_clinical_access(auth_context: AuthContext) -> None:
    ensure_role_allowed(auth_context, CLINICAL_ROLES)


# ---------------------------------------------------------------------------
# 8. authorize_clinic_access
# ---------------------------------------------------------------------------


def authorize_clinic_access(
    auth_context: AuthContext,
    requested_clinic_id: str,
    allowed_roles: Optional[Set[str]] = None,
) -> AuthContext:
    ensure_same_clinic(auth_context, requested_clinic_id)
    if allowed_roles is not None:
        ensure_role_allowed(auth_context, allowed_roles)
    return auth_context
