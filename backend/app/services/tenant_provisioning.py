"""
Tenant Provisioning Service — PraxisMed Sprint 19 / Module 135.

Creates a safe clinic shell from an approved onboarding request.

Safety invariants (enforced by construction):
  - Only provisions when onboarding request status is 'pilot_approved'.
  - Uses the existing clinics table — no new migration required.
  - production_phi_enabled is NOT a column in the clinics table; PHI activation
    is never triggered here and requires a separate, guarded compliance process.
  - No Vapi credentials are accepted, stored, or returned.
  - No patients are created.
  - No doctor passwords are generated automatically.
  - Provisioning event is recorded in audit_log (immutable).
  - Idempotent: returns existing clinic info if already provisioned.
  - Production PHI remains NO-GO.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, Optional

from backend.app.db.repositories import audit_repo, clinic_onboarding_repo


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ProvisioningError(RuntimeError):
    """Base class for provisioning errors."""


class ProvisioningNotFoundError(ProvisioningError):
    """Raised when the referenced onboarding request does not exist."""


class ProvisioningBlockedError(ProvisioningError):
    """Raised when the onboarding request is not in pilot_approved status."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REQUIRED_STATUS = "pilot_approved"

_LANG_TO_LOCALE: Dict[str, str] = {
    "de": "de-AT",
    "en": "en-US",
}

PROVISIONING_MESSAGE = "Clinic shell provisioned. Production PHI remains disabled."


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _locale_from_language(preferred_language: str) -> str:
    return _LANG_TO_LOCALE.get(str(preferred_language).lower(), "de-AT")


def _make_clinic_slug(clinic_name: str) -> str:
    """Derive a URL-safe slug: lowercase clinic name + 8-char UUID suffix."""
    base = re.sub(r"[^a-z0-9]+", "-", str(clinic_name).lower()).strip("-")
    base = (base[:32] or "clinic").strip("-") or "clinic"
    short_id = str(uuid.uuid4()).split("-")[0]  # 8 hex chars
    return f"{base}-{short_id}"


def _parse_supported_languages(raw: Any) -> List[str]:
    """Return supported_languages as a list.

    asyncpg may return JSONB columns as raw JSON strings depending on codec
    configuration — this helper handles array, JSON string, and None.
    """
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
    return ["de", "en"]


async def _find_existing_provisioning(
    pool: Any,
    request_id: str,
) -> Optional[Dict[str, Any]]:
    """Return metadata from a previous successful provisioning event, or None.

    Queries audit_log directly (not via audit_repo.list_audit_logs) because
    we do not know the clinic_id before provisioning completes.
    """
    sql = """
        SELECT metadata
        FROM   audit_log
        WHERE  resource_type             = 'clinic_onboarding_request'
          AND  resource_id               = $1
          AND  action                    = 'create_clinic_shell'
          AND  metadata->>'_result'      = 'success'
        ORDER BY created_at DESC
        LIMIT 1
    """
    row = await pool.fetchrow(sql, request_id)
    if row is None:
        return None
    raw = row["metadata"]
    if isinstance(raw, str):
        return json.loads(raw)
    return dict(raw)


async def _insert_clinic_shell(
    pool: Any,
    name: str,
    slug: str,
    locale: str,
) -> Dict[str, Any]:
    """Insert a new clinic row in pilot_setup state and return the created row.

    The clinics table has no production_phi_enabled column — PHI activation
    state is never stored here. Status 'pilot_setup' signals that this clinic
    is pending full configuration and is not production-ready.
    """
    sql = """
        INSERT INTO clinics (slug, name, status, locale, timezone)
        VALUES ($1, $2, 'pilot_setup', $3, 'Europe/Vienna')
        RETURNING *
    """
    row = await pool.fetchrow(sql, slug, name, locale)
    return dict(row)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def provision_clinic_shell_from_onboarding_request(
    pool: Any,
    request_id: str,
    actor_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a safe clinic shell from a pilot_approved onboarding request.

    Steps:
      1. Load the onboarding request — raise ProvisioningNotFoundError if missing.
      2. Guard: status must be 'pilot_approved' — raise ProvisioningBlockedError otherwise.
      3. Idempotency: if already provisioned, return existing clinic info.
      4. Insert clinic shell (status='pilot_setup') into existing clinics table.
      5. Write immutable audit event to audit_log.
      6. Return safe provisioning result.

    Returned dict keys:
      onboarding_request_id, clinic_id, clinic_name, clinic_slug,
      preferred_language, fallback_language, supported_languages,
      production_phi_enabled (always False), message, already_provisioned.

    Raises:
      ProvisioningNotFoundError  — request does not exist
      ProvisioningBlockedError   — request status is not 'pilot_approved'
    """
    # Step 1 — Load onboarding request
    req = await clinic_onboarding_repo.get_clinic_onboarding_request_by_id(
        pool, request_id
    )
    if req is None:
        raise ProvisioningNotFoundError(
            f"Onboarding request not found: {request_id}"
        )

    # Step 2 — Status guard
    current_status = req.get("status", "")
    if current_status != _REQUIRED_STATUS:
        raise ProvisioningBlockedError(
            f"Provisioning only allowed for pilot_approved requests. "
            f"Current status: {current_status!r}"
        )

    # Step 3 — Idempotency: return existing clinic if already provisioned
    existing = await _find_existing_provisioning(pool, request_id)
    if existing is not None:
        return {
            "onboarding_request_id": request_id,
            "clinic_id":             existing.get("clinic_id"),
            "clinic_name":           existing.get("clinic_name"),
            "clinic_slug":           existing.get("clinic_slug"),
            "preferred_language":    existing.get("preferred_language", "de"),
            "fallback_language":     existing.get("fallback_language", "en"),
            "supported_languages":   existing.get("supported_languages", ["de", "en"]),
            "production_phi_enabled": False,
            "message":               PROVISIONING_MESSAGE,
            "already_provisioned":   True,
        }

    # Step 4 — Build clinic shell parameters
    clinic_name         = req.get("clinic_name", "Unknown Clinic")
    preferred_language  = req.get("preferred_language", "de")
    fallback_language   = req.get("fallback_language", "en")
    supported_languages = _parse_supported_languages(req.get("supported_languages"))

    slug   = _make_clinic_slug(clinic_name)
    locale = _locale_from_language(preferred_language)

    clinic    = await _insert_clinic_shell(pool, clinic_name, slug, locale)
    clinic_id = str(clinic["id"])

    # Step 5 — Write immutable audit event
    audit_metadata: Dict[str, Any] = {
        "clinic_id":              clinic_id,
        "onboarding_request_id":  request_id,
        "clinic_name":            clinic_name,
        "clinic_slug":            slug,
        "preferred_language":     preferred_language,
        "fallback_language":      fallback_language,
        "supported_languages":    supported_languages,
        "production_phi_enabled": False,
        "message":                PROVISIONING_MESSAGE,
    }
    await audit_repo.create_audit_log(
        pool=pool,
        clinic_id=clinic_id,
        action="create_clinic_shell",
        resource_type="clinic_onboarding_request",
        actor_type="user" if actor_user_id else "system",
        actor_id=actor_user_id,
        resource_id=request_id,
        result="success",
        severity="info",
        metadata=audit_metadata,
    )

    # Step 6 — Return safe result (never includes Vapi credentials)
    return {
        "onboarding_request_id": request_id,
        "clinic_id":             clinic_id,
        "clinic_name":           clinic_name,
        "clinic_slug":           slug,
        "preferred_language":    preferred_language,
        "fallback_language":     fallback_language,
        "supported_languages":   supported_languages,
        "production_phi_enabled": False,
        "message":               PROVISIONING_MESSAGE,
        "already_provisioned":   False,
    }
