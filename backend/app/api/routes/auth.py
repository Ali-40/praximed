"""
Auth routes — PraxisMed Sprint 7 / Module 60

POST /auth/login — issue a JWT access token for a verified clinic user.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import get_db_pool
from backend.app.core.jwt_tokens import (
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    MissingJWTSecretError,
    create_access_token,
)
from backend.app.core.password_hashing import verify_password
from backend.app.db.repositories.user_repo import get_user_by_email
from backend.app.schemas.auth import LoginRequest, LoginResponse, LoginUserInfo

router = APIRouter(prefix="/auth", tags=["auth"])

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
