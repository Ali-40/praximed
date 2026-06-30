"""
Tests for health routes — PraxisMed Sprint 1 / Module 7

Uses FastAPI's synchronous TestClient (backed by httpx) so no async
test infrastructure is required.  No database connection is made.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /health — liveness probe
# ---------------------------------------------------------------------------


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_expected_json():
    response = client.get("/health")
    body = response.json()
    assert body["status"]  == "ok"
    assert body["service"] == "PraxisMed API"


def test_health_content_type_is_json():
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]


# ---------------------------------------------------------------------------
# GET /health/ready — readiness probe
# ---------------------------------------------------------------------------


def test_health_ready_returns_200():
    response = client.get("/health/ready")
    assert response.status_code == 200


def test_health_ready_returns_expected_json():
    response = client.get("/health/ready")
    body = response.json()
    assert body["status"]          == "ready"
    assert body["checks"]["app"]   == "ok"


def test_health_ready_content_type_is_json():
    response = client.get("/health/ready")
    assert "application/json" in response.headers["content-type"]


# ---------------------------------------------------------------------------
# App meta — confirm import and title
# ---------------------------------------------------------------------------


def test_app_title():
    assert app.title == "PraxisMed API"


def test_app_version():
    assert app.version == "0.1.0"


# ---------------------------------------------------------------------------
# Non-existent routes return 404
# ---------------------------------------------------------------------------


def test_unknown_route_returns_404():
    response = client.get("/does-not-exist")
    assert response.status_code == 404
