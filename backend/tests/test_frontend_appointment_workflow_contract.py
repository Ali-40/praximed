"""
Contract tests — Sprint 11 / Module 81
Appointment Request Workflow UI Foundation

Static checks that verify the frontend Confirm action is wired correctly
without running any JavaScript/TypeScript or touching a real database.
"""

import pathlib

REPO_ROOT = pathlib.Path(__file__).parents[2]
API_TS = REPO_ROOT / "frontend" / "lib" / "api.ts"
DASHBOARD_TSX = REPO_ROOT / "frontend" / "app" / "dashboard" / "page.tsx"


def _api() -> str:
    return API_TS.read_text(encoding="utf-8")


def _dash() -> str:
    return DASHBOARD_TSX.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. confirmAppointmentRequest defined in lib/api.ts
# ---------------------------------------------------------------------------

def test_confirm_helper_defined_in_api_ts():
    assert "confirmAppointmentRequest" in _api(), (
        "confirmAppointmentRequest must be defined in frontend/lib/api.ts"
    )


# ---------------------------------------------------------------------------
# 2. Helper uses PATCH method
# ---------------------------------------------------------------------------

def test_confirm_helper_uses_patch():
    content = _api()
    # Locate the confirmAppointmentRequest function block and check for PATCH
    idx = content.find("confirmAppointmentRequest")
    assert idx != -1
    # PATCH should appear after the function definition
    assert "'PATCH'" in content[idx:] or '"PATCH"' in content[idx:], (
        "confirmAppointmentRequest must use PATCH method"
    )


# ---------------------------------------------------------------------------
# 3. Helper targets /appointment-requests/{id}/status endpoint
# ---------------------------------------------------------------------------

def test_confirm_helper_uses_correct_endpoint():
    content = _api()
    assert "/appointment-requests/" in content and "/status" in content, (
        "confirmAppointmentRequest must call /appointment-requests/{id}/status"
    )


# ---------------------------------------------------------------------------
# 4. Helper uses Bearer token via apiFetch
# ---------------------------------------------------------------------------

def test_confirm_helper_uses_bearer_token():
    content = _api()
    idx = content.find("confirmAppointmentRequest")
    assert idx != -1
    # Helper delegates to apiFetch which adds the Bearer header
    assert "apiFetch" in content[idx:], (
        "confirmAppointmentRequest must use apiFetch to send the Bearer token"
    )


# ---------------------------------------------------------------------------
# 5. Dashboard imports confirmAppointmentRequest
# ---------------------------------------------------------------------------

def test_dashboard_imports_confirm_helper():
    content = _dash()
    assert "confirmAppointmentRequest" in content, (
        "dashboard/page.tsx must import confirmAppointmentRequest"
    )


# ---------------------------------------------------------------------------
# 6. Confirm button only shown for status === 'new'
# ---------------------------------------------------------------------------

def test_confirm_button_gated_on_new_status():
    content = _dash()
    assert "status === 'new'" in content or 'status === "new"' in content, (
        "Confirm button must be gated on appt.status === 'new'"
    )


# ---------------------------------------------------------------------------
# 7. Dashboard handles loading / disabled state while in-flight
# ---------------------------------------------------------------------------

def test_confirm_button_has_disabled_state():
    content = _dash()
    assert "disabled" in content, (
        "Confirm button must set disabled attribute while in-flight"
    )
    # confirmingIds tracks which rows are loading
    assert "confirmingIds" in content, (
        "dashboard/page.tsx must track in-flight confirm IDs"
    )


# ---------------------------------------------------------------------------
# 8. Dashboard shows generic error on action failure
# ---------------------------------------------------------------------------

def test_confirm_action_error_state():
    content = _dash()
    assert "apptActionError" in content, (
        "dashboard/page.tsx must have an apptActionError state for action failures"
    )
    assert "Could not confirm" in content, (
        "dashboard/page.tsx must show a generic error message on Confirm failure"
    )


# ---------------------------------------------------------------------------
# 9. Dashboard refetches / updates appointments on success
# ---------------------------------------------------------------------------

def test_dashboard_refetches_after_confirm():
    content = _dash()
    # After confirming, the helper re-calls fetchAppointmentRequests
    assert "fetchAppointmentRequests" in content, (
        "dashboard/page.tsx must call fetchAppointmentRequests to refresh after confirm"
    )
    assert "setAppointments" in content, (
        "dashboard/page.tsx must update appointments state after successful confirm"
    )


# ---------------------------------------------------------------------------
# 10. No hardcoded tokens or real patient data
# ---------------------------------------------------------------------------

def test_no_hardcoded_credentials_in_workflow_files():
    for label, content in [("api.ts", _api()), ("dashboard/page.tsx", _dash())]:
        assert "Bearer eyJ" not in content, (
            f"{label} must not contain a hardcoded Bearer token"
        )
        assert "local-dev-password" not in content, (
            f"{label} must not contain hardcoded passwords"
        )
        assert "patient.local@praximed.test" not in content, (
            f"{label} must not contain real (or fake-real) patient emails"
        )
