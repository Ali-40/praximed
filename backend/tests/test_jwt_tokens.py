"""
Tests for jwt_tokens — PraxisMed Sprint 7 / Module 59

No real DB, no external services.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from backend.app.core.jwt_tokens import (
    ExpiredJWTError,
    InvalidJWTError,
    MissingJWTSecretError,
    create_access_token,
    decode_access_token,
)

JWT_SECRET = "test-jwt-secret-for-unit-tests"
USER_ID    = "user-uuid-abc"
CLINIC_ID  = "clinic-uuid-xyz"
ROLE       = "doctor"


# ---------------------------------------------------------------------------
# 1. create_access_token returns a non-empty string
# ---------------------------------------------------------------------------


def test_create_access_token_returns_string(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(USER_ID, CLINIC_ID, ROLE)
    assert isinstance(token, str)
    assert len(token) > 0


# ---------------------------------------------------------------------------
# 2. create_access_token encodes expected claims
# ---------------------------------------------------------------------------


def test_create_access_token_claims(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(USER_ID, CLINIC_ID, ROLE)
    payload = decode_access_token(token)
    assert payload["sub"]       == USER_ID
    assert payload["clinic_id"] == CLINIC_ID
    assert payload["role"]      == ROLE
    assert "exp" in payload
    assert "iat" in payload


# ---------------------------------------------------------------------------
# 3. create_access_token raises MissingJWTSecretError when env not set
# ---------------------------------------------------------------------------


def test_create_token_missing_secret_raises(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(MissingJWTSecretError):
        create_access_token(USER_ID, CLINIC_ID, ROLE)


# ---------------------------------------------------------------------------
# 4. create_access_token raises MissingJWTSecretError for empty env var
# ---------------------------------------------------------------------------


def test_create_token_empty_secret_raises(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "   ")
    with pytest.raises(MissingJWTSecretError):
        create_access_token(USER_ID, CLINIC_ID, ROLE)


# ---------------------------------------------------------------------------
# 5. decode_access_token returns payload for valid token
# ---------------------------------------------------------------------------


def test_decode_access_token_valid(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(USER_ID, CLINIC_ID, ROLE)
    payload = decode_access_token(token)
    assert payload["sub"] == USER_ID


# ---------------------------------------------------------------------------
# 6. decode_access_token raises InvalidJWTError for garbage token
# ---------------------------------------------------------------------------


def test_decode_access_token_garbage(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    with pytest.raises(InvalidJWTError):
        decode_access_token("not.a.valid.jwt")


# ---------------------------------------------------------------------------
# 7. decode_access_token raises InvalidJWTError for wrong secret
# ---------------------------------------------------------------------------


def test_decode_access_token_wrong_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(USER_ID, CLINIC_ID, ROLE)
    monkeypatch.setenv("JWT_SECRET_KEY", "completely-different-secret")
    with pytest.raises(InvalidJWTError):
        decode_access_token(token)


# ---------------------------------------------------------------------------
# 8. decode_access_token raises ExpiredJWTError for expired token
# ---------------------------------------------------------------------------


def test_decode_access_token_expired(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(
        USER_ID, CLINIC_ID, ROLE,
        expires_delta=timedelta(seconds=-1),
    )
    with pytest.raises(ExpiredJWTError):
        decode_access_token(token)


# ---------------------------------------------------------------------------
# 9. ExpiredJWTError is a subclass of InvalidJWTError
# ---------------------------------------------------------------------------


def test_expired_jwt_error_is_invalid_jwt_error():
    assert issubclass(ExpiredJWTError, InvalidJWTError)


# ---------------------------------------------------------------------------
# 10. decode_access_token raises MissingJWTSecretError when env not set
# ---------------------------------------------------------------------------


def test_decode_token_missing_secret_raises(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(USER_ID, CLINIC_ID, ROLE)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(MissingJWTSecretError):
        decode_access_token(token)


# ---------------------------------------------------------------------------
# 11. custom expires_delta is respected
# ---------------------------------------------------------------------------


def test_create_token_custom_expiry(monkeypatch):
    import time
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(
        USER_ID, CLINIC_ID, ROLE,
        expires_delta=timedelta(hours=2),
    )
    payload = decode_access_token(token)
    now = int(time.time())
    assert payload["exp"] > now + 7000  # roughly 2 hours


# ---------------------------------------------------------------------------
# 12. JWT source does not contain plaintext secret
# ---------------------------------------------------------------------------


def test_token_does_not_contain_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(USER_ID, CLINIC_ID, ROLE)
    assert JWT_SECRET not in token
