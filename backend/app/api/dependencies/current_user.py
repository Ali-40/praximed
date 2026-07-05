"""
Current user dependency — PraxisMed Sprint 7 / Module 59
Updated Sprint 17 / Module 120 — cookie fallback for browser sessions.

Provides get_current_user: a FastAPI dependency that extracts a JWT from:
  1. Authorization: Bearer <token>  (machine clients, backward compat)
  2. praximed_session cookie         (browser sessions, httpOnly)

Not yet wired into existing PHI routes — this is the foundation layer.
Route-level wiring happens in a subsequent module.
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import ALLOWED_ROLES, AuthContext
from backend.app.core.jwt_tokens import (
    ExpiredJWTError,
    InvalidJWTError,
    MissingJWTSecretError,
    decode_access_token,
)
from backend.app.db.repositories import user_repo

_COOKIE_NAME = "praximed_session"

# HTTPBearer with auto_error=False lets us return a custom 401 message
# instead of the generic FastAPI one.
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    pool=Depends(get_db_pool),
) -> AuthContext:
    """FastAPI dependency — decode JWT from Bearer header or session cookie.

    Auth priority:
      1. Authorization: Bearer <token>
      2. praximed_session cookie

    HTTP 401  missing token, invalid token, expired token, inactive user.
    HTTP 503  JWT_SECRET_KEY not configured.
    """
    token: Optional[str] = None

    if credentials is not None and credentials.credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get(_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)
    except MissingJWTSecretError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except ExpiredJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id  = payload.get("sub")
    clinic_id = payload.get("clinic_id")
    role      = payload.get("role")

    if not user_id or not clinic_id or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing required claims",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token contains unknown role: {role!r}",
        )

    user = await user_repo.get_user_by_id(pool, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthContext(
        user_id=str(user["id"]),
        clinic_id=str(user["clinic_id"]),
        role=str(user["role"]),
        auth_scheme="jwt_bearer",
        raw_claims=payload,
    )
