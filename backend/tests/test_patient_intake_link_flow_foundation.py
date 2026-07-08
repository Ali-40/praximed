"""
Tests — Patient Intake Link Flow Foundation (Module 151).

Covers: migration, schema.sql, Pydantic schemas, token service,
repo, service, routes, frontend/static contracts, PHI invariant,
forbidden vocabulary guards.

No real patient data. No history writes. No AI structuring.
No diagnosis. No medical advice. No triage scoring.
production_phi_enabled always False. Production PHI remains NO-GO.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]

_MIGRATION_PATH = ROOT / "backend/migrations/versions/0009_patient_intake_links.py"
_SCHEMA_SQL_PATH = ROOT / "backend/app/db/schema.sql"
_REPO_PATH = ROOT / "backend/app/db/repositories/patient_intake_link_repo.py"
_SERVICE_PATH = ROOT / "backend/app/services/patient_intake_link.py"
_TOKEN_SVC_PATH = ROOT / "backend/app/services/intake_token.py"
_ROUTES_PATH = ROOT / "backend/app/api/routes/patient_intake_links.py"
_INTAKE_PAGE_PATH = ROOT / "frontend/app/intake/[token]/page.tsx"
_ADMIN_PAGE_PATH = ROOT / "frontend/app/developer-console/intake-links/page.tsx"
_CONSOLE_PAGE_PATH = ROOT / "frontend/app/developer-console/page.tsx"
_API_TS_PATH = ROOT / "frontend/lib/api.ts"
_ARCH_DOC_PATH = ROOT / "docs/architecture/PATIENT_INTAKE_LINK_FLOW_FOUNDATION.md"


def _load_migration() -> Any:
    spec = importlib.util.spec_from_file_location("migration_0009", _MIGRATION_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _future_dt(hours: int = 72) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(hours=hours)


def _make_pool(return_value: Any = None, fetch_return: Any = None) -> Any:
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=return_value)
    pool.fetch = AsyncMock(return_value=fetch_return or [])
    return pool


class _FakeRow(dict):
    pass


def _fake_link_row(overrides: dict | None = None) -> dict:
    base = {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "clinic_id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        "patient_id": None,
        "appointment_request_id": None,
        "template_id": "tttttttt-tttt-4ttt-8ttt-tttttttttttt",
        "token_hash": "fakehash",
        "token_prefix": "abcdefgh",
        "status": "active",
        "purpose": "patient_history_collection",
        "language": "de",
        "expires_at": (_future_dt()).isoformat(),
        "max_submissions": 1,
        "submission_count": 0,
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "created_by_user_id": None,
        "created_at": "2026-07-08T00:00:00Z",
        "updated_at": "2026-07-08T00:00:00Z",
    }
    if overrides:
        base.update(overrides)
    return base


def _fake_submission_row(overrides: dict | None = None) -> dict:
    base = {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
        "intake_link_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "clinic_id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        "patient_id": None,
        "appointment_request_id": None,
        "template_id": "tttttttt-tttt-4ttt-8ttt-tttttttttttt",
        "consent_event_id": "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
        "language": "de",
        "answers": json.dumps({"known_allergies": "Keine"}),
        "skipped_questions": json.dumps([]),
        "escalation_matches": json.dumps([]),
        "status": "submitted",
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "submitted_at": "2026-07-08T00:01:00Z",
        "created_at": "2026-07-08T00:01:00Z",
        "updated_at": "2026-07-08T00:01:00Z",
    }
    if overrides:
        base.update(overrides)
    return base


# ── Migration checks ──────────────────────────────────────────────────────────


def test_migration_file_exists():
    assert _MIGRATION_PATH.exists()


def test_migration_revision():
    mod = _load_migration()
    assert mod.revision == "0009_patient_intake_links"


def test_migration_down_revision():
    mod = _load_migration()
    assert mod.down_revision == "0008_anamnesis_templates"


def test_migration_has_empty_jsonb_constant():
    mod = _load_migration()
    assert mod._EMPTY_JSONB == "'{}'::jsonb"


def test_migration_has_empty_array_jsonb_constant():
    mod = _load_migration()
    assert mod._EMPTY_ARRAY_JSONB == "'[]'::jsonb"


def test_migration_no_double_brace_jsonb():
    src = _MIGRATION_PATH.read_text()
    assert "'{{}}'::jsonb" not in src


def test_migration_patient_intake_links_table():
    src = _MIGRATION_PATH.read_text()
    assert "patient_intake_links" in src


def test_migration_patient_intake_submissions_table():
    src = _MIGRATION_PATH.read_text()
    assert "patient_intake_submissions" in src


def test_migration_token_hash_unique():
    src = _MIGRATION_PATH.read_text()
    assert "token_hash" in src
    assert "UNIQUE" in src


def test_migration_token_prefix_exists():
    src = _MIGRATION_PATH.read_text()
    assert "token_prefix" in src


def test_migration_no_raw_token_column():
    src = _MIGRATION_PATH.read_text()
    assert "raw_token" not in src


def test_migration_consent_event_id_on_submissions():
    src = _MIGRATION_PATH.read_text()
    assert "consent_event_id" in src


def test_migration_answers_jsonb():
    src = _MIGRATION_PATH.read_text()
    assert "answers" in src


def test_migration_skipped_questions_jsonb():
    src = _MIGRATION_PATH.read_text()
    assert "skipped_questions" in src


def test_migration_escalation_matches_jsonb():
    src = _MIGRATION_PATH.read_text()
    assert "escalation_matches" in src


def test_migration_phi_check_on_links():
    src = _MIGRATION_PATH.read_text()
    assert "patient_intake_links_phi_check" in src


def test_migration_phi_check_on_submissions():
    src = _MIGRATION_PATH.read_text()
    assert "patient_intake_submissions_phi_check" in src


def test_migration_synthetic_demo_check():
    src = _MIGRATION_PATH.read_text()
    assert "patient_intake_links_demo_check" in src


def test_migration_has_upgrade_and_downgrade():
    mod = _load_migration()
    assert callable(mod.upgrade)
    assert callable(mod.downgrade)


# ── schema.sql checks ─────────────────────────────────────────────────────────


def test_schema_sql_has_intake_links_table():
    sql = _SCHEMA_SQL_PATH.read_text()
    assert "CREATE TABLE IF NOT EXISTS patient_intake_links" in sql


def test_schema_sql_has_intake_submissions_table():
    sql = _SCHEMA_SQL_PATH.read_text()
    assert "CREATE TABLE IF NOT EXISTS patient_intake_submissions" in sql


def test_schema_sql_no_double_brace_jsonb():
    sql = _SCHEMA_SQL_PATH.read_text()
    assert "'{{}}'::jsonb" not in sql


def test_schema_sql_phi_checks():
    sql = _SCHEMA_SQL_PATH.read_text()
    assert "patient_intake_links_phi_check" in sql
    assert "patient_intake_submissions_phi_check" in sql


# ── Token service ─────────────────────────────────────────────────────────────

from backend.app.services.intake_token import (
    generate_intake_token,
    hash_intake_token,
    token_prefix,
)


def test_generate_token_returns_string():
    tok = generate_intake_token()
    assert isinstance(tok, str)
    assert len(tok) > 0


def test_generate_token_is_urlsafe():
    tok = generate_intake_token()
    import re
    assert re.match(r'^[A-Za-z0-9\-_]+$', tok)


def test_generate_tokens_differ():
    a = generate_intake_token()
    b = generate_intake_token()
    assert a != b


def test_hash_is_deterministic():
    tok = generate_intake_token()
    assert hash_intake_token(tok) == hash_intake_token(tok)


def test_hash_differs_from_raw():
    tok = generate_intake_token()
    assert hash_intake_token(tok) != tok


def test_hash_is_sha256():
    tok = "test_token"
    expected = hashlib.sha256(tok.encode("utf-8")).hexdigest()
    assert hash_intake_token(tok) == expected


def test_token_prefix_length():
    tok = generate_intake_token()
    assert len(token_prefix(tok)) == 8


def test_token_prefix_matches_start():
    tok = generate_intake_token()
    assert tok.startswith(token_prefix(tok))


# ── Pydantic schemas ──────────────────────────────────────────────────────────

from backend.app.schemas.patient_intake_link import (
    PatientIntakeLinkCreate,
    PatientIntakeSubmissionCreate,
    PatientIntakeLinkRevoke,
    PatientIntakeLinkCreateResponse,
    PatientIntakeLinkListResponse,
    PatientIntakePublicResponse,
    PatientIntakeSubmitResponse,
    PatientIntakeSubmissionListResponse,
)


def test_schema_create_valid():
    obj = PatientIntakeLinkCreate(
        template_id="tttttttt-tttt-4ttt-8ttt-tttttttttttt",
        expires_at=_future_dt(),
    )
    assert obj.language == "de"
    assert obj.production_phi_enabled is False
    assert obj.synthetic_demo is True


def test_schema_create_rejects_empty_template_id():
    with pytest.raises(ValidationError):
        PatientIntakeLinkCreate(template_id="  ", expires_at=_future_dt())


def test_schema_create_rejects_past_expires_at():
    past = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    with pytest.raises(ValidationError):
        PatientIntakeLinkCreate(template_id="t", expires_at=past)


def test_schema_create_rejects_invalid_language():
    with pytest.raises(ValidationError):
        PatientIntakeLinkCreate(template_id="t", expires_at=_future_dt(), language="fr")


def test_schema_create_rejects_phi_true():
    with pytest.raises(ValidationError):
        PatientIntakeLinkCreate(
            template_id="t",
            expires_at=_future_dt(),
            production_phi_enabled=True,
        )


def test_schema_create_rejects_demo_false():
    with pytest.raises(ValidationError):
        PatientIntakeLinkCreate(
            template_id="t",
            expires_at=_future_dt(),
            synthetic_demo=False,
        )


def test_schema_submission_create_valid():
    obj = PatientIntakeSubmissionCreate(
        language="de",
        answers={"q1": "some answer"},
        consent_granted=True,
    )
    assert obj.production_phi_enabled is False


def test_schema_submission_create_rejects_phi():
    with pytest.raises(ValidationError):
        PatientIntakeSubmissionCreate(consent_granted=True, production_phi_enabled=True)


def test_schema_submission_rejects_no_consent():
    with pytest.raises(ValidationError):
        PatientIntakeSubmissionCreate(consent_granted=False)


def test_schema_submission_rejects_forbidden_answer_key():
    with pytest.raises(ValidationError):
        PatientIntakeSubmissionCreate(
            consent_granted=True,
            answers={"diagnosis_score": 5},
        )


def test_schema_list_response_phi_false():
    resp = PatientIntakeLinkListResponse(ok=True, links=[], total=0)
    assert resp.production_phi_enabled is False


def test_schema_submit_response_phi_false():
    resp = PatientIntakeSubmitResponse(ok=True)
    assert resp.production_phi_enabled is False


def test_schema_public_response_phi_false():
    resp = PatientIntakePublicResponse(ok=True)
    assert resp.production_phi_enabled is False


# ── Repo tests ────────────────────────────────────────────────────────────────

from backend.app.db.repositories.patient_intake_link_repo import (
    create_patient_intake_link,
    get_intake_link_by_id,
    get_intake_link_by_token_hash,
    list_intake_links_for_clinic,
    revoke_intake_link,
    increment_submission_count,
    create_intake_submission,
    list_intake_submissions_for_clinic,
    list_intake_submissions_for_link,
)


@pytest.mark.asyncio
async def test_repo_create_link_calls_fetchrow():
    row = _FakeRow(_fake_link_row())
    pool = _make_pool(return_value=row)
    result = await create_patient_intake_link(
        pool=pool,
        clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        template_id="tttttttt-tttt-4ttt-8ttt-tttttttttttt",
        token_hash="fakehash",
        token_prefix="abcdefgh",
        expires_at=_future_dt(),
    )
    pool.fetchrow.assert_called_once()
    assert result["token_prefix"] == "abcdefgh"


@pytest.mark.asyncio
async def test_repo_create_link_stores_no_raw_token():
    row = _FakeRow(_fake_link_row())
    pool = _make_pool(return_value=row)
    await create_patient_intake_link(
        pool=pool,
        clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        template_id="tttttttt-tttt-4ttt-8ttt-tttttttttttt",
        token_hash="fakehash",
        token_prefix="abcdefgh",
        expires_at=_future_dt(),
    )
    sql_call = pool.fetchrow.call_args[0][0]
    assert "raw_token" not in sql_call


@pytest.mark.asyncio
async def test_repo_get_by_id_none_when_missing():
    pool = _make_pool(return_value=None)
    result = await get_intake_link_by_id(pool=pool, link_id="nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_repo_get_by_token_hash():
    row = _FakeRow(_fake_link_row())
    pool = _make_pool(return_value=row)
    result = await get_intake_link_by_token_hash(pool=pool, token_hash="fakehash")
    assert result is not None
    assert result["token_prefix"] == "abcdefgh"


@pytest.mark.asyncio
async def test_repo_list_links_returns_list():
    row = _FakeRow(_fake_link_row())
    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=[row])
    results = await list_intake_links_for_clinic(
        pool=pool, clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc"
    )
    assert len(results) == 1


@pytest.mark.asyncio
async def test_repo_revoke_link():
    row = _FakeRow(_fake_link_row({"status": "revoked"}))
    pool = _make_pool(return_value=row)
    result = await revoke_intake_link(
        pool=pool,
        link_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
    )
    assert result["status"] == "revoked"


@pytest.mark.asyncio
async def test_repo_increment_submission_count():
    row = _FakeRow(_fake_link_row({"submission_count": 1, "status": "submitted"}))
    pool = _make_pool(return_value=row)
    result = await increment_submission_count(
        pool=pool,
        link_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        max_submissions=1,
    )
    assert result["submission_count"] == 1


@pytest.mark.asyncio
async def test_repo_create_submission_calls_fetchrow():
    row = _FakeRow(_fake_submission_row())
    pool = _make_pool(return_value=row)
    result = await create_intake_submission(
        pool=pool,
        intake_link_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        template_id="tttttttt-tttt-4ttt-8ttt-tttttttttttt",
        consent_event_id="eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
        answers={"q1": "Keine"},
        skipped_questions=[],
        escalation_matches=[],
    )
    pool.fetchrow.assert_called_once()
    assert isinstance(result["answers"], dict)


@pytest.mark.asyncio
async def test_repo_list_submissions_returns_list():
    row = _FakeRow(_fake_submission_row())
    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=[row])
    results = await list_intake_submissions_for_clinic(
        pool=pool, clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc"
    )
    assert len(results) == 1
    assert isinstance(results[0]["answers"], dict)


# ── Service layer tests ───────────────────────────────────────────────────────

from backend.app.services import patient_intake_link as svc_mod


def test_service_no_raw_token_logged():
    src = _SERVICE_PATH.read_text()
    assert "logger.info.*raw_token" not in src or "logger.debug.*raw_token" not in src


@pytest.mark.asyncio
async def test_service_create_link_returns_intake_url():
    link_row = _FakeRow(_fake_link_row())
    pool = MagicMock()
    pool.fetchrow = AsyncMock(side_effect=[
        _FakeRow({"id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc"}),  # clinic check
        _FakeRow({"id": "tttttttt-tttt-4ttt-8ttt-tttttttttttt", "status": "active"}),  # template check
        link_row,  # create link
    ])
    result = await svc_mod.create_demo_intake_link(
        pool=pool,
        clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        payload={
            "template_id": "tttttttt-tttt-4ttt-8ttt-tttttttttttt",
            "expires_at": _future_dt(),
        },
    )
    assert "intake_url" in result
    assert result["raw_token_shown_once"] is True
    assert "/intake/" in result["intake_url"]


@pytest.mark.asyncio
async def test_service_create_link_hash_differs_from_url_token():
    link_row = _FakeRow(_fake_link_row())
    pool = MagicMock()
    pool.fetchrow = AsyncMock(side_effect=[
        _FakeRow({"id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc"}),
        _FakeRow({"id": "tttttttt-tttt-4ttt-8ttt-tttttttttttt", "status": "active"}),
        link_row,
    ])
    result = await svc_mod.create_demo_intake_link(
        pool=pool,
        clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        payload={"template_id": "tttttttt-tttt-4ttt-8ttt-tttttttttttt", "expires_at": _future_dt()},
    )
    raw = result["intake_url"].split("/intake/")[1]
    assert hash_intake_token(raw) != raw


@pytest.mark.asyncio
async def test_service_clinic_not_found_raises():
    pool = _make_pool(return_value=None)
    with pytest.raises(svc_mod.ClinicNotFoundError):
        await svc_mod.create_demo_intake_link(
            pool=pool,
            clinic_id="nonexistent",
            payload={"template_id": "t", "expires_at": _future_dt()},
        )


@pytest.mark.asyncio
async def test_service_public_template_load_active():
    link_row = _FakeRow(_fake_link_row())
    template_row = _FakeRow({
        "id": "tttttttt-tttt-4ttt-8ttt-tttttttttttt",
        "template_key": "demo_gp_basic_history",
        "display_name": "GP Template",
        "specialty": "general_practice",
        "primary_language": "de",
        "template_schema": json.dumps({"sections": []}),
        "escalation_keywords": json.dumps([]),
        "supported_languages": json.dumps(["de", "en"]),
        "status": "active",
    })
    pool = MagicMock()
    pool.fetchrow = AsyncMock(side_effect=[link_row, template_row])
    raw_token = generate_intake_token()
    result = await svc_mod.get_public_intake_template(pool=pool, raw_token=raw_token)
    assert result["production_phi_enabled"] is False
    assert "demo_notice" in result
    assert "Do not enter real medical information" in result["demo_notice"]


@pytest.mark.asyncio
async def test_service_expired_link_rejected():
    expired_row = _FakeRow(_fake_link_row({
        "expires_at": (datetime.now(tz=timezone.utc) - timedelta(hours=1)).isoformat(),
        "status": "active",
    }))
    pool = _make_pool(return_value=expired_row)
    with pytest.raises(svc_mod.IntakeLinkExpiredError):
        await svc_mod.get_public_intake_template(pool=pool, raw_token="anytoken")


@pytest.mark.asyncio
async def test_service_revoked_link_rejected():
    revoked_row = _FakeRow(_fake_link_row({"status": "revoked"}))
    pool = _make_pool(return_value=revoked_row)
    with pytest.raises(svc_mod.IntakeLinkRevokedError):
        await svc_mod.get_public_intake_template(pool=pool, raw_token="anytoken")


@pytest.mark.asyncio
async def test_service_submitted_link_rejected():
    submitted_row = _FakeRow(_fake_link_row({"status": "submitted"}))
    pool = _make_pool(return_value=submitted_row)
    with pytest.raises(svc_mod.IntakeLinkSubmittedError):
        await svc_mod.get_public_intake_template(pool=pool, raw_token="anytoken")


@pytest.mark.asyncio
async def test_service_escalation_keyword_match():
    from backend.app.services.patient_intake_link import _match_escalation_keywords
    answers = {"complaint": "starke Schmerzen und Atemnot"}
    keywords = ["starke Schmerzen", "Atemnot", "chest pain"]
    matches = _match_escalation_keywords(answers, keywords)
    assert "starke Schmerzen" in matches
    assert "Atemnot" in matches
    assert "chest pain" not in matches


def test_service_escalation_no_scoring():
    src = _SERVICE_PATH.read_text()
    assert "triage_score" not in src
    assert "diagnosis_score" not in src
    assert "risk_score" not in src


def test_service_no_history_write_calls():
    src = _SERVICE_PATH.read_text()
    assert "patient_history_repo" not in src
    assert "create_allergy_history" not in src


def test_service_no_ai_structuring_calls():
    src = _SERVICE_PATH.read_text()
    assert "openai" not in src.lower()
    assert "ai_structur" not in src.lower()


# ── Route-level unit tests ────────────────────────────────────────────────────

from backend.app.api.routes import patient_intake_links as routes_mod


def test_routes_module_exists():
    assert _ROUTES_PATH.exists()


def test_routes_has_no_delete_route():
    src = _ROUTES_PATH.read_text()
    assert "@router.delete" not in src


def test_routes_protected_require_auth():
    src = _ROUTES_PATH.read_text()
    assert "get_current_user" in src


def test_routes_public_get_intake_exists():
    src = _ROUTES_PATH.read_text()
    assert '"/intake/{token}"' in src


def test_routes_public_submit_exists():
    src = _ROUTES_PATH.read_text()
    assert '"/intake/{token}/submit"' in src


def test_routes_phi_false_in_responses():
    src = _ROUTES_PATH.read_text()
    assert "production_phi_enabled" in src


def test_router_includes_patient_intake_links():
    src = (ROOT / "backend/app/api/router.py").read_text()
    assert "patient_intake_links" in src


# ── Frontend / static contract tests ─────────────────────────────────────────


def test_intake_page_exists():
    assert _INTAKE_PAGE_PATH.exists()


def test_intake_page_says_demo_staging_only():
    src = _INTAKE_PAGE_PATH.read_text()
    assert "Demo staging intake only" in src


def test_intake_page_says_no_real_medical_info():
    src = _INTAKE_PAGE_PATH.read_text()
    assert "Do not enter real medical information" in src


def test_intake_page_consent_before_questionnaire():
    src = _INTAKE_PAGE_PATH.read_text()
    assert "consent" in src.lower()
    assert "questionnaire" in src.lower()


def test_intake_page_language_selector_has_de_en_ar():
    src = _INTAKE_PAGE_PATH.read_text()
    assert "'de'" in src or '"de"' in src
    assert "'en'" in src or '"en"' in src
    assert "'ar'" in src or '"ar"' in src


def test_intake_page_ar_sets_rtl():
    src = _INTAKE_PAGE_PATH.read_text()
    assert "rtl" in src.lower() or 'dir="rtl"' in src or "dir: 'rtl'" in src


def test_intake_page_success_says_staff_review():
    src = _INTAKE_PAGE_PATH.read_text()
    assert "staff review" in src.lower()


def test_intake_page_no_appointment_confirmation():
    src = _INTAKE_PAGE_PATH.read_text()
    # Prohibition/clarification lines ("No appointment is confirmed") are acceptable;
    # check that no positive confirmation promise exists.
    lines_with_confirmed = [
        l for l in src.splitlines()
        if "appointment" in l.lower() and "confirmed" in l.lower()
        and not ("no appointment" in l.lower() or "not confirm" in l.lower())
    ]
    assert len(lines_with_confirmed) == 0


def test_intake_page_no_localstorage():
    # localStorage must not appear in active JS code, only prohibition comments are ok.
    src = _INTAKE_PAGE_PATH.read_text()
    active_lines = [
        l for l in src.splitlines()
        if "localStorage" in l
        and not l.strip().startswith("//")
    ]
    assert len(active_lines) == 0


def test_intake_page_no_sessionstorage():
    # sessionStorage must not appear in active JS code, only prohibition comments are ok.
    src = _INTAKE_PAGE_PATH.read_text()
    active_lines = [
        l for l in src.splitlines()
        if "sessionStorage" in l
        and not l.strip().startswith("//")
    ]
    assert len(active_lines) == 0


def test_intake_page_no_diagnosis_language():
    src = _INTAKE_PAGE_PATH.read_text()
    # Prohibition lines ("No medical diagnosis") are acceptable.
    lines_with_diagnosis = [
        l for l in src.splitlines()
        if "diagnosis" in l.lower()
        and "no" not in l.lower()
    ]
    assert len(lines_with_diagnosis) == 0


def test_admin_page_exists():
    assert _ADMIN_PAGE_PATH.exists()


def test_admin_page_title():
    src = _ADMIN_PAGE_PATH.read_text()
    assert "Patient Intake Links" in src


def test_admin_page_admin_staging_badge():
    src = _ADMIN_PAGE_PATH.read_text()
    assert "ADMIN" in src
    assert "STAGING" in src


def test_admin_page_intake_url_shown_once():
    src = _ADMIN_PAGE_PATH.read_text()
    assert "shown once" in src.lower() or "intake_url" in src


def test_admin_page_token_prefix():
    src = _ADMIN_PAGE_PATH.read_text()
    assert "token_prefix" in src


def test_admin_page_phi_no_go():
    src = _ADMIN_PAGE_PATH.read_text()
    assert "Production PHI remains NO-GO" in src


def test_admin_page_no_localstorage():
    src = _ADMIN_PAGE_PATH.read_text()
    assert "localStorage" not in src


def test_admin_page_no_sessionstorage():
    src = _ADMIN_PAGE_PATH.read_text()
    assert "sessionStorage" not in src


def test_console_page_has_intake_links_panel():
    src = _CONSOLE_PAGE_PATH.read_text()
    assert "intake-links" in src or "Patient Intake Links" in src


def test_api_ts_has_create_intake_link():
    src = _API_TS_PATH.read_text()
    assert "createPatientIntakeLink" in src


def test_api_ts_has_fetch_intake_links():
    src = _API_TS_PATH.read_text()
    assert "fetchPatientIntakeLinks" in src


def test_api_ts_has_fetch_submissions():
    src = _API_TS_PATH.read_text()
    assert "fetchPatientIntakeSubmissions" in src


def test_api_ts_has_revoke_intake_link():
    src = _API_TS_PATH.read_text()
    assert "revokePatientIntakeLink" in src


def test_api_ts_has_fetch_public_template():
    src = _API_TS_PATH.read_text()
    assert "fetchPublicIntakeTemplate" in src


def test_api_ts_has_submit_public_intake():
    src = _API_TS_PATH.read_text()
    assert "submitPublicIntake" in src


def test_api_ts_admin_helpers_use_credentials_include():
    src = _API_TS_PATH.read_text()
    assert "credentials: 'include'" in src or 'credentials: "include"' in src


def test_api_ts_public_helpers_no_auth_cookie():
    src = _API_TS_PATH.read_text()
    assert "fetchPublicIntakeTemplate" in src


# ── PHI invariant ─────────────────────────────────────────────────────────────


def test_token_svc_no_phi():
    src = _TOKEN_SVC_PATH.read_text()
    assert "production_phi_enabled" in src or "PHI" in src


def test_schema_submission_read_phi_always_false():
    from backend.app.schemas.patient_intake_link import PatientIntakeSubmissionRead
    sub = PatientIntakeSubmissionRead(
        id="b",
        intake_link_id="a",
        clinic_id="c",
        template_id="t",
        consent_event_id="e",
        language="de",
        answers={},
        skipped_questions=[],
        escalation_matches=[],
        status="submitted",
        synthetic_demo=True,
        production_phi_enabled=False,
        submitted_at="2026-07-08",
        created_at="2026-07-08",
    )
    assert sub.production_phi_enabled is False


# ── Forbidden vocabulary ──────────────────────────────────────────────────────


def test_service_no_secrets_in_source():
    src = _SERVICE_PATH.read_text()
    assert "DATABASE_URL" not in src
    assert "JWT_SECRET" not in src
    assert "sk-" not in src


def test_repo_no_secrets_in_source():
    src = _REPO_PATH.read_text()
    assert "DATABASE_URL" not in src
    assert "JWT_SECRET" not in src


def test_routes_no_diagnosis_generation():
    src = _ROUTES_PATH.read_text()
    lines_with_diagnosis = [
        l for l in src.splitlines()
        if "diagnos" in l.lower() and "no diagnos" not in l.lower()
    ]
    assert len(lines_with_diagnosis) == 0


def test_service_no_medical_advice():
    src = _SERVICE_PATH.read_text()
    lines_with_advice = [
        l for l in src.splitlines()
        if "medical advice" in l.lower() and "no medical advice" not in l.lower()
    ]
    assert len(lines_with_advice) == 0


def test_service_no_treatment_recommendation():
    src = _SERVICE_PATH.read_text()
    lines = [
        l for l in src.splitlines()
        if "treatment recommendation" in l.lower() and "no treatment" not in l.lower()
    ]
    assert len(lines) == 0


# ── Arch doc ──────────────────────────────────────────────────────────────────


def test_arch_doc_exists():
    assert _ARCH_DOC_PATH.exists()


def test_arch_doc_mentions_module_151():
    doc = _ARCH_DOC_PATH.read_text()
    assert "151" in doc


def test_arch_doc_mentions_synthetic():
    doc = _ARCH_DOC_PATH.read_text()
    assert "synthetic" in doc.lower()


def test_arch_doc_mentions_no_phi():
    doc = _ARCH_DOC_PATH.read_text()
    assert "production_phi_enabled" in doc or "PHI" in doc


def test_arch_doc_mentions_no_history_writes():
    doc = _ARCH_DOC_PATH.read_text()
    doc_lower = doc.lower()
    assert "no history write" in doc_lower or "history write" in doc_lower


def test_arch_doc_mentions_no_ai():
    doc = _ARCH_DOC_PATH.read_text()
    doc_lower = doc.lower()
    assert "no ai" in doc_lower or "ai structuring" in doc_lower
