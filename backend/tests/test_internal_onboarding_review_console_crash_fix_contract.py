"""
Sprint 19 / Module 134A — Crash fix: defensive rendering in onboarding review console.
Static contract tests verifying the page has defensive helpers for nullable/optional
fields returned by the backend.  No backend server is started.
"""

import pathlib

ROOT = pathlib.Path(__file__).parent.parent.parent
REVIEW_PAGE = ROOT / "frontend" / "app" / "developer-console" / "onboarding-requests" / "page.tsx"


def _page() -> str:
    return REVIEW_PAGE.read_text()


# ---------------------------------------------------------------------------
# Defensive helpers present
# ---------------------------------------------------------------------------

class TestDefensiveHelpersExist:
    def test_safe_text_helper_defined(self):
        assert "safeText" in _page()

    def test_safe_date_helper_defined(self):
        assert "safeDate" in _page()

    def test_safe_boolean_helper_defined(self):
        assert "safeBoolean" in _page()

    def test_safe_languages_helper_defined(self):
        assert "safeLanguages" in _page()

    def test_safe_text_returns_fallback(self):
        # helper must return a fallback string for null/undefined
        text = _page()
        assert "safeText" in text
        assert "fallback" in text or "'—'" in text or '"—"' in text

    def test_safe_date_guards_invalid(self):
        text = _page()
        assert "safeDate" in text
        assert "isNaN" in text or "try" in text

    def test_safe_boolean_guards_null(self):
        text = _page()
        assert "safeBoolean" in text
        assert "null" in text

    def test_safe_languages_handles_array(self):
        text = _page()
        assert "safeLanguages" in text
        assert "Array.isArray" in text

    def test_safe_languages_handles_string(self):
        text = _page()
        assert "JSON.parse" in text

    def test_safe_languages_handles_null(self):
        # should return a default like 'de, en' when value is null
        text = _page()
        assert "de, en" in text


# ---------------------------------------------------------------------------
# supported_languages is not called with .join() directly
# ---------------------------------------------------------------------------

class TestSupportedLanguagesSafe:
    def test_supported_languages_uses_safe_languages(self):
        text = _page()
        assert "safeLanguages(selected.supported_languages)" in text

    def test_no_direct_join_on_supported_languages(self):
        # The raw field must not be .join()-ed without safeLanguages guard
        text = _page()
        assert "supported_languages).join" not in text
        assert "supported_languages ?? []).join" not in text
        assert "supported_languages!.join" not in text


# ---------------------------------------------------------------------------
# Date fields use safeDate, not raw .toLocaleString()
# ---------------------------------------------------------------------------

class TestDateFieldsSafe:
    def test_created_at_uses_safe_date(self):
        text = _page()
        assert "safeDate(selected.created_at)" in text

    def test_updated_at_uses_safe_date(self):
        text = _page()
        assert "safeDate(selected.updated_at)" in text

    def test_no_direct_to_locale_string_in_jsx(self):
        # toLocaleString should only be inside safeDate, not in JSX directly
        text = _page()
        # Check toLocaleString is inside safeDate helper (not called on selected.X directly)
        assert "selected.created_at.toLocaleString" not in text
        assert "selected.updated_at.toLocaleString" not in text


# ---------------------------------------------------------------------------
# Boolean fields use safeBoolean
# ---------------------------------------------------------------------------

class TestBooleanFieldsSafe:
    def test_wants_ai_phone_intake_uses_safe_boolean(self):
        text = _page()
        assert "safeBoolean(selected.wants_ai_phone_intake)" in text

    def test_wants_dashboard_uses_safe_boolean(self):
        text = _page()
        assert "safeBoolean(selected.wants_dashboard)" in text

    def test_wants_notifications_uses_safe_boolean(self):
        text = _page()
        assert "safeBoolean(selected.wants_notifications)" in text

    def test_consent_pilot_contact_uses_safe_boolean(self):
        text = _page()
        assert "safeBoolean(selected.consent_pilot_contact)" in text

    def test_acknowledges_no_phi_uses_safe_boolean(self):
        text = _page()
        assert "safeBoolean(selected.acknowledges_no_phi)" in text

    def test_production_phi_enabled_uses_safe_boolean(self):
        text = _page()
        assert "safeBoolean(selected.production_phi_enabled)" in text

    def test_bool_row_handles_null(self):
        text = _page()
        # BoolRow must branch on null to avoid rendering undefined as false
        assert "value === null" in text or "value === null" in text


# ---------------------------------------------------------------------------
# Optional text fields use safeText
# ---------------------------------------------------------------------------

class TestOptionalTextFieldsSafe:
    def test_clinic_type_uses_safe_text(self):
        assert "safeText(selected.clinic_type)" in _page()

    def test_specialty_uses_safe_text(self):
        assert "safeText(selected.specialty)" in _page()

    def test_workflow_notes_uses_safe_text(self):
        assert "safeText(selected.workflow_notes)" in _page()

    def test_contact_phone_uses_safe_text(self):
        assert "safeText(selected.contact_phone)" in _page()

    def test_pilot_interest_level_uses_safe_text(self):
        assert "safeText(selected.pilot_interest_level)" in _page()

    def test_source_uses_safe_text(self):
        assert "safeText(selected.source)" in _page()


# ---------------------------------------------------------------------------
# Interface types updated to allow null
# ---------------------------------------------------------------------------

class TestInterfaceNullability:
    def test_supported_languages_allows_null(self):
        text = _page()
        assert "supported_languages: string[] | string | null" in text

    def test_boolean_fields_allow_null(self):
        text = _page()
        assert "boolean | null" in text

    def test_created_at_allows_null(self):
        text = _page()
        assert "created_at: string | null" in text

    def test_updated_at_allows_null(self):
        text = _page()
        assert "updated_at: string | null" in text


# ---------------------------------------------------------------------------
# Key UI strings preserved
# ---------------------------------------------------------------------------

class TestKeyUiStringsPreserved:
    def test_select_a_request_to_view_details(self):
        assert "Select a request to view details" in _page()

    def test_clinic_onboarding_requests_heading(self):
        assert "Clinic Onboarding Requests" in _page()

    def test_update_status_present(self):
        assert "Update status" in _page()

    def test_no_tenant_activation_safety(self):
        assert "No tenant activation" in _page()

    def test_production_phi_no_go(self):
        assert "Production PHI remains NO-GO" in _page()

    def test_internal_review_console_copy(self):
        assert "Internal review console" in _page()

    def test_all_statuses_still_present(self):
        text = _page()
        for s in ("submitted", "reviewed", "demo_booked", "pilot_approved", "rejected", "archived"):
            assert s in text, f"Missing status: {s}"


# ---------------------------------------------------------------------------
# Storage safety unchanged
# ---------------------------------------------------------------------------

class TestStorageSafetyPreserved:
    def test_credentials_include(self):
        assert "credentials" in _page() and "include" in _page()

    def test_no_session_storage(self):
        assert "sessionStorage" not in _page()

    def test_no_local_storage(self):
        assert "localStorage" not in _page()

    def test_no_hardcoded_bearer(self):
        assert "Bearer " not in _page()

    def test_patch_method_present(self):
        assert "PATCH" in _page()
