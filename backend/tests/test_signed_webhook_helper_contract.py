"""
Static/unit contract tests for the signed webhook helper — PraxisMed Sprint 5 / Module 48

Strategy:
- No external service calls.
- No real database connection.
- No backend server started.
- File-existence checks via pathlib.
- Functional tests via direct import of sign_payload and main.
"""

from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_DIR  = Path(__file__).parent.parent
SCRIPTS_DIR  = BACKEND_DIR / "scripts"

HELPER_PATH  = SCRIPTS_DIR / "sign_webhook_payload.py"
RUNBOOK_PATH = PROJECT_ROOT / "docs" / "integrations" / "LOCAL_INTEGRATION_RUNBOOK.md"

# ---------------------------------------------------------------------------
# Import helper lazily so tests can verify import safety independently
# ---------------------------------------------------------------------------

def _load_helper():
    spec   = importlib.util.spec_from_file_location("sign_webhook_payload", HELPER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ===========================================================================
# Helper script existence and structure (tests 1, 12, 13)
# ===========================================================================


def test_sign_webhook_payload_script_exists():
    """Test 1 — sign_webhook_payload.py exists in backend/scripts/."""
    assert HELPER_PATH.exists(), f"Missing: {HELPER_PATH}"


def test_script_has_main_guard():
    """Test 12 — Script contains if __name__ == '__main__': guard."""
    content = HELPER_PATH.read_text()
    assert 'if __name__ == "__main__":' in content or "if __name__ == '__main__':" in content


def test_importing_script_does_not_execute_main(monkeypatch, capsys):
    """Test 13 — Importing the script does not call main or print anything."""
    _load_helper()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


# ===========================================================================
# sign_payload function tests (tests 2–6)
# ===========================================================================


def test_sign_payload_returns_sha256_prefixed_signature():
    """Test 2 — sign_payload returns 'sha256=<hex>' by default."""
    mod = _load_helper()
    result = mod.sign_payload(b'{"event":"test"}', "mysecret")
    assert result.startswith("sha256=")
    assert len(result) > len("sha256=")


def test_sign_payload_returns_plain_digest_when_prefix_false():
    """Test 3 — sign_payload returns plain hex digest when prefix=False."""
    mod = _load_helper()
    result = mod.sign_payload(b'{"event":"test"}', "mysecret", prefix=False)
    assert not result.startswith("sha256=")
    assert len(result) == 64  # SHA-256 hex digest is always 64 chars


def test_sign_payload_is_deterministic():
    """Test 4 — Same inputs always produce the same signature."""
    mod    = _load_helper()
    payload = b'{"clinic_id":"clinic-1","event_type":"call.started"}'
    secret  = "deterministic-secret"
    assert mod.sign_payload(payload, secret) == mod.sign_payload(payload, secret)


def test_sign_payload_rejects_non_bytes_payload():
    """Test 5 — Non-bytes payload raises TypeError."""
    mod = _load_helper()
    with pytest.raises(TypeError):
        mod.sign_payload("not bytes", "secret")  # type: ignore[arg-type]


def test_sign_payload_rejects_empty_secret():
    """Test 6 — Empty secret raises ValueError."""
    mod = _load_helper()
    with pytest.raises(ValueError):
        mod.sign_payload(b'{"event":"test"}', "")


# ===========================================================================
# main() function tests (tests 7–11)
# ===========================================================================


def test_main_with_payload_prints_signature_and_returns_0(capsys):
    """Test 7 — main(['--secret', ..., '--payload', ...]) prints sig and returns 0."""
    mod = _load_helper()
    rc  = mod.main(["--secret", "testsecret", "--payload", '{"event":"test"}'])
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out.strip().startswith("sha256=")


def test_main_with_payload_file_prints_signature_and_returns_0(tmp_path, capsys):
    """Test 8 — main with --payload-file reads file and returns 0."""
    payload_file = tmp_path / "payload.json"
    payload_file.write_bytes(b'{"event":"file_test"}')

    mod = _load_helper()
    rc  = mod.main([
        "--secret", "testsecret",
        "--payload-file", str(payload_file),
    ])
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out.strip().startswith("sha256=")


def test_main_rejects_missing_secret(capsys):
    """Test 9 — main without --secret exits non-zero."""
    mod = _load_helper()
    with pytest.raises(SystemExit) as exc_info:
        mod.main(["--payload", '{"event":"test"}'])
    assert exc_info.value.code != 0


def test_main_rejects_both_payload_and_payload_file(tmp_path, capsys):
    """Test 10 — main with both --payload and --payload-file exits non-zero."""
    payload_file = tmp_path / "p.json"
    payload_file.write_bytes(b"{}")

    mod = _load_helper()
    with pytest.raises(SystemExit) as exc_info:
        mod.main([
            "--secret", "testsecret",
            "--payload", "{}",
            "--payload-file", str(payload_file),
        ])
    assert exc_info.value.code != 0


def test_main_does_not_print_the_secret(capsys):
    """Test 11 — The secret value never appears in stdout or stderr."""
    secret = "super-secret-value-must-not-appear"
    mod    = _load_helper()
    mod.main(["--secret", secret, "--payload", '{"event":"test"}'])
    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err


# ===========================================================================
# Runbook existence and content (tests 14–25)
# ===========================================================================


def test_local_integration_runbook_exists():
    """Test 14 — LOCAL_INTEGRATION_RUNBOOK.md exists in docs/integrations/."""
    assert RUNBOOK_PATH.exists(), f"Missing: {RUNBOOK_PATH}"


def _runbook() -> str:
    return RUNBOOK_PATH.read_text()


def test_runbook_documents_docker_postgres_startup():
    """Test 15 — Runbook includes docker compose ... up command."""
    content = _runbook()
    assert "docker compose" in content
    assert "docker-compose.postgres.yml" in content
    assert "up" in content


def test_runbook_documents_database_url():
    """Test 16 — Runbook mentions DATABASE_URL."""
    assert "DATABASE_URL" in _runbook()


def test_runbook_documents_vapi_webhook_secret():
    """Test 17 — Runbook mentions VAPI_WEBHOOK_SECRET."""
    assert "VAPI_WEBHOOK_SECRET" in _runbook()


def test_runbook_documents_n8n_webhook_secret():
    """Test 18 — Runbook mentions N8N_WEBHOOK_SECRET."""
    assert "N8N_WEBHOOK_SECRET" in _runbook()


def test_runbook_documents_x_service_headers():
    """Test 19 — Runbook documents X-Service-* machine auth headers."""
    content = _runbook()
    assert "X-Service-Name" in content
    assert "X-Service-Clinic-Id" in content
    assert "X-Service-Scopes" in content


def test_runbook_documents_x_vapi_signature():
    """Test 20 — Runbook documents X-Vapi-Signature header."""
    assert "X-Vapi-Signature" in _runbook()


def test_runbook_documents_x_n8n_signature():
    """Test 21 — Runbook documents X-N8N-Signature header."""
    assert "X-N8N-Signature" in _runbook()


def test_runbook_includes_curl_example_for_vapi_webhook():
    """Test 22 — Runbook includes a curl example for the Vapi webhook route."""
    content = _runbook()
    assert "curl" in content
    assert "/webhooks/vapi/call-event" in content


def test_runbook_includes_curl_example_for_n8n_calendar_sync():
    """Test 23 — Runbook includes a curl example for the n8n calendar sync route."""
    content = _runbook()
    assert "curl" in content
    assert "/webhooks/n8n/calendar-sync" in content


def test_runbook_warns_not_to_commit_production_secrets():
    """Test 24 — Runbook warns against committing production secrets."""
    content = _runbook().lower()
    assert "never commit" in content or "do not commit" in content or "not commit" in content


def test_runbook_states_real_vapi_n8n_setup_not_done():
    """Test 25 — Runbook makes clear real Vapi/n8n setup is not done yet."""
    content = _runbook().lower()
    assert "not done yet" in content or "not yet" in content or "later sprint" in content
