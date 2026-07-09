"""
Patient Timeline Repository — PraxisMed Sprint 20 / Module 156.

Aggregates patient timeline events from existing tables:
  - appointment_requests
  - patient_intake_submissions
  - consent_events
  - patient_history_structuring_runs
  - patient_history_proposals
  - patient_history_* (7 approved history tables)

All queries are tenant-scoped by clinic_id + patient_id.
No new tables. No writes. No delete. No external calls.
No diagnosis. No medical advice. No triage scoring.
production_phi_enabled always false. Production PHI remains NO-GO.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


class PatientTimelineRepoError(RuntimeError):
    """Base error for patient timeline repo."""


class PatientNotInClinicError(PatientTimelineRepoError):
    """Raised when the patient_id does not belong to the given clinic_id."""


_APPROVED_HISTORY_TABLES = [
    ("patient_history_allergies",       "allergies",       "AllergyIntolerance"),
    ("patient_history_medications",     "medications",     "MedicationStatement"),
    ("patient_history_conditions",      "conditions",      "Condition"),
    ("patient_history_procedures",      "procedures",      "Procedure"),
    ("patient_history_immunizations",   "immunizations",   "Immunization"),
    ("patient_history_family_history",  "family-history",  "FamilyMemberHistory"),
    ("patient_history_social_history",  "social-history",  "Observation"),
]


async def list_patient_appointment_events(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    rows = await pool.fetch(
        """
        SELECT id, clinic_id, patient_id, status, created_at,
               'appointment_request'   AS item_type,
               'appointment_requests'  AS item_source,
               'Appointment request'   AS title
        FROM appointment_requests
        WHERE clinic_id = $1::uuid AND patient_id = $2::uuid
        ORDER BY created_at DESC LIMIT $3
        """,
        clinic_id, patient_id, limit,
    )
    return [dict(r) for r in rows]


async def list_patient_intake_submission_events(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    rows = await pool.fetch(
        """
        SELECT id, clinic_id, patient_id, status, consent_event_id, created_at,
               'intake_submission'              AS item_type,
               'patient_intake_submissions'     AS item_source,
               'Intake questionnaire submitted' AS title
        FROM patient_intake_submissions
        WHERE clinic_id = $1::uuid AND patient_id = $2::uuid
        ORDER BY created_at DESC LIMIT $3
        """,
        clinic_id, patient_id, limit,
    )
    return [dict(r) for r in rows]


async def list_patient_consent_events(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    rows = await pool.fetch(
        """
        SELECT id, clinic_id, patient_id, purpose, channel, granted, created_at,
               'consent_event'   AS item_type,
               'consent_events'  AS item_source,
               'Consent event recorded' AS title
        FROM consent_events
        WHERE clinic_id = $1::uuid AND patient_id = $2::uuid
        ORDER BY created_at DESC LIMIT $3
        """,
        clinic_id, patient_id, limit,
    )
    return [dict(r) for r in rows]


async def list_patient_structuring_run_events(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    rows = await pool.fetch(
        """
        SELECT id, clinic_id, patient_id, status, provider, extraction_mode, created_at,
               'structuring_run'                      AS item_type,
               'patient_history_structuring_runs'     AS item_source,
               'Structuring run completed'            AS title
        FROM patient_history_structuring_runs
        WHERE clinic_id = $1::uuid AND patient_id = $2::uuid
        ORDER BY created_at DESC LIMIT $3
        """,
        clinic_id, patient_id, limit,
    )
    return [dict(r) for r in rows]


async def list_patient_history_proposal_events(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    include_unverified: bool = True,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    if include_unverified:
        where_status = ""
    else:
        where_status = "AND proposal_status != 'unverified'"

    rows = await pool.fetch(
        f"""
        SELECT id, clinic_id, patient_id, proposal_status AS status,
               history_type, fhir_resource_type, consent_event_id,
               staff_review_required, extraction_confidence, created_at,
               'history_proposal'             AS item_type,
               'patient_history_proposals'    AS item_source,
               'Unverified history proposal'  AS title
        FROM patient_history_proposals
        WHERE clinic_id = $1::uuid AND patient_id = $2::uuid
        {where_status}
        ORDER BY created_at DESC LIMIT $3
        """,
        clinic_id, patient_id, limit,
    )
    return [dict(r) for r in rows]


async def list_patient_approved_history_events(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    per_table = max(1, limit // len(_APPROVED_HISTORY_TABLES))

    for table, history_type, fhir_type in _APPROVED_HISTORY_TABLES:
        rows = await pool.fetch(
            f"""
            SELECT id, clinic_id, patient_id, status, source_type, consent_event_id, created_at
            FROM {table}
            WHERE clinic_id = $1::uuid AND patient_id = $2::uuid AND status = 'approved'
            ORDER BY created_at DESC LIMIT $3
            """,
            clinic_id, patient_id, per_table,
        )
        for r in rows:
            d = dict(r)
            d["item_type"] = "approved_history"
            d["item_source"] = table
            d["history_type"] = history_type
            d["fhir_resource_type"] = fhir_type
            d["title"] = f"Approved {history_type.replace('-', ' ')} history"
            results.append(d)

    return results


async def get_last_visit_anchor(
    pool: Any,
    clinic_id: str,
    patient_id: str,
) -> Optional[Dict[str, Any]]:
    row = await pool.fetchrow(
        """
        SELECT id, clinic_id, patient_id, status, created_at,
               'appointment_request'  AS item_type,
               'appointment_requests' AS item_source,
               'Appointment request'  AS title
        FROM appointment_requests
        WHERE clinic_id = $1::uuid AND patient_id = $2::uuid
        ORDER BY created_at DESC LIMIT 1
        """,
        clinic_id, patient_id,
    )
    return dict(row) if row is not None else None


async def list_patient_timeline_events(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    include_unverified: bool = True,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    per_source = max(1, limit // 6)

    appts = await list_patient_appointment_events(pool, clinic_id, patient_id, per_source)
    intakes = await list_patient_intake_submission_events(pool, clinic_id, patient_id, per_source)
    consents = await list_patient_consent_events(pool, clinic_id, patient_id, per_source)
    runs = await list_patient_structuring_run_events(pool, clinic_id, patient_id, per_source)
    proposals = await list_patient_history_proposal_events(
        pool, clinic_id, patient_id, include_unverified=include_unverified, limit=per_source,
    )
    approved = await list_patient_approved_history_events(pool, clinic_id, patient_id, per_source)

    all_items = appts + intakes + consents + runs + proposals + approved
    all_items.sort(key=lambda x: x.get("created_at") or datetime.min, reverse=True)
    return all_items[:limit]


async def list_patient_delta_since(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    since_datetime: datetime,
    include_unverified: bool = True,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    all_items = await list_patient_timeline_events(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
        include_unverified=include_unverified,
        limit=limit * 3,
    )
    delta = [
        item for item in all_items
        if item.get("created_at") is not None
        and item["created_at"] > since_datetime
    ]
    return delta[:limit]
