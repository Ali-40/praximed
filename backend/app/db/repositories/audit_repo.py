"""
Audit Log Repository — PraxisMed Sprint 4 / Module 42

Provides async read/write operations for the ``audit_log`` table.
All SQL is parameterised ($1, $2, …) — no string interpolation.

Schema column mapping
---------------------
The audit_log table has: id, clinic_id, actor_type, actor_id, action,
resource_type, resource_id, metadata, created_at.

The following function parameters do NOT have dedicated columns and are
folded into the metadata JSONB payload before insert:
  result      → metadata["_result"]
  severity    → metadata["_severity"]
  ip_address  → metadata["_ip_address"]
  user_agent  → metadata["_user_agent"]
  request_id  → metadata["_request_id"]

Callers may also supply arbitrary metadata; these system fields are merged
in and prefixed with "_" to avoid collisions.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class AuditRepoError(RuntimeError):
    """Base class for audit repository errors."""


class InvalidAuditEventError(AuditRepoError):
    """Raised when required fields are missing or values are invalid."""


# ---------------------------------------------------------------------------
# Allowed enum values
# ---------------------------------------------------------------------------

_VALID_ACTOR_TYPES = frozenset({"user", "machine", "system"})
_VALID_RESULTS = frozenset({"success", "failure", "denied"})
_VALID_SEVERITIES = frozenset({"info", "warning", "critical"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _assert_nonempty(value: Any, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidAuditEventError(f"{name!r} must not be empty")


def _assert_valid_enum(value: str, name: str, valid: frozenset) -> None:
    if value not in valid:
        raise InvalidAuditEventError(
            f"{name!r} must be one of {sorted(valid)!r}; got {value!r}"
        )


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _build_metadata_payload(
    metadata: Optional[Dict[str, Any]],
    result: str,
    severity: str,
    ip_address: Optional[str],
    user_agent: Optional[str],
    request_id: Optional[str],
) -> Dict[str, Any]:
    """Merge caller metadata with system fields into a single JSONB dict."""
    payload: Dict[str, Any] = dict(metadata) if metadata else {}
    payload["_result"] = result
    payload["_severity"] = severity
    if ip_address is not None:
        payload["_ip_address"] = ip_address
    if user_agent is not None:
        payload["_user_agent"] = user_agent
    if request_id is not None:
        payload["_request_id"] = request_id
    return payload


# ---------------------------------------------------------------------------
# 1. create_audit_log
# ---------------------------------------------------------------------------


async def create_audit_log(
    pool: Any,
    clinic_id: Optional[str],
    action: str,
    resource_type: str,
    actor_type: str = "system",
    actor_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    result: str = "success",
    severity: str = "info",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(action, "action")
    _assert_nonempty(resource_type, "resource_type")
    _assert_valid_enum(actor_type, "actor_type", _VALID_ACTOR_TYPES)
    _assert_valid_enum(result, "result", _VALID_RESULTS)
    _assert_valid_enum(severity, "severity", _VALID_SEVERITIES)

    if metadata is not None and not isinstance(metadata, dict):
        raise InvalidAuditEventError("'metadata' must be a dict if provided")

    payload = _build_metadata_payload(
        metadata, result, severity, ip_address, user_agent, request_id
    )
    metadata_json = json.dumps(payload)

    sql = """
        INSERT INTO audit_log (
            clinic_id, actor_type, actor_id,
            action, resource_type, resource_id, metadata
        ) VALUES (
            $1, $2, $3,
            $4, $5, $6, $7::jsonb
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id, actor_type, actor_id,
        action, resource_type, resource_id, metadata_json,
    )
    return _row_to_dict(row)


# ---------------------------------------------------------------------------
# 2. get_audit_log_by_id
# ---------------------------------------------------------------------------


async def get_audit_log_by_id(
    pool: Any,
    clinic_id: str,
    audit_log_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT *
        FROM audit_log
        WHERE clinic_id = $1
          AND id        = $2
    """
    row = await pool.fetchrow(sql, clinic_id, audit_log_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 3. list_audit_logs
# ---------------------------------------------------------------------------


async def list_audit_logs(
    pool: Any,
    clinic_id: str,
    actor_type: Optional[str] = None,
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    result: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if limit < 1 or limit > 100:
        raise InvalidAuditEventError("'limit' must be between 1 and 100")

    if actor_type is not None:
        _assert_valid_enum(actor_type, "actor_type", _VALID_ACTOR_TYPES)
    if result is not None:
        _assert_valid_enum(result, "result", _VALID_RESULTS)
    if severity is not None:
        _assert_valid_enum(severity, "severity", _VALID_SEVERITIES)

    conditions = ["clinic_id = $1"]
    params: List[Any] = [clinic_id]
    idx = 2

    if actor_type is not None:
        conditions.append(f"actor_type = ${idx}")
        params.append(actor_type)
        idx += 1
    if actor_id is not None:
        conditions.append(f"actor_id = ${idx}")
        params.append(actor_id)
        idx += 1
    if action is not None:
        conditions.append(f"action = ${idx}")
        params.append(action)
        idx += 1
    if resource_type is not None:
        conditions.append(f"resource_type = ${idx}")
        params.append(resource_type)
        idx += 1
    if resource_id is not None:
        conditions.append(f"resource_id = ${idx}")
        params.append(resource_id)
        idx += 1
    # result and severity live inside metadata JSONB; filter via ->> operator
    if result is not None:
        conditions.append(f"metadata->>'_result' = ${idx}")
        params.append(result)
        idx += 1
    if severity is not None:
        conditions.append(f"metadata->>'_severity' = ${idx}")
        params.append(severity)
        idx += 1

    where_clause = " AND ".join(conditions)
    sql = f"""
        SELECT *
        FROM audit_log
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${idx}
    """
    params.append(limit)

    rows = await pool.fetch(sql, *params)
    return [_row_to_dict(r) for r in rows]
