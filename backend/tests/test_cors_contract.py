"""
CORS contract tests — PraxisMed Sprint 9 / Module 74.

Verifies that the FastAPI app correctly handles CORS preflight requests from
the local frontend origins and rejects unknown origins.

Strategy:
- Use FastAPI TestClient (no real HTTP; ASGI middleware is active).
- No database or auth needed — CORS middleware handles OPTIONS before routes.
- No external services.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app, _cors_origins, _DEFAULT_CORS_ORIGINS

client = TestClient(app, raise_server_exceptions=False)

_PREFLIGHT_HEADERS = {
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "Content-Type, Authorization",
}


# ---------------------------------------------------------------------------
# 1. OPTIONS /auth/login from localhost:3000 returns allow-origin
# ---------------------------------------------------------------------------

def test_options_auth_login_from_localhost_3000_returns_allow_origin():
    resp = client.options(
        "/auth/login",
        headers={"Origin": "http://localhost:3000", **_PREFLIGHT_HEADERS},
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000", (
        "CORSMiddleware must echo the allowed origin back in the preflight response"
    )


# ---------------------------------------------------------------------------
# 2. OPTIONS /auth/login allows POST method
# ---------------------------------------------------------------------------

def test_options_auth_login_allows_post():
    resp = client.options(
        "/auth/login",
        headers={"Origin": "http://localhost:3000", **_PREFLIGHT_HEADERS},
    )
    allowed = resp.headers.get("access-control-allow-methods", "")
    assert "POST" in allowed, (
        "CORSMiddleware preflight must include POST in Access-Control-Allow-Methods"
    )


# ---------------------------------------------------------------------------
# 3. OPTIONS allows Content-Type header
# ---------------------------------------------------------------------------

def test_options_allows_content_type_header():
    resp = client.options(
        "/auth/login",
        headers={"Origin": "http://localhost:3000", **_PREFLIGHT_HEADERS},
    )
    allowed = resp.headers.get("access-control-allow-headers", "").lower()
    assert "content-type" in allowed, (
        "CORSMiddleware preflight must permit the Content-Type header"
    )


# ---------------------------------------------------------------------------
# 4. OPTIONS allows Authorization header
# ---------------------------------------------------------------------------

def test_options_allows_authorization_header():
    resp = client.options(
        "/auth/login",
        headers={"Origin": "http://localhost:3000", **_PREFLIGHT_HEADERS},
    )
    allowed = resp.headers.get("access-control-allow-headers", "").lower()
    assert "authorization" in allowed, (
        "CORSMiddleware preflight must permit the Authorization header"
    )


# ---------------------------------------------------------------------------
# 5. OPTIONS from 127.0.0.1:3000 is also allowed
# ---------------------------------------------------------------------------

def test_options_from_127_0_0_1_3000_is_allowed():
    resp = client.options(
        "/auth/login",
        headers={"Origin": "http://127.0.0.1:3000", **_PREFLIGHT_HEADERS},
    )
    assert resp.headers.get("access-control-allow-origin") == "http://127.0.0.1:3000", (
        "http://127.0.0.1:3000 must be in the allowed CORS origins"
    )


# ---------------------------------------------------------------------------
# 6. Unknown origin is not echoed back
# ---------------------------------------------------------------------------

def test_unknown_origin_is_not_allowed():
    resp = client.options(
        "/auth/login",
        headers={
            "Origin": "http://evil.example.com",
            **_PREFLIGHT_HEADERS,
        },
    )
    allow_origin = resp.headers.get("access-control-allow-origin", "")
    assert allow_origin != "http://evil.example.com", (
        "An unknown origin must not receive an Access-Control-Allow-Origin header "
        "matching that origin"
    )
    assert allow_origin != "*", (
        "Wildcard origin must never be returned"
    )


# ---------------------------------------------------------------------------
# 7. CORS config does not use wildcard origin with credentials
# ---------------------------------------------------------------------------

def test_cors_config_no_wildcard_with_credentials():
    origins = _cors_origins()
    assert "*" not in origins, (
        "allow_origins must never contain '*' — only explicit origins are permitted"
    )
    for origin in origins:
        assert origin != "*", f"Found wildcard in allowed origins: {origins!r}"


# ---------------------------------------------------------------------------
# 8. GET /health still works after CORS middleware is installed
# ---------------------------------------------------------------------------

def test_health_route_still_works():
    resp = client.get("/health")
    assert resp.status_code == 200, (
        "GET /health must still return 200 after CORSMiddleware is added"
    )
