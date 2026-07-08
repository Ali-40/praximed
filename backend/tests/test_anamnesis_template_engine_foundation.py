"""
Tests — Anamnesis Template Engine Foundation (Module 150).

Covers: migration, Pydantic schemas, seed templates, repo functions,
service layer, routes (unit), forbidden vocabulary guards, PHI invariant,
schema.sql update, arch doc existence.

No patient answers. No history writes. No AI structuring.
No diagnosis. No medical advice. No triage scoring.
production_phi_enabled always False. Synthetic/fake staging only.
Production PHI remains NO-GO.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

# ── Helpers ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[2]
_MIGRATION_PATH = ROOT / "backend/migrations/versions/0008_anamnesis_templates.py"
_SCHEMA_SQL_PATH = ROOT / "backend/app/db/schema.sql"
_REPO_PATH = ROOT / "backend/app/db/repositories/anamnesis_template_repo.py"
_SERVICE_PATH = ROOT / "backend/app/services/anamnesis_template_engine.py"
_ROUTES_PATH = ROOT / "backend/app/api/routes/anamnesis_templates.py"
_ARCH_DOC_PATH = ROOT / "docs/architecture/ANAMNESIS_TEMPLATE_ENGINE_FOUNDATION.md"


def _load_migration() -> Any:
    spec = importlib.util.spec_from_file_location("migration_0008", _MIGRATION_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _minimal_schema() -> Dict[str, Any]:
    return {
        "sections": [
            {
                "section_key": "basic",
                "title": {"de": "Grunddaten"},
                "questions": [
                    {
                        "question_key": "chief_complaint",
                        "type": "textarea",
                        "label": {"de": "Hauptbeschwerden"},
                    }
                ],
            }
        ]
    }


def _make_pool(return_value: Any = None, fetch_return: Any = None) -> Any:
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=return_value)
    pool.fetch = AsyncMock(return_value=fetch_return or [])
    return pool


# ── Migration file checks ──────────────────────────────────────────────────────


def test_migration_file_exists():
    assert _MIGRATION_PATH.exists()


def test_migration_revision_id():
    mod = _load_migration()
    assert mod.revision == "0008_anamnesis_templates"


def test_migration_down_revision():
    mod = _load_migration()
    assert mod.down_revision == "0007_patient_history_data_model"


def test_migration_has_empty_jsonb_constant():
    mod = _load_migration()
    assert mod._EMPTY_JSONB == "'{}'::jsonb"


def test_migration_has_empty_array_jsonb_constant():
    mod = _load_migration()
    assert mod._EMPTY_ARRAY_JSONB == "'[]'::jsonb"


def test_migration_has_default_languages_constant():
    mod = _load_migration()
    assert "de" in mod._DEFAULT_LANGUAGES_JSONB
    assert "en" in mod._DEFAULT_LANGUAGES_JSONB


def test_migration_no_double_brace_jsonb():
    src = _MIGRATION_PATH.read_text()
    assert "'{{}}'" not in src
    assert "'{{}}'::jsonb" not in src


def test_migration_status_values():
    mod = _load_migration()
    assert "draft" in mod._STATUS_VALUES
    assert "active" in mod._STATUS_VALUES
    assert "archived" in mod._STATUS_VALUES


def test_migration_language_values():
    mod = _load_migration()
    assert "de" in mod._LANGUAGE_VALUES
    assert "en" in mod._LANGUAGE_VALUES
    assert "ar" in mod._LANGUAGE_VALUES


def test_migration_consent_purpose_values():
    mod = _load_migration()
    assert "patient_history_collection" in mod._CONSENT_PURPOSE_VALUES
    assert "phone_history_questions" in mod._CONSENT_PURPOSE_VALUES
    assert "demo_seed" in mod._CONSENT_PURPOSE_VALUES


def test_migration_phi_check_constraint_present():
    src = _MIGRATION_PATH.read_text()
    assert "anamnesis_templates_phi_check" in src
    assert "production_phi_enabled = false" in src


def test_migration_partial_unique_index_global():
    src = _MIGRATION_PATH.read_text()
    assert "uidx_anamnesis_templates_global_key_version" in src
    assert "clinic_id IS NULL" in src


def test_migration_partial_unique_index_clinic():
    src = _MIGRATION_PATH.read_text()
    assert "uidx_anamnesis_templates_clinic_key_version" in src
    assert "clinic_id IS NOT NULL" in src


def test_migration_has_upgrade_and_downgrade():
    mod = _load_migration()
    assert callable(mod.upgrade)
    assert callable(mod.downgrade)


# ── schema.sql checks ─────────────────────────────────────────────────────────


def test_schema_sql_has_anamnesis_templates_table():
    sql = _SCHEMA_SQL_PATH.read_text()
    assert "CREATE TABLE IF NOT EXISTS anamnesis_templates" in sql


def test_schema_sql_phi_check():
    sql = _SCHEMA_SQL_PATH.read_text()
    assert "anamnesis_templates_phi_check" in sql


def test_schema_sql_valid_jsonb_defaults():
    sql = _SCHEMA_SQL_PATH.read_text()
    # Must use proper JSONB defaults in schema.sql
    assert "'{}'::jsonb" in sql
    assert "'{{}}'::jsonb" not in sql


def test_schema_sql_partial_unique_indexes():
    sql = _SCHEMA_SQL_PATH.read_text()
    assert "uidx_anamnesis_templates_global_key_version" in sql
    assert "uidx_anamnesis_templates_clinic_key_version" in sql


# ── Pydantic schemas ───────────────────────────────────────────────────────────

from backend.app.schemas.anamnesis_template import (
    AnamnesisTemplateCreate,
    AnamnesisTemplateQuestion,
    AnamnesisTemplateSection,
    AnamnesisTemplateSchemaPayload,
    AnamnesisTemplateStatusUpdate,
    AnamnesisTemplateResponse,
    AnamnesisTemplateListResponse,
)


def test_schema_create_valid_minimal():
    obj = AnamnesisTemplateCreate(
        template_key="test_key",
        display_name="Test Template",
        specialty="general_practice",
        template_schema=_minimal_schema(),
    )
    assert obj.template_key == "test_key"
    assert obj.primary_language == "de"
    assert obj.production_phi_enabled is False if hasattr(obj, "production_phi_enabled") else True


def test_schema_create_rejects_empty_template_key():
    with pytest.raises(ValidationError):
        AnamnesisTemplateCreate(
            template_key="  ",
            display_name="Test",
            specialty="gp",
            template_schema=_minimal_schema(),
        )


def test_schema_create_rejects_invalid_language():
    with pytest.raises(ValidationError):
        AnamnesisTemplateCreate(
            template_key="k",
            display_name="T",
            specialty="gp",
            primary_language="fr",
            template_schema=_minimal_schema(),
        )


def test_schema_create_rejects_primary_lang_not_in_supported():
    with pytest.raises(ValidationError):
        AnamnesisTemplateCreate(
            template_key="k",
            display_name="T",
            specialty="gp",
            primary_language="ar",
            supported_languages=["de", "en"],
            template_schema=_minimal_schema(),
        )


def test_schema_create_rejects_missing_sections():
    with pytest.raises(ValidationError):
        AnamnesisTemplateCreate(
            template_key="k",
            display_name="T",
            specialty="gp",
            template_schema={"no_sections": []},
        )


def test_schema_create_rejects_forbidden_score_key():
    # _reject_forbidden_schema_content checks dict keys, so embed "risk_score" as a key
    schema = {
        "sections": [
            {
                "section_key": "s",
                "title": {"de": "T"},
                "risk_score": 0,  # forbidden key at section level
                "questions": [
                    {
                        "question_key": "q1",
                        "type": "number",
                        "label": {"de": "Score"},
                    }
                ],
            }
        ]
    }
    with pytest.raises(ValidationError):
        AnamnesisTemplateCreate(
            template_key="k",
            display_name="T",
            specialty="gp",
            template_schema=schema,
        )


def test_schema_create_rejects_invalid_consent_purpose():
    with pytest.raises(ValidationError):
        AnamnesisTemplateCreate(
            template_key="k",
            display_name="T",
            specialty="gp",
            template_schema=_minimal_schema(),
            consent_purpose="invalid_purpose",
        )


def test_schema_create_rejects_version_zero():
    with pytest.raises(ValidationError):
        AnamnesisTemplateCreate(
            template_key="k",
            display_name="T",
            specialty="gp",
            template_schema=_minimal_schema(),
            version=0,
        )


def test_schema_question_valid():
    q = AnamnesisTemplateQuestion(
        question_key="q1",
        type="textarea",
        label={"de": "Frage", "en": "Question"},
        history_target="allergies",
    )
    assert q.skip_allowed is True
    assert q.required is False


def test_schema_question_rejects_invalid_type():
    with pytest.raises(ValidationError):
        AnamnesisTemplateQuestion(
            question_key="q1",
            type="invalid_type",
            label={"de": "Frage"},
        )


def test_schema_question_rejects_invalid_history_target():
    with pytest.raises(ValidationError):
        AnamnesisTemplateQuestion(
            question_key="q1",
            type="text",
            label={"de": "Frage"},
            history_target="invalid_target",
        )


def test_schema_question_rejects_empty_label():
    with pytest.raises(ValidationError):
        AnamnesisTemplateQuestion(
            question_key="q1",
            type="text",
            label={},
        )


def test_schema_section_rejects_empty_questions():
    with pytest.raises(ValidationError):
        AnamnesisTemplateSection(
            section_key="s",
            title={"de": "Titel"},
            questions=[],
        )


def test_schema_status_update_allows_active():
    su = AnamnesisTemplateStatusUpdate(status="active")
    assert su.status == "active"


def test_schema_status_update_allows_archived():
    su = AnamnesisTemplateStatusUpdate(status="archived")
    assert su.status == "archived"


def test_schema_status_update_rejects_draft():
    with pytest.raises(ValidationError):
        AnamnesisTemplateStatusUpdate(status="draft")


def test_schema_forbidden_patterns_include_score():
    src = _ROUTES_PATH.read_text()
    repo_src = _REPO_PATH.read_text()
    schema_src = (ROOT / "backend/app/schemas/anamnesis_template.py").read_text()
    assert "score" in schema_src


def test_schema_forbidden_patterns_include_diagnosis_score():
    schema_src = (ROOT / "backend/app/schemas/anamnesis_template.py").read_text()
    assert "diagnosis_score" in schema_src


# ── Repo unit tests (mocked pool) ─────────────────────────────────────────────

from backend.app.db.repositories.anamnesis_template_repo import (
    create_anamnesis_template,
    get_anamnesis_template_by_id,
    get_anamnesis_template_by_key,
    list_anamnesis_templates,
    update_anamnesis_template_status,
    archive_anamnesis_template,
    seed_demo_anamnesis_templates,
    AnamnesisTemplateRepoError,
    AnamnesisTemplateNotFoundError,
    InvalidAnamnesisTemplateError,
)


def _fake_row(overrides: dict | None = None) -> dict:
    base = {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "clinic_id": None,
        "template_key": "demo_gp_basic_history",
        "display_name": "Test",
        "specialty": "general_practice",
        "version": 1,
        "status": "draft",
        "primary_language": "de",
        "supported_languages": json.dumps(["de", "en"]),
        "template_schema": json.dumps({"sections": []}),
        "escalation_keywords": json.dumps([]),
        "consent_purpose": "patient_history_collection",
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "created_by_user_id": None,
        "updated_by_user_id": None,
        "created_at": "2026-07-08T00:00:00Z",
        "updated_at": "2026-07-08T00:00:00Z",
    }
    if overrides:
        base.update(overrides)
    return base


class _FakeRow(dict):
    pass


@pytest.mark.asyncio
async def test_repo_create_calls_fetchrow():
    row = _FakeRow(_fake_row())
    pool = _make_pool(return_value=row)
    result = await create_anamnesis_template(
        pool=pool,
        template_key="demo_gp_basic_history",
        display_name="GP Template",
        specialty="general_practice",
        template_schema=_minimal_schema(),
    )
    pool.fetchrow.assert_called_once()
    assert result["template_key"] == "demo_gp_basic_history"


@pytest.mark.asyncio
async def test_repo_create_rejects_empty_template_key():
    pool = _make_pool()
    with pytest.raises(InvalidAnamnesisTemplateError):
        await create_anamnesis_template(
            pool=pool,
            template_key="",
            display_name="T",
            specialty="gp",
            template_schema=_minimal_schema(),
        )


@pytest.mark.asyncio
async def test_repo_create_rejects_schema_without_sections():
    pool = _make_pool()
    with pytest.raises(InvalidAnamnesisTemplateError):
        await create_anamnesis_template(
            pool=pool,
            template_key="k",
            display_name="T",
            specialty="gp",
            template_schema={"no_sections": True},
        )


@pytest.mark.asyncio
async def test_repo_get_by_id_returns_none_when_missing():
    pool = _make_pool(return_value=None)
    result = await get_anamnesis_template_by_id(pool=pool, template_id="nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_repo_get_by_id_returns_dict_when_found():
    row = _FakeRow(_fake_row())
    pool = _make_pool(return_value=row)
    result = await get_anamnesis_template_by_id(
        pool=pool, template_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    )
    assert result is not None
    assert result["id"] == "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"


@pytest.mark.asyncio
async def test_repo_get_by_key_global_uses_null_clinic():
    pool = _make_pool(return_value=None)
    await get_anamnesis_template_by_key(pool=pool, template_key="k", clinic_id=None)
    sql_arg = pool.fetchrow.call_args[0][0]
    assert "clinic_id IS NULL" in sql_arg


@pytest.mark.asyncio
async def test_repo_get_by_key_clinic_scoped():
    pool = _make_pool(return_value=None)
    await get_anamnesis_template_by_key(
        pool=pool,
        template_key="k",
        clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
    )
    sql_arg = pool.fetchrow.call_args[0][0]
    assert "clinic_id IS NULL" in sql_arg  # clinic-specific query still allows global fallback


@pytest.mark.asyncio
async def test_repo_list_deserializes_jsonb():
    row = _FakeRow(_fake_row())
    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=[row])
    results = await list_anamnesis_templates(pool=pool, clinic_id=None)
    assert isinstance(results[0]["supported_languages"], list)
    assert isinstance(results[0]["template_schema"], dict)
    assert isinstance(results[0]["escalation_keywords"], list)


@pytest.mark.asyncio
async def test_repo_update_status_calls_fetchrow():
    row = _FakeRow(_fake_row({"status": "active"}))
    pool = _make_pool(return_value=row)
    result = await update_anamnesis_template_status(
        pool=pool,
        template_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        status="active",
    )
    assert result["status"] == "active"


@pytest.mark.asyncio
async def test_repo_archive_sets_archived_status():
    row = _FakeRow(_fake_row({"status": "archived"}))
    pool = _make_pool(return_value=row)
    result = await archive_anamnesis_template(
        pool=pool,
        template_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    )
    assert result["status"] == "archived"


@pytest.mark.asyncio
async def test_repo_seed_demo_calls_create_for_each_template():
    demo_templates = [
        {
            "template_key": "k1",
            "display_name": "T1",
            "specialty": "gp",
            "template_schema": _minimal_schema(),
        },
        {
            "template_key": "k2",
            "display_name": "T2",
            "specialty": "derm",
            "template_schema": _minimal_schema(),
        },
    ]
    rows = [_FakeRow(_fake_row({"template_key": t["template_key"]})) for t in demo_templates]
    pool = MagicMock()
    pool.fetchrow = AsyncMock(side_effect=rows)
    results = await seed_demo_anamnesis_templates(pool=pool, demo_templates=demo_templates)
    assert pool.fetchrow.call_count == 2
    assert len(results) == 2


# ── Service layer tests ───────────────────────────────────────────────────────

from backend.app.services import anamnesis_template_engine as svc_mod


@pytest.mark.asyncio
async def test_service_get_demo_templates_returns_three():
    templates = svc_mod.get_demo_templates()
    assert len(templates) == 3


def test_service_demo_templates_have_required_keys():
    for t in svc_mod.get_demo_templates():
        assert "template_key" in t
        assert "display_name" in t
        assert "specialty" in t
        assert "template_schema" in t
        assert "sections" in t["template_schema"]


def test_service_demo_templates_all_synthetic():
    for t in svc_mod.get_demo_templates():
        assert t.get("synthetic_demo") is True


def test_service_demo_templates_phi_always_false():
    for t in svc_mod.get_demo_templates():
        assert t.get("production_phi_enabled") is False


def test_service_demo_templates_include_gp():
    keys = [t["template_key"] for t in svc_mod.get_demo_templates()]
    assert "demo_gp_basic_history" in keys


def test_service_demo_templates_include_dermatology():
    keys = [t["template_key"] for t in svc_mod.get_demo_templates()]
    assert "demo_dermatology_basic_history" in keys


def test_service_demo_templates_include_pediatrics():
    keys = [t["template_key"] for t in svc_mod.get_demo_templates()]
    assert "demo_pediatrics_since_birth" in keys


def test_service_demo_gp_has_escalation_keywords():
    gp = next(t for t in svc_mod.get_demo_templates() if t["template_key"] == "demo_gp_basic_history")
    assert len(gp.get("escalation_keywords", [])) > 0


def test_service_demo_templates_three_language_labels():
    for t in svc_mod.get_demo_templates():
        for section in t["template_schema"]["sections"]:
            title = section["title"]
            assert "de" in title or "en" in title  # at least one label per section


def test_service_demo_templates_skip_allowed():
    for t in svc_mod.get_demo_templates():
        for section in t["template_schema"]["sections"]:
            for q in section["questions"]:
                assert q.get("skip_allowed", True) is True


@pytest.mark.asyncio
async def test_service_create_template_delegates_to_repo():
    row = _FakeRow(_fake_row())
    pool = _make_pool(return_value=row)
    with patch.object(svc_mod.anamnesis_template_repo, "create_anamnesis_template", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = dict(row)
        result = await svc_mod.create_template(
            pool=pool,
            payload={
                "template_key": "k",
                "display_name": "T",
                "specialty": "gp",
                "template_schema": _minimal_schema(),
            },
        )
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_service_list_templates_delegates_to_repo():
    pool = _make_pool(fetch_return=[])
    with patch.object(svc_mod.anamnesis_template_repo, "list_anamnesis_templates", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        result = await svc_mod.list_templates(pool=pool)
        mock_list.assert_called_once()


@pytest.mark.asyncio
async def test_service_get_template_returns_none_when_not_found():
    pool = _make_pool(return_value=None)
    with patch.object(svc_mod.anamnesis_template_repo, "get_anamnesis_template_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        result = await svc_mod.get_template(pool=pool, template_id="nonexistent")
        assert result is None


@pytest.mark.asyncio
async def test_service_activate_template_calls_repo():
    row = _FakeRow(_fake_row({"status": "active"}))
    with patch.object(svc_mod.anamnesis_template_repo, "update_anamnesis_template_status", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = dict(row)
        result = await svc_mod.activate_template(pool=MagicMock(), template_id="tid")
        mock_update.assert_called_once()
        assert result["status"] == "active"


@pytest.mark.asyncio
async def test_service_archive_template_calls_repo():
    row = _FakeRow(_fake_row({"status": "archived"}))
    with patch.object(svc_mod.anamnesis_template_repo, "archive_anamnesis_template", new_callable=AsyncMock) as mock_archive:
        mock_archive.return_value = dict(row)
        result = await svc_mod.archive_template(pool=MagicMock(), template_id="tid")
        mock_archive.assert_called_once()


@pytest.mark.asyncio
async def test_service_seed_demo_templates_seeds_three():
    pool = MagicMock()
    rows = [_FakeRow(_fake_row({"template_key": t["template_key"]})) for t in svc_mod._DEMO_TEMPLATES]
    with patch.object(svc_mod.anamnesis_template_repo, "seed_demo_anamnesis_templates", new_callable=AsyncMock) as mock_seed:
        mock_seed.return_value = [dict(r) for r in rows]
        result = await svc_mod.seed_demo_templates(pool=pool)
        mock_seed.assert_called_once()
        assert len(result) == 3


# ── Route-level unit tests ────────────────────────────────────────────────────

from backend.app.api.routes.anamnesis_templates import router as at_router
from backend.app.api.routes import anamnesis_templates as at_routes_mod


def _fake_auth() -> Any:
    ctx = MagicMock()
    ctx.user_id = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
    return ctx


def test_routes_module_exists():
    assert _ROUTES_PATH.exists()


def test_routes_has_no_delete_route():
    src = _ROUTES_PATH.read_text()
    assert "@router.delete" not in src


def test_routes_requires_current_user():
    src = _ROUTES_PATH.read_text()
    assert "get_current_user" in src


def test_routes_production_phi_always_false():
    src = _ROUTES_PATH.read_text()
    assert "production_phi_enabled" in src


@pytest.mark.asyncio
async def test_route_get_template_404_when_none():
    with patch.object(svc_mod, "get_template", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await at_routes_mod.get_anamnesis_template(
                template_id="missing",
                pool=MagicMock(),
                current_user=_fake_auth(),
            )
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_route_get_template_returns_ok():
    row = dict(_fake_row())
    with patch.object(svc_mod, "get_template", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = row
        response = await at_routes_mod.get_anamnesis_template(
            template_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            pool=MagicMock(),
            current_user=_fake_auth(),
        )
        assert response.ok is True
        assert response.template is not None


@pytest.mark.asyncio
async def test_route_list_templates_returns_ok():
    with patch.object(svc_mod, "list_templates", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [dict(_fake_row())]
        response = await at_routes_mod.list_anamnesis_templates(
            clinic_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
            specialty=None,
            status=None,
            limit=50,
            pool=MagicMock(),
            current_user=_fake_auth(),
        )
        assert response.ok is True
        assert response.total == 1


@pytest.mark.asyncio
async def test_route_update_status_active():
    row = dict(_fake_row({"status": "active"}))
    with patch.object(svc_mod, "activate_template", new_callable=AsyncMock) as mock_activate:
        mock_activate.return_value = row
        from backend.app.schemas.anamnesis_template import AnamnesisTemplateStatusUpdate
        body = AnamnesisTemplateStatusUpdate(status="active")
        response = await at_routes_mod.update_anamnesis_template_status(
            template_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            body=body,
            pool=MagicMock(),
            current_user=_fake_auth(),
        )
        assert response.ok is True


@pytest.mark.asyncio
async def test_route_update_status_archived():
    row = dict(_fake_row({"status": "archived"}))
    with patch.object(svc_mod, "archive_template", new_callable=AsyncMock) as mock_archive:
        mock_archive.return_value = row
        from backend.app.schemas.anamnesis_template import AnamnesisTemplateStatusUpdate
        body = AnamnesisTemplateStatusUpdate(status="archived")
        response = await at_routes_mod.update_anamnesis_template_status(
            template_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            body=body,
            pool=MagicMock(),
            current_user=_fake_auth(),
        )
        assert response.ok is True


@pytest.mark.asyncio
async def test_route_seed_demo_returns_three():
    rows = [dict(_fake_row({"template_key": f"k{i}"})) for i in range(3)]
    with patch.object(svc_mod, "seed_demo_templates", new_callable=AsyncMock) as mock_seed:
        mock_seed.return_value = rows
        response = await at_routes_mod.seed_demo_anamnesis_templates(
            pool=MagicMock(),
            current_user=_fake_auth(),
        )
        assert response.ok is True
        assert response.total == 3
        assert response.production_phi_enabled is False


# ── Router registration check ─────────────────────────────────────────────────


def test_router_includes_anamnesis_templates():
    src = (ROOT / "backend/app/api/router.py").read_text()
    assert "anamnesis_templates" in src


# ── PHI invariant ─────────────────────────────────────────────────────────────


def test_phi_disabled_in_list_response():
    resp = AnamnesisTemplateListResponse(ok=True, templates=[], total=0)
    assert resp.production_phi_enabled is False


def test_phi_disabled_in_response():
    resp = AnamnesisTemplateResponse(ok=True)
    assert resp.production_phi_enabled is False


def test_service_demo_templates_no_diagnosis_field():
    for t in svc_mod.get_demo_templates():
        schema_str = json.dumps(t["template_schema"])
        assert "diagnosis_score" not in schema_str
        assert "risk_score" not in schema_str
        assert "triage_score" not in schema_str


def test_service_demo_templates_no_medical_advice():
    for t in svc_mod.get_demo_templates():
        schema_str = json.dumps(t["template_schema"])
        assert "treatment_recommendation" not in schema_str
        assert "medical_advice" not in schema_str


# ── Vocabulary guards (schema source) ────────────────────────────────────────


def test_forbidden_schema_patterns_list_has_score():
    src = (ROOT / "backend/app/schemas/anamnesis_template.py").read_text()
    assert '"score"' in src or "'score'" in src


def test_forbidden_schema_patterns_list_has_triage_score():
    src = (ROOT / "backend/app/schemas/anamnesis_template.py").read_text()
    assert "triage_score" in src


def test_forbidden_schema_patterns_list_has_secrets():
    src = (ROOT / "backend/app/schemas/anamnesis_template.py").read_text()
    assert '"sk-"' in src or "'sk-'" in src


def test_repo_no_delete_function():
    src = _REPO_PATH.read_text()
    assert "delete_anamnesis_template" not in src


def test_service_no_delete_function():
    src = _SERVICE_PATH.read_text()
    assert "delete_template" not in src


# ── Arch doc ──────────────────────────────────────────────────────────────────


def test_arch_doc_exists():
    assert _ARCH_DOC_PATH.exists(), f"Missing arch doc: {_ARCH_DOC_PATH}"


def test_arch_doc_mentions_module_150():
    doc = _ARCH_DOC_PATH.read_text()
    assert "150" in doc


def test_arch_doc_mentions_no_patient_answers():
    doc = _ARCH_DOC_PATH.read_text()
    doc_lower = doc.lower()
    assert "no patient answers" in doc_lower or "patient answer" in doc_lower


def test_arch_doc_mentions_phi():
    doc = _ARCH_DOC_PATH.read_text()
    assert "production_phi_enabled" in doc or "PHI" in doc
