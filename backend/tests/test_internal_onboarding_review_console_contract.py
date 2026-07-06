"""
Sprint 19 / Module 134 — Internal Clinic Onboarding Review Console
Static contract tests: verify the review page source and api.ts contain required
strings and exclude forbidden content.  No backend server is started.
"""

import pathlib

ROOT = pathlib.Path(__file__).parent.parent.parent

REVIEW_PAGE = ROOT / "frontend" / "app" / "developer-console" / "onboarding-requests" / "page.tsx"
DEV_CONSOLE  = ROOT / "frontend" / "app" / "developer-console" / "page.tsx"
API_TS       = ROOT / "frontend" / "lib" / "api.ts"
ARCH_DOC     = ROOT / "docs" / "architecture" / "INTERNAL_ONBOARDING_REVIEW_CONSOLE.md"


def _review() -> str:
    return REVIEW_PAGE.read_text()


def _dev_console() -> str:
    return DEV_CONSOLE.read_text()


def _api() -> str:
    return API_TS.read_text()


def _arch() -> str:
    return ARCH_DOC.read_text()


# ---------------------------------------------------------------------------
# Review page — existence and routing
# ---------------------------------------------------------------------------

class TestReviewPageExists:
    def test_file_exists(self):
        assert REVIEW_PAGE.exists(), f"Review page not found: {REVIEW_PAGE}"

    def test_heading_clinic_onboarding_requests(self):
        assert "Clinic Onboarding Requests" in _review()

    def test_internal_review_console_copy(self):
        assert "Internal review console" in _review()

    def test_developer_console_nav_link(self):
        assert "/developer-console" in _review()

    def test_admin_staging_badge(self):
        assert "ADMIN" in _review().upper() or "STAGING" in _review().upper()


# ---------------------------------------------------------------------------
# Review page — safety copy
# ---------------------------------------------------------------------------

class TestReviewPageSafetyCopy:
    def test_no_tenant_activation(self):
        assert "No tenant activation" in _review()

    def test_no_phi_copy(self):
        assert "No PHI" in _review()

    def test_production_phi_no_go(self):
        assert "Production PHI remains NO-GO" in _review()

    def test_approving_does_not_create_tenant(self):
        text = _review()
        assert "does not create a tenant" in text or "does not activate" in text

    def test_status_updates_are_internal_markers_only(self):
        text = _review()
        assert "internal review markers" in text or "internal" in text.lower()


# ---------------------------------------------------------------------------
# Review page — API integration
# ---------------------------------------------------------------------------

class TestReviewPageApiIntegration:
    def test_fetches_clinic_onboarding_requests(self):
        assert "/clinic-onboarding-requests" in _review()

    def test_credentials_include(self):
        assert "credentials" in _review() and "include" in _review()

    def test_patch_status_endpoint(self):
        text = _review()
        assert "/clinic-onboarding-requests/" in text
        assert "/status" in text

    def test_patch_method_present(self):
        assert "PATCH" in _review()

    def test_auth_error_handling(self):
        text = _review()
        assert "401" in text or "403" in text or "auth_error" in text

    def test_admin_session_required_copy(self):
        assert "Admin session required" in _review() or "log in" in _review().lower()


# ---------------------------------------------------------------------------
# Review page — field display
# ---------------------------------------------------------------------------

class TestReviewPageFieldDisplay:
    def test_displays_clinic_name(self):
        assert "clinic_name" in _review()

    def test_displays_doctor_name(self):
        assert "doctor_name" in _review()

    def test_displays_contact_email(self):
        assert "contact_email" in _review()

    def test_displays_preferred_language(self):
        assert "preferred_language" in _review()

    def test_displays_fallback_language(self):
        assert "fallback_language" in _review()

    def test_displays_workflow_notes(self):
        assert "workflow_notes" in _review()

    def test_displays_production_phi_enabled(self):
        assert "production_phi_enabled" in _review()


# ---------------------------------------------------------------------------
# Review page — status values
# ---------------------------------------------------------------------------

class TestReviewPageStatusValues:
    def test_status_submitted(self):
        assert "submitted" in _review()

    def test_status_reviewed(self):
        assert "reviewed" in _review()

    def test_status_demo_booked(self):
        assert "demo_booked" in _review()

    def test_status_pilot_approved(self):
        assert "pilot_approved" in _review()

    def test_status_rejected(self):
        assert "rejected" in _review()

    def test_status_archived(self):
        assert "archived" in _review()

    def test_update_status_action(self):
        assert "Update status" in _review()


# ---------------------------------------------------------------------------
# Review page — storage safety
# ---------------------------------------------------------------------------

class TestReviewPageStorageSafety:
    def test_no_session_storage(self):
        assert "sessionStorage" not in _review()

    def test_no_local_storage(self):
        assert "localStorage" not in _review()

    def test_no_hardcoded_jwt(self):
        text = _review()
        assert "Bearer " not in text
        assert "eyJ" not in text

    def test_no_phi_patient_fields(self):
        text = _review().lower()
        assert "sozialversicherung" not in text
        assert "svnr" not in text
        assert "date_of_birth" not in text


# ---------------------------------------------------------------------------
# Developer console — links to review page
# ---------------------------------------------------------------------------

class TestDeveloperConsoleLink:
    def test_dev_console_exists(self):
        assert DEV_CONSOLE.exists(), f"Developer console page not found: {DEV_CONSOLE}"

    def test_dev_console_links_to_onboarding_requests(self):
        assert "/developer-console/onboarding-requests" in _dev_console()

    def test_dev_console_review_onboarding_copy(self):
        text = _dev_console().lower()
        assert "onboarding" in text

    def test_dev_console_pilot_review_panel(self):
        text = _dev_console()
        assert "Pilot" in text or "pilot" in text


# ---------------------------------------------------------------------------
# api.ts — onboarding request helpers
# ---------------------------------------------------------------------------

class TestApiTsHelpers:
    def test_fetch_clinic_onboarding_requests_exists(self):
        assert "fetchClinicOnboardingRequests" in _api()

    def test_update_clinic_onboarding_request_status_exists(self):
        assert "updateClinicOnboardingRequestStatus" in _api()

    def test_api_ts_uses_clinic_onboarding_requests_path(self):
        assert "/clinic-onboarding-requests" in _api()

    def test_api_ts_patch_method(self):
        assert "PATCH" in _api()

    def test_api_ts_no_hardcoded_secrets(self):
        text = _api()
        assert "sk-" not in text
        assert "Bearer " not in text


# ---------------------------------------------------------------------------
# Architecture doc
# ---------------------------------------------------------------------------

class TestArchDoc:
    def test_arch_doc_exists(self):
        assert ARCH_DOC.exists(), f"Arch doc not found: {ARCH_DOC}"

    def test_arch_doc_mentions_module_134(self):
        assert "134" in _arch() or "Module 134" in _arch()

    def test_arch_doc_mentions_onboarding_requests_route(self):
        assert "onboarding-requests" in _arch() or "onboarding_requests" in _arch()

    def test_arch_doc_no_automatic_tenant_creation(self):
        text = _arch().lower()
        assert "no automatic" in text or "not create" in text or "does not create" in text

    def test_arch_doc_production_phi_no_go(self):
        assert "NO-GO" in _arch() or "no-go" in _arch().lower()
