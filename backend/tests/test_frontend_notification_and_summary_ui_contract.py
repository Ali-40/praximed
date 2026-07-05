"""
Static contract tests for Sprint 17 / Module 125 — Dashboard Notification and Summary UI Foundation.

Verifies file content only. No JS/TS runtime. No database. No network. No secrets.
"""

from __future__ import annotations

import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")


def _read(rel: str) -> str:
    with open(os.path.join(FRONTEND, rel), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. api.ts defines PreAppointmentSummary interface
# ---------------------------------------------------------------------------

def test_api_defines_pre_appointment_summary_interface():
    content = _read("lib/api.ts")
    assert "PreAppointmentSummary" in content


# ---------------------------------------------------------------------------
# 2. api.ts defines fetchPreAppointmentSummary function
# ---------------------------------------------------------------------------

def test_api_defines_fetch_pre_appointment_summary():
    content = _read("lib/api.ts")
    assert "fetchPreAppointmentSummary" in content


# ---------------------------------------------------------------------------
# 3. fetchPreAppointmentSummary calls the correct endpoint
# ---------------------------------------------------------------------------

def test_api_pre_appointment_summary_calls_correct_endpoint():
    content = _read("lib/api.ts")
    assert "pre-appointment-summary" in content


# ---------------------------------------------------------------------------
# 4. fetchPreAppointmentSummary uses credentials: include (cookie-based auth)
# ---------------------------------------------------------------------------

def test_api_uses_credentials_include():
    content = _read("lib/api.ts")
    assert "credentials" in content
    assert "include" in content


# ---------------------------------------------------------------------------
# 5. Dashboard imports fetchPreAppointmentSummary and PreAppointmentSummary
# ---------------------------------------------------------------------------

def test_dashboard_imports_fetch_pre_appointment_summary():
    content = _read("app/dashboard/page.tsx")
    assert "fetchPreAppointmentSummary" in content
    assert "PreAppointmentSummary" in content


# ---------------------------------------------------------------------------
# 6. Dashboard has a "View summary" button on appointment rows
# ---------------------------------------------------------------------------

def test_dashboard_has_view_summary_action():
    content = _read("app/dashboard/page.tsx")
    assert "view-summary" in content or "View summary" in content


# ---------------------------------------------------------------------------
# 7. Dashboard has a summary panel (data-state="summary-panel")
# ---------------------------------------------------------------------------

def test_dashboard_has_summary_panel():
    content = _read("app/dashboard/page.tsx")
    assert 'summary-panel' in content


# ---------------------------------------------------------------------------
# 8. Summary panel shows suggested_next_action
# ---------------------------------------------------------------------------

def test_summary_panel_shows_suggested_next_action():
    content = _read("app/dashboard/page.tsx")
    assert "suggested_next_action" in content


# ---------------------------------------------------------------------------
# 9. Summary panel shows safety_note
# ---------------------------------------------------------------------------

def test_summary_panel_shows_safety_note():
    content = _read("app/dashboard/page.tsx")
    assert "safety_note" in content


# ---------------------------------------------------------------------------
# 10. Summary panel shows patient_name
# ---------------------------------------------------------------------------

def test_summary_panel_shows_patient_name():
    content = _read("app/dashboard/page.tsx")
    assert "patient_name" in content


# ---------------------------------------------------------------------------
# 11. Summary panel shows patient_type
# ---------------------------------------------------------------------------

def test_summary_panel_shows_patient_type():
    content = _read("app/dashboard/page.tsx")
    assert "patient_type" in content


# ---------------------------------------------------------------------------
# 12. Summary panel shows reason
# ---------------------------------------------------------------------------

def test_summary_panel_shows_reason():
    content = _read("app/dashboard/page.tsx")
    assert "reason" in content


# ---------------------------------------------------------------------------
# 13. No diagnosis shown in summary panel
# ---------------------------------------------------------------------------

def test_summary_panel_no_diagnosis():
    content = _read("app/dashboard/page.tsx")
    assert "diagnosis" not in content.lower()


# ---------------------------------------------------------------------------
# 14. No medical advice shown in summary panel
# ---------------------------------------------------------------------------

def test_summary_panel_no_medical_advice():
    content = _read("app/dashboard/page.tsx")
    assert "medical advice" not in content.lower()


# ---------------------------------------------------------------------------
# 15. Notifications section shows message field
# ---------------------------------------------------------------------------

def test_notifications_section_shows_message():
    content = _read("app/dashboard/page.tsx")
    assert "notif.message" in content or "notification_message" in content or "truncatedMsg" in content


# ---------------------------------------------------------------------------
# 16. Notifications section shows status field
# ---------------------------------------------------------------------------

def test_notifications_section_shows_status():
    content = _read("app/dashboard/page.tsx")
    assert "notif.status" in content


# ---------------------------------------------------------------------------
# 17. Pending notifications are highlighted
# ---------------------------------------------------------------------------

def test_notifications_pending_highlighted():
    content = _read("app/dashboard/page.tsx")
    assert "pending" in content


# ---------------------------------------------------------------------------
# 18. Confirm button remains present for new appointments
# ---------------------------------------------------------------------------

def test_confirm_button_remains():
    content = _read("app/dashboard/page.tsx")
    assert 'data-action="confirm"' in content
    assert "handleConfirm" in content


# ---------------------------------------------------------------------------
# 19. fetchNotifications still called — existing integration intact
# ---------------------------------------------------------------------------

def test_fetch_notifications_still_called():
    content = _read("app/dashboard/page.tsx")
    assert "fetchNotifications" in content


# ---------------------------------------------------------------------------
# 20. No token storage — no functional sessionStorage or localStorage calls
# ---------------------------------------------------------------------------

def test_no_token_storage():
    content = _read("app/dashboard/page.tsx")
    # Comments may mention sessionStorage for documentation purposes; only flag actual usage.
    non_comment_lines = [ln for ln in content.splitlines() if not ln.strip().startswith("//")]
    non_comment = "\n".join(non_comment_lines)
    assert "sessionStorage" not in non_comment
    assert "localStorage" not in non_comment


# ---------------------------------------------------------------------------
# 21. No hardcoded secrets or real patient data
# ---------------------------------------------------------------------------

def test_no_hardcoded_secrets():
    for rel in ("lib/api.ts", "app/dashboard/page.tsx"):
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), \
            f"{rel} must not contain a hardcoded JWT"
        assert "sk-" not in content, f"{rel} must not contain an API key"
