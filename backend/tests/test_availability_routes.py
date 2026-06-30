"""
Integration tests for availability API routes — PraxisMed Sprint 1 / Module 10

Strategy
--------
• All tests use FastAPI's synchronous TestClient — no real event loop needed.
• ``get_db_pool`` and ``get_config_loader`` are overridden via
  ``app.dependency_overrides`` so no real DB or filesystem access occurs.
• ``is_slot_bookable`` and ``suggest_available_slots`` are patched at their
  import site in the route module so no real availability logic runs.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import get_db_pool, get_config_loader

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CHECK_URL   = "/calendar/availability/check"
SUGGEST_URL = "/calendar/availability/suggest"

TENANT_ID = "11111111-1111-4111-8111-111111111111"
CLINIC_REF = TENANT_ID

T0 = datetime(2024, 6, 3, 9, 0, tzinfo=timezone.utc)
T1 = datetime(2024, 6, 3, 9, 30, tzinfo=timezone.utc)

CHECK_PAYLOAD = {
    "clinic_ref": CLINIC_REF,
    "starts_at": T0.isoformat(),
    "ends_at":   T1.isoformat(),
}

SUGGEST_PAYLOAD = {
    "clinic_ref": CLINIC_REF,
    "date": "2024-06-03",
    "limit": 3,
}

IS_SLOT_BOOKABLE = (
    "backend.app.api.routes.availability.availability_engine.is_slot_bookable"
)
SUGGEST_SLOTS = (
    "backend.app.api.routes.availability.availability_engine.suggest_available_slots"
)

FAKE_POOL = object()

# ---------------------------------------------------------------------------
# Shared fake config
# ---------------------------------------------------------------------------

def _make_fake_config(tenant_id: str = TENANT_ID) -> MagicMock:
    cfg = MagicMock()
    cfg.tenant_id = tenant_id
    return cfg


def _make_fake_loader(config: Any = None) -> MagicMock:
    cfg = config or _make_fake_config()
    loader = MagicMock()
    loader.load = AsyncMock(return_value=cfg)
    return loader


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client_full():
    """TestClient with both pool and config_loader overrides."""
    fake_config = _make_fake_config()
    fake_loader = _make_fake_loader(fake_config)
    app.dependency_overrides[get_db_pool]       = lambda: FAKE_POOL
    app.dependency_overrides[get_config_loader] = lambda: fake_loader
    yield TestClient(app), fake_loader, fake_config
    app.dependency_overrides.pop(get_db_pool,       None)
    app.dependency_overrides.pop(get_config_loader, None)


@pytest.fixture()
def client_no_pool():
    """TestClient with only config_loader override — no pool."""
    app.dependency_overrides.pop(get_db_pool, None)
    try:
        del app.state.db_pool
    except (AttributeError, KeyError):
        pass
    fake_loader = _make_fake_loader()
    app.dependency_overrides[get_config_loader] = lambda: fake_loader
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,       None)
    app.dependency_overrides.pop(get_config_loader, None)


@pytest.fixture()
def client_no_loader():
    """TestClient with only pool override — no config_loader."""
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides.pop(get_config_loader, None)
    try:
        del app.state.config_loader
    except (AttributeError, KeyError):
        pass
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,       None)
    app.dependency_overrides.pop(get_config_loader, None)


# ---------------------------------------------------------------------------
# 1. Check returns 200 and available=True
# ---------------------------------------------------------------------------

def test_check_availability_returns_200_available_true(client_full):
    client, _loader, _cfg = client_full
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)):
        response = client.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["available"] is True
    assert body["clinic_id"] == TENANT_ID


# ---------------------------------------------------------------------------
# 2. Check route calls config_loader.load
# ---------------------------------------------------------------------------

def test_check_route_calls_config_loader(client_full):
    client, fake_loader, _cfg = client_full
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)):
        client.post(CHECK_URL, json=CHECK_PAYLOAD)

    fake_loader.load.assert_awaited_once_with(CLINIC_REF)


# ---------------------------------------------------------------------------
# 3. Check route passes pool to is_slot_bookable
# ---------------------------------------------------------------------------

def test_check_route_passes_pool_to_engine(client_full):
    client, _loader, fake_config = client_full
    captured: list[Any] = []

    async def capture(pool, config, starts_at, ends_at):
        captured.append(pool)
        return True

    with patch(IS_SLOT_BOOKABLE, new=capture):
        client.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert len(captured) == 1
    assert captured[0] is FAKE_POOL


# ---------------------------------------------------------------------------
# 4. Check returns available=False when engine returns False
# ---------------------------------------------------------------------------

def test_check_availability_returns_available_false(client_full):
    client, _loader, _cfg = client_full
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=False)):
        response = client.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["available"] is False


# ---------------------------------------------------------------------------
# 5. Suggest returns 200 and a list of slots
# ---------------------------------------------------------------------------

def test_suggest_slots_returns_200_with_slots(client_full):
    client, _loader, _cfg = client_full
    fake_slots = [
        {"starts_at": T0, "ends_at": T1},
    ]
    with patch(SUGGEST_SLOTS, new=AsyncMock(return_value=fake_slots)):
        response = client.post(SUGGEST_URL, json=SUGGEST_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["clinic_id"] == TENANT_ID
    assert len(body["slots"]) == 1


# ---------------------------------------------------------------------------
# 6. Missing db_pool → 503
# ---------------------------------------------------------------------------

def test_missing_pool_returns_503(client_no_pool):
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)):
        response = client_no_pool.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert response.status_code == 503


# ---------------------------------------------------------------------------
# 7. Missing config_loader → 503
# ---------------------------------------------------------------------------

def test_missing_config_loader_returns_503(client_no_loader):
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)):
        response = client_no_loader.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert response.status_code == 503


# ---------------------------------------------------------------------------
# 8. Invalid request body → 422
# ---------------------------------------------------------------------------

def test_invalid_body_returns_422(client_full):
    client, _loader, _cfg = client_full
    response = client.post(CHECK_URL, json={"clinic_ref": ""})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 9. InvalidAvailabilityRangeError → 400
# ---------------------------------------------------------------------------

def test_engine_range_error_returns_400(client_full):
    from backend.app.modules.calendar_sync.availability_engine import (
        InvalidAvailabilityRangeError,
    )
    client, _loader, _cfg = client_full
    with patch(
        IS_SLOT_BOOKABLE,
        new=AsyncMock(side_effect=InvalidAvailabilityRangeError("bad range")),
    ):
        response = client.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# 10. Unexpected engine error → 500
# ---------------------------------------------------------------------------

def test_unexpected_engine_error_returns_500(client_full):
    client, _loader, _cfg = client_full
    with patch(
        IS_SLOT_BOOKABLE,
        new=AsyncMock(side_effect=RuntimeError("something exploded")),
    ):
        response = client.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert response.status_code == 500
    assert "Internal error" in response.json()["detail"]
