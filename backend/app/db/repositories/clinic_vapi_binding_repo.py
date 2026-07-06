"""
Clinic Vapi Binding Repository — PraxisMed Sprint 19 / Module 145.

Async CRUD for clinic_vapi_bindings. All SQL is parameterised.
Secret reference names only — no actual secret values stored or returned.
No VAPI_API_KEY value. No VAPI_WEBHOOK_SECRET value. No PHI. No live Vapi calls.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

_VALID_STATUSES = frozenset({"draft", "configured", "disabled", "revoked"})
_VALID_LANGUAGE_MODES = frozenset({"german_first", "english_first", "bilingual_auto"})


class ClinicVapiBindingRepoError(RuntimeError):
    """Base class for clinic Vapi binding repository errors."""


class InvalidClinicVapiBindingError(ClinicVapiBindingRepoError):
    """Raised when required fields are missing or values are invalid."""


class ClinicVapiBindingNotFoundError(ClinicVapiBindingRepoError):
    """Raised when a requested binding does not exist."""


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _assert_nonempty(value: str, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidClinicVapiBindingError(f"{name!r} must not be empty")


def _assert_valid_enum(value: str, name: str, valid: frozenset) -> None:
    if value not in valid:
        raise InvalidClinicVapiBindingError(
            f"{name!r} must be one of {sorted(valid)!r}; got {value!r}"
        )


async def create_clinic_vapi_binding(
    pool: Any,
    clinic_id: str,
    api_key_secret_ref: str,
    webhook_secret_ref: str,
    language_mode: str = "german_first",
    created_by_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(api_key_secret_ref, "api_key_secret_ref")
    _assert_nonempty(webhook_secret_ref, "webhook_secret_ref")
    _assert_valid_enum(language_mode, "language_mode", _VALID_LANGUAGE_MODES)

    sql = """
        INSERT INTO clinic_vapi_bindings (
            clinic_id, api_key_secret_ref, webhook_secret_ref,
            language_mode, status, created_by_user_id
        ) VALUES (
            $1::uuid, $2, $3,
            $4, 'draft', $5::uuid
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id,
        api_key_secret_ref,
        webhook_secret_ref,
        language_mode,
        created_by_user_id,
    )
    return _row_to_dict(row)


async def get_clinic_vapi_binding_by_id(
    pool: Any,
    binding_id: str,
) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM clinic_vapi_bindings WHERE id = $1::uuid"
    row = await pool.fetchrow(sql, binding_id)
    return _row_to_dict(row) if row is not None else None


async def get_clinic_vapi_binding_by_clinic_id(
    pool: Any,
    clinic_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT * FROM clinic_vapi_bindings
        WHERE clinic_id = $1::uuid
        ORDER BY created_at DESC
        LIMIT 1
    """
    row = await pool.fetchrow(sql, clinic_id)
    return _row_to_dict(row) if row is not None else None


async def list_clinic_vapi_bindings(
    pool: Any,
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if limit < 1 or limit > 200:
        raise InvalidClinicVapiBindingError("limit must be between 1 and 200")

    sql = """
        SELECT * FROM clinic_vapi_bindings
        WHERE ($1::text IS NULL OR status = $1)
        ORDER BY created_at DESC
        LIMIT $2
    """
    rows = await pool.fetch(sql, status, limit)
    return [_row_to_dict(r) for r in rows]


async def update_clinic_vapi_binding_status(
    pool: Any,
    binding_id: str,
    status: str,
) -> Optional[Dict[str, Any]]:
    _assert_valid_enum(status, "status", _VALID_STATUSES)

    sql = """
        UPDATE clinic_vapi_bindings
        SET status     = $1,
            updated_at = now()
        WHERE id = $2::uuid
        RETURNING *
    """
    row = await pool.fetchrow(sql, status, binding_id)
    return _row_to_dict(row) if row is not None else None


async def disable_or_revoke_clinic_vapi_binding(
    pool: Any,
    binding_id: str,
    revoke: bool = False,
) -> Optional[Dict[str, Any]]:
    new_status = "revoked" if revoke else "disabled"
    return await update_clinic_vapi_binding_status(pool, binding_id, new_status)
