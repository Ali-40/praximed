"""
Sprint 17 / Module 120 — Auth/session hardening tests.

Verifies:
  - POST /auth/login sets praximed_session cookie (httpOnly, Secure, SameSite configurable)
  - Default SameSite is "none" (cross-site Vercel→Railway staging) — Module 120A
  - POST /auth/logout clears the cookie (Max-Age=0 / delete_cookie)
  - GET  /auth/me resolves via session cookie (no Bearer header needed)
  - No Bearer + no cookie → 401 from get_current_user
  - Valid cookie accepted as auth by get_current_user
  - Existing Bearer-header path still works (backward compat)

No real database, no real secrets committed.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.deps import get_db_pool
from backend.app.api.dependencies.current_user import get_current_user
from backend.app.core.auth_context import AuthContext
from backend.app.core.jwt_tokens import create_access_token

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

JWT_SECRET = "test-secret-module-120"
CLINIC_ID  = "clinic-uuid-m120"
USER_ID    = "user-uuid-m120"
EMAIL      = "doctor@m120.example"
ROLE       = "doctor"
PASSWORD   = "correct-password"
HASH       = "$2b$12$fakehashformodule120"

COOKIE_NAME = "praximed_session"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_user(status: str = "active") -> dict:
    return {
        "id":            USER_ID,
        "clinic_id":     CLINIC_ID,
        "email":         EMAIL,
        "full_name":     "Dr. Module 120",
        "role":          ROLE,
        "status":        status,
        "password_hash": HASH,
        "created_at":    "2026-07-05T00:00:00+00:00",
        "updated_at":    "2026-07-05T00:00:00+00:00",
    }


def _make_pool(user_row) -> MagicMock:
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=user_row)
    return pool


def _valid_login_body() -> dict:
    return {"clinic_id": CLINIC_ID, "email": EMAIL, "password": PASSWORD}


def _make_token(monkeypatch) -> str:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    return create_access_token(USER_ID, CLINIC_ID, ROLE)


# ---------------------------------------------------------------------------
# Apps under test
# ---------------------------------------------------------------------------

# Full auth router app (login, logout, me).
_auth_app = FastAPI()
_auth_app.include_router(auth_router)

# Minimal app for testing get_current_user cookie fallback in isolation.
_dep_app = FastAPI()


@_dep_app.get("/test/protected")
async def _protected(user: AuthContext = Depends(get_current_user)) -> dict:
    return {"user_id": user.user_id, "clinic_id": user.clinic_id}


# ===========================================================================
# 1. Login sets httpOnly Secure cookie (SameSite=None default for cross-site staging)
# ===========================================================================


@pytest.fixture()
def login_client(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    # Default SESSION_COOKIE_SAMESITE is "none" (cross-site Vercel→Railway staging).
    monkeypatch.delenv("SESSION_COOKIE_SAMESITE", raising=False)
    pool = _make_pool(_fake_user())
    _auth_app.dependency_overrides[get_db_pool] = lambda: pool
    with patch("backend.app.api.routes.auth.verify_password", return_value=True):
        yield TestClient(_auth_app, raise_server_exceptions=False)
    _auth_app.dependency_overrides.pop(get_db_pool, None)


def test_login_sets_cookie(login_client):
    """1 — Successful login sets the praximed_session cookie."""
    resp = login_client.post("/auth/login", json=_valid_login_body())
    assert resp.status_code == 200
    assert COOKIE_NAME in resp.cookies


def test_login_cookie_is_httponly(login_client):
    """2 — Cookie must be httpOnly (not readable by JS)."""
    resp = login_client.post("/auth/login", json=_valid_login_body())
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    assert "httponly" in set_cookie.lower()


def test_login_cookie_is_secure(login_client):
    """3 — Cookie must be Secure (HTTPS only)."""
    resp = login_client.post("/auth/login", json=_valid_login_body())
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    assert "secure" in set_cookie.lower()


def test_login_cookie_has_samesite_attribute(login_client):
    """4 — Cookie must carry a SameSite attribute (value is env-configurable;
    default is 'none' for cross-site Vercel→Railway staging)."""
    resp = login_client.post("/auth/login", json=_valid_login_body())
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    assert "samesite=" in set_cookie.lower()


def test_login_cookie_default_samesite_is_none(login_client):
    """4b — Default SameSite is 'none' (SESSION_COOKIE_SAMESITE not set → cross-site staging)."""
    resp = login_client.post("/auth/login", json=_valid_login_body())
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    assert "samesite=none" in set_cookie.lower()


def test_login_cookie_has_max_age(login_client):
    """5 — Cookie must carry a Max-Age (not a session-only cookie)."""
    resp = login_client.post("/auth/login", json=_valid_login_body())
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    assert "max-age=" in set_cookie.lower()


def test_login_still_returns_json_body(login_client):
    """6 — JSON body with access_token is still returned (migration window)."""
    resp = login_client.post("/auth/login", json=_valid_login_body())
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in_seconds"] == 3600


# ===========================================================================
# 2. Logout clears the cookie
# ===========================================================================


def test_logout_returns_200(login_client):
    """7 — POST /auth/logout returns HTTP 200."""
    resp = login_client.post("/auth/logout")
    assert resp.status_code == 200


def test_logout_returns_ok_true(login_client):
    """8 — POST /auth/logout body is {"ok": true}."""
    resp = login_client.post("/auth/logout")
    assert resp.json() == {"ok": True}


def test_logout_clears_cookie(login_client):
    """9 — Logout response clears praximed_session cookie (max-age=0 or empty value)."""
    resp = login_client.post("/auth/logout")
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    # FastAPI's delete_cookie sets Max-Age=0 to expire the cookie immediately.
    assert "max-age=0" in set_cookie.lower() or COOKIE_NAME in set_cookie


# ===========================================================================
# 3. Cookie auth accepted by get_current_user
# ===========================================================================


@pytest.fixture()
def cookie_dep_client(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    pool = _make_pool(_fake_user())
    _dep_app.dependency_overrides[get_db_pool] = lambda: pool
    yield TestClient(_dep_app, raise_server_exceptions=False)
    _dep_app.dependency_overrides.pop(get_db_pool, None)


def test_cookie_auth_accepted(cookie_dep_client, monkeypatch):
    """10 — Valid praximed_session cookie → 200 and correct user context."""
    token = _make_token(monkeypatch)
    cookie_dep_client.cookies.set(COOKIE_NAME, token)
    resp = cookie_dep_client.get("/test/protected")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == USER_ID
    assert data["clinic_id"] == CLINIC_ID


def test_no_bearer_no_cookie_returns_401(cookie_dep_client):
    """11 — No Bearer header AND no cookie → 401."""
    cookie_dep_client.cookies.clear()
    resp = cookie_dep_client.get("/test/protected")
    assert resp.status_code == 401


def test_bearer_still_works_with_cookie_fallback(cookie_dep_client, monkeypatch):
    """12 — Bearer header still works (backward compat); cookie fallback is secondary."""
    token = _make_token(monkeypatch)
    cookie_dep_client.cookies.clear()
    resp = cookie_dep_client.get(
        "/test/protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["user_id"] == USER_ID


def test_expired_cookie_token_returns_401(cookie_dep_client, monkeypatch):
    """13 — Expired token in cookie → 401."""
    from datetime import timedelta
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(USER_ID, CLINIC_ID, ROLE, expires_delta=timedelta(seconds=-1))
    cookie_dep_client.cookies.set(COOKIE_NAME, token)
    resp = cookie_dep_client.get("/test/protected")
    assert resp.status_code == 401
    assert "expired" in resp.json()["detail"].lower()


def test_invalid_cookie_token_returns_401(cookie_dep_client, monkeypatch):
    """14 — Malformed token in cookie → 401."""
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    cookie_dep_client.cookies.set(COOKIE_NAME, "not.a.valid.jwt")
    resp = cookie_dep_client.get("/test/protected")
    assert resp.status_code == 401


# ===========================================================================
# 4. GET /auth/me resolves via cookie
# ===========================================================================


def test_me_endpoint_with_cookie(monkeypatch):
    """15 — GET /auth/me resolves the current user via session cookie."""
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    token = create_access_token(USER_ID, CLINIC_ID, ROLE)
    pool = _make_pool(_fake_user())
    _auth_app.dependency_overrides[get_db_pool] = lambda: pool
    try:
        client = TestClient(_auth_app, raise_server_exceptions=False)
        client.cookies.set(COOKIE_NAME, token)
        resp = client.get("/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == USER_ID
        assert data["clinic_id"] == CLINIC_ID
        assert data["role"] == ROLE
    finally:
        _auth_app.dependency_overrides.pop(get_db_pool, None)


def test_me_endpoint_unauthenticated_returns_401(monkeypatch):
    """16 — GET /auth/me with no cookie and no Bearer → 401.

    Uses a fresh FastAPI + router instance to avoid any cookie carry-over
    from the login tests that share _auth_app at module scope.
    """
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    from fastapi import FastAPI as _FastAPI
    from backend.app.api.routes.auth import router as _r
    isolated_app = _FastAPI()
    isolated_app.include_router(_r)
    pool = _make_pool(_fake_user())
    isolated_app.dependency_overrides[get_db_pool] = lambda: pool
    client = TestClient(isolated_app, raise_server_exceptions=False)
    resp = client.get("/auth/me")
    assert resp.status_code == 401
