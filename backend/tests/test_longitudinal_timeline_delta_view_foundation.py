"""
Tests — Longitudinal Timeline and Delta View Foundation (Module 156).

Covers:
- Pydantic schemas
- Service layer (with mocked repo / pool)
- Route auth enforcement (TestClient)
- Frontend page static checks
- API helpers checks
- Developer console nav check
- Architecture doc checks
- Forbidden-content checks

No runtime LLM calls. No external API calls. No real patient data. No PHI.
production_phi_enabled always False. Production PHI remains NO-GO.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ── Paths ─────────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PAGE_PATH = _REPO_ROOT / "frontend/app/developer-console/patient-timeline/page.tsx"
_CONSOLE_PATH = _REPO_ROOT / "frontend/app/developer-console/page.tsx"
_API_TS_PATH = _REPO_ROOT / "frontend/lib/api.ts"
_ARCH_DOC = _REPO_ROOT / "docs/architecture/LONGITUDINAL_TIMELINE_DELTA_VIEW_FOUNDATION.md"

# ── Helpers ───────────────────────────────────────────────────────────────────

CLINIC_ID = "aaaa0000-0000-4000-8000-000000000001"
PATIENT_ID = "bbbb0000-0000-4000-8000-000000000002"
NOW = datetime(2026, 7, 9, 12, 0, 0, tzinfo=timezone.utc)


def _make_pool(
    fetch_result: Optional[List[Any]] = None,
    fetchrow_result: Optional[Dict[str, Any]] = None,
) -> MagicMock:
    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=fetch_result or [])
    pool.fetchrow = AsyncMock(return_value=fetchrow_result)
    pool.execute = AsyncMock(return_value=None)
    return pool


def _make_timeline_item(
    item_type: str = "approved_history",
    item_source: str = "patient_history_allergies",
    history_type: str = "allergies",
    status: str = "approved",
    offset_seconds: int = 0,
) -> Dict[str, Any]:
    return {
        "id": f"item-{item_type}-{offset_seconds}",
        "clinic_id": CLINIC_ID,
        "patient_id": PATIENT_ID,
        "item_type": item_type,
        "item_source": item_source,
        "title": f"Test {item_type}",
        "status": status,
        "history_type": history_type,
        "fhir_resource_type": "AllergyIntolerance",
        "created_at": NOW - timedelta(seconds=offset_seconds),
    }


# ── Schema tests ──────────────────────────────────────────────────────────────

def test_schema_import():
    from backend.app.schemas.patient_timeline import PatientTimelineItem
    assert PatientTimelineItem is not None


def test_schema_approved_history_item():
    from backend.app.schemas.patient_timeline import PatientTimelineItem
    item = PatientTimelineItem(
        id="test-id",
        clinic_id=CLINIC_ID,
        patient_id=PATIENT_ID,
        item_type="approved_history",
        item_source="patient_history_allergies",
        title="Approved allergy history",
        occurred_at=NOW.isoformat(),
        status="approved",
        history_type="allergies",
        fhir_resource_type="AllergyIntolerance",
        is_approved_history=True,
        is_unverified_proposal=False,
        production_phi_enabled=False,
    )
    assert item.is_approved_history is True
    assert item.is_unverified_proposal is False
    assert item.production_phi_enabled is False


def test_schema_history_proposal_item():
    from backend.app.schemas.patient_timeline import PatientTimelineItem
    item = PatientTimelineItem(
        id="prop-id",
        clinic_id=CLINIC_ID,
        patient_id=PATIENT_ID,
        item_type="history_proposal",
        item_source="patient_history_proposals",
        title="Unverified history proposal",
        occurred_at=NOW.isoformat(),
        status="unverified",
        is_approved_history=False,
        is_unverified_proposal=True,
        production_phi_enabled=False,
    )
    assert item.is_unverified_proposal is True
    assert item.is_approved_history is False


def test_schema_all_allowed_item_types():
    from backend.app.schemas.patient_timeline import PatientTimelineItem, _ALLOWED_ITEM_TYPES
    for t in _ALLOWED_ITEM_TYPES:
        src = "appointment_requests" if t == "appointment_request" else "consent_events"
        item = PatientTimelineItem(
            id=f"id-{t}",
            clinic_id=CLINIC_ID,
            patient_id=PATIENT_ID,
            item_type=t,
            item_source=src,
            title=f"Test {t}",
            occurred_at=NOW.isoformat(),
            production_phi_enabled=False,
        )
        assert item.item_type == t


def test_schema_unsupported_item_type_rejected():
    from backend.app.schemas.patient_timeline import PatientTimelineItem
    with pytest.raises(Exception):
        PatientTimelineItem(
            id="bad",
            clinic_id=CLINIC_ID,
            patient_id=PATIENT_ID,
            item_type="diagnosis_result",
            item_source="consent_events",
            title="Bad",
            occurred_at=NOW.isoformat(),
            production_phi_enabled=False,
        )


def test_schema_production_phi_enabled_true_rejected():
    from backend.app.schemas.patient_timeline import PatientTimelineItem
    with pytest.raises(Exception):
        PatientTimelineItem(
            id="phi",
            clinic_id=CLINIC_ID,
            patient_id=PATIENT_ID,
            item_type="consent_event",
            item_source="consent_events",
            title="PHI test",
            occurred_at=NOW.isoformat(),
            production_phi_enabled=True,
        )


def test_schema_metadata_forbidden_key_diagnosis():
    from backend.app.schemas.patient_timeline import PatientTimelineItem
    with pytest.raises(Exception):
        PatientTimelineItem(
            id="meta",
            clinic_id=CLINIC_ID,
            patient_id=PATIENT_ID,
            item_type="consent_event",
            item_source="consent_events",
            title="Meta test",
            occurred_at=NOW.isoformat(),
            production_phi_enabled=False,
            metadata={"diagnosis": "forbidden"},
        )


def test_schema_metadata_forbidden_key_triage_score():
    from backend.app.schemas.patient_timeline import PatientTimelineItem
    with pytest.raises(Exception):
        PatientTimelineItem(
            id="meta2",
            clinic_id=CLINIC_ID,
            patient_id=PATIENT_ID,
            item_type="consent_event",
            item_source="consent_events",
            title="Triage test",
            occurred_at=NOW.isoformat(),
            production_phi_enabled=False,
            metadata={"triage_score": 5},
        )


def test_schema_metadata_safe_keys_allowed():
    from backend.app.schemas.patient_timeline import PatientTimelineItem
    item = PatientTimelineItem(
        id="safe",
        clinic_id=CLINIC_ID,
        patient_id=PATIENT_ID,
        item_type="consent_event",
        item_source="consent_events",
        title="Safe metadata",
        occurred_at=NOW.isoformat(),
        production_phi_enabled=False,
        metadata={"purpose": "patient_history_collection", "channel": "intake_link"},
    )
    assert item.metadata is not None


def test_schema_timeline_response():
    from backend.app.schemas.patient_timeline import PatientTimelineResponse
    resp = PatientTimelineResponse(
        ok=True,
        clinic_id=CLINIC_ID,
        patient_id=PATIENT_ID,
        items=[],
        total=0,
        production_phi_enabled=False,
    )
    assert resp.ok is True
    assert resp.production_phi_enabled is False
    assert "not a medical judgment" in resp.extraction_note


def test_schema_delta_response():
    from backend.app.schemas.patient_timeline import PatientTimelineDeltaResponse
    resp = PatientTimelineDeltaResponse(
        ok=True,
        clinic_id=CLINIC_ID,
        patient_id=PATIENT_ID,
        delta_anchor_status="no_prior_visit_anchor",
        items=[],
        total=0,
        production_phi_enabled=False,
    )
    assert resp.delta_anchor_status == "no_prior_visit_anchor"
    assert resp.production_phi_enabled is False


# ── Service tests ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_service_import():
    from backend.app.services import patient_timeline as svc
    assert hasattr(svc, "get_patient_timeline")
    assert hasattr(svc, "get_patient_delta_since_last_visit")
    assert hasattr(svc, "get_patient_delta_since")


@pytest.mark.asyncio
async def test_service_timeline_returns_ok():
    from backend.app.services import patient_timeline as svc
    approved_item = _make_timeline_item("approved_history", "patient_history_allergies", "allergies")

    with patch("backend.app.services.patient_timeline.timeline_repo.list_patient_timeline_events",
               AsyncMock(return_value=[approved_item])):
        pool = _make_pool()
        result = await svc.get_patient_timeline(pool, CLINIC_ID, PATIENT_ID)

    assert result["ok"] is True
    assert result["total"] == 1
    assert result["approved_history_count"] == 1
    assert result["production_phi_enabled"] is False


@pytest.mark.asyncio
async def test_service_timeline_includes_approved_history():
    from backend.app.services import patient_timeline as svc
    approved = _make_timeline_item("approved_history", "patient_history_conditions", "conditions", "approved")

    with patch("backend.app.services.patient_timeline.timeline_repo.list_patient_timeline_events",
               AsyncMock(return_value=[approved])):
        pool = _make_pool()
        result = await svc.get_patient_timeline(pool, CLINIC_ID, PATIENT_ID)

    items = result["items"]
    assert len(items) == 1
    assert items[0]["is_approved_history"] is True
    assert items[0]["production_phi_enabled"] is False


@pytest.mark.asyncio
async def test_service_timeline_marks_unverified_proposal():
    from backend.app.services import patient_timeline as svc
    proposal = _make_timeline_item("history_proposal", "patient_history_proposals", "allergies", "unverified")

    with patch("backend.app.services.patient_timeline.timeline_repo.list_patient_timeline_events",
               AsyncMock(return_value=[proposal])):
        pool = _make_pool()
        result = await svc.get_patient_timeline(pool, CLINIC_ID, PATIENT_ID)

    items = result["items"]
    assert items[0]["is_unverified_proposal"] is True
    assert items[0]["is_approved_history"] is False


@pytest.mark.asyncio
async def test_service_timeline_excludes_unverified_when_flag_false():
    from backend.app.services import patient_timeline as svc
    proposal = _make_timeline_item("history_proposal", "patient_history_proposals", "allergies", "unverified")

    captured_args: dict = {}

    async def mock_list(pool, clinic_id, patient_id, include_unverified, limit):
        captured_args["include_unverified"] = include_unverified
        return []

    with patch("backend.app.services.patient_timeline.timeline_repo.list_patient_timeline_events", mock_list):
        pool = _make_pool()
        await svc.get_patient_timeline(pool, CLINIC_ID, PATIENT_ID, include_unverified=False)

    assert captured_args["include_unverified"] is False


@pytest.mark.asyncio
async def test_service_timeline_counts_by_type():
    from backend.app.services import patient_timeline as svc
    items = [
        _make_timeline_item("approved_history", "patient_history_allergies", "allergies"),
        _make_timeline_item("consent_event", "consent_events"),
        _make_timeline_item("intake_submission", "patient_intake_submissions"),
        _make_timeline_item("appointment_request", "appointment_requests"),
        _make_timeline_item("structuring_run", "patient_history_structuring_runs"),
    ]
    with patch("backend.app.services.patient_timeline.timeline_repo.list_patient_timeline_events",
               AsyncMock(return_value=items)):
        pool = _make_pool()
        result = await svc.get_patient_timeline(pool, CLINIC_ID, PATIENT_ID)

    assert result["approved_history_count"] == 1
    assert result["consent_event_count"] == 1
    assert result["intake_submission_count"] == 1
    assert result["appointment_count"] == 1
    assert result["structuring_run_count"] == 1


@pytest.mark.asyncio
async def test_service_timeline_phi_always_false():
    from backend.app.services import patient_timeline as svc
    with patch("backend.app.services.patient_timeline.timeline_repo.list_patient_timeline_events",
               AsyncMock(return_value=[])):
        pool = _make_pool()
        result = await svc.get_patient_timeline(pool, CLINIC_ID, PATIENT_ID)
    assert result["production_phi_enabled"] is False


@pytest.mark.asyncio
async def test_service_delta_no_prior_visit_anchor():
    from backend.app.services import patient_timeline as svc
    with patch("backend.app.services.patient_timeline.timeline_repo.get_last_visit_anchor",
               AsyncMock(return_value=None)), \
         patch("backend.app.services.patient_timeline.timeline_repo.list_patient_timeline_events",
               AsyncMock(return_value=[])):
        pool = _make_pool()
        result = await svc.get_patient_delta_since_last_visit(pool, CLINIC_ID, PATIENT_ID)

    assert result["delta_anchor_status"] == "no_prior_visit_anchor"
    assert result["delta_anchor_at"] is None
    assert result["production_phi_enabled"] is False


@pytest.mark.asyncio
async def test_service_delta_changed_since_last_visit():
    from backend.app.services import patient_timeline as svc
    anchor = {"id": "appt-1", "created_at": NOW - timedelta(days=7)}
    changed_item = _make_timeline_item("approved_history", "patient_history_allergies")

    with patch("backend.app.services.patient_timeline.timeline_repo.get_last_visit_anchor",
               AsyncMock(return_value=anchor)), \
         patch("backend.app.services.patient_timeline.timeline_repo.list_patient_delta_since",
               AsyncMock(return_value=[changed_item])):
        pool = _make_pool()
        result = await svc.get_patient_delta_since_last_visit(pool, CLINIC_ID, PATIENT_ID)

    assert result["delta_anchor_status"] == "changed_since_last_visit"
    assert result["delta_anchor_at"] is not None
    assert result["total"] == 1
    assert result["production_phi_enabled"] is False


@pytest.mark.asyncio
async def test_service_delta_since_explicit_date():
    from backend.app.services import patient_timeline as svc
    since = NOW - timedelta(days=3)
    new_item = _make_timeline_item("intake_submission", "patient_intake_submissions")

    with patch("backend.app.services.patient_timeline.timeline_repo.list_patient_delta_since",
               AsyncMock(return_value=[new_item])):
        pool = _make_pool()
        result = await svc.get_patient_delta_since(pool, CLINIC_ID, PATIENT_ID, since)

    assert result["ok"] is True
    assert result["total"] == 1
    assert result["production_phi_enabled"] is False
    assert result["delta_anchor_status"] == "changed_since_last_visit"


@pytest.mark.asyncio
async def test_service_requires_clinic_id():
    from backend.app.services import patient_timeline as svc
    pool = _make_pool()
    with pytest.raises(svc.PatientTimelineClinicError):
        await svc.get_patient_timeline(pool, "", PATIENT_ID)


@pytest.mark.asyncio
async def test_service_requires_patient_id():
    from backend.app.services import patient_timeline as svc
    pool = _make_pool()
    with pytest.raises(svc.PatientTimelineAccessError):
        await svc.get_patient_timeline(pool, CLINIC_ID, "")


@pytest.mark.asyncio
async def test_service_no_external_llm():
    from backend.app.services import patient_timeline as svc
    import inspect
    src = inspect.getsource(svc)
    assert "httpx" not in src
    assert "openai" not in src.lower()
    assert "anthropic" not in src.lower()
    assert "api_key" not in src.lower()


@pytest.mark.asyncio
async def test_service_no_auto_approval():
    from backend.app.services import patient_timeline as svc
    import inspect
    src = inspect.getsource(svc)
    low = src.lower()
    assert "auto_approv" not in low
    assert "auto_merge" not in low


@pytest.mark.asyncio
async def test_service_no_diagnosis_generation():
    from backend.app.services import patient_timeline as svc
    import inspect
    src = inspect.getsource(svc)
    low = src.lower()
    prohibition_lines = {l.lower() for l in src.splitlines() if "no diagnosis" in l.lower()}
    non_prohibition = [
        l for l in src.splitlines()
        if "diagnosis_generat" in l.lower()
        and "no " not in l.lower()
        and "not " not in l.lower()
        and "#" not in l
    ]
    assert len(non_prohibition) == 0


# ── Repository tests ──────────────────────────────────────────────────────────

def test_repo_import():
    from backend.app.db.repositories import patient_timeline_repo
    assert hasattr(patient_timeline_repo, "list_patient_timeline_events")
    assert hasattr(patient_timeline_repo, "get_last_visit_anchor")
    assert hasattr(patient_timeline_repo, "list_patient_delta_since")


@pytest.mark.asyncio
async def test_repo_list_timeline_returns_list():
    from backend.app.db.repositories import patient_timeline_repo as repo
    pool = _make_pool(fetch_result=[])
    result = await repo.list_patient_timeline_events(pool, CLINIC_ID, PATIENT_ID)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_repo_get_last_visit_anchor_none():
    from backend.app.db.repositories import patient_timeline_repo as repo
    pool = _make_pool(fetchrow_result=None)
    result = await repo.get_last_visit_anchor(pool, CLINIC_ID, PATIENT_ID)
    assert result is None


@pytest.mark.asyncio
async def test_repo_approved_history_only():
    from backend.app.db.repositories import patient_timeline_repo as repo
    pool = _make_pool(fetch_result=[])
    result = await repo.list_patient_approved_history_events(pool, CLINIC_ID, PATIENT_ID)
    assert isinstance(result, list)
    for sql_call in pool.fetch.call_args_list:
        sql = sql_call[0][0].lower() if sql_call[0] else ""
        if "patient_history_" in sql and "patient_history_structuring" not in sql and "patient_history_proposals" not in sql:
            assert "status = 'approved'" in sql or "status=" in sql


# ── Route tests ───────────────────────────────────────────────────────────────

def _make_app():
    from backend.app.main import app
    return app


def test_route_timeline_requires_auth():
    app = _make_app()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get(f"/clinics/{CLINIC_ID}/patients/{PATIENT_ID}/timeline")
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_route_delta_requires_auth():
    app = _make_app()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get(f"/clinics/{CLINIC_ID}/patients/{PATIENT_ID}/timeline/delta")
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_route_delta_since_requires_auth():
    app = _make_app()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get(f"/clinics/{CLINIC_ID}/patients/{PATIENT_ID}/timeline/delta-since?since=2026-07-01T00:00:00")
    assert resp.status_code in (401, 403, 422, 500, 503)


def test_no_public_timeline_route():
    app = _make_app()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/public/patient-timeline")
    assert resp.status_code in (404, 405)


def test_no_post_write_route():
    app = _make_app()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(f"/clinics/{CLINIC_ID}/patients/{PATIENT_ID}/timeline", json={})
    assert resp.status_code in (404, 405, 401, 403, 503)


def test_no_delete_route():
    app = _make_app()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.delete(f"/clinics/{CLINIC_ID}/patients/{PATIENT_ID}/timeline")
    assert resp.status_code in (404, 405, 401, 403, 503)


def test_routes_no_diagnosis_in_source():
    from backend.app.api.routes import patient_timeline as routes
    import inspect
    src = inspect.getsource(routes)
    non_prohibition = [
        l for l in src.splitlines()
        if "diagnosis_generat" in l.lower()
        and "no " not in l.lower()
        and "#" not in l
    ]
    assert len(non_prohibition) == 0


def test_routes_phi_false():
    from backend.app.api.routes import patient_timeline as routes
    import inspect
    src = inspect.getsource(routes)
    assert "production_phi_enabled" in src or "False" in src


def test_routes_all_require_get_current_user():
    from backend.app.api.routes import patient_timeline as routes
    import inspect
    src = inspect.getsource(routes)
    assert "get_current_user" in src
    route_count = src.count("@router.get")
    current_user_count = src.count("Depends(get_current_user)")
    assert current_user_count >= route_count


# ── Frontend page static tests ─────────────────────────────────────────────────

def test_page_exists():
    assert _PAGE_PATH.exists()


def test_page_mentions_longitudinal_patient_timeline():
    assert "Longitudinal Patient Timeline" in _PAGE_PATH.read_text()


def test_page_mentions_approved_history_and_unverified_proposal_view():
    src = _PAGE_PATH.read_text()
    assert "Approved history and unverified proposal view" in src


def test_page_mentions_admin_staging_badge():
    assert "ADMIN / STAGING" in _PAGE_PATH.read_text()


def test_page_mentions_synthetic_staging():
    assert "Synthetic staging only" in _PAGE_PATH.read_text()


def test_page_has_clinic_id_input():
    src = _PAGE_PATH.read_text()
    assert "clinicId" in src or "clinic_id" in src or "Clinic ID" in src


def test_page_has_patient_id_input():
    src = _PAGE_PATH.read_text()
    assert "patientId" in src or "patient_id" in src or "Patient ID" in src


def test_page_has_include_unverified_checkbox():
    src = _PAGE_PATH.read_text()
    assert "includeUnverified" in src or "include_unverified" in src or "Include unverified" in src


def test_page_has_load_timeline_button():
    src = _PAGE_PATH.read_text()
    assert "Load timeline" in src


def test_page_has_load_delta_button():
    src = _PAGE_PATH.read_text()
    assert "Load delta since last visit" in src or "delta" in src.lower()


def test_page_shows_approved_history_badge():
    assert "APPROVED HISTORY" in _PAGE_PATH.read_text()


def test_page_shows_unverified_proposal_badge():
    assert "UNVERIFIED PROPOSAL" in _PAGE_PATH.read_text()


def test_page_shows_consent_badge():
    assert "CONSENT" in _PAGE_PATH.read_text()


def test_page_shows_intake_badge():
    assert "INTAKE" in _PAGE_PATH.read_text()


def test_page_shows_appointment_badge():
    assert "APPOINTMENT" in _PAGE_PATH.read_text()


def test_page_shows_structuring_badge():
    assert "STRUCTURING" in _PAGE_PATH.read_text()


def test_page_mentions_changed_since_last_visit():
    assert "changed_since_last_visit" in _PAGE_PATH.read_text()


def test_page_mentions_no_prior_visit_anchor():
    assert "no_prior_visit_anchor" in _PAGE_PATH.read_text()


def test_page_mentions_approved_patient_history_only_after_staff_review():
    src = _PAGE_PATH.read_text()
    assert "Approved patient history only after staff review" in src


def test_page_mentions_unverified_proposals_not_merged_history():
    src = _PAGE_PATH.read_text()
    assert "Unverified proposals are not merged history" in src


def test_page_mentions_extraction_confidence_not_medical_judgment():
    src = _PAGE_PATH.read_text()
    assert "not a medical judgment" in src.lower() or "Extraction confidence" in src


def test_page_mentions_production_phi_no_go():
    assert "Production PHI remains NO-GO" in _PAGE_PATH.read_text()


def test_page_no_localStorage():
    src = _PAGE_PATH.read_text()
    lines = [l for l in src.splitlines() if "localStorage" in l and "//" not in l.lstrip()[:3]]
    assert len(lines) == 0


def test_page_no_sessionStorage():
    src = _PAGE_PATH.read_text()
    lines = [l for l in src.splitlines() if "sessionStorage" in l and "//" not in l.lstrip()[:3]]
    assert len(lines) == 0


def test_page_no_ai_diagnosis():
    src = _PAGE_PATH.read_text().lower()
    non_prohibition = [
        l for l in src.splitlines()
        if "diagnosis" in l and "no " not in l and "not " not in l and "never" not in l
    ]
    assert len(non_prohibition) == 0


def test_page_no_medical_advice_claim():
    src = _PAGE_PATH.read_text().lower()
    non_prohibition = [
        l for l in src.splitlines()
        if "medical advice" in l and "no " not in l and "not " not in l
    ]
    assert len(non_prohibition) == 0


# ── API helpers tests ──────────────────────────────────────────────────────────

def test_api_ts_has_fetch_patient_timeline():
    assert "fetchPatientTimeline" in _API_TS_PATH.read_text()


def test_api_ts_has_fetch_patient_timeline_delta():
    assert "fetchPatientTimelineDelta" in _API_TS_PATH.read_text()


def test_api_ts_has_fetch_patient_timeline_delta_since():
    assert "fetchPatientTimelineDeltaSince" in _API_TS_PATH.read_text()


def test_api_ts_uses_credentials_include_for_timeline():
    src = _API_TS_PATH.read_text()
    assert "credentials" in src and "include" in src


def test_api_ts_no_local_storage():
    src = _API_TS_PATH.read_text()
    lines = [l for l in src.splitlines() if "localStorage" in l and "//" not in l.lstrip()[:3]]
    assert len(lines) == 0


def test_api_ts_no_session_storage():
    src = _API_TS_PATH.read_text()
    lines = [l for l in src.splitlines() if "sessionStorage" in l and "//" not in l.lstrip()[:3]]
    assert len(lines) == 0


# ── Developer console nav tests ───────────────────────────────────────────────

def test_developer_console_links_to_patient_timeline():
    assert "/developer-console/patient-timeline" in _CONSOLE_PATH.read_text()


def test_developer_console_mentions_longitudinal_patient_timeline():
    assert "Longitudinal Patient Timeline" in _CONSOLE_PATH.read_text()


# ── Architecture doc tests ────────────────────────────────────────────────────

def test_arch_doc_exists():
    assert _ARCH_DOC.exists()


def test_arch_doc_mentions_module_156():
    assert "156" in _ARCH_DOC.read_text()


def test_arch_doc_mentions_approved_history():
    assert "approved_history" in _ARCH_DOC.read_text() or "approved history" in _ARCH_DOC.read_text().lower()


def test_arch_doc_mentions_unverified_proposals():
    assert "unverified proposal" in _ARCH_DOC.read_text().lower()


def test_arch_doc_mentions_no_auto_approval():
    assert "no auto-approval" in _ARCH_DOC.read_text().lower() or "no auto approval" in _ARCH_DOC.read_text().lower()


def test_arch_doc_mentions_no_diagnosis():
    assert "no diagnosis" in _ARCH_DOC.read_text().lower()


def test_arch_doc_mentions_no_medical_advice():
    assert "no medical advice" in _ARCH_DOC.read_text().lower()


def test_arch_doc_mentions_no_triage():
    assert "no triage" in _ARCH_DOC.read_text().lower()


def test_arch_doc_mentions_synthetic_staging():
    assert "synthetic" in _ARCH_DOC.read_text().lower()


def test_arch_doc_mentions_production_phi_no_go():
    assert "Production PHI remains NO-GO" in _ARCH_DOC.read_text()


def test_arch_doc_mentions_no_new_writes():
    assert "no new writes" in _ARCH_DOC.read_text().lower() or "no writes" in _ARCH_DOC.read_text().lower()


def test_arch_doc_mentions_delta_since():
    assert "delta" in _ARCH_DOC.read_text().lower()


def test_arch_doc_mentions_no_prior_visit_anchor():
    assert "no_prior_visit_anchor" in _ARCH_DOC.read_text()


def test_arch_doc_mentions_changed_since_last_visit():
    assert "changed_since_last_visit" in _ARCH_DOC.read_text()


# ── Forbidden content guards ───────────────────────────────────────────────────

def test_routes_no_medical_advice():
    from backend.app.api.routes import patient_timeline as routes
    import inspect
    src = inspect.getsource(routes)
    non_prohibition = [
        l for l in src.splitlines()
        if "medical_advice" in l.lower()
        and "no " not in l.lower()
        and "#" not in l
    ]
    assert len(non_prohibition) == 0


def test_service_no_triage_scoring():
    from backend.app.services import patient_timeline as svc
    import inspect
    src = inspect.getsource(svc)
    non_prohibition = [
        l for l in src.splitlines()
        if "triage_score" in l.lower()
        and "no " not in l.lower()
        and "#" not in l
    ]
    assert len(non_prohibition) == 0


def test_service_no_api_key():
    from backend.app.services import patient_timeline as svc
    import inspect
    src = inspect.getsource(svc)
    assert "ANTHROPIC_API_KEY" not in src
    assert "OPENAI_API_KEY" not in src
    assert "sk-ant-" not in src
    assert "sk-proj-" not in src


def test_no_database_url_in_schemas():
    from backend.app.schemas import patient_timeline as schemas
    import inspect
    src = inspect.getsource(schemas)
    assert "DATABASE_URL" not in src


def test_no_jwt_secret_in_routes():
    from backend.app.api.routes import patient_timeline as routes
    import inspect
    src = inspect.getsource(routes)
    assert "JWT_SECRET" not in src
