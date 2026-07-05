"""
Auth routes — PraxisMed Sprint 7 / Module 60
Updated Sprint 17 / Module 120 — httpOnly Secure SameSite cookie session model.

POST /auth/login  — issue a JWT and set it as an httpOnly Secure SameSite=Lax cookie.
POST /auth/logout — clear the session cookie; return HTTP 200.
GET  /auth/me     — return current user info (resolved via cookie or Bearer JWT).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.app.api.deps import get_db_pool
from backend.app.api.dependencies.current_user import get_current_user
from backend.app.core.auth_context import AuthContext
from backend.app.core.jwt_tokens import (
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    MissingJWTSecretError,
    create_access_token,
)
from backend.app.core.password_hashing import verify_password
from backend.app.db.repositories.user_repo import get_user_by_email
from backend.app.schemas.auth import LoginRequest, LoginResponse, LoginUserInfo

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_NAME = "praximed_session"
_COOKIE_MAX_AGE = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 3600 s

_INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
)

_INACTIVE_ACCOUNT = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Account is not active",
)


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    response: Response,
    pool: Any = Depends(get_db_pool),
) -> LoginResponse:
    try:
        user = await get_user_by_email(pool, body.clinic_id, body.email)
    except Exception:
        raise _INVALID_CREDENTIALS

    if user is None:
        raise _INVALID_CREDENTIALS

    if not user.get("password_hash"):
        raise _INVALID_CREDENTIALS

    if not verify_password(body.password, user["password_hash"]):
        raise _INVALID_CREDENTIALS

    if user.get("status") != "active":
        raise _INACTIVE_ACCOUNT

    try:
        token = create_access_token(
            user_id=str(user["id"]),
            clinic_id=str(user["clinic_id"]),
            role=str(user["role"]),
        )
    except MissingJWTSecretError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable",
        )

    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=_COOKIE_MAX_AGE,
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in_seconds=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=LoginUserInfo(
            id=str(user["id"]),
            clinic_id=str(user["clinic_id"]),
            email=str(user["email"]),
            role=str(user["role"]),
        ),
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response) -> dict:
    """Clear the session cookie. The JWT remains valid until expiry but the browser
    discards the cookie immediately, ending the browser session."""
    response.delete_cookie(key=_COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me")
async def me(current_user: AuthContext = Depends(get_current_user)) -> dict:
    """Return current user identity. Accepts Bearer header or praximed_session cookie."""
    return {
        "user_id": current_user.user_id,
        "clinic_id": current_user.clinic_id,
        "role": current_user.role,
    }
