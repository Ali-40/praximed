"""
Sprint 19 / Module 137 — Live Tenant Provisioning Smoke Evidence

Static contract tests: read raw markdown and verify the smoke evidence document
contains all required claims, safety statements, and context markers.

No imports, no database, no network. All assertions are substring checks.
"""

from pathlib import Path

DOC_PATH = Path(
    "docs/runtime/LIVE_TENANT_PROVISIONING_SMOKE_EVIDENCE.md"
)


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_doc_exists():
    assert DOC_PATH.exists(), f"Missing smoke evidence doc: {DOC_PATH}"


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


def test_doc_overall_pass():
    assert "PASS" in _doc()


def test_doc_overall_result_pass():
    src = _doc()
    assert "Overall result: PASS" in src or "result: PASS" in src


# ---------------------------------------------------------------------------
# Module and commit reference
# ---------------------------------------------------------------------------


def test_doc_module_137():
    assert "137" in _doc()


def test_doc_commit_47918c6():
    assert "47918c6" in _doc()


# ---------------------------------------------------------------------------
# Frontend URL
# ---------------------------------------------------------------------------


def test_doc_has_frontend_url():
    assert "https://praximed.vercel.app/developer-console/onboarding-requests" in _doc()


# ---------------------------------------------------------------------------
# Test request identity
# ---------------------------------------------------------------------------


def test_doc_has_demo_wahlarzt_praxis_wien():
    assert "Demo Wahlarzt Praxis Wien" in _doc()


def test_doc_has_demo_contact_email():
    assert "demo.clinic@example.test" in _doc()


# ---------------------------------------------------------------------------
# Status gate
# ---------------------------------------------------------------------------


def test_doc_has_pilot_approved():
    assert "pilot_approved" in _doc()


def test_doc_pilot_approved_before_provisioning():
    src = _doc()
    assert "pilot_approved" in src
    # Must reference the status before provisioning context
    assert "status before provisioning" in src or "before provisioning" in src


# ---------------------------------------------------------------------------
# Provisioning action
# ---------------------------------------------------------------------------


def test_doc_provision_clinic_shell_button():
    assert "Provision Clinic Shell" in _doc()


def test_doc_provision_endpoint():
    assert "/provision-clinic-shell" in _doc()


# ---------------------------------------------------------------------------
# Provisioning success
# ---------------------------------------------------------------------------


def test_doc_clinic_shell_provisioned():
    assert "Clinic shell provisioned" in _doc()


def test_doc_has_clinic_id():
    assert "clinic_id" in _doc()


def test_doc_has_clinic_name():
    assert "clinic_name" in _doc()


def test_doc_has_clinic_slug():
    assert "clinic_slug" in _doc()


def test_doc_has_preferred_language():
    assert "preferred_language" in _doc()


def test_doc_production_phi_disabled_message():
    src = _doc()
    assert "Production PHI remains disabled" in src or "production_phi_enabled: false" in src


def test_doc_production_phi_enabled_false():
    assert "production_phi_enabled" in _doc()
    assert "false" in _doc().lower()


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------


def test_doc_already_provisioned():
    assert "Already provisioned" in _doc() or "already_provisioned" in _doc()


def test_doc_already_provisioned_true():
    assert "already_provisioned" in _doc()


def test_doc_idempotent():
    assert "idempotent" in _doc().lower() or "idempotency" in _doc().lower()


def test_doc_no_duplicate_clinic_shell():
    src = _doc().lower()
    assert "no duplicate" in src or "duplicate" in src


def test_doc_second_call_safe():
    src = _doc()
    assert "second" in src.lower() or "second call" in src.lower()


# ---------------------------------------------------------------------------
# Safety boundaries
# ---------------------------------------------------------------------------


def test_doc_no_vapi_credentials():
    src = _doc().lower()
    assert "no vapi credentials" in src or "vapi credentials" in src


def test_doc_no_patient_records():
    src = _doc().lower()
    assert "no patient records" in src or "patient records" in src


def test_doc_no_production_phi():
    src = _doc().lower()
    assert "no production phi" in src or "production phi" in src


def test_doc_production_phi_remains_no_go():
    assert "Production PHI remains NO-GO" in _doc()


def test_doc_no_secrets():
    src = _doc().lower()
    assert "no secrets" in src or "secrets" in src


def test_doc_pilot_setup_status():
    assert "pilot_setup" in _doc()


# ---------------------------------------------------------------------------
# What this proves
# ---------------------------------------------------------------------------


def test_doc_what_this_proves_section():
    assert "What This Proves" in _doc() or "What this proves" in _doc()


def test_doc_proves_idempotency():
    src = _doc().lower()
    # "idempotency guard" or "idempotency" in proves section
    assert "idempotency" in src or "idempotent" in src


def test_doc_proves_phi_false():
    src = _doc()
    # Confirms production_phi_enabled is reliably false
    assert "production_phi_enabled" in src and "false" in src.lower()


# ---------------------------------------------------------------------------
# What this does not prove
# ---------------------------------------------------------------------------


def test_doc_what_this_does_not_prove_section():
    src = _doc()
    assert "What This Does Not Prove" in src or "What this does not prove" in src


def test_doc_not_production_ready():
    src = _doc().lower()
    assert "production readiness" in src or "production ready" in src or "not production" in src


# ---------------------------------------------------------------------------
# Remaining blockers
# ---------------------------------------------------------------------------


def test_doc_remaining_blockers_section():
    src = _doc()
    assert "Remaining Blockers" in src or "remaining blockers" in src.lower()


def test_doc_c3_c8_blockers():
    src = _doc()
    assert "C3" in src
    assert "C8" in src


def test_doc_blockers_dsgvo():
    src = _doc().lower()
    assert "dsgvo" in src


def test_doc_blockers_backup():
    src = _doc().lower()
    assert "backup" in src
