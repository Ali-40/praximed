"""
Anamnesis Template Repository — PraxisMed Sprint 20 / Module 150.

Async CRUD for anamnesis_templates.
All SQL is parameterised. Tenant-scoped with global (clinic_id IS NULL) support.
No DELETE. Status transitions: draft → active → archived.

No patient answers. No history writes. No AI structuring.
No diagnosis. No medical advice. No triage scoring.
production_phi_enabled always false. Synthetic/fake staging only.
Production PHI remains NO-GO.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


class AnamnesisTemplateRepoError(RuntimeError):
    """Base class for anamnesis template repository errors."""


class AnamnesisTemplateNotFoundError(AnamnesisTemplateRepoError):
    """Raised when a template does not exist."""


class InvalidAnamnesisTemplateError(AnamnesisTemplateRepoError):
    """Raised when required fields are missing or invalid."""


def _row_to_dict(row: Any) -> Dict[str, Any]:
    d = dict(row)
    for key in ("template_schema", "escalation_keywords", "supported_languages"):
        if isinstance(d.get(key), str):
            try:
                d[key] = json.loads(d[key])
            except (ValueError, TypeError):
                pass
    return d


def _assert_nonempty(value: str, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidAnamnesisTemplateError(f"{name!r} must not be empty")


async def create_anamnesis_template(
    pool: Any,
    template_key: str,
    display_name: str,
    specialty: str,
    template_schema: Dict[str, Any],
    clinic_id: Optional[str] = None,
    version: int = 1,
    status: str = "draft",
    primary_language: str = "de",
    supported_languages: Optional[List[str]] = None,
    escalation_keywords: Optional[List[str]] = None,
    consent_purpose: str = "patient_history_collection",
    synthetic_demo: bool = True,
    created_by_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    _assert_nonempty(template_key, "template_key")
    _assert_nonempty(display_name, "display_name")
    _assert_nonempty(specialty, "specialty")
    if "sections" not in template_schema:
        raise InvalidAnamnesisTemplateError("template_schema must contain 'sections'")

    langs = supported_languages or ["de", "en"]
    keywords = escalation_keywords or []

    sql = """
        INSERT INTO anamnesis_templates (
            clinic_id, template_key, display_name, specialty, version,
            status, primary_language, supported_languages, template_schema,
            escalation_keywords, consent_purpose, synthetic_demo,
            production_phi_enabled, created_by_user_id
        ) VALUES (
            $1::uuid, $2, $3, $4, $5,
            $6, $7, $8::jsonb, $9::jsonb,
            $10::jsonb, $11, $12,
            false, $13::uuid
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id,
        template_key,
        display_name,
        specialty,
        version,
        status,
        primary_language,
        json.dumps(langs),
        json.dumps(template_schema),
        json.dumps(keywords),
        consent_purpose,
        synthetic_demo,
        created_by_user_id,
    )
    return _row_to_dict(row)


async def get_anamnesis_template_by_id(
    pool: Any,
    template_id: str,
) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM anamnesis_templates WHERE id = $1::uuid"
    row = await pool.fetchrow(sql, template_id)
    return _row_to_dict(row) if row is not None else None


async def get_anamnesis_template_by_key(
    pool: Any,
    template_key: str,
    clinic_id: Optional[str] = None,
    version: int = 1,
) -> Optional[Dict[str, Any]]:
    if clinic_id is None:
        sql = """
            SELECT * FROM anamnesis_templates
            WHERE template_key = $1 AND version = $2 AND clinic_id IS NULL
        """
        row = await pool.fetchrow(sql, template_key, version)
    else:
        sql = """
            SELECT * FROM anamnesis_templates
            WHERE template_key = $1 AND version = $2
              AND (clinic_id = $3::uuid OR clinic_id IS NULL)
            ORDER BY clinic_id DESC NULLS LAST
            LIMIT 1
        """
        row = await pool.fetchrow(sql, template_key, version, clinic_id)
    return _row_to_dict(row) if row is not None else None


async def list_anamnesis_templates(
    pool: Any,
    clinic_id: Optional[str] = None,
    specialty: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    filters = []
    params: List[Any] = []
    idx = 1

    if clinic_id is not None:
        filters.append(f"(clinic_id = ${idx}::uuid OR clinic_id IS NULL)")
        params.append(clinic_id)
        idx += 1
    else:
        filters.append("clinic_id IS NULL")

    if specialty is not None:
        filters.append(f"specialty = ${idx}")
        params.append(specialty)
        idx += 1

    if status is not None:
        filters.append(f"status = ${idx}")
        params.append(status)
        idx += 1

    where = "WHERE " + " AND ".join(filters) if filters else ""
    params.append(limit)
    sql = f"SELECT * FROM anamnesis_templates {where} ORDER BY created_at DESC LIMIT ${idx}"
    rows = await pool.fetch(sql, *params)
    return [_row_to_dict(r) for r in rows]


async def update_anamnesis_template_status(
    pool: Any,
    template_id: str,
    status: str,
    updated_by_user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE anamnesis_templates
        SET status             = $2,
            updated_by_user_id = $3::uuid,
            updated_at         = now()
        WHERE id = $1::uuid
        RETURNING *
    """
    row = await pool.fetchrow(sql, template_id, status, updated_by_user_id)
    return _row_to_dict(row) if row is not None else None


async def archive_anamnesis_template(
    pool: Any,
    template_id: str,
    updated_by_user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    return await update_anamnesis_template_status(
        pool=pool,
        template_id=template_id,
        status="archived",
        updated_by_user_id=updated_by_user_id,
    )


async def seed_demo_anamnesis_templates(
    pool: Any,
    demo_templates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    results = []
    for t in demo_templates:
        row = await create_anamnesis_template(
            pool=pool,
            template_key=t["template_key"],
            display_name=t["display_name"],
            specialty=t["specialty"],
            template_schema=t["template_schema"],
            clinic_id=t.get("clinic_id"),
            version=t.get("version", 1),
            status=t.get("status", "active"),
            primary_language=t.get("primary_language", "de"),
            supported_languages=t.get("supported_languages", ["de", "en", "ar"]),
            escalation_keywords=t.get("escalation_keywords", []),
            consent_purpose=t.get("consent_purpose", "patient_history_collection"),
            synthetic_demo=True,
            created_by_user_id=t.get("created_by_user_id"),
        )
        results.append(row)
    return results
