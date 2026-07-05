"""
Sprint 17 / Module 120A — Cross-site staging cookie compatibility tests.

Verifies that SESSION_COOKIE_SAMESITE controls the SameSite attribute:
  - Unset (default)  → SameSite=None  (cross-site Vercel→Railway staging)
  - "none"           → SameSite=None
  - "lax"            → SameSite=Lax   (same-site / custom domain production)
  - "strict"         → SameSite=Strict
  - Unknown value    → falls back to SameSite=None
  - SameSite=None cookies are still HttpOnly + Secure

No real database, no real secrets committed.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.deps import get_db_pool

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

JWT_SECRET  = "test-secret-module-120a"
CLINIC_ID   = "clinic-uuid-m120a"
USER_ID     = "user-uuid-m120a"
EMAIL       = "doctor@m120a.example"
PASSWORD    = "correct-password"
HASH        = "$2b$12$fakehashformodule120a"
ROLE        = "doctor"

COOKIE_NAME = "praximed_session"
LOGIN_URL   = "/auth/login"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_user() -> dict:
    return {
        "id":            USER_ID,
        "clinic_id":     CLINIC_ID,
        "email":         EMAIL,
        "full_name":     "Dr. Module 120A",
        "role":          ROLE,
        "status":        "active",
        "password_hash": HASH,
        "created_at":    "2026-07-05T00:00:00+00:00",
        "updated_at":    "2026-07-05T00:00:00+00:00",
    }


def _make_pool() -> MagicMock:
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=_fake_user())
    return pool


def _valid_body() -> dict:
    return {"clinic_id": CLINIC_ID, "email": EMAIL, "password": PASSWORD}


# ---------------------------------------------------------------------------
# Helpers — read Set-Cookie header
# ---------------------------------------------------------------------------


def _set_cookie(monkeypatch, samesite_env: str | None) -> str:
    """POST to /auth/login with the given SESSION_COOKIE_SAMESITE and return
    the lowercased Set-Cookie header value.

    Uses a fresh isolated FastAPI+TestClient per call so env-var changes in one
    test cannot leak into another.  The verify_password patch and the HTTP
    request must both occur inside the same `with patch(...)` block.
    """
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    if samesite_env is None:
        monkeypatch.delenv("SESSION_COOKIE_SAMESITE", raising=False)
    else:
        monkeypatch.setenv("SESSION_COOKIE_SAMESITE", samesite_env)

    fresh_app = FastAPI()
    fresh_app.include_router(auth_router)
    fresh_app.dependency_overrides[get_db_pool] = lambda: _make_pool()

    with patch("backend.app.api.routes.auth.verify_password", return_value=True):
        client = TestClient(fresh_app, raise_server_exceptions=False)
        resp = client.post(LOGIN_URL, json=_valid_body())

    assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    return resp.headers.get("set-cookie", "").lower()


# ===========================================================================
# 1. Default (env var not set) → SameSite=None
# ===========================================================================


def test_default_samesite_is_none(monkeypatch):
    """1 — SESSION_COOKIE_SAMESITE not set → SameSite=None (cross-site staging default)."""
    sc = _set_cookie(monkeypatch, None)
    assert "samesite=none" in sc, f"Expected samesite=none in Set-Cookie; got: {sc!r}"


# ===========================================================================
# 2. Explicit "none" → SameSite=None
# ===========================================================================


def test_explicit_none_samesite(monkeypatch):
    """2 — SESSION_COOKIE_SAMESITE=none → SameSite=None."""
    sc = _set_cookie(monkeypatch, "none")
    assert "samesite=none" in sc


# ===========================================================================
# 3. "lax" → SameSite=Lax
# ===========================================================================


def test_lax_samesite(monkeypatch):
    """3 — SESSION_COOKIE_SAMESITE=lax → SameSite=Lax (same-site / custom domain)."""
    sc = _set_cookie(monkeypatch, "lax")
    assert "samesite=lax" in sc
    assert "samesite=none" not in sc


# ===========================================================================
# 4. "strict" → SameSite=Strict
# ===========================================================================


def test_strict_samesite(monkeypatch):
    """4 — SESSION_COOKIE_SAMESITE=strict → SameSite=Strict."""
    sc = _set_cookie(monkeypatch, "strict")
    assert "samesite=strict" in sc
    assert "samesite=none" not in sc


# ===========================================================================
# 5. Case-insensitive env var
# ===========================================================================


def test_samesite_env_is_case_insensitive(monkeypatch):
    """5 — SESSION_COOKIE_SAMESITE=LAX (uppercase) is accepted."""
    sc = _set_cookie(monkeypatch, "LAX")
    assert "samesite=lax" in sc


def test_samesite_env_mixed_case(monkeypatch):
    """6 — SESSION_COOKIE_SAMESITE=None (mixed case) is accepted."""
    sc = _set_cookie(monkeypatch, "None")
    assert "samesite=none" in sc


# ===========================================================================
# 6. Unknown value falls back to "none"
# ===========================================================================


def test_unknown_samesite_value_falls_back_to_none(monkeypatch):
    """7 — SESSION_COOKIE_SAMESITE=invalid → falls back to SameSite=None."""
    sc = _set_cookie(monkeypatch, "bogus-value")
    assert "samesite=none" in sc


# ===========================================================================
# 7. SameSite=None cookies retain HttpOnly + Secure
# ===========================================================================


def test_samesite_none_cookie_is_still_httponly(monkeypatch):
    """8 — SameSite=None cookie must still be HttpOnly."""
    sc = _set_cookie(monkeypatch, "none")
    assert "httponly" in sc


def test_samesite_none_cookie_is_still_secure(monkeypatch):
    """9 — SameSite=None requires Secure (browser mandates this for cross-site cookies)."""
    sc = _set_cookie(monkeypatch, "none")
    assert "secure" in sc


def test_samesite_none_cookie_has_max_age(monkeypatch):
    """10 — SameSite=None cookie still carries Max-Age."""
    sc = _set_cookie(monkeypatch, "none")
    assert "max-age=" in sc


# ===========================================================================
# 8. SameSite=Lax cookies retain HttpOnly + Secure
# ===========================================================================


def test_samesite_lax_cookie_is_still_httponly(monkeypatch):
    """11 — SameSite=Lax cookie must still be HttpOnly."""
    sc = _set_cookie(monkeypatch, "lax")
    assert "httponly" in sc


def test_samesite_lax_cookie_is_still_secure(monkeypatch):
    """12 — SameSite=Lax cookie must still be Secure."""
    sc = _set_cookie(monkeypatch, "lax")
    assert "secure" in sc


# ===========================================================================
# 9. Verify _get_cookie_samesite helper directly
# ===========================================================================


def test_get_cookie_samesite_default(monkeypatch):
    """13 — _get_cookie_samesite() returns 'none' when env var is absent."""
    monkeypatch.delenv("SESSION_COOKIE_SAMESITE", raising=False)
    from backend.app.api.routes.auth import _get_cookie_samesite
    assert _get_cookie_samesite() == "none"


def test_get_cookie_samesite_lax(monkeypatch):
    """14 — _get_cookie_samesite() returns 'lax' when SESSION_COOKIE_SAMESITE=lax."""
    monkeypatch.setenv("SESSION_COOKIE_SAMESITE", "lax")
    from backend.app.api.routes.auth import _get_cookie_samesite
    assert _get_cookie_samesite() == "lax"


def test_get_cookie_samesite_strict(monkeypatch):
    """15 — _get_cookie_samesite() returns 'strict' when SESSION_COOKIE_SAMESITE=strict."""
    monkeypatch.setenv("SESSION_COOKIE_SAMESITE", "strict")
    from backend.app.api.routes.auth import _get_cookie_samesite
    assert _get_cookie_samesite() == "strict"


def test_get_cookie_samesite_fallback_on_invalid(monkeypatch):
    """16 — _get_cookie_samesite() returns 'none' for unrecognised values."""
    monkeypatch.setenv("SESSION_COOKIE_SAMESITE", "whatever")
    from backend.app.api.routes.auth import _get_cookie_samesite
    assert _get_cookie_samesite() == "none"
