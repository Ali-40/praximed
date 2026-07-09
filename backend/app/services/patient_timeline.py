"""
Patient Timeline Service — PraxisMed Sprint 20 / Module 156.

Aggregates the longitudinal patient timeline from approved history entries,
unverified proposals, structuring runs, consent events, and intake submissions.
Also provides a delta view showing items changed since the last visit anchor.

No diagnosis generation. No medical advice. No triage scoring.
No treatment recommendations. No external LLM. No PHI unlock.
Approved history is clearly separated from unverified proposals.
production_phi_enabled always False. Synthetic/fake staging only.
Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import patient_timeline_repo as timeline_repo

logger = logging.getLogger(__name__)

_EXTRACTION_NOTE = "Extraction confidence only — not a medical judgment."


class PatientTimelineError(RuntimeError):
    """Base error for patient timeline service."""


class PatientTimelineClinicError(PatientTimelineError):
    """Raised when clinic validation fails."""


class PatientTimelineAccessError(PatientTimelineError):
    """Raised when patient does not belong to the clinic or access is denied."""


def _annotate_item(item: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(item)
    item_type = item.get("item_type", "")
    item["production_phi_enabled"] = False
    item["synthetic_demo"] = True
    item["is_approved_history"] = item_type == "approved_history"
    item["is_unverified_proposal"] = (
        item_type == "history_proposal"
        and item.get("status") == "unverified"
    )
    if "extraction_confidence" in item:
        item["extraction_note"] = _EXTRACTION_NOTE
    return item


def _count_by_type(items: List[Dict[str, Any]], type_key: str) -> int:
    return sum(1 for it in items if it.get("item_type") == type_key)


async def get_patient_timeline(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    include_unverified: bool = True,
    limit: int = 100,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    if not clinic_id or not clinic_id.strip():
        raise PatientTimelineClinicError("clinic_id is required.")
    if not patient_id or not patient_id.strip():
        raise PatientTimelineAccessError("patient_id is required.")

    raw_items = await timeline_repo.list_patient_timeline_events(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
        include_unverified=include_unverified,
        limit=limit,
    )

    items = [_annotate_item(it) for it in raw_items]

    approved_count = sum(1 for it in items if it.get("is_approved_history"))
    unverified_count = sum(1 for it in items if it.get("is_unverified_proposal"))
    consent_count = _count_by_type(items, "consent_event")
    intake_count = _count_by_type(items, "intake_submission")
    appt_count = _count_by_type(items, "appointment_request")
    run_count = _count_by_type(items, "structuring_run")

    return {
        "ok": True,
        "clinic_id": clinic_id,
        "patient_id": patient_id,
        "items": items,
        "total": len(items),
        "approved_history_count": approved_count,
        "unverified_proposal_count": unverified_count,
        "consent_event_count": consent_count,
        "intake_submission_count": intake_count,
        "appointment_count": appt_count,
        "structuring_run_count": run_count,
        "include_unverified": include_unverified,
        "production_phi_enabled": False,
        "extraction_note": _EXTRACTION_NOTE,
    }


async def get_patient_delta_since_last_visit(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    include_unverified: bool = True,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    if not clinic_id or not clinic_id.strip():
        raise PatientTimelineClinicError("clinic_id is required.")
    if not patient_id or not patient_id.strip():
        raise PatientTimelineAccessError("patient_id is required.")

    anchor = await timeline_repo.get_last_visit_anchor(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
    )

    if anchor is None:
        all_items = await timeline_repo.list_patient_timeline_events(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            include_unverified=include_unverified,
            limit=100,
        )
        items = [_annotate_item(it) for it in all_items]
        return {
            "ok": True,
            "clinic_id": clinic_id,
            "patient_id": patient_id,
            "delta_anchor_status": "no_prior_visit_anchor",
            "delta_anchor_at": None,
            "items": items,
            "total": len(items),
            "approved_history_count": sum(1 for it in items if it.get("is_approved_history")),
            "unverified_proposal_count": sum(1 for it in items if it.get("is_unverified_proposal")),
            "includes_unverified_proposals": include_unverified,
            "since": None,
            "production_phi_enabled": False,
            "extraction_note": _EXTRACTION_NOTE,
        }

    anchor_at: datetime = anchor["created_at"]
    delta_items = await timeline_repo.list_patient_delta_since(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
        since_datetime=anchor_at,
        include_unverified=include_unverified,
    )
    items = [_annotate_item(it) for it in delta_items]

    return {
        "ok": True,
        "clinic_id": clinic_id,
        "patient_id": patient_id,
        "delta_anchor_status": "changed_since_last_visit",
        "delta_anchor_at": anchor_at.isoformat() if hasattr(anchor_at, "isoformat") else str(anchor_at),
        "items": items,
        "total": len(items),
        "approved_history_count": sum(1 for it in items if it.get("is_approved_history")),
        "unverified_proposal_count": sum(1 for it in items if it.get("is_unverified_proposal")),
        "includes_unverified_proposals": include_unverified,
        "since": anchor_at.isoformat() if hasattr(anchor_at, "isoformat") else str(anchor_at),
        "production_phi_enabled": False,
        "extraction_note": _EXTRACTION_NOTE,
    }


async def get_patient_delta_since(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    since_datetime: datetime,
    include_unverified: bool = True,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    if not clinic_id or not clinic_id.strip():
        raise PatientTimelineClinicError("clinic_id is required.")
    if not patient_id or not patient_id.strip():
        raise PatientTimelineAccessError("patient_id is required.")

    delta_items = await timeline_repo.list_patient_delta_since(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
        since_datetime=since_datetime,
        include_unverified=include_unverified,
    )
    items = [_annotate_item(it) for it in delta_items]

    return {
        "ok": True,
        "clinic_id": clinic_id,
        "patient_id": patient_id,
        "delta_anchor_status": "changed_since_last_visit",
        "delta_anchor_at": since_datetime.isoformat() if hasattr(since_datetime, "isoformat") else str(since_datetime),
        "items": items,
        "total": len(items),
        "approved_history_count": sum(1 for it in items if it.get("is_approved_history")),
        "unverified_proposal_count": sum(1 for it in items if it.get("is_unverified_proposal")),
        "includes_unverified_proposals": include_unverified,
        "since": since_datetime.isoformat() if hasattr(since_datetime, "isoformat") else str(since_datetime),
        "production_phi_enabled": False,
        "extraction_note": _EXTRACTION_NOTE,
    }
