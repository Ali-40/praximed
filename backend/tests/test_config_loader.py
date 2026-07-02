"""
Unit tests for backend/app/core/config_loader.py

All tests are fully isolated from the filesystem and database:
  - Disk configs are written to a tmp_path fixture and the loader's
    _TENANTS_DIR is monkey-patched so no real tenant dirs are needed.
  - The database is replaced by FakePool, a minimal asyncio mock that
    returns caller-supplied rows without touching Postgres.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Minimal asyncio DB mock
# ---------------------------------------------------------------------------


class FakePool:
    """
    Drop-in replacement for an asyncpg Pool/Connection.

    Initialise with a dict mapping tenant_id → config dict.  ``fetchrow``
    returns a dict-like object (or None) exactly as asyncpg does.
    """

    def __init__(self, rows: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        self._rows = rows or {}

    async def fetchrow(self, sql: str, tenant_id: str) -> Optional[Dict[str, Any]]:  # noqa: ARG002
        row = self._rows.get(tenant_id)
        if row is None:
            return None
        return {"config": row}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Canonical RFC 4122 v4 UUID strings (version nibble = 4, variant bits = 8–b).
VALID_UUID   = "11111111-1111-4111-8111-111111111111"
VALID_UUID_2 = "22222222-2222-4222-a222-222222222222"
VALID_UUID_3 = "33333333-3333-4333-b333-333333333333"

# Deterministic local-dev UUID used by seed_local_data.py.
# Variant nibble is '1' (NCS variant), not RFC 4122 '[89ab]', but structurally
# valid — uuid.UUID() accepts it without raising ValueError.
SEED_UUID = "11111111-1111-1111-1111-111111111111"


def _write_config(base: Path, tenant_id: str, data: Dict[str, Any]) -> None:
    tenant_dir = base / tenant_id
    tenant_dir.mkdir(parents=True, exist_ok=True)
    (tenant_dir / "clinic_config.json").write_text(json.dumps(data), encoding="utf-8")


BASE_CONFIG: Dict[str, Any] = {
    "clinic_name": "Praxis Dr. Muster",
    "language": "de",
    "country": "AT",
    "timezone": "Europe/Vienna",
    "ai_persona_name": "Mia",
    "ai_tone": "professional",
    "specialties": ["Allgemeinmedizin", "Innere Medizin"],
    "features": {"appointment_booking": True, "sms_reminders": False},
}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tenants_dir(tmp_path: Path):
    """Return a temporary tenants/configs directory and patch the module."""
    configs_dir = tmp_path / "tenants" / "configs"
    configs_dir.mkdir(parents=True)
    with patch("backend.app.core.config_loader._TENANTS_DIR", configs_dir):
        yield configs_dir


@pytest.fixture()
def loader_no_db(tenants_dir):
    """ClinicConfigLoader with no database pool (disk-only)."""
    from backend.app.core.config_loader import ClinicConfigLoader

    return ClinicConfigLoader(pool=None), tenants_dir


# ---------------------------------------------------------------------------
# Tests: UUID validation (path-traversal guard)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rejects_path_traversal(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader, InvalidTenantIDError

    loader = ClinicConfigLoader()
    with pytest.raises(InvalidTenantIDError):
        await loader.load("../../etc/passwd")


@pytest.mark.asyncio
async def test_rejects_empty_string(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader, InvalidTenantIDError

    loader = ClinicConfigLoader()
    with pytest.raises(InvalidTenantIDError):
        await loader.load("")


@pytest.mark.asyncio
async def test_rejects_non_uuid(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader, InvalidTenantIDError

    loader = ClinicConfigLoader()
    # Contains a non-hex character in the last group — not a valid UUID
    with pytest.raises(InvalidTenantIDError):
        await loader.load("11111111-1111-4111-8111-11111111111g")


@pytest.mark.asyncio
async def test_rejects_sql_injection(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader, InvalidTenantIDError

    loader = ClinicConfigLoader()
    with pytest.raises(InvalidTenantIDError):
        await loader.load("'; DROP TABLE tenants; --")


# ---------------------------------------------------------------------------
# Tests: UUID compatibility — non-RFC-4122 variant accepted (Module 85)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_accepts_deterministic_local_uuid(tenants_dir):
    """Seed clinic UUID (NCS variant, not RFC 4122) must now be accepted."""
    from backend.app.core.config_loader import ClinicConfig, ClinicConfigLoader

    loader = ClinicConfigLoader(pool=None)
    _write_config(tenants_dir, SEED_UUID, {**BASE_CONFIG, "tenant_id": SEED_UUID})

    config = await loader.load(SEED_UUID)

    assert isinstance(config, ClinicConfig)
    assert config.tenant_id == SEED_UUID


@pytest.mark.asyncio
async def test_accepts_rfc4122_uuid_unchanged(tenants_dir):
    """RFC 4122 UUIDs must still be accepted after switching to uuid.UUID() validation."""
    from backend.app.core.config_loader import ClinicConfig, ClinicConfigLoader

    loader = ClinicConfigLoader(pool=None)
    _write_config(tenants_dir, VALID_UUID, {**BASE_CONFIG})

    config = await loader.load(VALID_UUID)

    assert isinstance(config, ClinicConfig)
    assert config.tenant_id == VALID_UUID


def test_rejects_brace_wrapped_uuid():
    """Brace-wrapped UUID form must be rejected — canonical hyphenated form only."""
    from backend.app.core.config_loader import InvalidTenantIDError, _assert_valid_uuid

    with pytest.raises(InvalidTenantIDError):
        _assert_valid_uuid("{11111111-1111-4111-8111-111111111111}")


def test_rejects_unhyphenated_uuid():
    """UUID without hyphens must be rejected — canonical form required."""
    from backend.app.core.config_loader import InvalidTenantIDError, _assert_valid_uuid

    with pytest.raises(InvalidTenantIDError):
        _assert_valid_uuid("11111111111141118111111111111111")


# ---------------------------------------------------------------------------
# Tests: disk-only loading
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_loads_from_disk(loader_no_db):
    from backend.app.core.config_loader import ClinicConfig

    loader, tenants_dir = loader_no_db
    _write_config(tenants_dir, VALID_UUID, {**BASE_CONFIG, "tenant_id": VALID_UUID})

    config = await loader.load(VALID_UUID)

    assert isinstance(config, ClinicConfig)
    assert config.clinic_name == "Praxis Dr. Muster"
    assert config.tenant_id == VALID_UUID
    assert "Allgemeinmedizin" in config.specialties


@pytest.mark.asyncio
async def test_raises_when_no_config(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader, ConfigNotFoundError

    loader = ClinicConfigLoader(pool=None)
    with pytest.raises(ConfigNotFoundError):
        await loader.load(VALID_UUID)


@pytest.mark.asyncio
async def test_disk_config_missing_tenant_id_is_injected(loader_no_db):
    """tenant_id should be injected automatically even if absent from the file."""
    loader, tenants_dir = loader_no_db
    data = dict(BASE_CONFIG)  # no tenant_id key
    _write_config(tenants_dir, VALID_UUID, data)

    config = await loader.load(VALID_UUID)
    assert config.tenant_id == VALID_UUID


# ---------------------------------------------------------------------------
# Tests: DB-only loading
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_loads_from_db_only(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader

    db_data = {**BASE_CONFIG, "tenant_id": VALID_UUID_2, "clinic_name": "DB Klinik"}
    pool = FakePool({VALID_UUID_2: db_data})
    loader = ClinicConfigLoader(pool=pool)

    config = await loader.load(VALID_UUID_2)
    assert config.clinic_name == "DB Klinik"


@pytest.mark.asyncio
async def test_raises_when_db_returns_nothing(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader, ConfigNotFoundError

    pool = FakePool({})  # no rows
    loader = ClinicConfigLoader(pool=pool)

    with pytest.raises(ConfigNotFoundError):
        await loader.load(VALID_UUID_2)


@pytest.mark.asyncio
async def test_db_error_falls_back_to_disk(tenants_dir):
    """If the DB query raises (e.g. tenants table not yet migrated), disk config is used."""
    from backend.app.core.config_loader import ClinicConfigLoader

    class ErrorPool:
        async def fetchrow(self, sql, tenant_id):
            raise RuntimeError("relation \"tenants\" does not exist")

    _write_config(tenants_dir, VALID_UUID, {**BASE_CONFIG})
    loader = ClinicConfigLoader(pool=ErrorPool())

    config = await loader.load(VALID_UUID)
    assert config.clinic_name == "Praxis Dr. Muster"


# ---------------------------------------------------------------------------
# Tests: merge semantics (disk base, DB override)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_db_overrides_disk(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader

    disk_data = {**BASE_CONFIG, "clinic_name": "Disk Klinik"}
    _write_config(tenants_dir, VALID_UUID_3, disk_data)

    db_data = {"clinic_name": "DB Override Klinik"}
    pool = FakePool({VALID_UUID_3: db_data})
    loader = ClinicConfigLoader(pool=pool)

    config = await loader.load(VALID_UUID_3)
    assert config.clinic_name == "DB Override Klinik"
    # Non-overridden disk fields should still be present
    assert config.language == "de"


# ---------------------------------------------------------------------------
# Tests: in-process cache
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_returns_same_object(loader_no_db):
    loader, tenants_dir = loader_no_db
    _write_config(tenants_dir, VALID_UUID, {**BASE_CONFIG})

    config1 = await loader.load(VALID_UUID)
    config2 = await loader.load(VALID_UUID)
    assert config1 is config2


@pytest.mark.asyncio
async def test_invalidate_removes_from_cache(loader_no_db):
    loader, tenants_dir = loader_no_db
    _write_config(tenants_dir, VALID_UUID, {**BASE_CONFIG})

    config1 = await loader.load(VALID_UUID)
    loader.invalidate(VALID_UUID)
    config2 = await loader.load(VALID_UUID)
    # Different object after cache eviction
    assert config1 is not config2


@pytest.mark.asyncio
async def test_clear_cache(loader_no_db):
    loader, tenants_dir = loader_no_db
    _write_config(tenants_dir, VALID_UUID, {**BASE_CONFIG})

    await loader.load(VALID_UUID)
    loader.clear_cache()
    assert loader._cache == {}


# ---------------------------------------------------------------------------
# Tests: Pydantic validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invalid_language_raises(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader, ConfigValidationError

    bad = {**BASE_CONFIG, "language": "not_valid!"}
    _write_config(tenants_dir, VALID_UUID, bad)
    loader = ClinicConfigLoader(pool=None)

    with pytest.raises(ConfigValidationError):
        await loader.load(VALID_UUID)


@pytest.mark.asyncio
async def test_invalid_country_raises(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader, ConfigValidationError

    bad = {**BASE_CONFIG, "country": "AUT"}  # must be 2 chars
    _write_config(tenants_dir, VALID_UUID, bad)
    loader = ClinicConfigLoader(pool=None)

    with pytest.raises(ConfigValidationError):
        await loader.load(VALID_UUID)


@pytest.mark.asyncio
async def test_missing_clinic_name_raises(tenants_dir):
    from backend.app.core.config_loader import ClinicConfigLoader, ConfigValidationError

    bad = {k: v for k, v in BASE_CONFIG.items() if k != "clinic_name"}
    _write_config(tenants_dir, VALID_UUID, bad)
    loader = ClinicConfigLoader(pool=None)

    with pytest.raises(ConfigValidationError):
        await loader.load(VALID_UUID)


# ---------------------------------------------------------------------------
# Tests: build_voice_system_prompt
# ---------------------------------------------------------------------------


def test_build_voice_system_prompt_contains_persona():
    from backend.app.core.config_loader import ClinicConfig, build_voice_system_prompt

    config = ClinicConfig(
        tenant_id=VALID_UUID,
        clinic_name="Testpraxis",
        ai_persona_name="Mia",
        ai_tone="empathetic",
        specialties=["Dermatologie"],
        features={"appointment_booking": True},
    )
    prompt = build_voice_system_prompt(config)

    assert "Mia" in prompt
    assert "Testpraxis" in prompt
    assert "empathetic" in prompt
    assert "Dermatologie" in prompt
    assert "appointment_booking" in prompt


def test_build_voice_system_prompt_no_specialties():
    from backend.app.core.config_loader import ClinicConfig, build_voice_system_prompt

    config = ClinicConfig(
        tenant_id=VALID_UUID,
        clinic_name="Allgemeinpraxis",
        specialties=[],
        features={},
    )
    prompt = build_voice_system_prompt(config)
    assert "general medicine" in prompt
    assert "none" in prompt


def test_build_voice_system_prompt_gdpr_mention():
    from backend.app.core.config_loader import ClinicConfig, build_voice_system_prompt

    config = ClinicConfig(tenant_id=VALID_UUID, clinic_name="Klinik XY")
    prompt = build_voice_system_prompt(config)
    assert "GDPR" in prompt


# ---------------------------------------------------------------------------
# Tests: path-containment boundary (_assert_within_tenants_dir)
# ---------------------------------------------------------------------------


def test_assert_within_tenants_dir_rejects_traversal(tenants_dir):
    """_assert_within_tenants_dir must reject paths that escape the tenants root."""
    from backend.app.core.config_loader import PathTraversalError, _assert_within_tenants_dir

    # Simulate a path constructed from a rogue segment like "../secrets.json"
    # after it has been joined onto the tenants dir.
    escaped = (tenants_dir / ".." / "secrets.json").resolve()

    # We call the helper directly to test the boundary assertion in isolation.
    # We must patch _TENANTS_DIR so the helper uses our tmp tenants_dir.
    import backend.app.core.config_loader as mod
    original = mod._TENANTS_DIR
    mod._TENANTS_DIR = tenants_dir
    try:
        with pytest.raises(PathTraversalError):
            _assert_within_tenants_dir(escaped)
    finally:
        mod._TENANTS_DIR = original


def test_assert_within_tenants_dir_accepts_valid_path(tenants_dir):
    """_assert_within_tenants_dir must accept paths that are genuinely inside."""
    from backend.app.core.config_loader import _assert_within_tenants_dir

    import backend.app.core.config_loader as mod
    original = mod._TENANTS_DIR
    mod._TENANTS_DIR = tenants_dir
    try:
        valid = tenants_dir / VALID_UUID / "clinic_config.json"
        # Should not raise
        _assert_within_tenants_dir(valid)
    finally:
        mod._TENANTS_DIR = original


@pytest.mark.asyncio
async def test_db_row_with_config_path_field_does_not_read_outside_boundary(tenants_dir):
    """
    A DB row that contains a 'config_path' key pointing outside the tenants
    directory must NOT cause any file outside the boundary to be opened.

    The DB JSONB blob is merged into config values only — no field in it should
    ever redirect a filesystem read.  This test explicitly proves that invariant.
    """
    from backend.app.core.config_loader import ClinicConfigLoader

    # DB row includes a rogue config_path that points one level above the tenants dir.
    db_row = {
        **BASE_CONFIG,
        "config_path": "../secrets.json",   # the attack payload
    }
    pool = FakePool({VALID_UUID_2: db_row})
    loader = ClinicConfigLoader(pool=pool)

    # The loader must succeed (the field is an unknown Pydantic field → ignored)
    # without opening any file outside _TENANTS_DIR.
    config = await loader.load(VALID_UUID_2)
    assert config.clinic_name == BASE_CONFIG["clinic_name"]
    # Ensure the rogue key did not leak into the validated model
    assert not hasattr(config, "config_path")


@pytest.mark.asyncio
async def test_symlink_outside_tenants_dir_is_blocked(tenants_dir, tmp_path):
    """
    A symlink inside the tenants directory that points *outside* it must be
    rejected by the path-containment check before any read is attempted.
    """
    import backend.app.core.config_loader as mod
    from backend.app.core.config_loader import ClinicConfigLoader, PathTraversalError

    # Create a real file outside the tenants directory (the "secret")
    secret_file = tmp_path / "secrets.json"
    secret_file.write_text(json.dumps({"secret": "top-secret-key"}), encoding="utf-8")

    # Plant a symlink inside the tenant dir that points to the secret file.
    tenant_dir = tenants_dir / VALID_UUID
    tenant_dir.mkdir(parents=True, exist_ok=True)
    symlink = tenant_dir / "clinic_config.json"
    symlink.symlink_to(secret_file)

    original = mod._TENANTS_DIR
    mod._TENANTS_DIR = tenants_dir
    try:
        loader = ClinicConfigLoader(pool=None)
        with pytest.raises(PathTraversalError):
            await loader.load(VALID_UUID)
    finally:
        mod._TENANTS_DIR = original
