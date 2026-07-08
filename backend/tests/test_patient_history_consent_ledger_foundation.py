"""
Tests for Sprint 20 / Module 148 — Patient History Consent Ledger Foundation.

Covers: migration contract, schema validation, repository layer, service layer,
API routes (auth, no-delete, no-public), vocabulary guards, safety invariants.

No real patient PHI. No diagnosis. No medical advice. No triage.
Synthetic/fake staging only. Production PHI remains NO-GO.
production_phi_enabled always False.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app
from backend.app.schemas.consent_event import (
    ConsentEventCreate,
    ConsentEventRevoke,
)
from backend.app.db.repositories.consent_event_repo import (
    InvalidConsentEventError,
)

_REPO_ROOT = Path(__file__).parent.parent.parent
_MIGRATION = _REPO_ROOT / "backend/migrations/versions/0006_consent_events.py"
_SCHEMA_SQL = _REPO_ROOT / "backend/app/db/schema.sql"
_SCHEMA_SRC = _REPO_ROOT / "backend/app/schemas/consent_event.py"
_REPO_SRC = _REPO_ROOT / "backend/app/db/repositories/consent_event_repo.py"
_SERVICE_SRC = _REPO_ROOT / "backend/app/services/consent_ledger.py"
_ROUTES_SRC = _REPO_ROOT / "backend/app/api/routes/consent_events.py"
_ROUTER_SRC = _REPO_ROOT / "backend/app/api/router.py"

_FAKE_CLINIC_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
_FAKE_PATIENT_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
_FAKE_EVENT_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
_FAKE_APPT_REQ_ID = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"

FAKE_CONSENT_ROW: Dict[str, Any] = {
    "id": _FAKE_EVENT_ID,
    "clinic_id": _FAKE_CLINIC_ID,
    "patient_id": _FAKE_PATIENT_ID,
    "appointment_request_id": None,
    "consent_subject_type": "patient",
    "consent_subject_ref": None,
    "purpose": "appointment_intake",
    "scope": "intake_v1",
    "channel": "onboarding_form",
    "language": "de",
    "consent_text_version": "v1.0",
    "consent_text_snapshot": "Ich stimme zu.",
    "granted": True,
    "revoked_at": None,
    "revoked_by_user_id": None,
    "revocation_reason": None,
    "captured_by_user_id": None,
    "captured_by_system": None,
    "source_ip_hash": None,
    "user_agent_hash": None,
    "metadata": {},
    "production_phi_enabled": False,
    "created_at": "2026-07-08T10:00:00+00:00",
    "updated_at": "2026-07-08T10:00:00+00:00",
}

_FAKE_POOL = MagicMock()


def _admin_auth() -> AuthContext:
    return AuthContext(
        user_id="admin-user-1",
        clinic_id=_FAKE_CLINIC_ID,
        role="admin",
    )


@pytest.fixture()
def client_auth():
    app.dependency_overrides[get_db_pool] = lambda: _FAKE_POOL
    app.dependency_overrides[get_current_user] = _admin_auth
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def client_no_auth():
    app.dependency_overrides[get_db_pool] = lambda: _FAKE_POOL
    app.dependency_overrides.pop(get_current_user, None)
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── migration contract ──────────────────────────────────────────────────────


def test_migration_file_exists():
    assert _MIGRATION.exists(), f"Migration not found: {_MIGRATION}"


def test_migration_revision_id():
    src = _MIGRATION.read_text()
    assert 'revision = "0006_consent_events"' in src


def test_migration_down_revision():
    src = _MIGRATION.read_text()
    assert 'down_revision = "0005_clinic_vapi_bindings"' in src


def test_migration_table_name():
    src = _MIGRATION.read_text()
    assert "consent_events" in src


def test_migration_has_clinic_id_column():
    src = _MIGRATION.read_text()
    assert "clinic_id" in src


def test_migration_has_patient_id_column():
    src = _MIGRATION.read_text()
    assert "patient_id" in src


def test_migration_has_appointment_request_id_column():
    src = _MIGRATION.read_text()
    assert "appointment_request_id" in src


def test_migration_has_purpose_column():
    src = _MIGRATION.read_text()
    assert "purpose" in src


def test_migration_has_scope_column():
    src = _MIGRATION.read_text()
    assert "scope" in src


def test_migration_has_channel_column():
    src = _MIGRATION.read_text()
    assert "channel" in src


def test_migration_has_language_column():
    src = _MIGRATION.read_text()
    assert "language" in src


def test_migration_has_consent_text_version_column():
    src = _MIGRATION.read_text()
    assert "consent_text_version" in src


def test_migration_has_consent_text_snapshot_column():
    src = _MIGRATION.read_text()
    assert "consent_text_snapshot" in src


def test_migration_has_granted_column():
    src = _MIGRATION.read_text()
    assert "granted" in src


def test_migration_has_revoked_at_column():
    src = _MIGRATION.read_text()
    assert "revoked_at" in src


def test_migration_has_revocation_reason_column():
    src = _MIGRATION.read_text()
    assert "revocation_reason" in src


def test_migration_has_production_phi_enabled_false():
    src = _MIGRATION.read_text()
    assert "production_phi_enabled" in src
    assert "false" in src.lower()


def test_migration_has_channel_check_constraint():
    src = _MIGRATION.read_text()
    assert "consent_events_channel_check" in src


def test_migration_has_language_check_constraint():
    src = _MIGRATION.read_text()
    assert "consent_events_language_check" in src


def test_migration_has_purpose_check_constraint():
    src = _MIGRATION.read_text()
    assert "consent_events_purpose_check" in src


def test_migration_has_phi_check_constraint():
    src = _MIGRATION.read_text()
    assert "consent_events_production_phi_check" in src


def test_migration_has_downgrade():
    src = _MIGRATION.read_text()
    assert "def downgrade" in src
    assert "DROP TABLE IF EXISTS consent_events" in src


# ── schema.sql contract ─────────────────────────────────────────────────────


def test_schema_sql_has_consent_events_table():
    src = _SCHEMA_SQL.read_text()
    assert "consent_events" in src


# ── Pydantic schema validation ──────────────────────────────────────────────


def _valid_payload(**overrides) -> Dict[str, Any]:
    base = {
        "clinic_id": _FAKE_CLINIC_ID,
        "purpose": "appointment_intake",
        "scope": "intake_v1",
        "channel": "onboarding_form",
        "language": "de",
        "consent_text_version": "v1.0",
        "consent_text_snapshot": "Ich stimme zu.",
    }
    base.update(overrides)
    return base


def test_schema_accepts_valid_de_consent_event():
    obj = ConsentEventCreate(**_valid_payload(language="de"))
    assert obj.language == "de"


def test_schema_accepts_valid_en_consent_event():
    obj = ConsentEventCreate(**_valid_payload(language="en"))
    assert obj.language == "en"


def test_schema_accepts_valid_ar_consent_event():
    obj = ConsentEventCreate(**_valid_payload(language="ar"))
    assert obj.language == "ar"


def test_schema_rejects_unsupported_language():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(language="fr"))


def test_schema_rejects_unsupported_channel():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(channel="sms"))


def test_schema_rejects_unsupported_purpose():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(purpose="diagnose_patient"))


def test_schema_rejects_empty_consent_text_snapshot():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(consent_text_snapshot="   "))


def test_schema_rejects_empty_consent_text_version():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(consent_text_version=""))


def test_schema_rejects_empty_scope():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(scope=""))


def test_schema_rejects_empty_clinic_id():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(clinic_id="  "))


def test_schema_accepts_all_valid_channels():
    valid_channels = [
        "onboarding_form", "intake_link", "phone_call",
        "staff_console", "developer_console", "import_demo",
    ]
    for ch in valid_channels:
        obj = ConsentEventCreate(**_valid_payload(channel=ch))
        assert obj.channel == ch


def test_schema_accepts_all_valid_purposes():
    valid_purposes = [
        "appointment_intake", "patient_history_collection",
        "phone_history_questions", "demo_seed",
        "data_processing_acknowledgement",
    ]
    for p in valid_purposes:
        obj = ConsentEventCreate(**_valid_payload(purpose=p))
        assert obj.purpose == p


def test_schema_rejects_secret_like_metadata_key():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(metadata={"diagnosis_code": "X99"}))


def test_schema_rejects_triage_metadata_key():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(metadata={"triage_score": 3}))


def test_schema_rejects_sk_metadata_key():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(metadata={"sk-secret-key": "value"}))


def test_schema_rejects_jwt_metadata_key():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConsentEventCreate(**_valid_payload(metadata={"jwt_token": "xxx"}))


def test_schema_accepts_safe_metadata():
    obj = ConsentEventCreate(**_valid_payload(metadata={"source": "web_form"}))
    assert obj.metadata["source"] == "web_form"


def test_schema_default_granted_is_true():
    obj = ConsentEventCreate(**_valid_payload())
    assert obj.granted is True


def test_schema_default_language_is_de():
    payload = _valid_payload()
    payload.pop("language", None)
    obj = ConsentEventCreate(**payload)
    assert obj.language == "de"


# ── repository layer (unit, mock pool) ─────────────────────────────────────


@pytest.mark.asyncio
async def test_repo_create_consent_event_calls_fetchrow():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=dict(FAKE_CONSENT_ROW))
    from backend.app.db.repositories.consent_event_repo import create_consent_event
    result = await create_consent_event(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        purpose="appointment_intake",
        scope="intake_v1",
        channel="onboarding_form",
        language="de",
        consent_text_version="v1.0",
        consent_text_snapshot="Ich stimme zu.",
    )
    pool.fetchrow.assert_called_once()
    assert result["clinic_id"] == _FAKE_CLINIC_ID


@pytest.mark.asyncio
async def test_repo_create_rejects_invalid_channel():
    pool = MagicMock()
    with pytest.raises(InvalidConsentEventError):
        from backend.app.db.repositories.consent_event_repo import create_consent_event
        await create_consent_event(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            purpose="appointment_intake",
            scope="intake_v1",
            channel="invalid_channel",
            language="de",
            consent_text_version="v1.0",
            consent_text_snapshot="Ich stimme zu.",
        )


@pytest.mark.asyncio
async def test_repo_create_rejects_invalid_language():
    pool = MagicMock()
    with pytest.raises(InvalidConsentEventError):
        from backend.app.db.repositories.consent_event_repo import create_consent_event
        await create_consent_event(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            purpose="appointment_intake",
            scope="intake_v1",
            channel="onboarding_form",
            language="fr",
            consent_text_version="v1.0",
            consent_text_snapshot="Ich stimme zu.",
        )


@pytest.mark.asyncio
async def test_repo_get_consent_event_by_id():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=dict(FAKE_CONSENT_ROW))
    from backend.app.db.repositories.consent_event_repo import get_consent_event_by_id
    result = await get_consent_event_by_id(pool=pool, event_id=_FAKE_EVENT_ID)
    assert result["id"] == _FAKE_EVENT_ID


@pytest.mark.asyncio
async def test_repo_get_consent_event_returns_none_if_not_found():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    from backend.app.db.repositories.consent_event_repo import get_consent_event_by_id
    result = await get_consent_event_by_id(pool=pool, event_id=_FAKE_EVENT_ID)
    assert result is None


@pytest.mark.asyncio
async def test_repo_list_consent_events_for_clinic():
    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=[dict(FAKE_CONSENT_ROW)])
    from backend.app.db.repositories.consent_event_repo import list_consent_events_for_clinic
    rows = await list_consent_events_for_clinic(pool=pool, clinic_id=_FAKE_CLINIC_ID)
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_repo_list_consent_events_for_patient():
    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=[dict(FAKE_CONSENT_ROW)])
    from backend.app.db.repositories.consent_event_repo import list_consent_events_for_patient
    rows = await list_consent_events_for_patient(
        pool=pool, clinic_id=_FAKE_CLINIC_ID, patient_id=_FAKE_PATIENT_ID
    )
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_repo_revoke_consent_event():
    revoked = dict(FAKE_CONSENT_ROW)
    revoked["revoked_at"] = "2026-07-08T11:00:00+00:00"
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=revoked)
    from backend.app.db.repositories.consent_event_repo import revoke_consent_event
    result = await revoke_consent_event(pool=pool, event_id=_FAKE_EVENT_ID)
    assert result["revoked_at"] is not None


@pytest.mark.asyncio
async def test_repo_revoke_returns_none_if_not_found():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    from backend.app.db.repositories.consent_event_repo import revoke_consent_event
    result = await revoke_consent_event(pool=pool, event_id=_FAKE_EVENT_ID)
    assert result is None


@pytest.mark.asyncio
async def test_repo_has_valid_consent_true():
    pool = MagicMock()
    pool.fetchval = AsyncMock(return_value=True)
    from backend.app.db.repositories.consent_event_repo import has_valid_consent_for_purpose
    result = await has_valid_consent_for_purpose(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        patient_id=_FAKE_PATIENT_ID,
        purpose="patient_history_collection",
    )
    assert result is True


@pytest.mark.asyncio
async def test_repo_has_valid_consent_false_for_revoked():
    pool = MagicMock()
    pool.fetchval = AsyncMock(return_value=False)
    from backend.app.db.repositories.consent_event_repo import has_valid_consent_for_purpose
    result = await has_valid_consent_for_purpose(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        patient_id=_FAKE_PATIENT_ID,
        purpose="patient_history_collection",
    )
    assert result is False


# ── service layer (unit, mock pool) ────────────────────────────────────────


@pytest.mark.asyncio
async def test_service_assert_valid_consent_rejects_invalid_purpose():
    pool = MagicMock()
    from backend.app.services.consent_ledger import (
        assert_valid_consent_for_history_write,
        ConsentValidationError,
    )
    with pytest.raises(ConsentValidationError, match="not valid for a history write"):
        await assert_valid_consent_for_history_write(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            consent_event_id=_FAKE_EVENT_ID,
            purpose="appointment_intake",
        )


@pytest.mark.asyncio
async def test_service_assert_valid_consent_rejects_missing_event():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    from backend.app.services.consent_ledger import (
        assert_valid_consent_for_history_write,
        ConsentValidationError,
    )
    with pytest.raises(ConsentValidationError, match="not found"):
        await assert_valid_consent_for_history_write(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            consent_event_id=_FAKE_EVENT_ID,
            purpose="patient_history_collection",
        )


@pytest.mark.asyncio
async def test_service_assert_valid_consent_rejects_wrong_clinic():
    row = dict(FAKE_CONSENT_ROW)
    row["clinic_id"] = "ffffffff-ffff-4fff-8fff-ffffffffffff"
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row)
    from backend.app.services.consent_ledger import (
        assert_valid_consent_for_history_write,
        ConsentValidationError,
    )
    with pytest.raises(ConsentValidationError, match="does not belong to clinic"):
        await assert_valid_consent_for_history_write(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            consent_event_id=_FAKE_EVENT_ID,
            purpose="patient_history_collection",
        )


@pytest.mark.asyncio
async def test_service_assert_valid_consent_rejects_not_granted():
    row = dict(FAKE_CONSENT_ROW)
    row["granted"] = False
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row)
    from backend.app.services.consent_ledger import (
        assert_valid_consent_for_history_write,
        ConsentValidationError,
    )
    with pytest.raises(ConsentValidationError, match="not granted"):
        await assert_valid_consent_for_history_write(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            consent_event_id=_FAKE_EVENT_ID,
            purpose="patient_history_collection",
        )


@pytest.mark.asyncio
async def test_service_assert_valid_consent_rejects_revoked():
    row = dict(FAKE_CONSENT_ROW)
    row["revoked_at"] = "2026-07-08T11:00:00+00:00"
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row)
    from backend.app.services.consent_ledger import (
        assert_valid_consent_for_history_write,
        ConsentValidationError,
    )
    with pytest.raises(ConsentValidationError, match="revoked"):
        await assert_valid_consent_for_history_write(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            consent_event_id=_FAKE_EVENT_ID,
            purpose="patient_history_collection",
        )


@pytest.mark.asyncio
async def test_service_assert_valid_consent_passes_for_history_collection():
    row = dict(FAKE_CONSENT_ROW)
    row["clinic_id"] = _FAKE_CLINIC_ID
    row["granted"] = True
    row["revoked_at"] = None
    row["production_phi_enabled"] = False
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row)
    from backend.app.services.consent_ledger import assert_valid_consent_for_history_write
    await assert_valid_consent_for_history_write(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        consent_event_id=_FAKE_EVENT_ID,
        purpose="patient_history_collection",
    )


@pytest.mark.asyncio
async def test_service_assert_valid_consent_passes_for_phone_history():
    row = dict(FAKE_CONSENT_ROW)
    row["clinic_id"] = _FAKE_CLINIC_ID
    row["granted"] = True
    row["revoked_at"] = None
    row["production_phi_enabled"] = False
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row)
    from backend.app.services.consent_ledger import assert_valid_consent_for_history_write
    await assert_valid_consent_for_history_write(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        consent_event_id=_FAKE_EVENT_ID,
        purpose="phone_history_questions",
    )


# ── API routes — auth guard ─────────────────────────────────────────────────


def test_post_consent_event_requires_auth(client_no_auth):
    resp = client_no_auth.post(
        f"/clinics/{_FAKE_CLINIC_ID}/consent-events",
        json=_valid_payload(),
    )
    assert resp.status_code in (401, 403)


def test_get_consent_events_requires_auth(client_no_auth):
    resp = client_no_auth.get(f"/clinics/{_FAKE_CLINIC_ID}/consent-events")
    assert resp.status_code in (401, 403)


def test_get_single_consent_event_requires_auth(client_no_auth):
    resp = client_no_auth.get(f"/consent-events/{_FAKE_EVENT_ID}")
    assert resp.status_code in (401, 403)


def test_revoke_consent_event_requires_auth(client_no_auth):
    resp = client_no_auth.patch(
        f"/consent-events/{_FAKE_EVENT_ID}/revoke",
        json={},
    )
    assert resp.status_code in (401, 403)


# ── API routes — no DELETE ──────────────────────────────────────────────────


def test_no_delete_route_for_consent_event(client_auth):
    resp = client_auth.delete(f"/consent-events/{_FAKE_EVENT_ID}")
    assert resp.status_code == 405


def test_no_delete_route_for_clinic_consent_events(client_auth):
    resp = client_auth.delete(f"/clinics/{_FAKE_CLINIC_ID}/consent-events")
    assert resp.status_code == 405


# ── API routes — happy-path with mock pool ─────────────────────────────────


def test_post_consent_event_201(client_auth):
    _FAKE_POOL.fetchrow = AsyncMock(return_value=dict(FAKE_CONSENT_ROW))
    resp = client_auth.post(
        f"/clinics/{_FAKE_CLINIC_ID}/consent-events",
        json=_valid_payload(),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["ok"] is True
    assert body["production_phi_enabled"] is False


def test_post_consent_event_clinic_id_mismatch_400(client_auth):
    payload = _valid_payload()
    payload["clinic_id"] = "ffffffff-ffff-4fff-8fff-ffffffffffff"
    resp = client_auth.post(
        f"/clinics/{_FAKE_CLINIC_ID}/consent-events",
        json=payload,
    )
    assert resp.status_code == 400


def test_get_consent_events_200(client_auth):
    _FAKE_POOL.fetchrow = AsyncMock(return_value={"id": _FAKE_CLINIC_ID})
    _FAKE_POOL.fetch = AsyncMock(return_value=[dict(FAKE_CONSENT_ROW)])
    resp = client_auth.get(f"/clinics/{_FAKE_CLINIC_ID}/consent-events")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["production_phi_enabled"] is False
    assert isinstance(body["events"], list)


def test_get_single_consent_event_200(client_auth):
    _FAKE_POOL.fetchrow = AsyncMock(return_value=dict(FAKE_CONSENT_ROW))
    resp = client_auth.get(f"/consent-events/{_FAKE_EVENT_ID}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["production_phi_enabled"] is False


def test_get_single_consent_event_404(client_auth):
    _FAKE_POOL.fetchrow = AsyncMock(return_value=None)
    resp = client_auth.get(f"/consent-events/{_FAKE_EVENT_ID}")
    assert resp.status_code == 404


def test_revoke_consent_event_200(client_auth):
    revoked = dict(FAKE_CONSENT_ROW)
    revoked["revoked_at"] = "2026-07-08T11:00:00+00:00"
    _FAKE_POOL.fetchrow = AsyncMock(return_value=revoked)
    resp = client_auth.patch(
        f"/consent-events/{_FAKE_EVENT_ID}/revoke",
        json={"revocation_reason": "Patient withdrew consent"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["production_phi_enabled"] is False


# ── production_phi_enabled invariant ───────────────────────────────────────


def test_routes_always_return_production_phi_enabled_false_on_create(client_auth):
    _FAKE_POOL.fetchrow = AsyncMock(return_value=dict(FAKE_CONSENT_ROW))
    resp = client_auth.post(
        f"/clinics/{_FAKE_CLINIC_ID}/consent-events",
        json=_valid_payload(),
    )
    assert resp.json().get("production_phi_enabled") is False


def test_routes_always_return_production_phi_enabled_false_on_list(client_auth):
    _FAKE_POOL.fetchrow = AsyncMock(return_value={"id": _FAKE_CLINIC_ID})
    _FAKE_POOL.fetch = AsyncMock(return_value=[dict(FAKE_CONSENT_ROW)])
    resp = client_auth.get(f"/clinics/{_FAKE_CLINIC_ID}/consent-events")
    assert resp.json().get("production_phi_enabled") is False


def test_routes_always_return_production_phi_enabled_false_on_revoke(client_auth):
    revoked = dict(FAKE_CONSENT_ROW)
    revoked["revoked_at"] = "2026-07-08T11:00:00+00:00"
    _FAKE_POOL.fetchrow = AsyncMock(return_value=revoked)
    resp = client_auth.patch(
        f"/consent-events/{_FAKE_EVENT_ID}/revoke",
        json={},
    )
    assert resp.json().get("production_phi_enabled") is False


# ── router registration ────────────────────────────────────────────────────


def test_router_imports_consent_events():
    src = _ROUTER_SRC.read_text()
    assert "consent_events" in src


def test_router_includes_consent_events_router():
    src = _ROUTER_SRC.read_text()
    assert "consent_events.router" in src


# ── vocabulary guards — no diagnosis in source files ───────────────────────


def _all_sources() -> str:
    return "\n".join([
        _SCHEMA_SRC.read_text(),
        _REPO_SRC.read_text(),
        _SERVICE_SRC.read_text(),
        _ROUTES_SRC.read_text(),
    ])


def _diagnos_lines_outside_prohibition(src: str) -> list:
    import re
    lines = [l for l in src.splitlines() if re.search(r"diagnos", l, re.IGNORECASE)]
    return [l for l in lines if not re.search(r"\bno\s+diagnos", l, re.IGNORECASE)]


def _medical_advice_lines_outside_prohibition(src: str) -> list:
    import re
    lines = [l for l in src.splitlines() if re.search(r"medical.?advice", l, re.IGNORECASE)]
    return [l for l in lines if not re.search(r"\bno\s+medical", l, re.IGNORECASE)]


def test_schema_forbidden_patterns_include_diagnosis():
    src = _SCHEMA_SRC.read_text()
    assert '"diagnosis"' in src, "Schema must list 'diagnosis' as a forbidden metadata key"


def test_schema_forbidden_patterns_include_medical_advice():
    src = _SCHEMA_SRC.read_text()
    assert '"medical_advice"' in src, "Schema must list 'medical_advice' as a forbidden metadata key"


def test_no_triage_scoring_in_service():
    src = _SERVICE_SRC.read_text().lower()
    assert "triage_score" not in src


def test_no_diagnosis_vocabulary_in_service():
    src = _SERVICE_SRC.read_text()
    bad = _diagnos_lines_outside_prohibition(src)
    assert not bad, f"Unexpected diagnosis vocabulary in service: {bad}"


def test_no_diagnosis_vocabulary_in_routes():
    src = _ROUTES_SRC.read_text()
    bad = _diagnos_lines_outside_prohibition(src)
    assert not bad, f"Unexpected diagnosis vocabulary in routes: {bad}"


def test_no_medical_advice_vocabulary_in_routes():
    src = _ROUTES_SRC.read_text()
    bad = _medical_advice_lines_outside_prohibition(src)
    assert not bad, f"Unexpected medical advice vocabulary in routes: {bad}"


def test_no_database_url_in_source_files():
    src = _all_sources()
    assert "DATABASE_URL" not in src


def test_no_jwt_secret_in_source_files():
    src = _all_sources()
    assert "JWT_SECRET" not in src


def test_no_actual_sk_key_in_source_files():
    import re
    src = _all_sources()
    assert not re.search(r"sk-[A-Za-z0-9]{10,}", src), "Actual sk-... key found in source"


def test_no_vapi_live_credential_in_source_files():
    import re
    src = _all_sources()
    assert not re.search(r"vapi_live_[A-Za-z0-9]{6,}", src), "Actual vapi_live_... found in source"


def test_routes_production_phi_enabled_always_false_keyword():
    src = _ROUTES_SRC.read_text()
    assert "production_phi_enabled=False" in src


def test_service_production_phi_enabled_always_false_keyword():
    src = _SERVICE_SRC.read_text()
    assert "production_phi_enabled" in src
    assert "False" in src


def test_routes_no_delete_endpoint():
    import re
    src = _ROUTES_SRC.read_text()
    assert not re.search(r"@router\.delete", src), "DELETE route found — consent events are append-only"


def test_service_has_assert_valid_consent_gate():
    src = _SERVICE_SRC.read_text()
    assert "assert_valid_consent_for_history_write" in src


def test_service_has_history_write_purposes():
    src = _SERVICE_SRC.read_text()
    assert "patient_history_collection" in src
    assert "phone_history_questions" in src
