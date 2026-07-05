"""
Static contract tests for Sprint 18 / Module 126 — Fabel 5 Premium Dashboard UI/UX Polish.

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
# 1. Dashboard has premium header / clinic dashboard wording
# ---------------------------------------------------------------------------

def test_dashboard_has_premium_header():
    content = _read("app/dashboard/page.tsx")
    assert "Clinic Dashboard" in content or "PraxisMed" in content


# ---------------------------------------------------------------------------
# 2. Dashboard has staging demo status indicator
# ---------------------------------------------------------------------------

def test_dashboard_has_staging_demo_indicator():
    content = _read("app/dashboard/page.tsx")
    assert "Staging demo" in content or "staging" in content.lower()


# ---------------------------------------------------------------------------
# 3. Dashboard has overview metric cards
# ---------------------------------------------------------------------------

def test_dashboard_has_metric_cards():
    content = _read("app/dashboard/page.tsx")
    assert "MetricCard" in content or "metric" in content.lower() or "Appointments" in content


# ---------------------------------------------------------------------------
# 4. Dashboard has pending confirmations metric
# ---------------------------------------------------------------------------

def test_dashboard_has_pending_confirmations_metric():
    content = _read("app/dashboard/page.tsx")
    assert "Pending" in content or "pendingCount" in content


# ---------------------------------------------------------------------------
# 5. Appointments section still exists with data-section attribute
# ---------------------------------------------------------------------------

def test_appointments_section_exists():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="appointments"' in content


# ---------------------------------------------------------------------------
# 6. Patients section still exists
# ---------------------------------------------------------------------------

def test_patients_section_exists():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="patients"' in content


# ---------------------------------------------------------------------------
# 7. Notifications section still exists
# ---------------------------------------------------------------------------

def test_notifications_section_exists():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="notifications"' in content


# ---------------------------------------------------------------------------
# 8. Consultations section still exists
# ---------------------------------------------------------------------------

def test_consultations_section_exists():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="consultations"' in content


# ---------------------------------------------------------------------------
# 9. View summary button still exists
# ---------------------------------------------------------------------------

def test_view_summary_button_exists():
    content = _read("app/dashboard/page.tsx")
    assert "View summary" in content or 'data-action="view-summary"' in content


# ---------------------------------------------------------------------------
# 10. Hide summary button still exists
# ---------------------------------------------------------------------------

def test_hide_summary_button_exists():
    content = _read("app/dashboard/page.tsx")
    assert "Hide summary" in content


# ---------------------------------------------------------------------------
# 11. Confirm button still exists
# ---------------------------------------------------------------------------

def test_confirm_button_exists():
    content = _read("app/dashboard/page.tsx")
    assert 'data-action="confirm"' in content


# ---------------------------------------------------------------------------
# 12. Summary panel still includes suggested_next_action
# ---------------------------------------------------------------------------

def test_summary_panel_has_suggested_next_action():
    content = _read("app/dashboard/page.tsx")
    assert "suggested_next_action" in content


# ---------------------------------------------------------------------------
# 13. Summary panel still includes safety_note
# ---------------------------------------------------------------------------

def test_summary_panel_has_safety_note():
    content = _read("app/dashboard/page.tsx")
    assert "safety_note" in content


# ---------------------------------------------------------------------------
# 14. No diagnosis wording added to display
# ---------------------------------------------------------------------------

def test_no_diagnosis_in_display():
    content = _read("app/dashboard/page.tsx")
    assert "diagnosis" not in content.lower()


# ---------------------------------------------------------------------------
# 15. No medical advice wording added to display
# ---------------------------------------------------------------------------

def test_no_medical_advice_in_display():
    content = _read("app/dashboard/page.tsx")
    assert "medical advice" not in content.lower()


# ---------------------------------------------------------------------------
# 16. credentials: include still used in api.ts
# ---------------------------------------------------------------------------

def test_credentials_include_in_api():
    content = _read("lib/api.ts")
    assert "credentials" in content and "include" in content


# ---------------------------------------------------------------------------
# 17. No sessionStorage or localStorage token usage (excluding comments)
# ---------------------------------------------------------------------------

def test_no_token_storage():
    content = _read("app/dashboard/page.tsx")
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "sessionStorage" not in non_comment
    assert "localStorage" not in non_comment


# ---------------------------------------------------------------------------
# 18. Notification UI is internal only — no external delivery claims
# ---------------------------------------------------------------------------

def test_notification_ui_internal_only():
    content = _read("app/dashboard/page.tsx")
    assert "external" not in content.lower() or "no external" in content.lower()


# ---------------------------------------------------------------------------
# 19. Fake / non-PHI staging wording exists
# ---------------------------------------------------------------------------

def test_fake_non_phi_staging_wording():
    content = _read("app/dashboard/page.tsx")
    text = content.lower()
    assert "fake" in text or "staging" in text or "non-phi" in text


# ---------------------------------------------------------------------------
# 20. SectionCard / premium card component present
# ---------------------------------------------------------------------------

def test_premium_card_component_present():
    content = _read("app/dashboard/page.tsx")
    assert "SectionCard" in content or "cardStyle" in content or "shadow" in content.lower()


# ---------------------------------------------------------------------------
# 21. globals.css has updated premium design tokens
# ---------------------------------------------------------------------------

def test_globals_css_has_premium_tokens():
    content = _read("app/globals.css")
    assert "--color-card" in content or "--shadow-md" in content or "--radius-lg" in content


# ---------------------------------------------------------------------------
# 22. No hardcoded secrets or real patient data
# ---------------------------------------------------------------------------

def test_no_hardcoded_secrets():
    for rel in ("lib/api.ts", "app/dashboard/page.tsx"):
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), \
            f"{rel} must not contain a hardcoded JWT"
        assert "sk-" not in content, f"{rel} must not contain an API key"
