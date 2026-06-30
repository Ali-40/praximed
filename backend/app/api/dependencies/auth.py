"""
FastAPI auth dependencies — PraxisMed Sprint 3 / Module 36

Header-based auth context injection. Maps auth errors to HTTP 401/403.
No database calls. No external auth provider.
"""

from __future__ import annotations

from typing import Optional, Set

from fastapi import Header, HTTPException

from backend.app.core.auth_context import (
    CLINICAL_ROLES,
    STAFF_ROLES,
    AuthContext,
    AuthContextError,
    InvalidAuthHeaderError,
    TenantAccessDeniedError,
    authorize_clinic_access,
    build_auth_context_from_headers,
)


# ---------------------------------------------------------------------------
# 1. get_auth_context
# ---------------------------------------------------------------------------


def get_auth_context(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    x_clinic_id: Optional[str] = Header(default=None, alias="X-Clinic-Id"),
    x_user_role: Optional[str] = Header(default=None, alias="X-User-Role"),
) -> AuthContext:
    try:
        return build_auth_context_from_headers(
            user_id=x_user_id,
            clinic_id=x_clinic_id,
            role=x_user_role,
        )
    except (InvalidAuthHeaderError, AuthContextError) as exc:
        raise HTTPException(status_code=401, detail=str(exc))


# ---------------------------------------------------------------------------
# 2. require_clinic_access
# ---------------------------------------------------------------------------


def require_clinic_access(
    requested_clinic_id: str,
    auth_context: AuthContext,
    allowed_roles: Optional[Set[str]] = None,
) -> AuthContext:
    try:
        return authorize_clinic_access(
            auth_context=auth_context,
            requested_clinic_id=requested_clinic_id,
            allowed_roles=allowed_roles,
        )
    except TenantAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


# ---------------------------------------------------------------------------
# 3. require_staff_clinic_access
# ---------------------------------------------------------------------------


def require_staff_clinic_access(
    requested_clinic_id: str,
    auth_context: AuthContext,
) -> AuthContext:
    return require_clinic_access(
        requested_clinic_id=requested_clinic_id,
        auth_context=auth_context,
        allowed_roles=STAFF_ROLES,
    )


# ---------------------------------------------------------------------------
# 4. require_clinical_clinic_access
# ---------------------------------------------------------------------------


def require_clinical_clinic_access(
    requested_clinic_id: str,
    auth_context: AuthContext,
) -> AuthContext:
    return require_clinic_access(
        requested_clinic_id=requested_clinic_id,
        auth_context=auth_context,
        allowed_roles=CLINICAL_ROLES,
    )
