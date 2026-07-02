"""
Static contract tests for frontend dashboard visual polish
— PraxisMed Sprint 10 / Module 79.

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
# 1. Dashboard renders the PraxisMed brand name
# ---------------------------------------------------------------------------

def test_dashboard_renders_praximed_brand():
    content = _read("app/dashboard/page.tsx")
    assert "PraxisMed" in content, \
        "dashboard/page.tsx must render the PraxisMed brand name"


# ---------------------------------------------------------------------------
# 2. Dashboard has a Logout button
# ---------------------------------------------------------------------------

def test_dashboard_has_logout_button():
    content = _read("app/dashboard/page.tsx")
    assert "Logout" in content, \
        "dashboard/page.tsx must include a Logout button"
    assert "handleLogout" in content or "clearToken" in content, \
        "dashboard/page.tsx must wire the Logout button to the logout action"


# ---------------------------------------------------------------------------
# 3. Dashboard includes an Appointments section
# ---------------------------------------------------------------------------

def test_dashboard_includes_appointments_section():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="appointments"' in content, \
        'dashboard/page.tsx must have data-section="appointments"'
    assert "fetchAppointmentRequests" in content, \
        "dashboard/page.tsx must call fetchAppointmentRequests"


# ---------------------------------------------------------------------------
# 4. Dashboard includes a Patients section
# ---------------------------------------------------------------------------

def test_dashboard_includes_patients_section():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="patients"' in content, \
        'dashboard/page.tsx must have data-section="patients"'
    assert "fetchPatients" in content, \
        "dashboard/page.tsx must call fetchPatients"


# ---------------------------------------------------------------------------
# 5. Dashboard includes a Notifications section
# ---------------------------------------------------------------------------

def test_dashboard_includes_notifications_section():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="notifications"' in content, \
        'dashboard/page.tsx must have data-section="notifications"'
    assert "fetchNotifications" in content, \
        "dashboard/page.tsx must call fetchNotifications"


# ---------------------------------------------------------------------------
# 6. Dashboard includes a Consultations section
# ---------------------------------------------------------------------------

def test_dashboard_includes_consultations_section():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="consultations"' in content, \
        'dashboard/page.tsx must have data-section="consultations"'
    assert "fetchConsultations" in content, \
        "dashboard/page.tsx must call fetchConsultations"


# ---------------------------------------------------------------------------
# 7. Dashboard has a clinical/professional heading (not just "Welcome")
# ---------------------------------------------------------------------------

def test_dashboard_has_clinical_context_heading():
    content = _read("app/dashboard/page.tsx")
    assert "Clinic" in content, \
        "dashboard/page.tsx must include a clinical context heading (e.g. 'Clinic Overview' or 'Clinic Dashboard')"
    assert "Overview" in content or "Dashboard" in content, \
        "dashboard/page.tsx must have a clinical overview or dashboard heading"


# ---------------------------------------------------------------------------
# 8. Dashboard keeps all four loading, error, and empty states
# ---------------------------------------------------------------------------

def test_dashboard_has_all_loading_error_empty_states():
    content = _read("app/dashboard/page.tsx")
    # Loading states
    for state_var in ("apptLoading", "patientsLoading", "notifLoading", "consultLoading"):
        assert state_var in content, \
            f"dashboard/page.tsx must still have {state_var} loading state"
    # Error states
    for err_var in ("apptError", "patientsError", "notifError", "consultError"):
        assert err_var in content, \
            f"dashboard/page.tsx must still have {err_var} error state"
    # data-state attrs
    for state in ('data-state="loading"', 'data-state="error"',
                  'data-state="empty"', 'data-state="list"'):
        assert state in content, \
            f"dashboard/page.tsx must still include {state!r} state attribute"


# ---------------------------------------------------------------------------
# 9. Dashboard uses badge styling (consistent inline styles or token refs)
# ---------------------------------------------------------------------------

def test_dashboard_uses_badge_styling():
    content = _read("app/dashboard/page.tsx")
    # Badge styling must reference colour tokens or inline color values
    assert "badge" in content.lower() or "background" in content, \
        "dashboard/page.tsx must have badge/background styling for status indicators"
    # The badgeStyle / BADGE_STYLES helper must exist or inline styles must be present
    assert "badgeStyle" in content or "BADGE_STYLES" in content or \
           "background:" in content or "background:" in content, \
        "dashboard/page.tsx must apply background styling to status badges"


# ---------------------------------------------------------------------------
# 10. No hard-coded credentials, tokens, or real patient data
# ---------------------------------------------------------------------------

def test_no_hardcoded_credentials_or_real_data():
    for rel in ("app/dashboard/page.tsx", "app/globals.css"):
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), \
            f"{rel} must not contain a hardcoded JWT token"
        assert "sk-" not in content, \
            f"{rel} must not contain an API key string"
        for marker in ("DOB:", "1234567890", "SVNR", "sozialversicherung"):
            assert marker not in content, \
                f"{rel} must not contain real patient data marker: {marker!r}"
