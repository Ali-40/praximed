"""
Static contract tests — Sprint 18 / Module 126C-FABEL5.

Premium Austrian Clinic Interface Overhaul:
- /dashboard replaced with premium 3-column split-screen clinical workspace
- Fabel 5 visual identity palette applied
- Dynamic multi-tenant identity banner via tenantDisplay helper
- Audio Transcript & Call Recording placeholder engine
- Patient Registry with search + history timeline
- Onboarding gateway flow (HTML entity bug fixed)
- Dark command-theme developer console
- Existing behavior, API contracts, and safety boundaries preserved

Fake-data staging only. No secrets. No real patient data. Production PHI: NO-GO.
"""

from __future__ import annotations

import os
import re

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_FRONTEND = os.path.join(_REPO_ROOT, "frontend")
_DOCS = os.path.join(_REPO_ROOT, "docs")


def _read(rel: str) -> str:
    with open(os.path.join(_FRONTEND, rel), encoding="utf-8") as f:
        return f.read()


def _read_doc(rel: str) -> str:
    with open(os.path.join(_DOCS, rel), encoding="utf-8") as f:
        return f.read()


def _dashboard() -> str:
    return _read("app/dashboard/page.tsx")


def _onboarding() -> str:
    return _read("app/onboarding/page.tsx")


def _console() -> str:
    return _read("app/developer-console/page.tsx")


# ---------------------------------------------------------------------------
# 1. Dashboard — 3-column premium workspace structure
# ---------------------------------------------------------------------------


def test_dashboard_has_incoming_ai_intake_queue() -> None:
    assert "Incoming AI Intake Queue" in _dashboard()


def test_dashboard_has_active_resolution_workspace() -> None:
    assert "Active Resolution Workspace" in _dashboard()


def test_dashboard_has_audio_transcript_and_call_recording() -> None:
    assert "Audio Transcript & Call Recording" in _dashboard()


def test_dashboard_has_patient_registry() -> None:
    assert "Patient Registry" in _dashboard()


def test_dashboard_has_search_clinical_registries() -> None:
    assert "Search Clinical Registries" in _dashboard()


def test_dashboard_has_combined_confirm_create_profile_cta() -> None:
    assert "Confirm Appointment & Create Patient Profile" in _dashboard()


def test_dashboard_preserves_view_and_hide_summary() -> None:
    content = _dashboard()
    assert "View summary" in content
    assert "Hide summary" in content


def test_dashboard_preserves_confirm() -> None:
    content = _dashboard()
    assert "Confirm" in content
    assert 'data-action="confirm"' in content


def test_dashboard_has_new_request_badge() -> None:
    assert "New Request" in _dashboard()


def test_dashboard_has_internal_notification_only_copy() -> None:
    assert "Internal notification only" in _dashboard()


def test_dashboard_has_safety_boundary_copy() -> None:
    content = _dashboard()
    assert "Fake-data staging" in content
    assert "No real patient data" in content
    assert "Production PHI" in content


# ---------------------------------------------------------------------------
# 2. Dashboard — Fabel 5 exact visual identity palette
# ---------------------------------------------------------------------------


def test_dashboard_has_primary_structural_ink() -> None:
    assert "#0B132B" in _dashboard()


def test_dashboard_has_clinical_accent() -> None:
    assert "#008080" in _dashboard()


def test_dashboard_has_highlight_muted_fill() -> None:
    assert "#E0F2F1" in _dashboard()


def test_dashboard_has_warning_new_state() -> None:
    assert "#FFB703" in _dashboard()


def test_dashboard_has_critical_error_state() -> None:
    assert "#E63946" in _dashboard()


def test_dashboard_has_canvas_background() -> None:
    assert "#F4F6F9" in _dashboard()


def test_globals_css_declares_fabel5_palette_tokens() -> None:
    css = _read("app/globals.css")
    for token in ("#0B132B", "#008080", "#E0F2F1", "#FFB703", "#E63946", "#F4F6F9"):
        assert token in css, f"globals.css must declare Fabel 5 token {token}"


def test_dashboard_uses_tabular_nums() -> None:
    css = _read("app/globals.css")
    dash = _dashboard()
    assert "tabular-nums" in css or "tabular-nums" in dash
    assert "pm-tabular" in dash


# ---------------------------------------------------------------------------
# 3. Dashboard — dynamic tenant identity via central helper
# ---------------------------------------------------------------------------


def test_dashboard_uses_tenant_display_helper() -> None:
    content = _dashboard()
    assert "getClinicDisplayName" in content
    assert "tenantDisplay" in content


def test_huber_fallback_centralized_in_tenant_display() -> None:
    tenant = _read("lib/tenantDisplay.ts")
    assert "Dr. Med. Alexander Huber | Innere Medizin Wien" in tenant
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in tenant


def test_huber_fallback_not_hardcoded_in_pages() -> None:
    # Display identity must come only from the central tenantDisplay helper.
    for rel in ("app/dashboard/page.tsx", "app/onboarding/page.tsx", "app/developer-console/page.tsx"):
        assert "Alexander Huber" not in _read(rel), (
            f"{rel} must not hardcode the tenant display name; use tenantDisplay helper"
        )


# ---------------------------------------------------------------------------
# 4. Dashboard — responsive 3-column layout
# ---------------------------------------------------------------------------


def test_dashboard_has_responsive_grid() -> None:
    content = _dashboard()
    assert "grid-template-columns" in content
    assert "minmax(" in content
    assert "@media" in content


def test_dashboard_has_three_column_ratio() -> None:
    content = _dashboard()
    assert "25%" in content and "45%" in content and "30%" in content


def test_dashboard_has_three_panels() -> None:
    content = _dashboard()
    for panel in ('data-panel="left"', 'data-panel="center"', 'data-panel="right"'):
        assert panel in content


# ---------------------------------------------------------------------------
# 5. Dashboard — intake queue and workspace behavior scaffolding
# ---------------------------------------------------------------------------


def test_dashboard_has_no_phone_captured_fallback() -> None:
    assert "No phone captured" in _dashboard()


def test_dashboard_has_intake_empty_state() -> None:
    assert "No incoming AI intake requests yet." in _dashboard()


def test_dashboard_has_recording_safe_empty_copy() -> None:
    assert (
        "Recording/transcript review will appear here when Vapi recording ingestion is enabled."
        in _dashboard()
    )


def test_dashboard_has_recording_ingestion_pending() -> None:
    assert "Recording ingestion pending" in _dashboard()


def test_dashboard_has_play_audio_call_button() -> None:
    assert "Play Audio Call" in _dashboard()


def test_dashboard_has_profile_automation_label() -> None:
    assert "Profile creation automation coming next" in _dashboard()


def test_dashboard_has_history_placeholders() -> None:
    content = _dashboard()
    assert "Linked history will appear here as appointment requests accumulate." in content
    assert "Appointment history will appear here as linked visits accumulate." in content


def test_dashboard_demo_placeholder_patients_clearly_marked() -> None:
    content = _dashboard()
    assert "Dr. Johann Huber" in content
    assert "Anna Wallner" in content
    assert "Demo placeholder" in content
    # Only rendered when the real patients array is empty
    assert "patients.length === 0" in content


# ---------------------------------------------------------------------------
# 6. Dashboard — no browser token storage, no unsafe content
# ---------------------------------------------------------------------------


def test_dashboard_no_session_or_local_storage() -> None:
    content = _dashboard()
    assert "sessionStorage" not in content
    assert "localStorage" not in content


def test_api_client_still_uses_cookie_credentials() -> None:
    api = _read("lib/api.ts")
    assert "credentials" in api and "include" in api
    assert "sessionStorage" not in api
    assert "localStorage" not in api


def test_auth_helper_no_browser_token_storage() -> None:
    # Strip comment lines — comments may explain that no browser storage is used.
    non_comment = "\n".join(
        line for line in _read("lib/auth.ts").splitlines()
        if not line.strip().startswith("//")
    )
    assert "sessionStorage" not in non_comment
    assert "localStorage" not in non_comment


# ---------------------------------------------------------------------------
# 7. Onboarding — gateway flow and entity bug fix
# ---------------------------------------------------------------------------


def test_onboarding_page_exists() -> None:
    assert os.path.isfile(os.path.join(_FRONTEND, "app", "onboarding", "page.tsx"))


def test_onboarding_has_gateway_choices() -> None:
    content = _onboarding()
    assert "Existing Clinic Login" in content
    assert "Request Pilot Access Registration" in content


def test_onboarding_has_five_step_titles() -> None:
    content = _onboarding()
    for title in (
        "Clinic Details",
        "Doctor / Admin Account",
        "Workflow Preferences",
        "AI Intake Setup",
        "Review & Pilot Activation",
    ):
        assert title in content, f"onboarding must include step title {title!r}"


def test_onboarding_entity_bug_fixed() -> None:
    content = _onboarding()
    # The escaped-entity label must no longer leak into the UI source.
    assert "Review &amp;" not in content
    assert "&amp; pilot activation" not in content.lower()


def test_onboarding_has_staging_scaffold_badge() -> None:
    text = _onboarding().upper()
    assert "STAGING SCAFFOLD" in text
    assert "NOT FUNCTIONAL" in text


def test_onboarding_has_pilot_activation_safety_copy() -> None:
    assert (
        "Pilot activation requires security, legal, and production-readiness review"
        in _onboarding()
    )


# ---------------------------------------------------------------------------
# 8. Developer console — dark command theme and guardrails
# ---------------------------------------------------------------------------


def test_console_page_exists() -> None:
    assert os.path.isfile(os.path.join(_FRONTEND, "app", "developer-console", "page.tsx"))


def test_console_has_title_and_panels() -> None:
    content = _console()
    assert "Developer Console" in content
    assert "Tenant Provisioning" in content
    assert "Clinic ID Scope Injection" in content
    assert "Vapi Machine Credential Binding" in content
    assert "Environment Checklist" in content
    assert "Safety Guardrails" in content


def test_console_has_guardrail_copy() -> None:
    content = _console()
    assert "Never paste secrets into browser UI" in content
    assert "Production PHI remains NO-GO" in content
    assert "Machine credentials are managed via secure environment variables" in content
    assert "Real tenant provisioning requires backend admin endpoint and audit trail" in content


def test_console_has_dark_ink_theme() -> None:
    content = _console()
    assert "#0B132B" in content
    assert "#008080" in content
    assert "#E63946" in content
    assert "#FFB703" in content


def test_console_env_checklist_labels_only() -> None:
    content = _console()
    for name in (
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "VAPI_WEBHOOK_SECRET",
        "INTERNAL_WEBHOOK_SECRET",
        "FRONTEND_CORS_ORIGINS",
    ):
        assert name in content, f"console must list env label {name}"
        # Label only — never an assigned value like NAME=... or NAME: "..."
        assert not re.search(name + r"\s*[=:]\s*['\"][^'\"]+['\"]", content), (
            f"console must never show a value for {name}"
        )


def test_console_actions_disabled() -> None:
    assert "disabled" in _console()


# ---------------------------------------------------------------------------
# 9. No secrets, no real patient data, anywhere in touched frontend files
# ---------------------------------------------------------------------------


def test_no_secrets_or_real_data_markers() -> None:
    for rel in (
        "app/dashboard/page.tsx",
        "app/onboarding/page.tsx",
        "app/developer-console/page.tsx",
        "app/globals.css",
        "lib/tenantDisplay.ts",
        "lib/api.ts",
        "lib/auth.ts",
    ):
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), f"{rel}: hardcoded JWT"
        assert "sk-" not in content, f"{rel}: API key marker"
        for marker in ("SVNR", "sozialversicherung", "DOB:"):
            assert marker not in content, f"{rel}: real patient data marker {marker!r}"


def test_dashboard_no_clinical_overreach_language() -> None:
    text = _dashboard().lower()
    assert "diagnosis" not in text
    assert "medical advice" not in text


# ---------------------------------------------------------------------------
# 10. Docs — architecture doc, CURRENT_STATE, NEXT_MODULE
# ---------------------------------------------------------------------------


def test_overhaul_architecture_doc_exists() -> None:
    path = os.path.join(
        _DOCS, "architecture", "FABEL5_PREMIUM_CLINIC_INTERFACE_OVERHAUL.md"
    )
    assert os.path.isfile(path)


def test_overhaul_architecture_doc_covers_required_sections() -> None:
    text = _read_doc("architecture/FABEL5_PREMIUM_CLINIC_INTERFACE_OVERHAUL.md")
    lower = text.lower()
    for needle in (
        "#0B132B",
        "#008080",
        "#E0F2F1",
        "#FFB703",
        "#E63946",
        "#F4F6F9",
        "Incoming AI Intake Queue",
        "Active Resolution Workspace",
        "Audio Transcript",
        "Patient Registry",
        "onboarding",
        "developer console",
    ):
        assert needle.lower() in lower, f"architecture doc must mention {needle!r}"
    assert "no-go" in lower
    assert "no real patient data" in lower
    assert "no secrets" in lower
    assert "limitation" in lower
    assert "wahlarzt" in lower or "wahlärzte" in lower or "austrian" in lower


def test_current_state_mentions_overhaul() -> None:
    text = _read_doc("claude/CURRENT_STATE.md")
    assert "126C-FABEL5" in text


def test_next_module_points_to_deployed_smoke_evidence() -> None:
    # Module 126D (deployed smoke evidence) has been completed.
    # NEXT_MODULE.md now points to a later sprint module that still
    # tracks smoke evidence or demo execution evidence.
    text = _read_doc("claude/NEXT_MODULE.md")
    assert "evidence" in text.lower() or "smoke" in text.lower() or "126D" in text
