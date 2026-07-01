"""
Integration tests for webhook signature FastAPI dependencies — PraxisMed Sprint 5 / Module 46
Updated: Sprint 6 / Module 53 — alias header acceptance tests

Strategy:
- Tiny test-only FastAPI app with three routes, one per provider dependency.
- FastAPI TestClient; no real database or external service calls.
- monkeypatch sets/clears the secret env vars.
- Valid signatures are computed with the same HMAC helper used by production code.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.app.api.dependencies.webhook_signature import (
    verify_internal_webhook_signature_dependency,
    verify_n8n_webhook_signature_dependency,
    verify_vapi_webhook_signature_dependency,
)
from backend.app.core.webhook_signature import compute_hmac_sha256_signature

# ---------------------------------------------------------------------------
# Test-only FastAPI app
# ---------------------------------------------------------------------------

_test_app = FastAPI()

VAPI_ROUTE     = "/test/vapi-sig"
N8N_ROUTE      = "/test/n8n-sig"
INTERNAL_ROUTE = "/test/internal-sig"


@_test_app.post(VAPI_ROUTE)
async def _vapi_endpoint(_ok: bool = Depends(verify_vapi_webhook_signature_dependency)):
    return {"ok": True}


@_test_app.post(N8N_ROUTE)
async def _n8n_endpoint(_ok: bool = Depends(verify_n8n_webhook_signature_dependency)):
    return {"ok": True}


@_test_app.post(INTERNAL_ROUTE)
async def _internal_endpoint(_ok: bool = Depends(verify_internal_webhook_signature_dependency)):
    return {"ok": True}


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PAYLOAD      = b'{"event": "test"}'
VAPI_SECRET  = "test-vapi-secret"
N8N_SECRET   = "test-n8n-secret"
INT_SECRET   = "test-internal-secret"

VAPI_ENV     = "VAPI_WEBHOOK_SECRET"
N8N_ENV      = "N8N_WEBHOOK_SECRET"
INTERNAL_ENV = "INTERNAL_WEBHOOK_SECRET"

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    return TestClient(_test_app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _sig(payload: bytes, secret: str) -> str:
    return compute_hmac_sha256_signature(payload, secret)


# ===========================================================================
# Vapi dependency tests (1–4) — original
# ===========================================================================


def test_vapi_dependency_returns_200_with_valid_signature(client, monkeypatch):
    """Test 1 — Valid HMAC signature + secret in env → 200."""
    monkeypatch.setenv(VAPI_ENV, VAPI_SECRET)
    resp = client.post(
        VAPI_ROUTE,
        content=PAYLOAD,
        headers={"X-Vapi-Signature": _sig(PAYLOAD, VAPI_SECRET)},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_vapi_dependency_returns_401_with_missing_signature(client, monkeypatch):
    """Test 2 — Missing signature header → 401."""
    monkeypatch.setenv(VAPI_ENV, VAPI_SECRET)
    resp = client.post(VAPI_ROUTE, content=PAYLOAD)
    assert resp.status_code == 401


def test_vapi_dependency_returns_401_with_invalid_signature(client, monkeypatch):
    """Test 3 — Wrong signature value → 401."""
    monkeypatch.setenv(VAPI_ENV, VAPI_SECRET)
    resp = client.post(
        VAPI_ROUTE,
        content=PAYLOAD,
        headers={"X-Vapi-Signature": "sha256=deadbeefdeadbeef"},
    )
    assert resp.status_code == 401


def test_vapi_dependency_returns_503_when_secret_missing(client, monkeypatch):
    """Test 4 — VAPI_WEBHOOK_SECRET not set → 503."""
    monkeypatch.delenv(VAPI_ENV, raising=False)
    resp = client.post(
        VAPI_ROUTE,
        content=PAYLOAD,
        headers={"X-Vapi-Signature": "sha256=anysig"},
    )
    assert resp.status_code == 503


# ===========================================================================
# n8n dependency tests (5–6) — original
# ===========================================================================


def test_n8n_dependency_returns_200_with_valid_signature(client, monkeypatch):
    """Test 5 — Valid HMAC signature + n8n secret in env → 200."""
    monkeypatch.setenv(N8N_ENV, N8N_SECRET)
    resp = client.post(
        N8N_ROUTE,
        content=PAYLOAD,
        headers={"X-N8N-Signature": _sig(PAYLOAD, N8N_SECRET)},
    )
    assert resp.status_code == 200


def test_n8n_dependency_returns_401_with_invalid_signature(client, monkeypatch):
    """Test 6 — Wrong n8n signature → 401."""
    monkeypatch.setenv(N8N_ENV, N8N_SECRET)
    resp = client.post(
        N8N_ROUTE,
        content=PAYLOAD,
        headers={"X-N8N-Signature": "sha256=wrongwrongwrong"},
    )
    assert resp.status_code == 401


# ===========================================================================
# internal dependency tests (7–8) — original
# ===========================================================================


def test_internal_dependency_returns_200_with_valid_signature(client, monkeypatch):
    """Test 7 — Valid HMAC signature + internal secret in env → 200."""
    monkeypatch.setenv(INTERNAL_ENV, INT_SECRET)
    resp = client.post(
        INTERNAL_ROUTE,
        content=PAYLOAD,
        headers={"X-Internal-Signature": _sig(PAYLOAD, INT_SECRET)},
    )
    assert resp.status_code == 200


def test_dependency_verifies_raw_request_body_exactly(client, monkeypatch):
    """Test 8 — Signature must match the exact bytes of the request body."""
    monkeypatch.setenv(VAPI_ENV, VAPI_SECRET)
    different_payload = b'{"event": "different"}'
    # Compute sig over original PAYLOAD but send different_payload
    wrong_sig = _sig(PAYLOAD, VAPI_SECRET)
    resp = client.post(
        VAPI_ROUTE,
        content=different_payload,
        headers={"X-Vapi-Signature": wrong_sig},
    )
    assert resp.status_code == 401


# ===========================================================================
# Safety checks (9–10) — original
# ===========================================================================


def test_no_database_usage():
    """Test 9 — Dependency module does not import any database modules."""
    import backend.app.api.dependencies.webhook_signature as mod
    content = open(mod.__file__).read()
    assert "import asyncpg" not in content
    assert "import sqlalchemy" not in content
    assert "get_db_pool" not in content


def test_no_external_service_calls():
    """Test 10 — Dependency module does not import requests or httpx."""
    import backend.app.api.dependencies.webhook_signature as mod
    content = open(mod.__file__).read()
    assert "import requests" not in content
    assert "import httpx" not in content


# ===========================================================================
# Alias header acceptance (tests 11–15) — Module 53
# ===========================================================================


def test_vapi_dependency_accepts_x_vapi_hmac_sha256(client, monkeypatch):
    """Test 11 — Vapi dependency accepts X-Vapi-Hmac-Sha256 alias → 200."""
    monkeypatch.setenv(VAPI_ENV, VAPI_SECRET)
    resp = client.post(
        VAPI_ROUTE,
        content=PAYLOAD,
        headers={"X-Vapi-Hmac-Sha256": _sig(PAYLOAD, VAPI_SECRET)},
    )
    assert resp.status_code == 200


def test_vapi_dependency_accepts_x_signature(client, monkeypatch):
    """Test 12 — Vapi dependency accepts shared X-Signature alias → 200."""
    monkeypatch.setenv(VAPI_ENV, VAPI_SECRET)
    resp = client.post(
        VAPI_ROUTE,
        content=PAYLOAD,
        headers={"X-Signature": _sig(PAYLOAD, VAPI_SECRET)},
    )
    assert resp.status_code == 200


def test_n8n_dependency_accepts_x_signature(client, monkeypatch):
    """Test 13 — n8n dependency accepts shared X-Signature alias → 200."""
    monkeypatch.setenv(N8N_ENV, N8N_SECRET)
    resp = client.post(
        N8N_ROUTE,
        content=PAYLOAD,
        headers={"X-Signature": _sig(PAYLOAD, N8N_SECRET)},
    )
    assert resp.status_code == 200


def test_internal_dependency_accepts_x_signature(client, monkeypatch):
    """Test 14 — Internal dependency accepts shared X-Signature alias → 200."""
    monkeypatch.setenv(INTERNAL_ENV, INT_SECRET)
    resp = client.post(
        INTERNAL_ROUTE,
        content=PAYLOAD,
        headers={"X-Signature": _sig(PAYLOAD, INT_SECRET)},
    )
    assert resp.status_code == 200


def test_dependency_rejects_conflicting_signature_headers(client, monkeypatch):
    """Test 15 — Two accepted headers with different values → 401."""
    monkeypatch.setenv(VAPI_ENV, VAPI_SECRET)
    valid_sig   = _sig(PAYLOAD, VAPI_SECRET)
    invalid_sig = "sha256=deadbeefdeadbeef"
    resp = client.post(
        VAPI_ROUTE,
        content=PAYLOAD,
        headers={
            "X-Vapi-Signature": valid_sig,
            "X-Vapi-Hmac-Sha256": invalid_sig,
        },
    )
    assert resp.status_code == 401
