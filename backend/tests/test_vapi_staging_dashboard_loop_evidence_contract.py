"""
Sprint 16 / Module 118B — Vapi staging dashboard loop evidence contract tests.

Static tests verifying the evidence doc records real PASS results for the deployed
Vapi staging dashboard loop: tool call, DB row insertion, dashboard display,
and staff Confirm — with no secrets and no real patient data.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE_DOC = ROOT / "docs" / "runtime" / "VAPI_STAGING_DASHBOARD_LOOP_EVIDENCE.md"


def _text() -> str:
    return EVIDENCE_DOC.read_text()


def test_vapi_evidence_doc_exists():
    assert EVIDENCE_DOC.exists(), (
        "VAPI_STAGING_DASHBOARD_LOOP_EVIDENCE.md must exist"
    )


def test_vapi_evidence_mentions_pass():
    assert "PASS" in _text(), "evidence doc must record PASS result"


def test_vapi_evidence_mentions_endpoint_url():
    assert (
        "https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request"
        in _text()
    ), "evidence doc must record the Vapi tool endpoint URL"


def test_vapi_evidence_mentions_dashboard_url():
    assert "https://praximed.vercel.app/dashboard" in _text(), (
        "evidence doc must record the Vercel dashboard URL"
    )


def test_vapi_evidence_mentions_content_type():
    assert "Content-Type" in _text(), (
        "evidence doc must document Content-Type header"
    )


def test_vapi_evidence_mentions_x_vapi_service_name():
    assert "X-Vapi-Service-Name" in _text(), (
        "evidence doc must document X-Vapi-Service-Name header"
    )


def test_vapi_evidence_mentions_x_vapi_clinic_id():
    assert "X-Vapi-Clinic-Id" in _text(), (
        "evidence doc must document X-Vapi-Clinic-Id header"
    )


def test_vapi_evidence_mentions_x_vapi_scopes():
    assert "X-Vapi-Scopes" in _text(), (
        "evidence doc must document X-Vapi-Scopes header"
    )


def test_vapi_evidence_mentions_x_clinic_ref_removed():
    assert "X-Clinic-Ref" in _text(), (
        "evidence doc must mention X-Clinic-Ref as removed"
    )


def test_vapi_evidence_mentions_clinic_uuid():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _text(), (
        "evidence doc must record the staging clinic UUID"
    )


def test_vapi_evidence_mentions_test_patient():
    assert "Test Patient" in _text(), (
        "evidence doc must record the fake patient name used in the test call"
    )


def test_vapi_evidence_mentions_appointments_count_2():
    text = _text()
    assert "count" in text.lower() and "2" in text, (
        "evidence doc must record Appointments count reached 2"
    )


def test_vapi_evidence_mentions_appointments_count_3():
    text = _text()
    assert "count" in text.lower() and "3" in text, (
        "evidence doc must record Appointments count reached 3"
    )


def test_vapi_evidence_mentions_status_new():
    assert "status: new" in _text() or "status=new" in _text() or "status\n| new" in _text() or "| new" in _text(), (
        "evidence doc must record status: new rows"
    )


def test_vapi_evidence_mentions_status_confirmed():
    assert "status: confirmed" in _text() or "status=confirmed" in _text() or "| confirmed" in _text(), (
        "evidence doc must record status: confirmed rows after staff Confirm"
    )


def test_vapi_evidence_mentions_priority_normal():
    assert "priority" in _text().lower() and "normal" in _text(), (
        "evidence doc must record priority: normal"
    )


def test_vapi_evidence_mentions_confirm():
    assert "Confirm" in _text(), (
        "evidence doc must mention Confirm button or Confirm flow"
    )


def test_vapi_evidence_mentions_fake_data_only():
    assert "fake data only" in _text().lower() or "fake/non-PHI" in _text(), (
        "evidence doc must confirm fake data only"
    )


def test_vapi_evidence_mentions_no_real_patient_data():
    assert "no real patient data" in _text().lower() or "No real patient data" in _text(), (
        "evidence doc must confirm no real patient data"
    )


def test_vapi_evidence_mentions_no_production_phi():
    assert "no production PHI" in _text().lower() or "No production PHI" in _text(), (
        "evidence doc must confirm no production PHI"
    )


def test_vapi_evidence_database_url_not_recorded():
    assert "DATABASE_URL not recorded" in _text(), (
        "evidence doc must confirm DATABASE_URL is not recorded"
    )


def test_vapi_evidence_token_not_recorded():
    assert "token not recorded" in _text().lower() or "Token not recorded" in _text(), (
        "evidence doc must confirm token value is not recorded"
    )


def test_vapi_evidence_password_not_recorded():
    assert "password not recorded" in _text().lower() or "Password not recorded" in _text(), (
        "evidence doc must confirm password is not recorded"
    )


def test_vapi_evidence_n8n_staging_pending():
    text = _text()
    assert "n8n" in text and (
        "PENDING" in text or "NOT PROVEN" in text or "DEFERRED" in text
    ), (
        "evidence doc must note n8n staging is still pending or deferred"
    )


def test_vapi_evidence_production_phi_no_go():
    text = _text()
    assert "production PHI" in text and (
        "NO-GO" in text or "NOT PROVEN" in text
    ), (
        "evidence doc must confirm production PHI readiness is NO-GO or NOT PROVEN"
    )
