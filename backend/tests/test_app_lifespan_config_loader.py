"""
Tests for config_loader lifespan wiring — PraxisMed Sprint 11 / Module 84

Verifies that app.state.config_loader is initialized on startup and cleared on
shutdown, without making real filesystem or database calls.

Strategy:
- Use TestClient as a context manager to trigger lifespan startup/shutdown.
- Monkeypatch DATABASE_URL when needed; patch create_db_pool to avoid real asyncpg.
- ClinicConfigLoader is a pure Python class — no patching needed; it does not open
  filesystem or database connections on __init__.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config_loader import ClinicConfigLoader
from backend.app.main import app

CREATE_POOL = "backend.app.main.create_db_pool"
FAKE_DB_URL = "postgresql://fakeuser:fakepass@localhost:5433/fakedb"


def _make_fake_pool() -> MagicMock:
    pool = MagicMock()
    pool.close = AsyncMock()
    return pool


# ---------------------------------------------------------------------------
# 1. config_loader initialized even without DATABASE_URL
# ---------------------------------------------------------------------------

def test_startup_sets_config_loader_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(app):
        assert app.state.config_loader is not None


# ---------------------------------------------------------------------------
# 2. config_loader is a ClinicConfigLoader instance
# ---------------------------------------------------------------------------

def test_startup_config_loader_is_clinic_config_loader_instance(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(app):
        assert isinstance(app.state.config_loader, ClinicConfigLoader)


# ---------------------------------------------------------------------------
# 3. config_loader initialized with pool when DATABASE_URL is set
# ---------------------------------------------------------------------------

def test_startup_config_loader_receives_db_pool(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", FAKE_DB_URL)
    fake_pool = _make_fake_pool()
    with patch(CREATE_POOL, new=AsyncMock(return_value=fake_pool)):
        with TestClient(app):
            # The config_loader's internal pool should be the db_pool
            assert app.state.config_loader._pool is fake_pool


# ---------------------------------------------------------------------------
# 4. config_loader pool is None when DATABASE_URL is absent
# ---------------------------------------------------------------------------

def test_startup_config_loader_has_no_pool_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(app):
        assert app.state.config_loader._pool is None


# ---------------------------------------------------------------------------
# 5. shutdown sets config_loader to None
# ---------------------------------------------------------------------------

def test_shutdown_sets_config_loader_to_none(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(app):
        pass  # TestClient __exit__ triggers shutdown
    assert app.state.config_loader is None


# ---------------------------------------------------------------------------
# 6. shutdown sets config_loader to None even when db_pool was set
# ---------------------------------------------------------------------------

def test_shutdown_config_loader_none_with_db_pool(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", FAKE_DB_URL)
    fake_pool = _make_fake_pool()
    with patch(CREATE_POOL, new=AsyncMock(return_value=fake_pool)):
        with TestClient(app):
            pass
    assert app.state.config_loader is None


# ---------------------------------------------------------------------------
# 7. db_pool lifespan still works correctly alongside config_loader
# ---------------------------------------------------------------------------

def test_db_pool_startup_still_works_with_config_loader(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", FAKE_DB_URL)
    fake_pool = _make_fake_pool()
    with patch(CREATE_POOL, new=AsyncMock(return_value=fake_pool)):
        with TestClient(app):
            assert app.state.db_pool is fake_pool
            assert app.state.config_loader is not None


# ---------------------------------------------------------------------------
# 8. health route still works after config_loader wiring
# ---------------------------------------------------------------------------

def test_health_route_works_after_config_loader_wiring(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(app) as client:
        resp = client.get("/health")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 9. db_pool shutdown unchanged — pool.close() still called
# ---------------------------------------------------------------------------

def test_db_pool_close_still_called_on_shutdown(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", FAKE_DB_URL)
    fake_pool = _make_fake_pool()
    with patch(CREATE_POOL, new=AsyncMock(return_value=fake_pool)):
        with TestClient(app):
            pass
    fake_pool.close.assert_awaited_once()
