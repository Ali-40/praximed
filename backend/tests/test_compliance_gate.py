"""
Compliance gate tests — Sprint 19 / Module 130.

Tests enforcement of the production PHI circuit breaker and pseudonymization pipeline.
Uses monkeypatch for env isolation. No database. No network. No real patient data. No secrets.
"""

from __future__ import annotations

import importlib

import pytest


# ---------------------------------------------------------------------------
# 1. Production auth gate: blocks unsafe AUTH_METHOD in production
# ---------------------------------------------------------------------------


def test_production_auth_gate_blocks_bearer_session_storage(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_METHOD", "BEARER_SESSION_STORAGE")
    from backend.app.core import compliance
    importlib.reload(compliance)
    with pytest.raises(AssertionError, match="COOKIE_HTTPONLY"):
        compliance.assert_production_auth_ready()


def test_production_cookie_auth_passes(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
    from backend.app.core import compliance
    importlib.reload(compliance)
    compliance.assert_production_auth_ready()  # must not raise


# ---------------------------------------------------------------------------
# 2. Production safeguard: blocks PHI when PRODUCTION_COMPLIANCE_UNLOCKED not set
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_production_safeguard_blocks_when_not_unlocked_unset(monkeypatch):
    from fastapi import HTTPException
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
    monkeypatch.delenv("PRODUCTION_COMPLIANCE_UNLOCKED", raising=False)
    from backend.app.core import compliance
    importlib.reload(compliance)
    with pytest.raises(HTTPException) as exc_info:
        await compliance.enforce_phi_safeguard()
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_production_safeguard_blocks_when_explicitly_false(monkeypatch):
    from fastapi import HTTPException
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
    monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "false")
    from backend.app.core import compliance
    importlib.reload(compliance)
    with pytest.raises(HTTPException) as exc_info:
        await compliance.enforce_phi_safeguard()
    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# 3. Production safeguard: passes only when explicitly unlocked
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_production_safeguard_passes_when_unlocked(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
    monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "true")
    from backend.app.core import compliance
    importlib.reload(compliance)
    await compliance.enforce_phi_safeguard()  # must not raise


@pytest.mark.asyncio
async def test_production_safeguard_passes_with_truthy_1(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
    monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "1")
    from backend.app.core import compliance
    importlib.reload(compliance)
    await compliance.enforce_phi_safeguard()  # must not raise


# ---------------------------------------------------------------------------
# 4. Staging does not block
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_staging_does_not_block(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.delenv("PRODUCTION_COMPLIANCE_UNLOCKED", raising=False)
    from backend.app.core import compliance
    importlib.reload(compliance)
    await compliance.enforce_phi_safeguard()  # must not raise


@pytest.mark.asyncio
async def test_local_does_not_block(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.delenv("PRODUCTION_COMPLIANCE_UNLOCKED", raising=False)
    from backend.app.core import compliance
    importlib.reload(compliance)
    await compliance.enforce_phi_safeguard()  # must not raise


@pytest.mark.asyncio
async def test_staging_does_not_block_even_with_wrong_auth_method(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("AUTH_METHOD", "BEARER_SESSION_STORAGE")
    from backend.app.core import compliance
    importlib.reload(compliance)
    await compliance.enforce_phi_safeguard()  # must not raise in staging


# ---------------------------------------------------------------------------
# 5. Pseudonymization: sanitize_vapi_webhook_payload
# ---------------------------------------------------------------------------


class TestSanitizeVapiWebhookPayload:
    def _sanitize(self, payload):
        from backend.app.core.pseudonymization import sanitize_vapi_webhook_payload
        return sanitize_vapi_webhook_payload(payload)

    def test_removes_patient_name(self):
        result = self._sanitize({"patient_name": "Demo Patient", "call_id": "abc"})
        assert result["patient_name"] != "Demo Patient"
        assert len(result["patient_name"]) == 64  # HMAC hex digest

    def test_removes_phone(self):
        result = self._sanitize({"phone": "+436601234567", "call_id": "abc"})
        assert result["phone"] != "+436601234567"
        assert len(result["phone"]) == 64

    def test_removes_transcript(self):
        result = self._sanitize({"transcript": "Patient said they have a headache.", "call_id": "abc"})
        assert "Patient said" not in result["transcript"]
        assert "REDACTED" in result["transcript"].upper()

    def test_removes_reason(self):
        result = self._sanitize({"reason": "Routine checkup", "call_id": "abc"})
        assert result["reason"] != "Routine checkup"
        assert len(result["reason"]) == 64

    def test_removes_message(self):
        result = self._sanitize({"message": "Patient wants an appointment", "call_id": "abc"})
        assert result["message"] != "Patient wants an appointment"
        assert len(result["message"]) == 64

    def test_removes_email(self):
        result = self._sanitize({"email": "patient@example.at", "call_id": "abc"})
        assert result["email"] != "patient@example.at"
        assert len(result["email"]) == 64

    def test_removes_recording_url(self):
        result = self._sanitize({"recording_url": "https://storage.example.com/call.mp3"})
        assert "https://" not in result.get("recording_url", "")
        assert "REDACTED" in result.get("recording_url", "").upper()

    def test_preserves_call_id(self):
        result = self._sanitize({"patient_name": "Demo", "call_id": "vapi-call-001"})
        assert result["call_id"] == "vapi-call-001"

    def test_preserves_clinic_ref(self):
        result = self._sanitize({"clinic_ref": "1a5bbc75-c1b0-4488-94aa-64b3f1c50056"})
        assert result["clinic_ref"] == "1a5bbc75-c1b0-4488-94aa-64b3f1c50056"

    def test_preserves_urgency_level(self):
        result = self._sanitize({"urgency_level": "normal", "patient_name": "Demo"})
        assert result["urgency_level"] == "normal"

    def test_preserves_status(self):
        result = self._sanitize({"status": "new", "patient_name": "Demo"})
        assert result["status"] == "new"

    def test_non_dict_returns_safe_envelope(self):
        result = self._sanitize("raw string payload")
        assert isinstance(result, dict)
        assert "_sanitized" in result

    def test_hash_placeholder_is_deterministic(self):
        from backend.app.core.pseudonymization import sanitize_vapi_webhook_payload
        r1 = sanitize_vapi_webhook_payload({"patient_name": "Demo Patient"})
        r2 = sanitize_vapi_webhook_payload({"patient_name": "Demo Patient"})
        assert r1["patient_name"] == r2["patient_name"]

    def test_nested_dict_sanitized(self):
        result = self._sanitize({"outer": {"patient_name": "Demo", "call_id": "abc"}})
        assert result["outer"]["patient_name"] != "Demo"
        assert result["outer"]["call_id"] == "abc"


# ---------------------------------------------------------------------------
# 6. Pseudonymization: sanitize_for_log
# ---------------------------------------------------------------------------


class TestSanitizeForLog:
    def test_list_items_sanitized(self):
        from backend.app.core.pseudonymization import sanitize_for_log
        result = sanitize_for_log([{"patient_name": "A"}, {"patient_name": "B"}])
        assert result[0]["patient_name"] != "A"
        assert result[1]["patient_name"] != "B"

    def test_scalar_passthrough(self):
        from backend.app.core.pseudonymization import sanitize_for_log
        assert sanitize_for_log(42) == 42
        assert sanitize_for_log(None) is None

    def test_notes_field_sanitized(self):
        from backend.app.core.pseudonymization import sanitize_for_log
        result = sanitize_for_log({"notes": "Patient has asthma"})
        assert result["notes"] != "Patient has asthma"

    def test_audio_url_redacted(self):
        from backend.app.core.pseudonymization import sanitize_for_log
        result = sanitize_for_log({"audio_url": "https://cdn.example.com/call.wav"})
        assert "https://" not in result.get("audio_url", "")


# ---------------------------------------------------------------------------
# 7. Frontend auth regression
# ---------------------------------------------------------------------------


class TestFrontendAuthRegression:
    def _read(self, rel: str) -> str:
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        return (root / "frontend" / rel).read_text(encoding="utf-8")

    def test_api_ts_has_credentials_include(self):
        content = self._read("lib/api.ts")
        assert "credentials" in content and "include" in content

    def test_dashboard_no_session_storage(self):
        content = self._read("app/dashboard/page.tsx")
        non_comment = "\n".join(
            ln for ln in content.splitlines()
            if not ln.strip().startswith("//")
        )
        assert "sessionStorage" not in non_comment

    def test_dashboard_no_local_storage(self):
        content = self._read("app/dashboard/page.tsx")
        non_comment = "\n".join(
            ln for ln in content.splitlines()
            if not ln.strip().startswith("//")
        )
        assert "localStorage" not in non_comment

    def test_api_ts_no_bearer_token_in_headers(self):
        content = self._read("lib/api.ts")
        non_comment = "\n".join(
            ln for ln in content.splitlines()
            if not ln.strip().startswith("//")
        )
        assert "Bearer" not in non_comment or "Authorization" not in non_comment


# ---------------------------------------------------------------------------
# 8. Route wiring — enforce_phi_safeguard applied to PHI routes
# ---------------------------------------------------------------------------


class TestRoutePhiWiring:
    """Verify enforce_phi_safeguard is wired to PHI-processing routers.

    Uses name-based matching to survive monkeypatch/reload in other tests —
    module reloads create distinct function objects so identity checks are fragile.
    """

    def _dep_names(self, module_path: str) -> list[str]:
        import importlib as il
        mod = il.import_module(module_path)
        router = mod.router
        return [
            getattr(d.dependency, "__name__", "") or getattr(d.dependency, "__qualname__", "")
            for d in getattr(router, "dependencies", [])
        ]

    def test_appointment_requests_router_has_phi_safeguard(self):
        assert "enforce_phi_safeguard" in self._dep_names(
            "backend.app.api.routes.appointment_requests"
        )

    def test_patients_router_has_phi_safeguard(self):
        assert "enforce_phi_safeguard" in self._dep_names(
            "backend.app.api.routes.patients"
        )

    def test_consultations_router_has_phi_safeguard(self):
        assert "enforce_phi_safeguard" in self._dep_names(
            "backend.app.api.routes.consultations"
        )

    def test_clinical_workflows_router_has_phi_safeguard(self):
        assert "enforce_phi_safeguard" in self._dep_names(
            "backend.app.api.routes.clinical_workflows"
        )
