"""
Pydantic schemas for auth endpoints — PraxisMed Sprint 7 / Module 60
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    clinic_id: str
    email: str
    password: str

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("email must not be empty")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("password must not be empty")
        return v


class LoginUserInfo(BaseModel):
    id: str
    clinic_id: str
    email: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: LoginUserInfo
