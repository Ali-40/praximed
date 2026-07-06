"""
Sprint 19 / Module 135 — Tenant Provisioning Backend Foundation.

Static + unit + route integration tests.
Fake data only. No real PHI. No secrets. No Vapi credentials.
No real database connection.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app
from backend.app.services.tenant_provisioning import (
    PROVISIONING_MESSAGE,
    ProvisioningBlockedError,
    ProvisioningNotFoundError,
    provision_clinic_shell_from_onboarding_request,
)

ROOT       = pathlib.Path(__file__).parent.parent.parent
SERVICE    = ROOT / "backend" / "app" / "services" / "tenant_provisioning.py"
ROUTE_FILE = ROOT / "backend" / "app" / "api" / "routes" / "clinic_onboarding.py"
ARCH_DOC   = ROOT / "docs" / "architecture" / "TENANT_PROVISIONING_BACKEND_FOUNDATION.md"

# ---------------------------------------------------------------------------
# Fake data — no real PHI, no real clinic names
# ---------------------------------------------------------------------------

FAKE_REQUEST_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
FAKE_CLINIC_ID  = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"

FAKE_APPROVED_REQUEST: Dict[str, Any] = {
    "id":                    FAKE_REQUEST_ID,
    "clinic_name":           "Demo Wahlarzt Praxis Wien",
    "doctor_name":           "Dr. Demo Arzt",
    "contact_email":         "demo.clinic@example.test",
    "status":                "pilot_approved",
    "preferred_language":    "de",
    "fallback_language":     "en",
    "supported_languages":   ["de", "en"],
    "specialty":             "Allgemeinmedizin",
    "city":                  "Wien",
    "production_phi_enabled": False,
    "consent_pilot_contact": True,
    "acknowledges_no_phi":   True,
}

FAKE_CLINIC_ROW: Dict[str, Any] = {
    "id":             FAKE_CLINIC_ID,
    "slug":           "demo-wahlarzt-praxis-wien-abc12345",
    "name":           "Demo Wahlarzt Praxis Wien",
    "status":         "pilot_setup",
    "locale":         "de-AT",
    "timezone":       "Europe/Vienna",
    "config_path":    None,
    "config_version": 1,
    "created_at":     "2026-07-06T10:00:00+00:00",
    "updated_at":     "2026-07-06T10:00:00+00:00",
}

FAKE_AUDIT_ROW: Dict[str, Any] = {
    "id":            "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
    "clinic_id":     FAKE_CLINIC_ID,
    "action":        "create_clinic_shell",
    "resource_type": "clinic_onboarding_request",
    "resource_id":   FAKE_REQUEST_ID,
    "metadata":      {"_result": "success", "_severity": "info"},
}

_EXISTING_METADATA = {
    "clinic_id":              FAKE_CLINIC_ID,
    "clinic_name":            "Demo Wahlarzt Praxis Wien",
    "clinic_slug":            "demo-wahlarzt-praxis-wien-abc12345",
    "preferred_language":     "de",
    "fallback_language":      "en",
    "supported_languages":    ["de", "en"],
    "production_phi_enabled": False,
    "message":                PROVISIONING_MESSAGE,
    "_result":                "success",
    "_severity":              "info",
}


def _pool_for_new_provisioning() -> AsyncMock:
    """Pool mock: idempotency check → None; clinic INSERT → FAKE_CLINIC_ROW."""
    pool = AsyncMock()
    pool.fetchrow.side_effect = [None, FAKE_CLINIC_ROW]
    return pool


def _pool_for_already_provisioned() -> AsyncMock:
    """Pool mock: idempotency check finds existing audit row."""
    pool = AsyncMock()
    pool.fetchrow.return_value = {"metadata": json.dumps(_EXISTING_METADATA)}
    return pool


def _staff_auth() -> AuthContext:
    return AuthContext(
        user_id="staff-user-001",
        clinic_id="11111111-1111-4111-8111-111111111111",
        role="staff",
        auth_scheme="jwt_bearer",
    )


FAKE_POOL = MagicMock()


@pytest.fixture()
def client_auth():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_current_user] = _staff_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def client_unauth():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides.pop(get_current_user, None)
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)


# ---------------------------------------------------------------------------
# 1. Static checks — file existence and key strings
# ---------------------------------------------------------------------------

class TestStaticFiles:
    def test_service_file_exists(self):
        assert SERVICE.exists(), f"Service file not found: {SERVICE}"

    def test_route_file_has_provision_endpoint(self):
        assert "provision-clinic-shell" in ROUTE_FILE.read_text()

    def test_route_provision_requires_auth(self):
        text = ROUTE_FILE.read_text()
        # The provision route must use get_current_user
        provision_idx = text.find("provision-clinic-shell")
        after = text[provision_idx:]
        assert "get_current_user" in after

    def test_arch_doc_exists(self):
        assert ARCH_DOC.exists(), f"Arch doc not found: {ARCH_DOC}"

    def test_service_imports_onboarding_repo(self):
        assert "clinic_onboarding_repo" in SERVICE.read_text()

    def test_service_imports_audit_repo(self):
        assert "audit_repo" in SERVICE.read_text()

    def test_service_has_pilot_approved_guard(self):
        assert "pilot_approved" in SERVICE.read_text()

    def test_service_production_phi_false_comment_or_code(self):
        text = SERVICE.read_text()
        assert "production_phi_enabled" in text
        assert "False" in text

    def test_no_vapi_credentials_in_service(self):
        text = SERVICE.read_text().lower()
        assert "vapi_api_key" not in text
        assert "vapi_secret" not in text

    def test_no_patient_insert_in_service(self):
        text = SERVICE.read_text()
        assert "INSERT INTO patients" not in text

    def test_public_submit_does_not_call_provision(self):
        text = ROUTE_FILE.read_text()
        start = text.find("async def submit_clinic_onboarding_request")
        end = text.find("async def ", start + 1)
        body = text[start:end]
        assert "provision" not in body.lower()


# ---------------------------------------------------------------------------
# 2. Service — blocking cases
# ---------------------------------------------------------------------------

_PATCH_GET = "backend.app.services.tenant_provisioning.clinic_onboarding_repo.get_clinic_onboarding_request_by_id"
_PATCH_AUDIT = "backend.app.services.tenant_provisioning.audit_repo.create_audit_log"


class TestProvisioningBlockedCases:
    @pytest.mark.asyncio
    async def test_missing_request_raises_not_found(self):
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=None):
            with pytest.raises(ProvisioningNotFoundError):
                await provision_clinic_shell_from_onboarding_request(
                    AsyncMock(), "nonexistent-id"
                )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("bad_status", [
        "submitted", "reviewed", "demo_booked", "rejected", "archived"
    ])
    async def test_non_pilot_approved_raises_blocked(self, bad_status: str):
        req = {**FAKE_APPROVED_REQUEST, "status": bad_status}
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=req):
            with pytest.raises(ProvisioningBlockedError) as exc_info:
                await provision_clinic_shell_from_onboarding_request(
                    AsyncMock(), FAKE_REQUEST_ID
                )
        assert bad_status in str(exc_info.value)


# ---------------------------------------------------------------------------
# 3. Service — successful provisioning
# ---------------------------------------------------------------------------

class TestProvisioningSuccess:
    @pytest.mark.asyncio
    async def test_pilot_approved_creates_clinic(self):
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW):
            result = await provision_clinic_shell_from_onboarding_request(
                pool, FAKE_REQUEST_ID, actor_user_id="staff-user-001"
            )
        assert result["clinic_id"] == FAKE_CLINIC_ID
        assert result["already_provisioned"] is False

    @pytest.mark.asyncio
    async def test_production_phi_always_false(self):
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW):
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        assert result["production_phi_enabled"] is False

    @pytest.mark.asyncio
    async def test_language_config_preserved(self):
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW):
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        assert result["preferred_language"] == "de"
        assert result["fallback_language"] == "en"
        assert "de" in result["supported_languages"]
        assert "en" in result["supported_languages"]

    @pytest.mark.asyncio
    async def test_message_says_phi_disabled(self):
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW):
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        assert "Production PHI remains disabled" in result["message"]

    @pytest.mark.asyncio
    async def test_no_vapi_credentials_in_result(self):
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW):
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        result_str = str(result).lower()
        assert "vapi_api_key" not in result_str
        assert "vapi_secret" not in result_str
        assert "password" not in result_str

    @pytest.mark.asyncio
    async def test_audit_event_recorded(self):
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW) as mock_audit:
            await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        mock_audit.assert_called_once()
        kwargs = mock_audit.call_args[1]
        assert kwargs["action"] == "create_clinic_shell"
        assert kwargs["resource_type"] == "clinic_onboarding_request"
        assert kwargs["resource_id"] == FAKE_REQUEST_ID

    @pytest.mark.asyncio
    async def test_clinic_name_in_result(self):
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW):
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        assert result["clinic_name"] == "Demo Wahlarzt Praxis Wien"

    @pytest.mark.asyncio
    async def test_slug_derived_from_name(self):
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW):
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        assert "demo" in result["clinic_slug"].lower()

    @pytest.mark.asyncio
    async def test_supported_languages_json_string_handled(self):
        req = {**FAKE_APPROVED_REQUEST, "supported_languages": '["de","en"]'}
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=req), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW):
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        assert isinstance(result["supported_languages"], list)
        assert "de" in result["supported_languages"]

    @pytest.mark.asyncio
    async def test_onboarding_request_id_in_result(self):
        pool = _pool_for_new_provisioning()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock, return_value=FAKE_AUDIT_ROW):
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        assert result["onboarding_request_id"] == FAKE_REQUEST_ID


# ---------------------------------------------------------------------------
# 4. Idempotency
# ---------------------------------------------------------------------------

class TestIdempotency:
    @pytest.mark.asyncio
    async def test_already_provisioned_returns_existing_clinic(self):
        pool = _pool_for_already_provisioned()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock) as mock_audit:
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        assert result["already_provisioned"] is True
        assert result["clinic_id"] == FAKE_CLINIC_ID
        assert result["production_phi_enabled"] is False
        mock_audit.assert_not_called()

    @pytest.mark.asyncio
    async def test_already_provisioned_no_duplicate_clinic_insert(self):
        pool = _pool_for_already_provisioned()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock):
            await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        # Only one pool.fetchrow call (idempotency check) — no INSERT
        pool.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_already_provisioned_message_preserved(self):
        pool = _pool_for_already_provisioned()
        with patch(_PATCH_GET, new_callable=AsyncMock, return_value=FAKE_APPROVED_REQUEST), \
             patch(_PATCH_AUDIT, new_callable=AsyncMock):
            result = await provision_clinic_shell_from_onboarding_request(pool, FAKE_REQUEST_ID)
        assert "Production PHI remains disabled" in result["message"]


# ---------------------------------------------------------------------------
# 5. Route integration tests
# ---------------------------------------------------------------------------

PROVISION_URL = f"/clinic-onboarding-requests/{FAKE_REQUEST_ID}/provision-clinic-shell"

_SUCCESS_RESULT = {
    "onboarding_request_id": FAKE_REQUEST_ID,
    "clinic_id":             FAKE_CLINIC_ID,
    "clinic_name":           "Demo Wahlarzt Praxis Wien",
    "clinic_slug":           "demo-wahlarzt-praxis-wien-abc12345",
    "preferred_language":    "de",
    "fallback_language":     "en",
    "supported_languages":   ["de", "en"],
    "production_phi_enabled": False,
    "message":               PROVISIONING_MESSAGE,
    "already_provisioned":   False,
}

_PATCH_SVC = "backend.app.services.tenant_provisioning.provision_clinic_shell_from_onboarding_request"


class TestProvisionRoute:
    def test_requires_auth(self, client_unauth):
        resp = client_unauth.post(PROVISION_URL)
        assert resp.status_code == 401

    def test_not_found_returns_404(self, client_auth):
        with patch(_PATCH_SVC, new_callable=AsyncMock,
                   side_effect=ProvisioningNotFoundError("not found")):
            resp = client_auth.post(PROVISION_URL)
        assert resp.status_code == 404

    def test_blocked_returns_409(self, client_auth):
        with patch(_PATCH_SVC, new_callable=AsyncMock,
                   side_effect=ProvisioningBlockedError("not pilot_approved")):
            resp = client_auth.post(PROVISION_URL)
        assert resp.status_code == 409

    def test_success_returns_200(self, client_auth):
        with patch(_PATCH_SVC, new_callable=AsyncMock, return_value=_SUCCESS_RESULT):
            resp = client_auth.post(PROVISION_URL)
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_response_has_clinic_id(self, client_auth):
        with patch(_PATCH_SVC, new_callable=AsyncMock, return_value=_SUCCESS_RESULT):
            resp = client_auth.post(PROVISION_URL)
        assert resp.json()["clinic_id"] == FAKE_CLINIC_ID

    def test_response_production_phi_false(self, client_auth):
        with patch(_PATCH_SVC, new_callable=AsyncMock, return_value=_SUCCESS_RESULT):
            resp = client_auth.post(PROVISION_URL)
        assert resp.json()["production_phi_enabled"] is False

    def test_response_message_says_phi_disabled(self, client_auth):
        with patch(_PATCH_SVC, new_callable=AsyncMock, return_value=_SUCCESS_RESULT):
            resp = client_auth.post(PROVISION_URL)
        assert "Production PHI remains disabled" in resp.json()["message"]

    def test_response_has_no_secrets(self, client_auth):
        with patch(_PATCH_SVC, new_callable=AsyncMock, return_value=_SUCCESS_RESULT):
            resp = client_auth.post(PROVISION_URL)
        resp_str = str(resp.json()).lower()
        assert "vapi_api_key" not in resp_str
        assert "password" not in resp_str
        assert "sk-" not in resp_str

    def test_response_has_language_fields(self, client_auth):
        with patch(_PATCH_SVC, new_callable=AsyncMock, return_value=_SUCCESS_RESULT):
            resp = client_auth.post(PROVISION_URL)
        data = resp.json()
        assert data["preferred_language"] == "de"
        assert data["fallback_language"] == "en"


# ---------------------------------------------------------------------------
# 6. Architecture doc checks
# ---------------------------------------------------------------------------

class TestArchDoc:
    def test_doc_mentions_pilot_approved_precondition(self):
        assert "pilot_approved" in ARCH_DOC.read_text()

    def test_doc_mentions_no_phi(self):
        text = ARCH_DOC.read_text()
        assert "NO-GO" in text or "production_phi_enabled" in text

    def test_doc_mentions_no_vapi_credentials(self):
        text = ARCH_DOC.read_text().lower()
        assert "vapi" in text
        assert "not stored" in text or "not accepted" in text or "no vapi" in text

    def test_doc_mentions_audit_log(self):
        assert "audit" in ARCH_DOC.read_text().lower()

    def test_doc_mentions_no_automatic_provisioning(self):
        text = ARCH_DOC.read_text().lower()
        assert "not automatically" in text or "no automatic" in text or "does not auto" in text

    def test_doc_mentions_language_preservation(self):
        assert "language" in ARCH_DOC.read_text().lower()

    def test_doc_mentions_idempotency(self):
        assert "idempotent" in ARCH_DOC.read_text().lower() or "idempotency" in ARCH_DOC.read_text().lower()

    def test_doc_mentions_pilot_setup_status(self):
        assert "pilot_setup" in ARCH_DOC.read_text()
