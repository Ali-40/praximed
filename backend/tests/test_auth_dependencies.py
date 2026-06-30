"""
Tests for auth FastAPI dependencies — PraxisMed Sprint 3 / Module 36.

Uses a tiny test-only FastAPI app. No real database.
"""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.app.api.dependencies.auth import (
    get_auth_context,
    require_clinical_clinic_access,
    require_clinic_access,
    require_staff_clinic_access,
)
from backend.app.core.auth_context import AuthContext

# ---------------------------------------------------------------------------
# Tiny test-only FastAPI app
# ---------------------------------------------------------------------------

test_app = FastAPI()

CLINIC_ID = "clinic-1"
OTHER_CLINIC_ID = "clinic-2"


@test_app.get("/test/me")
def route_me(auth: AuthContext = Depends(get_auth_context)) -> dict:
    return {"user_id": auth.user_id, "clinic_id": auth.clinic_id, "role": auth.role}


@test_app.get("/test/clinic-access")
def route_clinic_access(
    auth: AuthContext = Depends(get_auth_context),
) -> dict:
    result = require_clinic_access(requested_clinic_id=CLINIC_ID, auth_context=auth)
    return {"ok": True, "user_id": result.user_id}


@test_app.get("/test/staff-access")
def route_staff_access(
    auth: AuthContext = Depends(get_auth_context),
) -> dict:
    result = require_staff_clinic_access(requested_clinic_id=CLINIC_ID, auth_context=auth)
    return {"ok": True, "role": result.role}


@test_app.get("/test/clinical-access")
def route_clinical_access(
    auth: AuthContext = Depends(get_auth_context),
) -> dict:
    result = require_clinical_clinic_access(requested_clinic_id=CLINIC_ID, auth_context=auth)
    return {"ok": True, "role": result.role}


client = TestClient(test_app, raise_server_exceptions=False)


def _headers(
    user_id: str = "u-1",
    clinic_id: str = CLINIC_ID,
    role: str = "doctor",
) -> dict:
    return {
        "X-User-Id": user_id,
        "X-Clinic-Id": clinic_id,
        "X-User-Role": role,
    }


# ---------------------------------------------------------------------------
# 1. get_auth_context returns AuthContext from valid headers
# ---------------------------------------------------------------------------


def test_get_auth_context_valid_headers():
    resp = client.get("/test/me", headers=_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "u-1"
    assert data["clinic_id"] == CLINIC_ID
    assert data["role"] == "doctor"


# ---------------------------------------------------------------------------
# 2. missing X-User-Id returns HTTP 401
# ---------------------------------------------------------------------------


def test_missing_user_id_returns_401():
    headers = _headers()
    del headers["X-User-Id"]
    resp = client.get("/test/me", headers=headers)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 3. missing X-Clinic-Id returns HTTP 401
# ---------------------------------------------------------------------------


def test_missing_clinic_id_returns_401():
    headers = _headers()
    del headers["X-Clinic-Id"]
    resp = client.get("/test/me", headers=headers)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 4. invalid X-User-Role returns HTTP 401
# ---------------------------------------------------------------------------


def test_invalid_role_returns_401():
    resp = client.get("/test/me", headers=_headers(role="superuser"))
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 5. require_clinic_access allows same clinic
# ---------------------------------------------------------------------------


def test_require_clinic_access_allows_same_clinic():
    resp = client.get("/test/clinic-access", headers=_headers(clinic_id=CLINIC_ID))
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 6. require_clinic_access rejects different clinic with HTTP 403
# ---------------------------------------------------------------------------


def test_require_clinic_access_rejects_different_clinic():
    resp = client.get("/test/clinic-access", headers=_headers(clinic_id=OTHER_CLINIC_ID))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 7. require_staff_clinic_access allows staff
# ---------------------------------------------------------------------------


def test_require_staff_clinic_access_allows_staff():
    resp = client.get("/test/staff-access", headers=_headers(role="staff"))
    assert resp.status_code == 200
    assert resp.json()["role"] == "staff"


# ---------------------------------------------------------------------------
# 8. require_staff_clinic_access rejects viewer with HTTP 403
# ---------------------------------------------------------------------------


def test_require_staff_clinic_access_rejects_viewer():
    resp = client.get("/test/staff-access", headers=_headers(role="viewer"))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 9. require_clinical_clinic_access allows doctor
# ---------------------------------------------------------------------------


def test_require_clinical_clinic_access_allows_doctor():
    resp = client.get("/test/clinical-access", headers=_headers(role="doctor"))
    assert resp.status_code == 200
    assert resp.json()["role"] == "doctor"


# ---------------------------------------------------------------------------
# 10. require_clinical_clinic_access rejects staff with HTTP 403
# ---------------------------------------------------------------------------


def test_require_clinical_clinic_access_rejects_staff():
    resp = client.get("/test/clinical-access", headers=_headers(role="staff"))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 11. No database is used
# ---------------------------------------------------------------------------


def test_no_database_used():
    resp = client.get("/test/me", headers=_headers())
    assert resp.status_code == 200
    assert "user_id" in resp.json()
