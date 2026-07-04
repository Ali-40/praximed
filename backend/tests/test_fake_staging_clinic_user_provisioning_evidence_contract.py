"""
Sprint 16 / Module 115 — Fake staging clinic and user provisioning evidence contract tests.

Static tests verifying that the evidence doc records the real PASS result with correct
fake staging identifiers, no secrets, and accurate pending items.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE_DOC = (
    ROOT / "docs" / "runtime" / "FAKE_STAGING_CLINIC_USER_PROVISIONING_EVIDENCE.md"
)


def _text() -> str:
    return EVIDENCE_DOC.read_text()


def test_evidence_doc_exists():
    assert EVIDENCE_DOC.exists(), (
        "FAKE_STAGING_CLINIC_USER_PROVISIONING_EVIDENCE.md must exist"
    )


def test_evidence_doc_mentions_pass():
    assert "PASS" in _text(), "evidence doc must record PASS result"


def test_evidence_doc_mentions_fake_staging_clinic():
    text = _text()
    assert "fake staging clinic" in text.lower() or "staging fake clinic" in text.lower(), (
        "evidence doc must mention fake staging clinic"
    )


def test_evidence_doc_mentions_staging_fake_clinic_slug():
    assert "staging-fake-clinic" in _text(), (
        "evidence doc must record the staging-fake-clinic slug"
    )


def test_evidence_doc_mentions_clinic_uuid():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _text(), (
        "evidence doc must record the real staging clinic UUID"
    )


def test_evidence_doc_mentions_user_email():
    assert "doctor.staging@praximed.test" in _text(), (
        "evidence doc must record the staging user email"
    )


def test_evidence_doc_mentions_user_uuid():
    assert "5b63b514-7624-4e8e-9af0-71c153ba7b83" in _text(), (
        "evidence doc must record the real staging user UUID"
    )


def test_evidence_doc_mentions_role_doctor():
    assert "doctor" in _text(), (
        "evidence doc must confirm the user role is doctor"
    )


def test_evidence_doc_mentions_status_active():
    assert "active" in _text(), (
        "evidence doc must confirm both rows are active status"
    )


def test_evidence_doc_password_not_recorded():
    text = _text()
    assert "password not recorded" in text.lower() or "Password not recorded" in text, (
        "evidence doc must explicitly confirm password is not recorded"
    )


def test_evidence_doc_bcrypt_hash_not_recorded():
    text = _text()
    assert "hash not recorded" in text.lower() or "Bcrypt hash not recorded" in text, (
        "evidence doc must explicitly confirm bcrypt hash is not recorded"
    )


def test_evidence_doc_database_url_not_recorded():
    text = _text()
    assert "DATABASE_URL not recorded" in text or "DATABASE_URL` not recorded" in text, (
        "evidence doc must explicitly confirm DATABASE_URL is not recorded"
    )


def test_evidence_doc_no_real_patient_data():
    text = _text()
    assert "no real patient" in text.lower() or "No real patient" in text, (
        "evidence doc must confirm no real patient data"
    )


def test_evidence_doc_fake_non_phi_staging():
    text = _text()
    assert "fake" in text.lower() and ("non-PHI" in text or "non-phi" in text.lower()), (
        "evidence doc must confirm fake/non-PHI staging only"
    )


def test_evidence_doc_not_local_dev_password():
    text = _text()
    assert "local-dev-password" in text and (
        "not" in text.lower() or "Not" in text
    ), (
        "evidence doc must confirm local-dev-password was not used"
    )


def test_evidence_doc_login_endpoint_still_pending():
    text = _text()
    assert "auth/login" in text or "/auth/login" in text, (
        "evidence doc must mention the login endpoint as the next verification step"
    )
    assert "NOT PROVEN" in text or "PENDING" in text or "not yet" in text.lower(), (
        "evidence doc must note that login endpoint has not yet been verified"
    )


def test_evidence_doc_vercel_still_pending():
    text = _text()
    assert "Vercel" in text and (
        "NOT PROVEN" in text or "PENDING" in text
    ), (
        "evidence doc must note Vercel frontend is still pending"
    )


def test_evidence_doc_vapi_still_pending():
    text = _text()
    assert "Vapi" in text and (
        "NOT PROVEN" in text or "PENDING" in text
    ), (
        "evidence doc must note Vapi staging is still pending"
    )


def test_evidence_doc_mentions_module_116():
    assert "Module 116" in _text(), (
        "evidence doc must reference Module 116 for backend staging login smoke"
    )
