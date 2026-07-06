"""
Unit + contract tests for Sprint 19 / Module 130 — Compliance Readiness Gate and Language Foundation.

Covers:
  - backend/app/core/compliance.py — environment helpers, production gate, PHI safeguard
  - backend/app/core/pseudonymization.py — HMAC pseudonymization
  - backend/app/core/config_loader.py — fallback_language, language env helpers
  - frontend/app/onboarding/page.tsx — language selector scaffold (static content)

No database. No network. No real patient data. No secrets committed.
"""

from __future__ import annotations

import importlib
import os
import sys
import pytest

# ---------------------------------------------------------------------------
# Helpers to reload modules with patched env
# ---------------------------------------------------------------------------


def _reload(module_path: str):
    """Force a fresh import of module_path (bypasses lru_cache / module-level state)."""
    mod = sys.modules.get(module_path)
    if mod is not None:
        importlib.reload(mod)
    return importlib.import_module(module_path)


# ---------------------------------------------------------------------------
# 1. compliance.py — environment helpers
# ---------------------------------------------------------------------------


class TestGetEnvironment:
    def test_defaults_to_local(self, monkeypatch):
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        from backend.app.core import compliance
        importlib.reload(compliance)
        assert compliance.get_environment() == "local"

    def test_reads_staging(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "staging")
        from backend.app.core import compliance
        importlib.reload(compliance)
        assert compliance.get_environment() == "staging"

    def test_reads_production(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        from backend.app.core import compliance
        importlib.reload(compliance)
        assert compliance.get_environment() == "production"

    def test_normalizes_to_lowercase(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "STAGING")
        from backend.app.core import compliance
        importlib.reload(compliance)
        assert compliance.get_environment() == "staging"


class TestIsProduction:
    def test_false_in_local(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "local")
        from backend.app.core import compliance
        importlib.reload(compliance)
        assert compliance.is_production() is False

    def test_false_in_staging(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "staging")
        from backend.app.core import compliance
        importlib.reload(compliance)
        assert compliance.is_production() is False

    def test_true_in_production(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        from backend.app.core import compliance
        importlib.reload(compliance)
        assert compliance.is_production() is True


class TestIsProductionComplianceUnlocked:
    def test_false_by_default(self, monkeypatch):
        monkeypatch.delenv("PRODUCTION_COMPLIANCE_UNLOCKED", raising=False)
        from backend.app.core import compliance
        assert compliance.is_production_compliance_unlocked() is False

    def test_true_with_true(self, monkeypatch):
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "true")
        from backend.app.core import compliance
        assert compliance.is_production_compliance_unlocked() is True

    def test_true_with_1(self, monkeypatch):
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "1")
        from backend.app.core import compliance
        assert compliance.is_production_compliance_unlocked() is True

    def test_true_with_yes(self, monkeypatch):
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "yes")
        from backend.app.core import compliance
        assert compliance.is_production_compliance_unlocked() is True

    def test_false_with_false(self, monkeypatch):
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "false")
        from backend.app.core import compliance
        assert compliance.is_production_compliance_unlocked() is False

    def test_false_with_empty(self, monkeypatch):
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "")
        from backend.app.core import compliance
        assert compliance.is_production_compliance_unlocked() is False


class TestGetAuthMethod:
    def test_defaults_to_cookie_httponly(self, monkeypatch):
        monkeypatch.delenv("AUTH_METHOD", raising=False)
        from backend.app.core import compliance
        assert compliance.get_auth_method() == "COOKIE_HTTPONLY"

    def test_reads_env(self, monkeypatch):
        monkeypatch.setenv("AUTH_METHOD", "cookie_httponly")
        from backend.app.core import compliance
        assert compliance.get_auth_method() == "COOKIE_HTTPONLY"


# ---------------------------------------------------------------------------
# 2. compliance.py — assert_production_auth_ready
# ---------------------------------------------------------------------------


class TestAssertProductionAuthReady:
    def test_no_raise_in_local(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "local")
        monkeypatch.setenv("AUTH_METHOD", "OTHER")
        from backend.app.core import compliance
        importlib.reload(compliance)
        compliance.assert_production_auth_ready()  # must not raise

    def test_no_raise_in_staging(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "staging")
        monkeypatch.setenv("AUTH_METHOD", "OTHER")
        from backend.app.core import compliance
        importlib.reload(compliance)
        compliance.assert_production_auth_ready()  # must not raise

    def test_no_raise_in_production_with_correct_auth(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
        from backend.app.core import compliance
        importlib.reload(compliance)
        compliance.assert_production_auth_ready()  # must not raise

    def test_raises_in_production_with_wrong_auth(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AUTH_METHOD", "BEARER_TOKEN")
        from backend.app.core import compliance
        importlib.reload(compliance)
        with pytest.raises(AssertionError, match="COOKIE_HTTPONLY"):
            compliance.assert_production_auth_ready()


# ---------------------------------------------------------------------------
# 3. compliance.py — assert_production_compliance_ready
# ---------------------------------------------------------------------------


class TestAssertProductionComplianceReady:
    def test_no_raise_in_local(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "local")
        monkeypatch.delenv("PRODUCTION_COMPLIANCE_UNLOCKED", raising=False)
        from backend.app.core import compliance
        importlib.reload(compliance)
        compliance.assert_production_compliance_ready()  # must not raise

    def test_no_raise_in_staging(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "staging")
        monkeypatch.delenv("PRODUCTION_COMPLIANCE_UNLOCKED", raising=False)
        from backend.app.core import compliance
        importlib.reload(compliance)
        compliance.assert_production_compliance_ready()  # must not raise

    def test_raises_in_production_when_locked(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "false")
        from backend.app.core import compliance
        importlib.reload(compliance)
        with pytest.raises(AssertionError, match="locked"):
            compliance.assert_production_compliance_ready()

    def test_no_raise_in_production_when_unlocked(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "true")
        from backend.app.core import compliance
        importlib.reload(compliance)
        compliance.assert_production_compliance_ready()  # must not raise

    def test_blockers_mentioned_in_error(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "false")
        from backend.app.core import compliance
        importlib.reload(compliance)
        with pytest.raises(AssertionError) as exc_info:
            compliance.assert_production_compliance_ready()
        assert "C3" in str(exc_info.value) or "hardening" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# 4. compliance.py — enforce_phi_safeguard (async FastAPI dependency)
# ---------------------------------------------------------------------------


class TestEnforcePhiSafeguard:
    @pytest.mark.asyncio
    async def test_no_raise_in_local(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "local")
        monkeypatch.delenv("PRODUCTION_COMPLIANCE_UNLOCKED", raising=False)
        from backend.app.core import compliance
        importlib.reload(compliance)
        await compliance.enforce_phi_safeguard()  # must not raise

    @pytest.mark.asyncio
    async def test_no_raise_in_staging(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "staging")
        monkeypatch.delenv("PRODUCTION_COMPLIANCE_UNLOCKED", raising=False)
        from backend.app.core import compliance
        importlib.reload(compliance)
        await compliance.enforce_phi_safeguard()  # must not raise

    @pytest.mark.asyncio
    async def test_raises_403_in_production_when_locked(self, monkeypatch):
        from fastapi import HTTPException
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "false")
        from backend.app.core import compliance
        importlib.reload(compliance)
        with pytest.raises(HTTPException) as exc_info:
            await compliance.enforce_phi_safeguard()
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_no_raise_in_production_when_unlocked(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AUTH_METHOD", "COOKIE_HTTPONLY")
        monkeypatch.setenv("PRODUCTION_COMPLIANCE_UNLOCKED", "true")
        from backend.app.core import compliance
        importlib.reload(compliance)
        await compliance.enforce_phi_safeguard()  # must not raise


# ---------------------------------------------------------------------------
# 5. compliance.py — language env helpers
# ---------------------------------------------------------------------------


class TestLanguageHelpers:
    def test_get_default_clinic_language_defaults_de(self, monkeypatch):
        monkeypatch.delenv("DEFAULT_CLINIC_LANGUAGE", raising=False)
        from backend.app.core import compliance
        assert compliance.get_default_clinic_language() == "de"

    def test_get_default_clinic_language_reads_env(self, monkeypatch):
        monkeypatch.setenv("DEFAULT_CLINIC_LANGUAGE", "EN")
        from backend.app.core import compliance
        assert compliance.get_default_clinic_language() == "en"

    def test_get_supported_clinic_languages_defaults(self, monkeypatch):
        monkeypatch.delenv("SUPPORTED_CLINIC_LANGUAGES", raising=False)
        from backend.app.core import compliance
        langs = compliance.get_supported_clinic_languages()
        assert "de" in langs
        assert "en" in langs

    def test_get_supported_clinic_languages_reads_env(self, monkeypatch):
        monkeypatch.setenv("SUPPORTED_CLINIC_LANGUAGES", "de,en,fr")
        from backend.app.core import compliance
        langs = compliance.get_supported_clinic_languages()
        assert langs == ["de", "en", "fr"]


# ---------------------------------------------------------------------------
# 6. pseudonymization.py — core behavior
# ---------------------------------------------------------------------------


class TestPseudonymization:
    def test_empty_input_returns_empty(self):
        from backend.app.core.pseudonymization import pseudonymize
        assert pseudonymize("") == ""
        assert pseudonymize(None) == ""

    def test_returns_hex_string(self):
        from backend.app.core.pseudonymization import pseudonymize
        result = pseudonymize("Test Patient")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_stable_output_same_input(self):
        from backend.app.core.pseudonymization import pseudonymize
        a = pseudonymize("Demo Patient", context="patient_name")
        b = pseudonymize("Demo Patient", context="patient_name")
        assert a == b

    def test_different_values_produce_different_tokens(self):
        from backend.app.core.pseudonymization import pseudonymize
        a = pseudonymize("Demo Patient A", context="patient_name")
        b = pseudonymize("Demo Patient B", context="patient_name")
        assert a != b

    def test_different_context_produces_different_token(self):
        from backend.app.core.pseudonymization import pseudonymize
        a = pseudonymize("same-value", context="phone")
        b = pseudonymize("same-value", context="email")
        assert a != b

    def test_original_value_not_in_output(self):
        from backend.app.core.pseudonymization import pseudonymize
        result = pseudonymize("+436601234567", context="phone")
        assert "+436601234567" not in result

    def test_pseudonymize_phone(self):
        from backend.app.core.pseudonymization import pseudonymize_phone
        result = pseudonymize_phone("+436601234567")
        assert len(result) == 64
        assert "+436601234567" not in result

    def test_pseudonymize_name(self):
        from backend.app.core.pseudonymization import pseudonymize_name
        result = pseudonymize_name("Demo Patient")
        assert len(result) == 64
        assert "Demo Patient" not in result

    def test_pseudonymize_email(self):
        from backend.app.core.pseudonymization import pseudonymize_email
        result = pseudonymize_email("demo@example.at")
        assert len(result) == 64
        assert "demo@example.at" not in result

    def test_pepper_env_changes_output(self, monkeypatch):
        from backend.app.core.pseudonymization import pseudonymize
        monkeypatch.setenv("PSEUDONYMIZATION_PEPPER", "pepper-a")
        result_a = pseudonymize("same-value", context="test")
        monkeypatch.setenv("PSEUDONYMIZATION_PEPPER", "pepper-b")
        result_b = pseudonymize("same-value", context="test")
        assert result_a != result_b

    def test_assert_pseudonymization_ready_raises_when_no_pepper(self, monkeypatch):
        monkeypatch.delenv("PSEUDONYMIZATION_PEPPER", raising=False)
        from backend.app.core.pseudonymization import assert_pseudonymization_ready
        with pytest.raises(AssertionError, match="PSEUDONYMIZATION_PEPPER"):
            assert_pseudonymization_ready()

    def test_assert_pseudonymization_ready_passes_when_pepper_set(self, monkeypatch):
        monkeypatch.setenv("PSEUDONYMIZATION_PEPPER", "test-pepper-value")
        from backend.app.core.pseudonymization import assert_pseudonymization_ready
        assert_pseudonymization_ready()  # must not raise


# ---------------------------------------------------------------------------
# 7. config_loader.py — ClinicConfig fallback_language and new fields
# ---------------------------------------------------------------------------


class TestClinicConfigLanguageFields:
    def test_fallback_language_optional(self):
        from backend.app.core.config_loader import ClinicConfig
        config = ClinicConfig(
            tenant_id="1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
            clinic_name="Test Clinic",
        )
        assert config.fallback_language is None

    def test_fallback_language_accepts_en(self):
        from backend.app.core.config_loader import ClinicConfig
        config = ClinicConfig(
            tenant_id="1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
            clinic_name="Test Clinic",
            language="de",
            fallback_language="en",
        )
        assert config.fallback_language == "en"

    def test_fallback_language_rejects_invalid(self):
        from backend.app.core.config_loader import ClinicConfig
        import pydantic
        with pytest.raises((pydantic.ValidationError, ValueError)):
            ClinicConfig(
                tenant_id="1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
                clinic_name="Test Clinic",
                fallback_language="not-valid!!",
            )

    def test_clinic_display_name_optional(self):
        from backend.app.core.config_loader import ClinicConfig
        config = ClinicConfig(
            tenant_id="1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
            clinic_name="Test Clinic",
            clinic_display_name="Dr. Med. Alexander Huber",
        )
        assert config.clinic_display_name == "Dr. Med. Alexander Huber"

    def test_specialty_optional(self):
        from backend.app.core.config_loader import ClinicConfig
        config = ClinicConfig(
            tenant_id="1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
            clinic_name="Test Clinic",
            specialty="Innere Medizin",
        )
        assert config.specialty == "Innere Medizin"

    def test_city_optional(self):
        from backend.app.core.config_loader import ClinicConfig
        config = ClinicConfig(
            tenant_id="1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
            clinic_name="Test Clinic",
            city="Wien",
        )
        assert config.city == "Wien"


class TestConfigLoaderLanguageEnvHelpers:
    def test_get_default_clinic_language_defaults_de(self, monkeypatch):
        monkeypatch.delenv("DEFAULT_CLINIC_LANGUAGE", raising=False)
        from backend.app.core.config_loader import get_default_clinic_language
        assert get_default_clinic_language() == "de"

    def test_get_default_clinic_language_reads_env(self, monkeypatch):
        monkeypatch.setenv("DEFAULT_CLINIC_LANGUAGE", "EN")
        from backend.app.core.config_loader import get_default_clinic_language
        assert get_default_clinic_language() == "en"

    def test_get_supported_clinic_languages_defaults(self, monkeypatch):
        monkeypatch.delenv("SUPPORTED_CLINIC_LANGUAGES", raising=False)
        from backend.app.core.config_loader import get_supported_clinic_languages
        langs = get_supported_clinic_languages()
        assert "de" in langs
        assert "en" in langs

    def test_get_supported_clinic_languages_reads_env(self, monkeypatch):
        monkeypatch.setenv("SUPPORTED_CLINIC_LANGUAGES", "de,en,tr")
        from backend.app.core.config_loader import get_supported_clinic_languages
        langs = get_supported_clinic_languages()
        assert langs == ["de", "en", "tr"]


# ---------------------------------------------------------------------------
# 8. Staging clinic config JSON — language fields present
# ---------------------------------------------------------------------------


class TestStagingClinicConfigLanguageFields:
    def _load(self):
        import json
        from pathlib import Path
        path = (
            Path(__file__).resolve().parents[2]
            / "backend" / "tenants" / "configs"
            / "1a5bbc75-c1b0-4488-94aa-64b3f1c50056"
            / "clinic_config.json"
        )
        with path.open(encoding="utf-8") as f:
            return json.load(f)

    def test_language_de(self):
        assert self._load()["language"] == "de"

    def test_fallback_language_en(self):
        assert self._load()["fallback_language"] == "en"

    def test_has_clinic_display_name(self):
        assert self._load().get("clinic_display_name") is not None

    def test_has_specialty(self):
        assert self._load().get("specialty") is not None

    def test_recording_ingestion_disabled(self):
        assert self._load()["features"]["recording_ingestion_enabled"] is False

    def test_production_phi_disabled(self):
        assert self._load()["features"]["production_phi_enabled"] is False


# ---------------------------------------------------------------------------
# 9. Frontend onboarding — language foundation scaffold (static content check)
# ---------------------------------------------------------------------------


class TestOnboardingLanguageScaffold:
    def _read_onboarding(self) -> str:
        from pathlib import Path
        path = (
            Path(__file__).resolve().parents[2]
            / "frontend" / "app" / "onboarding" / "page.tsx"
        )
        return path.read_text(encoding="utf-8")

    def test_language_section_present(self):
        assert 'data-section="language-foundation"' in self._read_onboarding()

    def test_deutsch_language_option(self):
        assert "Deutsch" in self._read_onboarding()

    def test_english_language_option(self):
        assert "English" in self._read_onboarding()

    def test_language_option_data_attr_present(self):
        assert "data-language-option=" in self._read_onboarding()

    def test_language_codes_de_en_present(self):
        content = self._read_onboarding()
        assert "'de'" in content or '"de"' in content
        assert "'en'" in content or '"en"' in content

    def test_language_selector_is_functional_or_has_staging_note(self):
        # Module 133 made the language selector interactive.
        # Either an interactive handler or a staging note is acceptable.
        content = self._read_onboarding().lower()
        assert (
            "onclick" in content
            or "setfield" in content
            or "setform" in content
            or "not yet interactive" in content
            or "staging" in content
        )

    def test_no_hardcoded_secrets(self):
        import re
        content = self._read_onboarding()
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content)
        assert "sk-" not in content
