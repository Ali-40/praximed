"""
Clinic Language Settings Service — PraxisMed Sprint 19 / Module 138.

Reads and updates tenant language settings.

Storage:
  - clinics.locale is the authoritative DB value (e.g. 'de-AT').
  - Full language settings (including vapi_assistant_language_mode,
    default_patient_language, supported_languages, clinic_ui_language) are
    stored in the tenant config JSON file under the 'language_config' key.
  - On GET: derive primary_language from clinics.locale; overlay language_config
    from the JSON file if present.
  - On PATCH: update clinics.locale in the DB; write/merge language_config into
    the JSON config file.

No migration is required — clinics.locale already exists in the clinics table.

Safety:
  - No PHI stored or returned.
  - No Vapi credentials stored or returned.
  - No secrets stored or returned.
  - Production PHI remains NO-GO.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_TENANTS_DIR = (
    Path(__file__).resolve().parents[3] / "backend" / "tenants" / "configs"
)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ClinicNotFoundError(LookupError):
    """Raised when the referenced clinic does not exist."""


class LanguageSettingsValidationError(ValueError):
    """Raised when the proposed language settings are invalid."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GERMAN_FIRST_DEFAULTS: Dict[str, Any] = {
    "primary_language":           "de",
    "fallback_language":          "en",
    "supported_languages":        ["de", "en"],
    "default_patient_language":   "de",
    "vapi_assistant_language_mode": "german_first",
    "clinic_ui_language":         "de",
}

_LOCALE_TO_LANG: Dict[str, str] = {
    "de-AT": "de",
    "de-DE": "de",
    "de":    "de",
    "en-US": "en",
    "en-GB": "en",
    "en":    "en",
}

_LANG_TO_LOCALE: Dict[str, str] = {
    "de": "de-AT",
    "en": "en-US",
}

_ALLOWED_LANGS = frozenset({"de", "en"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _locale_to_primary_language(locale: str) -> str:
    if locale in _LOCALE_TO_LANG:
        return _LOCALE_TO_LANG[locale]
    prefix = locale.split("-")[0].lower()
    return prefix if prefix in _ALLOWED_LANGS else "de"


def _primary_language_to_locale(lang: str) -> str:
    return _LANG_TO_LOCALE.get(lang, "de-AT")


def _config_path(clinic_id: str) -> Path:
    return _TENANTS_DIR / clinic_id / "clinic_config.json"


def _load_language_config_from_file(clinic_id: str) -> Dict[str, Any]:
    """Return the language_config dict from the tenant JSON config, or {} if absent."""
    path = _config_path(clinic_id)
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw.get("language_config", {})
    except (json.JSONDecodeError, OSError):
        return {}


def _write_language_config_to_file(
    clinic_id: str,
    language_config: Dict[str, Any],
    clinic_name: Optional[str] = None,
) -> None:
    """Write/merge language_config into the tenant JSON config file.

    Creates the file if it does not exist. Preserves all existing keys.
    Never writes PHI, secrets, or Vapi credentials.
    """
    config_dir = _TENANTS_DIR / clinic_id
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "clinic_config.json"

    if config_path.is_file():
        try:
            existing: Dict[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}
    else:
        existing = {}

    existing.setdefault("tenant_id", clinic_id)
    if clinic_name:
        existing.setdefault("clinic_name", clinic_name)

    existing["language_config"] = language_config
    # Keep top-level language/fallback_language in sync for ClinicConfig compatibility
    if "primary_language" in language_config:
        existing["language"] = language_config["primary_language"]
    if "fallback_language" in language_config:
        existing["fallback_language"] = language_config["fallback_language"]

    config_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


async def _get_clinic_row(pool: Any, clinic_id: str) -> Optional[Dict[str, Any]]:
    row = await pool.fetchrow(
        "SELECT id, name, slug, status, locale, updated_at FROM clinics WHERE id = $1",
        clinic_id,
    )
    if row is None:
        return None
    return dict(row)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def get_clinic_language_settings(
    pool: Any,
    clinic_id: str,
) -> Dict[str, Any]:
    """Return language settings for a clinic.

    Derives primary_language from clinics.locale; overlays language_config
    from the tenant JSON config file if present. Falls back to German-first
    defaults for any missing field.

    Raises ClinicNotFoundError if the clinic does not exist.
    """
    clinic = await _get_clinic_row(pool, clinic_id)
    if clinic is None:
        raise ClinicNotFoundError(f"Clinic not found: {clinic_id}")

    locale_lang = _locale_to_primary_language(str(clinic.get("locale", "de-AT")))
    file_cfg = _load_language_config_from_file(clinic_id)

    updated_at_raw = clinic.get("updated_at")
    updated_at = str(updated_at_raw) if updated_at_raw is not None else None

    return {
        "clinic_id": clinic_id,
        "primary_language": file_cfg.get(
            "primary_language",
            GERMAN_FIRST_DEFAULTS["primary_language"] if locale_lang not in _ALLOWED_LANGS else locale_lang,
        ),
        "fallback_language": file_cfg.get(
            "fallback_language", GERMAN_FIRST_DEFAULTS["fallback_language"]
        ),
        "supported_languages": file_cfg.get(
            "supported_languages", list(GERMAN_FIRST_DEFAULTS["supported_languages"])
        ),
        "default_patient_language": file_cfg.get(
            "default_patient_language", locale_lang or GERMAN_FIRST_DEFAULTS["default_patient_language"]
        ),
        "vapi_assistant_language_mode": file_cfg.get(
            "vapi_assistant_language_mode", GERMAN_FIRST_DEFAULTS["vapi_assistant_language_mode"]
        ),
        "clinic_ui_language": file_cfg.get(
            "clinic_ui_language", locale_lang or GERMAN_FIRST_DEFAULTS["clinic_ui_language"]
        ),
        "updated_at": updated_at,
    }


async def update_clinic_language_settings(
    pool: Any,
    clinic_id: str,
    update: Dict[str, Any],
    actor_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Update language settings for a clinic.

    Applies a partial update over the current settings. Updates clinics.locale
    in the database when primary_language changes. Writes the full language_config
    to the tenant JSON config file.

    Raises ClinicNotFoundError if the clinic does not exist.
    Raises LanguageSettingsValidationError if primary_language is not in supported_languages.

    No PHI, no secrets, no Vapi credentials are written anywhere.
    """
    clinic = await _get_clinic_row(pool, clinic_id)
    if clinic is None:
        raise ClinicNotFoundError(f"Clinic not found: {clinic_id}")

    current = await get_clinic_language_settings(pool, clinic_id)

    # Apply partial update — only keys explicitly provided in update dict
    new_settings: Dict[str, Any] = {**current}
    updatable = {
        "primary_language",
        "fallback_language",
        "supported_languages",
        "default_patient_language",
        "vapi_assistant_language_mode",
        "clinic_ui_language",
    }
    for field in updatable:
        if field in update and update[field] is not None:
            new_settings[field] = update[field]

    # Guard: primary_language must be in supported_languages
    if new_settings["primary_language"] not in new_settings["supported_languages"]:
        raise LanguageSettingsValidationError(
            f"primary_language {new_settings['primary_language']!r} must be in "
            f"supported_languages {new_settings['supported_languages']}"
        )

    # Update clinics.locale to reflect primary_language
    new_locale = _primary_language_to_locale(new_settings["primary_language"])
    updated_row = await pool.fetchrow(
        "UPDATE clinics SET locale = $1, updated_at = now() WHERE id = $2 RETURNING updated_at",
        new_locale,
        clinic_id,
    )
    if updated_row is not None:
        new_settings["updated_at"] = str(updated_row["updated_at"])

    # Write language_config to tenant JSON config file
    lang_config_to_write = {
        k: v for k, v in new_settings.items() if k not in {"clinic_id", "updated_at"}
    }
    _write_language_config_to_file(
        clinic_id,
        lang_config_to_write,
        clinic_name=str(clinic.get("name", "")),
    )

    return new_settings
