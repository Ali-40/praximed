"""
Static contract tests for frontend patient list dashboard integration
— PraxisMed Sprint 8 / Module 69.

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
# 1. API helper defines fetchPatients
# ---------------------------------------------------------------------------

def test_api_helper_defines_fetch_patients():
    content = _read("lib/api.ts")
    assert "fetchPatients" in content, \
        "lib/api.ts must define a fetchPatients helper"


# ---------------------------------------------------------------------------
# 2. Patient helper uses Authorization Bearer token (via apiFetch)
# ---------------------------------------------------------------------------

def test_patient_helper_uses_bearer_token():
    content = _read("lib/api.ts")
    assert "Authorization" in content, \
        "lib/api.ts must set an Authorization header"
    assert "Bearer" in content, \
        "lib/api.ts must use the Bearer token scheme"


# ---------------------------------------------------------------------------
# 3. Patient helper routes through the shared apiFetch / base URL
# ---------------------------------------------------------------------------

def test_patient_helper_uses_api_base_url():
    content = _read("lib/api.ts")
    assert "apiFetch" in content, \
        "lib/api.ts must use apiFetch (which applies NEXT_PUBLIC_API_BASE_URL)"
    assert "/patients" in content, \
        "lib/api.ts must call the /patients endpoint"


# ---------------------------------------------------------------------------
# 4. Dashboard calls fetchPatients
# ---------------------------------------------------------------------------

def test_dashboard_calls_fetch_patients():
    content = _read("app/dashboard/page.tsx")
    assert "fetchPatients" in content, \
        "dashboard/page.tsx must call fetchPatients"


# ---------------------------------------------------------------------------
# 5. Dashboard has a loading state for patients
# ---------------------------------------------------------------------------

def test_dashboard_has_patient_loading_state():
    content = _read("app/dashboard/page.tsx")
    assert "patientsLoading" in content, \
        "dashboard/page.tsx must have a patientsLoading state"
    assert "Loading" in content or "loading" in content.lower(), \
        "dashboard/page.tsx must render a loading indicator for patients"


# ---------------------------------------------------------------------------
# 6. Dashboard has an error state for patients
# ---------------------------------------------------------------------------

def test_dashboard_has_patient_error_state():
    content = _read("app/dashboard/page.tsx")
    assert "patientsError" in content, \
        "dashboard/page.tsx must have a patientsError state"
    assert "Could not load" in content or "error" in content.lower(), \
        "dashboard/page.tsx must show a generic error message for patients"


# ---------------------------------------------------------------------------
# 7. Dashboard has an empty state for patients
# ---------------------------------------------------------------------------

def test_dashboard_has_patient_empty_state():
    content = _read("app/dashboard/page.tsx")
    assert "No patients" in content or \
           "patients.length === 0" in content or \
           "length === 0" in content, \
        "dashboard/page.tsx must handle the empty (zero results) state for patients"


# ---------------------------------------------------------------------------
# 8. Dashboard renders the Patients section
# ---------------------------------------------------------------------------

def test_dashboard_renders_patients_section():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="patients"' in content or \
           "section" in content.lower(), \
        "dashboard/page.tsx must have a patients section"
    assert "first_name" in content or "last_name" in content or \
           "patient." in content, \
        "dashboard/page.tsx must render individual patient data"


# ---------------------------------------------------------------------------
# 9. Appointments integration remains intact
# ---------------------------------------------------------------------------

def test_appointments_integration_remains():
    content = _read("app/dashboard/page.tsx")
    assert "fetchAppointmentRequests" in content, \
        "dashboard/page.tsx must still call fetchAppointmentRequests (Module 68 not removed)"
    assert "appointments" in content.lower(), \
        "dashboard/page.tsx must still have an appointments section"


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


# ---------------------------------------------------------------------------
# 11. Patient interface includes full_name (Sprint 10 / Module 78)
# ---------------------------------------------------------------------------

def test_patient_interface_includes_full_name():
    content = _read("lib/api.ts")
    assert "full_name" in content, (
        "lib/api.ts Patient interface must include full_name "
        "(backend patients table stores name as a single full_name column)"
    )


# ---------------------------------------------------------------------------
# 12. Dashboard patient name display uses full_name first
# ---------------------------------------------------------------------------

def test_dashboard_patient_display_uses_full_name():
    content = _read("app/dashboard/page.tsx")
    assert "patient.full_name" in content, (
        "dashboard/page.tsx must use patient.full_name in the patient name display expression"
    )


# ---------------------------------------------------------------------------
# 13. Dashboard patient name fallback is "Unnamed patient", not "—"
# ---------------------------------------------------------------------------

def test_dashboard_patient_fallback_is_unnamed_not_dash():
    content = _read("app/dashboard/page.tsx")
    assert "Unnamed patient" in content, (
        "dashboard/page.tsx must use 'Unnamed patient' as the patient name fallback, not '—'"
    )
    # The old broken pattern was: join(' ') || '—'
    # After the fix the expression uses 'Unnamed patient'; || '—' must not remain.
    assert "|| '—'" not in content, (
        "dashboard/page.tsx must not use \"|| '—'\" as the patient name fallback"
    )
