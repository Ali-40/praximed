"""
Clinic Configuration Loader — PraxisMed Sprint 1 / Module 1
Updated: Sprint 11 / Module 85 — uuid.UUID-based validation (accept any valid UUID)

Loads per-tenant clinic configuration from:
  1. A JSON file on disk  (backend/tenants/configs/<tenant_id>/clinic_config.json)
  2. A Postgres row       (tenants table, jsonb column `config`)

The two sources are merged: disk config is the authoritative base; DB values
override it at the top level.  Results are cached in-process so that repeated
calls within the same worker process do not hit the filesystem or database
repeatedly.

Security note: tenant_id is validated with Python's uuid.UUID parser before
being used as a path component — this prevents path-traversal attacks.
Any UUID string parseable by the standard library (regardless of version/variant)
is structurally safe as a directory name.  Path containment is additionally
enforced by _assert_within_tenants_dir.
"""

from __future__ import annotations

import json
import re
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[3]          # backend/
_TENANTS_DIR = _REPO_ROOT / "backend" / "tenants" / "configs"

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ConfigNotFoundError(FileNotFoundError):
    """Raised when no configuration can be found for the given tenant."""


class InvalidTenantIDError(ValueError):
    """Raised when the supplied tenant_id is not a valid UUID."""


class ConfigValidationError(ValueError):
    """Raised when the loaded configuration fails Pydantic validation."""


class PathTraversalError(PermissionError):
    """Raised when a resolved config path escapes the tenants directory."""


# ---------------------------------------------------------------------------
# Pydantic model
# ---------------------------------------------------------------------------


class ClinicConfig(BaseModel):
    """Validated configuration for a single clinic tenant."""

    tenant_id: str = Field(..., description="UUID identifying the tenant")
    clinic_name: str = Field(..., min_length=1)
    language: str = Field("de", description="BCP-47 language tag, e.g. 'de', 'en'")
    country: str = Field("AT", description="ISO 3166-1 alpha-2 country code")
    timezone: str = Field("Europe/Vienna")

    # Voice / AI persona
    ai_persona_name: str = Field("Mia", description="Display name of the AI assistant")
    ai_tone: str = Field(
        "professional",
        description="Tone of voice: professional | friendly | empathetic",
    )
    specialties: List[str] = Field(
        default_factory=list,
        description="Medical specialties offered by the clinic",
    )

    # Feature flags
    features: Dict[str, bool] = Field(
        default_factory=dict,
        description="Map of feature-flag name → enabled",
    )

    # Booking / availability rules — consumed by the availability engine
    opening_hours: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "Map of weekday name (lowercase) → {open: 'HH:MM', close: 'HH:MM'} "
            "or null / absent key for closed days. "
            "Example: {\"monday\": {\"open\": \"08:00\", \"close\": \"18:00\"}, \"sunday\": null}"
        ),
    )
    calendar_rules: Optional[Dict[str, Any]] = Field(
        None,
        description="Appointment booking rules, e.g. {\"slot_minutes\": 30}",
    )

    # Optional free-form extras stored in the DB
    extra: Optional[Dict[str, Any]] = Field(
        None,
        description="Arbitrary extra config merged in from the database row",
    )

    @field_validator("tenant_id")
    @classmethod
    def _validate_tenant_id(cls, v: str) -> str:
        _assert_valid_uuid(v)
        return v

    @field_validator("language")
    @classmethod
    def _validate_language(cls, v: str) -> str:
        if not re.fullmatch(r"[a-z]{2,3}(-[A-Z]{2,4})?", v):
            raise ValueError(f"Invalid BCP-47 language tag: {v!r}")
        return v

    @field_validator("country")
    @classmethod
    def _validate_country(cls, v: str) -> str:
        if not re.fullmatch(r"[A-Z]{2}", v):
            raise ValueError(f"Invalid ISO 3166-1 alpha-2 country code: {v!r}")
        return v


# ---------------------------------------------------------------------------
# Helper: voice system prompt
# ---------------------------------------------------------------------------


def build_voice_system_prompt(config: ClinicConfig) -> str:
    """
    Return a natural-language system prompt that instructs the LLM how to
    behave when acting as the clinic's AI voice assistant.

    The prompt is assembled from the validated ClinicConfig so callers never
    need to touch raw config dicts.
    """
    specialties_str = (
        ", ".join(config.specialties) if config.specialties else "general medicine"
    )
    features_on = [k for k, v in config.features.items() if v]
    features_str = ", ".join(features_on) if features_on else "none"

    return (
        f"You are {config.ai_persona_name}, the AI assistant for "
        f"{config.clinic_name} located in {config.country}. "
        f"Always respond in {config.language} with a {config.ai_tone} tone. "
        f"The clinic specialises in: {specialties_str}. "
        f"Active features for this clinic: {features_str}. "
        "You are HIPAA/GDPR-aware and must never store or repeat sensitive "
        "patient data beyond what is strictly necessary for the current request. "
        "If you are unsure about medical advice, always refer the patient to a "
        "qualified healthcare professional."
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _assert_valid_uuid(value: str) -> None:
    """Raise InvalidTenantIDError if *value* is not a valid canonical UUID string.

    Uses Python's standard-library uuid.UUID parser, which accepts any
    structurally valid UUID regardless of version or variant — including
    deterministic/nil-pattern UUIDs used in local development and testing.

    Requires canonical hyphenated lowercase form (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
    so the value is unambiguous as a filesystem path segment.  The primary
    security goal is to block path-traversal payloads (slashes, dots, null
    bytes, SQL fragments) — any UUID accepted by the standard library is safe
    to use as a directory name component.
    """
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        raise InvalidTenantIDError(
            f"tenant_id must be a valid UUID; got {value!r}"
        )
    if str(parsed) != value.lower():
        raise InvalidTenantIDError(
            f"tenant_id must be in canonical hyphenated UUID form; got {value!r}"
        )


def _assert_within_tenants_dir(path: Path) -> None:
    """Raise PathTraversalError if *path* resolves outside _TENANTS_DIR.

    Uses Path.resolve() so symlinks and ``..`` components are both expanded
    before the containment check — the UUID guard alone is not sufficient
    because a future symlink or concatenated segment could escape the boundary.
    """
    resolved = path.resolve()
    tenants_resolved = _TENANTS_DIR.resolve()
    try:
        resolved.relative_to(tenants_resolved)
    except ValueError:
        raise PathTraversalError(
            f"Resolved config path {resolved!r} escapes the tenants "
            f"directory {tenants_resolved!r}. Refusing to open."
        )


def _load_disk_config(tenant_id: str) -> Dict[str, Any]:
    """Load the JSON file for *tenant_id* from disk, or return {} if absent."""
    config_path = _TENANTS_DIR / tenant_id / "clinic_config.json"
    # Defense-in-depth: confirm the resolved path is inside _TENANTS_DIR even
    # though tenant_id has already been validated as a UUID.  This catches
    # symlink attacks and protects against future callers that might supply a
    # pre-built path segment.
    _assert_within_tenants_dir(config_path)
    if not config_path.is_file():
        return {}
    with config_path.open(encoding="utf-8") as fh:
        return json.load(fh)


async def _load_db_config(pool: Any, tenant_id: str) -> Dict[str, Any]:
    """
    Fetch the `config` JSONB column from the `tenants` table.

    *pool* is expected to be an asyncpg Connection or Pool object that
    supports ``pool.fetchrow(sql, *args)``.  Returns {} when no row exists or
    when the tenants table is not yet migrated — disk config is the fallback.
    """
    try:
        row = await pool.fetchrow(
            "SELECT config FROM tenants WHERE id = $1", tenant_id
        )
    except Exception:
        return {}
    if row is None:
        return {}
    raw = row["config"]
    if isinstance(raw, str):
        return json.loads(raw)
    return dict(raw) if raw else {}


# ---------------------------------------------------------------------------
# Main loader
# ---------------------------------------------------------------------------


class ClinicConfigLoader:
    """
    Multi-source, cached configuration loader for PraxisMed clinic tenants.

    Usage (async context, with DB):
        loader = ClinicConfigLoader(pool=pg_pool)
        config = await loader.load(tenant_id)

    Usage (offline / tests, disk-only):
        loader = ClinicConfigLoader()
        config = await loader.load(tenant_id)
    """

    def __init__(self, pool: Any = None) -> None:
        self._pool = pool
        self._cache: Dict[str, ClinicConfig] = {}

    async def load(self, tenant_id: str) -> ClinicConfig:
        """
        Return a validated :class:`ClinicConfig` for *tenant_id*.

        Resolution order:
          1. In-process cache (fastest)
          2. Disk JSON  (``backend/tenants/configs/<id>/clinic_config.json``)
          3. Database   (asyncpg pool, if provided)

        Disk values serve as defaults; DB values override them.
        Raises :class:`ConfigNotFoundError` when neither source has data.
        Raises :class:`InvalidTenantIDError` for malformed UUIDs (guards
        against path traversal).
        """
        # --- guard against path traversal before *anything* else ------------
        _assert_valid_uuid(tenant_id)

        if tenant_id in self._cache:
            return self._cache[tenant_id]

        disk = _load_disk_config(tenant_id)

        db: Dict[str, Any] = {}
        if self._pool is not None:
            db = await _load_db_config(self._pool, tenant_id)

        merged = {**disk, **db}

        if not merged:
            raise ConfigNotFoundError(
                f"No configuration found for tenant {tenant_id!r}. "
                "Expected a disk file or a database row."
            )

        # Inject tenant_id so the model can validate it even if omitted from
        # the stored config.
        merged.setdefault("tenant_id", tenant_id)

        try:
            config = ClinicConfig(**merged)
        except Exception as exc:
            raise ConfigValidationError(
                f"Config for tenant {tenant_id!r} failed validation: {exc}"
            ) from exc

        self._cache[tenant_id] = config
        return config

    def invalidate(self, tenant_id: str) -> None:
        """Evict a single tenant from the in-process cache."""
        self._cache.pop(tenant_id, None)

    def clear_cache(self) -> None:
        """Evict all tenants from the in-process cache."""
        self._cache.clear()
