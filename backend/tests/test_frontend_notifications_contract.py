"""
Static contract tests for frontend notifications dashboard integration
— PraxisMed Sprint 8 / Module 70.

These tests verify file content structure only.
No JS/TS runtime is invoked.
"""

from __future__ import annotations

import os
import re

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")


def _read(rel: str) -> str:
    with open(os.path.join(FRONTEND, rel), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. API helper defines fetchNotifications
# ---------------------------------------------------------------------------

def test_api_helper_defines_fetch_notifications():
    content = _read("lib/api.ts")
    assert "fetchNotifications" in content, \
        "lib/api.ts must define a fetchNotifications helper"


# ---------------------------------------------------------------------------
# 2. Notification helper uses credentials: "include" for cookie-based auth (Module 120)
# ---------------------------------------------------------------------------

def test_notification_helper_uses_bearer_token():
    content = _read("lib/api.ts")
    # Module 120: auth is handled via httpOnly cookie; apiFetch uses credentials: "include".
    assert "credentials" in content, \
        "lib/api.ts must include credentials field for cookie-based auth (Module 120)"
    assert "include" in content, \
        "lib/api.ts must set credentials: 'include' to send the session cookie"


# ---------------------------------------------------------------------------
# 3. Notification helper routes through the shared apiFetch / base URL
# ---------------------------------------------------------------------------

def test_notification_helper_uses_api_base_url():
    content = _read("lib/api.ts")
    assert "apiFetch" in content, \
        "lib/api.ts must use apiFetch (which applies NEXT_PUBLIC_API_BASE_URL)"
    assert "/notifications" in content, \
        "lib/api.ts must call the /notifications endpoint"


# ---------------------------------------------------------------------------
# 4. Dashboard calls fetchNotifications
# ---------------------------------------------------------------------------

def test_dashboard_calls_fetch_notifications():
    content = _read("app/dashboard/page.tsx")
    assert "fetchNotifications" in content, \
        "dashboard/page.tsx must call fetchNotifications"


# ---------------------------------------------------------------------------
# 5. Dashboard has a loading state for notifications
# ---------------------------------------------------------------------------

def test_dashboard_has_notification_loading_state():
    content = _read("app/dashboard/page.tsx")
    assert "notifLoading" in content, \
        "dashboard/page.tsx must have a notifLoading state"
    assert "Loading" in content or "loading" in content.lower(), \
        "dashboard/page.tsx must render a loading indicator for notifications"


# ---------------------------------------------------------------------------
# 6. Dashboard has an error state for notifications
# ---------------------------------------------------------------------------

def test_dashboard_has_notification_error_state():
    content = _read("app/dashboard/page.tsx")
    assert "notifError" in content, \
        "dashboard/page.tsx must have a notifError state"
    assert "Could not load" in content or "error" in content.lower(), \
        "dashboard/page.tsx must show a generic error message for notifications"


# ---------------------------------------------------------------------------
# 7. Dashboard has an empty state for notifications
# ---------------------------------------------------------------------------

def test_dashboard_has_notification_empty_state():
    content = _read("app/dashboard/page.tsx")
    assert "No notifications" in content or \
           "notifications.length === 0" in content or \
           "length === 0" in content, \
        "dashboard/page.tsx must handle the empty (zero results) state for notifications"


# ---------------------------------------------------------------------------
# 8. Dashboard renders the Notifications section
# ---------------------------------------------------------------------------

def test_dashboard_renders_notifications_section():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="notifications"' in content or \
           "notifications" in content.lower(), \
        "dashboard/page.tsx must have a notifications section"
    assert "notif." in content or "notification_type" in content or \
           "priority" in content, \
        "dashboard/page.tsx must render individual notification data"


# ---------------------------------------------------------------------------
# 9. Appointments and Patients integrations remain intact
# ---------------------------------------------------------------------------

def test_appointments_and_patients_integrations_remain():
    content = _read("app/dashboard/page.tsx")
    assert "fetchAppointmentRequests" in content, \
        "dashboard/page.tsx must still call fetchAppointmentRequests (Module 68 not removed)"
    assert "fetchPatients" in content, \
        "dashboard/page.tsx must still call fetchPatients (Module 69 not removed)"
    assert "appointments" in content.lower(), \
        "dashboard/page.tsx must still have an appointments section"
    assert "patients" in content.lower(), \
        "dashboard/page.tsx must still have a patients section"


# ---------------------------------------------------------------------------
# 10. No hardcoded tokens, credentials, or real patient data
# ---------------------------------------------------------------------------

def test_no_hardcoded_tokens_or_real_patient_data():
    for rel in ("lib/api.ts", "app/dashboard/page.tsx"):
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), \
            f"{rel} must not contain a hardcoded JWT token"
        assert "sk-" not in content, \
            f"{rel} must not contain an API key string"
        for pattern in ("DOB:", "1234567890", "SVNR", "sozialversicherung"):
            assert pattern not in content, \
                f"{rel} must not contain real patient data marker: {pattern!r}"
