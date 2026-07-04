"""
Sprint 16 / Module 117 — Vercel frontend deployment and API wiring evidence contract tests.

Static tests verifying the evidence doc records real PASS results for Vercel deployment,
CORS wiring, browser login, and dashboard load — with no secrets.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE_DOC = (
    ROOT
    / "docs"
    / "runtime"
    / "VERCEL_FRONTEND_DEPLOYMENT_AND_API_WIRING_EVIDENCE.md"
)


def _text() -> str:
    return EVIDENCE_DOC.read_text()


def test_vercel_evidence_doc_exists():
    assert EVIDENCE_DOC.exists(), (
        "VERCEL_FRONTEND_DEPLOYMENT_AND_API_WIRING_EVIDENCE.md must exist"
    )


def test_vercel_evidence_mentions_pass():
    assert "PASS" in _text(), "evidence doc must record PASS result"


def test_vercel_evidence_mentions_vercel_url():
    assert "https://praximed.vercel.app" in _text(), (
        "evidence doc must record the Vercel frontend URL"
    )


def test_vercel_evidence_mentions_railway_backend_url():
    assert "https://web-production-fd91d.up.railway.app" in _text(), (
        "evidence doc must record the Railway backend URL"
    )


def test_vercel_evidence_mentions_next_public_api_base_url():
    assert "NEXT_PUBLIC_API_BASE_URL" in _text(), (
        "evidence doc must confirm NEXT_PUBLIC_API_BASE_URL was set in Vercel"
    )


def test_vercel_evidence_mentions_frontend_cors_origins():
    assert "FRONTEND_CORS_ORIGINS" in _text(), (
        "evidence doc must confirm FRONTEND_CORS_ORIGINS was set in Railway"
    )


def test_vercel_evidence_mentions_health_endpoint():
    assert "/health" in _text(), (
        "evidence doc must record GET /health result after Railway redeploy"
    )


def test_vercel_evidence_mentions_health_ready_endpoint():
    assert "/health/ready" in _text(), (
        "evidence doc must record GET /health/ready result"
    )


def test_vercel_evidence_mentions_browser_login():
    text = _text()
    assert "browser login" in text.lower() or "Browser login" in text, (
        "evidence doc must confirm browser login succeeded"
    )


def test_vercel_evidence_mentions_dashboard():
    assert "dashboard" in _text().lower(), (
        "evidence doc must confirm dashboard loaded"
    )


def test_vercel_evidence_mentions_appointments():
    assert "Appointments" in _text() or "appointment" in _text().lower(), (
        "evidence doc must confirm Appointments section visible in dashboard"
    )


def test_vercel_evidence_mentions_patients():
    assert "Patients" in _text() or "patients" in _text().lower(), (
        "evidence doc must confirm Patients section visible in dashboard"
    )


def test_vercel_evidence_mentions_notifications():
    assert "Notifications" in _text() or "notifications" in _text().lower(), (
        "evidence doc must confirm Notifications section visible in dashboard"
    )


def test_vercel_evidence_mentions_consultations():
    assert "Consultations" in _text() or "consultations" in _text().lower(), (
        "evidence doc must confirm Consultations section visible in dashboard"
    )


def test_vercel_evidence_mentions_staging_email():
    assert "doctor.staging@praximed.test" in _text(), (
        "evidence doc must record the staging email used for browser login"
    )


def test_vercel_evidence_mentions_clinic_uuid():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _text(), (
        "evidence doc must record the staging clinic_id used for browser login"
    )


def test_vercel_evidence_password_not_recorded():
    text = _text()
    assert "password not recorded" in text.lower() or "Password not recorded" in text, (
        "evidence doc must explicitly confirm password is not recorded"
    )


def test_vercel_evidence_token_not_recorded():
    text = _text()
    assert "token not recorded" in text.lower() or "REDACTED" in text or "not recorded" in text, (
        "evidence doc must explicitly confirm token value is not recorded"
    )


def test_vercel_evidence_database_url_not_recorded():
    assert "DATABASE_URL" in _text(), (
        "evidence doc must confirm DATABASE_URL is not recorded"
    )


def test_vercel_evidence_no_real_patient_data():
    text = _text()
    assert "no real patient" in text.lower() or "No real patient" in text, (
        "evidence doc must confirm no real patient data"
    )


def test_vercel_evidence_fake_non_phi_staging():
    text = _text()
    assert "fake" in text.lower() and "non-PHI" in text, (
        "evidence doc must confirm fake/non-PHI staging only"
    )


def test_vercel_evidence_vapi_still_pending():
    text = _text()
    assert "Vapi" in text and (
        "NOT PROVEN" in text or "PENDING" in text
    ), (
        "evidence doc must note Vapi staging is still pending"
    )


def test_vercel_evidence_n8n_still_pending():
    text = _text()
    assert "n8n" in text and (
        "NOT PROVEN" in text or "PENDING" in text
    ), (
        "evidence doc must note n8n staging is still pending"
    )


def test_vercel_evidence_mentions_module_118():
    assert "Module 118" in _text(), (
        "evidence doc must reference Module 118 for Vapi staging dashboard loop"
    )
