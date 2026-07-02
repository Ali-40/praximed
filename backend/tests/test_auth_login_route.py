"""
Tests for POST /auth/login — PraxisMed Sprint 7 / Module 60

Uses a FastAPI TestClient with dependency overrides for the DB pool.
No real database. No real bcrypt hashes — verify_password is patched where needed.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.api.routes.auth import router
from backend.app.api.deps import get_db_pool
from fastapi import FastAPI

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

JWT_SECRET  = "test-secret-module-60"
CLINIC_ID   = "clinic-uuid-m60"
USER_ID     = "user-uuid-m60"
EMAIL       = "doctor@clinic.example"
ROLE        = "doctor"
PASSWORD    = "correct-password"
HASH        = "$2b$12$fakehashforlogintest"

URL = "/auth/login"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_user(status: str = "active", password_hash: str = HASH) -> dict:
    return {
        "id":            USER_ID,
        "clinic_id":     CLINIC_ID,
        "email":         EMAIL,
        "full_name":     "Dr. Login Test",
        "role":          ROLE,
        "status":        status,
        "password_hash": password_hash,
        "created_at":    "2026-07-02T00:00:00+00:00",
        "updated_at":    "2026-07-02T00:00:00+00:00",
    }


def _make_pool(user_row) -> MagicMock:
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=user_row)
    return pool


def _valid_body(**overrides) -> dict:
    base = {"clinic_id": CLINIC_ID, "email": EMAIL, "password": PASSWORD}
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# App fixture
# ---------------------------------------------------------------------------

_app = FastAPI()
_app.include_router(router)


@pytest.fixture()
def client_active(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    pool = _make_pool(_fake_user())
    _app.dependency_overrides[get_db_pool] = lambda: pool
    with patch("backend.app.api.routes.auth.verify_password", return_value=True):
        yield TestClient(_app, raise_server_exceptions=False)
    _app.dependency_overrides.pop(get_db_pool, None)


@pytest.fixture()
def client_wrong_password(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    pool = _make_pool(_fake_user())
    _app.dependency_overrides[get_db_pool] = lambda: pool
    with patch("backend.app.api.routes.auth.verify_password", return_value=False):
        yield TestClient(_app, raise_server_exceptions=False)
    _app.dependency_overrides.pop(get_db_pool, None)


@pytest.fixture()
def client_user_not_found(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    pool = _make_pool(None)
    _app.dependency_overrides[get_db_pool] = lambda: pool
    yield TestClient(_app, raise_server_exceptions=False)
    _app.dependency_overrides.pop(get_db_pool, None)


@pytest.fixture()
def client_inactive(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    pool = _make_pool(_fake_user(status="inactive"))
    _app.dependency_overrides[get_db_pool] = lambda: pool
    with patch("backend.app.api.routes.auth.verify_password", return_value=True):
        yield TestClient(_app, raise_server_exceptions=False)
    _app.dependency_overrides.pop(get_db_pool, None)


@pytest.fixture()
def client_no_hash(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    pool = _make_pool(_fake_user(password_hash=""))
    _app.dependency_overrides[get_db_pool] = lambda: pool
    yield TestClient(_app, raise_server_exceptions=False)
    _app.dependency_overrides.pop(get_db_pool, None)


# ===========================================================================
# Tests
# ===========================================================================


def test_valid_credentials_returns_200_with_token(client_active):
    """1 — Correct credentials → 200 with access_token and user info."""
    resp = client_active.post(URL, json=_valid_body())
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in_seconds"] == 3600
    assert data["user"]["id"] == USER_ID
    assert data["user"]["clinic_id"] == CLINIC_ID
    assert data["user"]["email"] == EMAIL
    assert data["user"]["role"] == ROLE


def test_response_does_not_contain_password_hash(client_active):
    """2 — Response must never include password_hash."""
    resp = client_active.post(URL, json=_valid_body())
    assert resp.status_code == 200
    assert "password_hash" not in resp.text
    assert "password" not in resp.json()["user"]


def test_wrong_password_returns_401(client_wrong_password):
    """3 — Wrong password → 401 with generic 'Invalid credentials'."""
    resp = client_wrong_password.post(URL, json=_valid_body(password="wrong"))
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_unknown_email_returns_401(client_user_not_found):
    """4 — Email not found → 401 with same generic message (no user enumeration)."""
    resp = client_user_not_found.post(URL, json=_valid_body(email="nobody@clinic.example"))
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_inactive_user_returns_401(client_inactive):
    """5 — Correct credentials but inactive account → 401."""
    resp = client_inactive.post(URL, json=_valid_body())
    assert resp.status_code == 401
    assert "not active" in resp.json()["detail"].lower()


def test_missing_password_hash_returns_401(client_no_hash):
    """6 — User row has no password_hash set → 401 (not 500)."""
    resp = client_no_hash.post(URL, json=_valid_body())
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_missing_jwt_secret_returns_503(monkeypatch):
    """7 — JWT_SECRET_KEY missing at token creation time → 503."""
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    pool = _make_pool(_fake_user())
    _app.dependency_overrides[get_db_pool] = lambda: pool
    try:
        with patch("backend.app.api.routes.auth.verify_password", return_value=True):
            with patch(
                "backend.app.api.routes.auth.create_access_token",
                side_effect=__import__(
                    "backend.app.core.jwt_tokens", fromlist=["MissingJWTSecretError"]
                ).MissingJWTSecretError("no secret"),
            ):
                client = TestClient(_app, raise_server_exceptions=False)
                resp = client.post(URL, json=_valid_body())
        assert resp.status_code == 503
    finally:
        _app.dependency_overrides.pop(get_db_pool, None)


def test_missing_clinic_id_returns_422(client_active):
    """8 — Missing clinic_id in body → 422 validation error."""
    resp = client_active.post(URL, json={"email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 422


def test_empty_email_returns_422(client_active):
    """9 — Empty email string → 422 validation error."""
    resp = client_active.post(URL, json=_valid_body(email=""))
    assert resp.status_code == 422


def test_email_normalized_to_lowercase(monkeypatch):
    """10 — Email in mixed case is normalized before lookup."""
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    pool = _make_pool(_fake_user())
    _app.dependency_overrides[get_db_pool] = lambda: pool
    try:
        with patch("backend.app.api.routes.auth.verify_password", return_value=True):
            client = TestClient(_app, raise_server_exceptions=False)
            resp = client.post(URL, json=_valid_body(email="Doctor@Clinic.EXAMPLE"))
        assert resp.status_code == 200
        call_args = pool.fetchrow.call_args[0]
        assert "doctor@clinic.example" in call_args
    finally:
        _app.dependency_overrides.pop(get_db_pool, None)
