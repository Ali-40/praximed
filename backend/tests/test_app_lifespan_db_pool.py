"""
Tests for FastAPI app lifespan DB pool startup/shutdown — PraxisMed Sprint 5 / Module 49

Strategy:
- Use TestClient as a context manager (``with TestClient(app) as client:``) to
  trigger startup and shutdown lifespan events.
- Monkeypatch create_db_pool so no real asyncpg connection is ever made.
- A MagicMock pool with an AsyncMock close() method stands in for asyncpg.Pool.
- Tests are completely isolated from Docker/PostgreSQL.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CREATE_POOL = "backend.app.main.create_db_pool"
CLOSE_POOL  = "backend.app.main.close_db_pool"
FAKE_DB_URL = "postgresql://fakeuser:fakepass@localhost:5433/fakedb"


def _make_fake_pool() -> MagicMock:
    """Return a MagicMock that looks enough like asyncpg.Pool for the lifespan."""
    pool = MagicMock()
    pool.close = AsyncMock()
    return pool


# ===========================================================================
# Startup — missing DATABASE_URL (tests 1–2)
# ===========================================================================


def test_startup_with_missing_database_url_does_not_crash(monkeypatch):
    """Test 1 — App starts without DATABASE_URL and does not raise."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(app):
        pass  # if we reach here startup did not crash


def test_startup_with_missing_database_url_sets_db_pool_to_none(monkeypatch):
    """Test 2 — Without DATABASE_URL app.state.db_pool is None after startup."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(app):
        assert app.state.db_pool is None


# ===========================================================================
# Startup — DATABASE_URL present (tests 3–4)
# ===========================================================================


def test_startup_with_database_url_calls_create_db_pool(monkeypatch):
    """Test 3 — create_db_pool is called once when DATABASE_URL is set."""
    monkeypatch.setenv("DATABASE_URL", FAKE_DB_URL)
    fake_pool = _make_fake_pool()
    with patch(CREATE_POOL, new=AsyncMock(return_value=fake_pool)) as mock_create:
        with TestClient(app):
            mock_create.assert_awaited_once()


def test_startup_stores_created_pool_in_app_state(monkeypatch):
    """Test 4 — The pool returned by create_db_pool is stored in app.state.db_pool."""
    monkeypatch.setenv("DATABASE_URL", FAKE_DB_URL)
    fake_pool = _make_fake_pool()
    with patch(CREATE_POOL, new=AsyncMock(return_value=fake_pool)):
        with TestClient(app):
            assert app.state.db_pool is fake_pool


# ===========================================================================
# Shutdown (tests 5–7)
# ===========================================================================


def test_shutdown_closes_existing_pool(monkeypatch):
    """Test 5 — pool.close() is awaited once during shutdown."""
    monkeypatch.setenv("DATABASE_URL", FAKE_DB_URL)
    fake_pool = _make_fake_pool()
    with patch(CREATE_POOL, new=AsyncMock(return_value=fake_pool)):
        with TestClient(app):
            pass  # TestClient __exit__ triggers shutdown
    fake_pool.close.assert_awaited_once()


def test_shutdown_sets_db_pool_to_none(monkeypatch):
    """Test 6 — app.state.db_pool is None after shutdown."""
    monkeypatch.setenv("DATABASE_URL", FAKE_DB_URL)
    fake_pool = _make_fake_pool()
    with patch(CREATE_POOL, new=AsyncMock(return_value=fake_pool)):
        with TestClient(app):
            pass
    assert app.state.db_pool is None


def test_shutdown_handles_missing_db_pool_safely(monkeypatch):
    """Test 7 — Shutdown does not crash when db_pool was never set (None)."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(app):
        pass  # startup sets pool=None; shutdown must not crash


# ===========================================================================
# Safety and integration (tests 8–9)
# ===========================================================================


def test_lifecycle_does_not_connect_to_real_database(monkeypatch):
    """Test 8 — create_db_pool is mocked; no real asyncpg connection is made."""
    monkeypatch.setenv("DATABASE_URL", FAKE_DB_URL)
    fake_pool = _make_fake_pool()
    with patch(CREATE_POOL, new=AsyncMock(return_value=fake_pool)) as mock_create:
        with TestClient(app):
            # The mock was used — real asyncpg.create_pool was never called
            mock_create.assert_awaited_once_with(FAKE_DB_URL)
        # After shutdown the fake pool's close() was called, not a real conn
        fake_pool.close.assert_awaited_once()


def test_existing_health_route_still_works(monkeypatch):
    """Test 9 — GET /health returns 200 regardless of db_pool state."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
