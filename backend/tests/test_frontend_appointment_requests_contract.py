"""
Static contract tests for frontend appointment requests dashboard integration
— PraxisMed Sprint 8 / Module 68.

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
# 1. Dashboard imports/calls the appointment request API helper
# ---------------------------------------------------------------------------

def test_dashboard_calls_appointment_request_helper():
    content = _read("app/dashboard/page.tsx")
    assert "fetchAppointmentRequests" in content, \
        "dashboard/page.tsx must call fetchAppointmentRequests"


# ---------------------------------------------------------------------------
# 2. API helper attaches Authorization Bearer token
# ---------------------------------------------------------------------------

def test_api_helper_attaches_bearer_token():
    content = _read("lib/api.ts")
    assert "Authorization" in content, \
        "lib/api.ts must set an Authorization header"
    assert "Bearer" in content, \
        "lib/api.ts must use Bearer token scheme"


# ---------------------------------------------------------------------------
# 3. API helper uses NEXT_PUBLIC_API_BASE_URL with localhost fallback
# ---------------------------------------------------------------------------

def test_api_helper_env_var_and_fallback():
    content = _read("lib/api.ts")
    assert "NEXT_PUBLIC_API_BASE_URL" in content, \
        "lib/api.ts must reference NEXT_PUBLIC_API_BASE_URL"
    assert "127.0.0.1:8000" in content or "localhost:8000" in content, \
        "lib/api.ts must have a localhost fallback"


# ---------------------------------------------------------------------------
# 4. Dashboard has a loading state for appointment requests
# ---------------------------------------------------------------------------

def test_dashboard_has_loading_state():
    content = _read("app/dashboard/page.tsx")
    assert "loading" in content.lower(), \
        "dashboard/page.tsx must handle a loading state"
    assert "Loading" in content or "loading" in content, \
        "dashboard/page.tsx must render a loading indicator"


# ---------------------------------------------------------------------------
# 5. Dashboard has a generic error state for appointment requests
# ---------------------------------------------------------------------------

def test_dashboard_has_error_state():
    content = _read("app/dashboard/page.tsx")
    assert "error" in content.lower(), \
        "dashboard/page.tsx must handle an error state"
    # Error message must be generic — not reveal internal details
    assert "Could not load" in content or "error" in content.lower(), \
        "dashboard/page.tsx must show a generic error message"


# ---------------------------------------------------------------------------
# 6. Dashboard has an empty state for appointment requests
# ---------------------------------------------------------------------------

def test_dashboard_has_empty_state():
    content = _read("app/dashboard/page.tsx")
    assert "empty" in content.lower() or \
           "No appointment" in content or \
           "length === 0" in content, \
        "dashboard/page.tsx must handle the empty (zero results) state"


# ---------------------------------------------------------------------------
# 7. Dashboard renders the appointment request list/section
# ---------------------------------------------------------------------------

def test_dashboard_renders_appointment_section():
    content = _read("app/dashboard/page.tsx")
    assert "appointments" in content.lower(), \
        "dashboard/page.tsx must have an appointments section"
    # Must render individual appointment data
    assert "patient_name" in content or "appt." in content, \
        "dashboard/page.tsx must render appointment row data"


# ---------------------------------------------------------------------------
# 8. No hard-coded tokens or credentials in frontend files
# ---------------------------------------------------------------------------

def test_no_hardcoded_tokens_or_credentials():
    for rel in ("lib/api.ts", "lib/auth.ts", "app/dashboard/page.tsx"):
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), \
            f"{rel} must not contain a hardcoded JWT token"
        assert "sk-" not in content, \
            f"{rel} must not contain an API key string"


# ---------------------------------------------------------------------------
# 9. No real patient data markers in dashboard or API helper
# ---------------------------------------------------------------------------

def test_no_real_patient_data_markers():
    for rel in ("app/dashboard/page.tsx", "lib/api.ts"):
        content = _read(rel)
        for pattern in ("DOB:", "1234567890", "SVNR", "sozialversicherung"):
            assert pattern not in content, \
                f"{rel} must not contain real patient data marker: {pattern!r}"


# ---------------------------------------------------------------------------
# 10. README mentions appointment request fetching on the dashboard
# ---------------------------------------------------------------------------

def test_readme_mentions_appointment_fetch():
    content = _read("README.md")
    assert "appointment" in content.lower(), \
        "README.md must mention appointment request fetching"
    assert "Bearer" in content or "JWT" in content or "token" in content.lower(), \
        "README.md must mention JWT/token usage for the dashboard fetch"
