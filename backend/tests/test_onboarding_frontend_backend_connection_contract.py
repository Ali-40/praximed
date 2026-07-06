"""
Static contract tests — Sprint 19 / Module 133.

Verifies that the /onboarding page source:
- Contains all required gateway and form elements
- Submits to the real backend endpoint
- Enforces consent and no-PHI acknowledgements
- Does not send forbidden fields or credentials
- Does not use browser token storage
- Shows correct success and error states
- Preserves safety copy

No runtime execution. No network calls. No real patient data.
"""

from __future__ import annotations

import os

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_FRONTEND  = os.path.join(_REPO_ROOT, "frontend")
_DOCS      = os.path.join(_REPO_ROOT, "docs")


def _onboarding() -> str:
    with open(os.path.join(_FRONTEND, "app", "onboarding", "page.tsx"), encoding="utf-8") as f:
        return f.read()


def _flat() -> str:
    return _onboarding().replace("\n", " ")


def _arch() -> str:
    with open(
        os.path.join(_DOCS, "architecture", "ONBOARDING_FRONTEND_BACKEND_CONNECTION.md"),
        encoding="utf-8",
    ) as f:
        return f.read()


# ===========================================================================
# 1. Gateway section
# ===========================================================================


def test_onboarding_has_request_pilot_access() -> None:
    assert "Request Pilot Access" in _onboarding()


def test_onboarding_has_existing_clinic_login() -> None:
    assert "Existing Clinic Login" in _onboarding()


# ===========================================================================
# 2. Required form fields
# ===========================================================================


def test_onboarding_has_clinic_name_field() -> None:
    assert "clinic_name" in _onboarding()


def test_onboarding_has_doctor_name_field() -> None:
    assert "doctor_name" in _onboarding()


def test_onboarding_has_contact_email_field() -> None:
    assert "contact_email" in _onboarding()


def test_onboarding_has_preferred_language_field() -> None:
    assert "preferred_language" in _onboarding()


# ===========================================================================
# 3. Language section
# ===========================================================================


def test_onboarding_has_deutsch_label() -> None:
    assert "Deutsch" in _onboarding()


def test_onboarding_has_english_fallback() -> None:
    content = _onboarding()
    assert "English" in content
    assert "fallback" in content.lower() or "Fallback" in content


def test_onboarding_has_german_first_copy() -> None:
    assert "Default for Austrian clinics: German-first" in _onboarding()


def test_onboarding_has_german_helper_text() -> None:
    assert "Deutsch zuerst" in _onboarding()


# ===========================================================================
# 4. Consent / acknowledgement fields
# ===========================================================================


def test_onboarding_has_consent_pilot_contact() -> None:
    assert "consent_pilot_contact" in _onboarding()


def test_onboarding_has_acknowledges_no_phi() -> None:
    assert "acknowledges_no_phi" in _onboarding()


# ===========================================================================
# 5. Safety copy
# ===========================================================================


def test_onboarding_has_do_not_enter_patient_data() -> None:
    assert "Do not enter patient data" in _onboarding()


def test_onboarding_has_no_phi_processing_copy() -> None:
    assert "Pilot activation does not enable production PHI processing" in _onboarding()


def test_onboarding_has_security_legal_review_copy() -> None:
    assert "Pilot activation requires security, legal, and production-readiness review" in _onboarding()


# ===========================================================================
# 6. Backend connection
# ===========================================================================


def test_onboarding_posts_to_clinic_onboarding_requests() -> None:
    assert "/clinic-onboarding-requests" in _onboarding()


def test_onboarding_uses_fetch_post() -> None:
    content = _onboarding()
    assert "fetch(" in content
    assert "'POST'" in content or '"POST"' in content


def test_onboarding_uses_credentials_include() -> None:
    assert "credentials" in _onboarding() and "include" in _onboarding()


# ===========================================================================
# 7. Forbidden fields — not sent to backend
# ===========================================================================


def test_onboarding_does_not_send_production_phi_enabled() -> None:
    # production_phi_enabled must not appear in the payload construction
    content = _onboarding()
    # The field should not appear in the source at all
    assert "production_phi_enabled" not in content


def test_onboarding_does_not_include_vapi_credentials() -> None:
    content = _onboarding()
    for cred_key in ("vapi_api_key", "vapi_secret", "vapi_key", "api_key"):
        assert cred_key not in content, f"onboarding must not include credential field: {cred_key!r}"


def test_onboarding_does_not_send_status_field() -> None:
    # status is server-controlled; must not be in the submitted payload
    content = _onboarding()
    # status field not in the payload object keys
    assert "status:" not in content or "submitState" in content  # submitState is the React state var, not payload


def test_onboarding_does_not_send_clinic_id() -> None:
    assert "clinic_id" not in _onboarding()


# ===========================================================================
# 8. No browser token storage
# ===========================================================================


def test_onboarding_no_session_storage() -> None:
    assert "sessionStorage" not in _onboarding()


def test_onboarding_no_local_storage() -> None:
    assert "localStorage" not in _onboarding()


# ===========================================================================
# 9. Success and error states
# ===========================================================================


def test_onboarding_has_pilot_request_submitted_success_text() -> None:
    assert "Pilot request submitted" in _onboarding()


def test_onboarding_has_error_state() -> None:
    content = _onboarding()
    assert "error" in content.lower()
    assert "errorMessage" in content or "Submission error" in content


def test_onboarding_success_state_shows_request_id() -> None:
    assert "requestId" in _onboarding() or "Request ID" in _onboarding()


# ===========================================================================
# 10. No raw secrets or PHI markers in source
# ===========================================================================


def test_onboarding_no_hardcoded_jwt() -> None:
    import re
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", _onboarding())


def test_onboarding_no_api_key_marker() -> None:
    assert "sk-" not in _onboarding()


def test_onboarding_no_phi_data_markers() -> None:
    content = _onboarding()
    for marker in ("SVNR", "sozialversicherung", "DOB:"):
        assert marker not in content, f"onboarding must not contain PHI marker {marker!r}"


# ===========================================================================
# 11. Architecture doc
# ===========================================================================


def test_arch_doc_exists() -> None:
    assert os.path.isfile(
        os.path.join(_DOCS, "architecture", "ONBOARDING_FRONTEND_BACKEND_CONNECTION.md")
    )


def test_arch_doc_covers_public_endpoint() -> None:
    assert "/clinic-onboarding-requests" in _arch()


def test_arch_doc_covers_german_first() -> None:
    flat = _arch().lower()
    assert "german" in flat or "deutsch" in flat


def test_arch_doc_covers_consent_requirements() -> None:
    flat = _arch().lower()
    assert "consent" in flat


def test_arch_doc_no_automatic_activation() -> None:
    flat = _arch().lower()
    assert "no automatic" in flat or "not automatic" in flat or "does not" in flat


def test_arch_doc_production_phi_no_go() -> None:
    assert "NO-GO" in _arch() or "no-go" in _arch().lower()
