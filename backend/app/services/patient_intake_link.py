"""
Patient Intake Link Service — PraxisMed Sprint 20 / Module 151.

Demo-only intake link flow. Generates tokenized consent-first questionnaire links.

Raw token returned only once at creation. Token hash stored. Raw token never logged.
Consent event created on submission. Answers stored as synthetic intake submissions only.
Escalation keyword matching for staff flags only — no scoring, no diagnosis.

No patient history writes. No AI structuring. No diagnosis. No medical advice.
No treatment recommendations. No triage scoring.
production_phi_enabled always False. synthetic_demo always True.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import patient_intake_link_repo
from backend.app.db.repositories.patient_intake_link_repo import (
    PatientIntakeLinkNotFoundError,
)
from backend.app.services import intake_token as token_svc

logger = logging.getLogger(__name__)

_INTAKE_URL_BASE = "/intake"
_DEFAULT_TTL_HOURS = 72


class IntakeLinkServiceError(RuntimeError):
    """Base error for intake link service."""


class IntakeLinkNotFoundError(IntakeLinkServiceError):
    """Raised when link not found by token or ID."""


class IntakeLinkExpiredError(IntakeLinkServiceError):
    """Raised when link is expired."""


class IntakeLinkRevokedError(IntakeLinkServiceError):
    """Raised when link has been revoked."""


class IntakeLinkSubmittedError(IntakeLinkServiceError):
    """Raised when link has already reached max submissions."""


class ClinicNotFoundError(IntakeLinkServiceError):
    """Raised when target clinic does not exist."""


class TemplateNotFoundError(IntakeLinkServiceError):
    """Raised when anamnesis template does not exist or is not active."""


async def _verify_clinic_exists(pool: Any, clinic_id: str) -> None:
    row = await pool.fetchrow(
        "SELECT id FROM clinics WHERE id = $1::uuid", clinic_id
    )
    if row is None:
        raise ClinicNotFoundError(f"Clinic not found: {clinic_id!r}")


async def _verify_template_active(pool: Any, template_id: str) -> Dict[str, Any]:
    row = await pool.fetchrow(
        "SELECT * FROM anamnesis_templates WHERE id = $1::uuid", template_id
    )
    if row is None:
        raise TemplateNotFoundError(f"Template not found: {template_id!r}")
    d = dict(row)
    if d.get("status") not in ("active", "draft"):
        raise TemplateNotFoundError(
            f"Template {template_id!r} is not active (status={d.get('status')!r})"
        )
    return d


def _match_escalation_keywords(
    answers: Dict[str, Any],
    keywords: List[str],
) -> List[str]:
    matches: List[str] = []
    answers_text = " ".join(str(v) for v in answers.values()).lower()
    for kw in keywords:
        if kw.lower() in answers_text:
            matches.append(kw)
    return matches


def _is_link_usable(link: Dict[str, Any]) -> None:
    if link.get("status") == "revoked":
        raise IntakeLinkRevokedError("This intake link has been revoked.")
    if link.get("status") == "expired":
        raise IntakeLinkExpiredError("This intake link has expired.")
    if link.get("status") == "submitted":
        raise IntakeLinkSubmittedError("This intake link has already been submitted.")
    expires_at = link.get("expires_at")
    if expires_at is not None:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        now = datetime.now(tz=timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if now > expires_at:
            raise IntakeLinkExpiredError("This intake link has expired.")


async def create_demo_intake_link(
    pool: Any,
    clinic_id: str,
    payload: Dict[str, Any],
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    await _verify_clinic_exists(pool, clinic_id)
    template_id = payload["template_id"]
    await _verify_template_active(pool, template_id)

    raw_token = token_svc.generate_intake_token()
    hashed = token_svc.hash_intake_token(raw_token)
    prefix = token_svc.token_prefix(raw_token)

    expires_at = payload.get("expires_at")
    if expires_at is None:
        expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=_DEFAULT_TTL_HOURS)

    link = await patient_intake_link_repo.create_patient_intake_link(
        pool=pool,
        clinic_id=clinic_id,
        template_id=template_id,
        token_hash=hashed,
        token_prefix=prefix,
        expires_at=expires_at,
        language=payload.get("language", "de"),
        purpose=payload.get("purpose", "patient_history_collection"),
        patient_id=payload.get("patient_id"),
        appointment_request_id=payload.get("appointment_request_id"),
        max_submissions=payload.get("max_submissions", 1),
        synthetic_demo=True,
        created_by_user_id=str(actor_user.user_id) if actor_user else None,
    )
    link["production_phi_enabled"] = False

    intake_url = f"{_INTAKE_URL_BASE}/{raw_token}"

    logger.info(
        "intake_link_created link_id=%s prefix=%s clinic=%s actor=%s",
        link.get("id"),
        prefix,
        clinic_id,
        actor_user.user_id if actor_user else "anonymous",
    )

    return {
        "link": link,
        "intake_url": intake_url,
        "raw_token_shown_once": True,
    }


async def get_public_intake_template(
    pool: Any,
    raw_token: str,
) -> Dict[str, Any]:
    hashed = token_svc.hash_intake_token(raw_token)
    link = await patient_intake_link_repo.get_intake_link_by_token_hash(
        pool=pool, token_hash=hashed
    )
    if link is None:
        raise IntakeLinkNotFoundError("Intake link not found.")
    _is_link_usable(link)

    template_row = await pool.fetchrow(
        "SELECT * FROM anamnesis_templates WHERE id = $1::uuid", link["template_id"]
    )
    if template_row is None:
        raise TemplateNotFoundError("Template for this intake link no longer exists.")

    import json as _json
    template = dict(template_row)
    for key in ("template_schema", "escalation_keywords", "supported_languages"):
        if isinstance(template.get(key), str):
            try:
                template[key] = _json.loads(template[key])
            except (ValueError, TypeError):
                pass

    return {
        "link_id": str(link["id"]),
        "clinic_id": str(link["clinic_id"]),
        "language": link["language"],
        "purpose": link["purpose"],
        "template_key": template.get("template_key"),
        "display_name": template.get("display_name"),
        "specialty": template.get("specialty"),
        "primary_language": template.get("primary_language"),
        "template_schema": template.get("template_schema", {}),
        "escalation_keywords": template.get("escalation_keywords", []),
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "demo_notice": "Demo staging intake only. Do not enter real medical information.",
    }


async def submit_public_intake(
    pool: Any,
    raw_token: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    hashed = token_svc.hash_intake_token(raw_token)
    link = await patient_intake_link_repo.get_intake_link_by_token_hash(
        pool=pool, token_hash=hashed
    )
    if link is None:
        raise IntakeLinkNotFoundError("Intake link not found.")
    _is_link_usable(link)

    language = payload.get("language", link["language"])
    answers = payload.get("answers", {})
    skipped_questions = payload.get("skipped_questions", [])

    template_row = await pool.fetchrow(
        "SELECT escalation_keywords FROM anamnesis_templates WHERE id = $1::uuid",
        link["template_id"],
    )
    import json as _json
    keywords: List[str] = []
    if template_row is not None:
        raw_kw = template_row["escalation_keywords"]
        if isinstance(raw_kw, str):
            try:
                keywords = _json.loads(raw_kw)
            except (ValueError, TypeError):
                keywords = []
        elif isinstance(raw_kw, list):
            keywords = raw_kw

    escalation_matches = _match_escalation_keywords(answers, keywords)

    from backend.app.db.repositories import consent_event_repo
    consent_row = await consent_event_repo.create_consent_event(
        pool=pool,
        clinic_id=str(link["clinic_id"]),
        patient_id=str(link["patient_id"]) if link.get("patient_id") else None,
        appointment_request_id=(
            str(link["appointment_request_id"])
            if link.get("appointment_request_id")
            else None
        ),
        channel="intake_link",
        purpose=link["purpose"],
        scope="anamnesis_intake",
        language=language,
        consent_text_version=payload.get("consent_text_version", "v1"),
        consent_text_snapshot=payload.get(
            "consent_text_snapshot",
            "I understand this is a demo intake and consent to submit synthetic information for testing.",
        ),
        granted=True,
        captured_by_system="intake_link_public",
    )
    consent_event_id = str(consent_row["id"])

    submission = await patient_intake_link_repo.create_intake_submission(
        pool=pool,
        intake_link_id=str(link["id"]),
        clinic_id=str(link["clinic_id"]),
        template_id=str(link["template_id"]),
        consent_event_id=consent_event_id,
        answers=answers,
        skipped_questions=skipped_questions,
        escalation_matches=escalation_matches,
        language=language,
        patient_id=str(link["patient_id"]) if link.get("patient_id") else None,
        appointment_request_id=(
            str(link["appointment_request_id"])
            if link.get("appointment_request_id")
            else None
        ),
        synthetic_demo=True,
    )

    await patient_intake_link_repo.increment_submission_count(
        pool=pool,
        link_id=str(link["id"]),
        max_submissions=link["max_submissions"],
    )

    logger.info(
        "intake_submitted link_id=%s submission_id=%s escalation_matches=%d",
        link.get("id"),
        submission.get("id"),
        len(escalation_matches),
    )

    return {
        "submission_id": str(submission["id"]),
        "consent_event_id": consent_event_id,
        "escalation_matches": escalation_matches,
        "status": "submitted",
        "production_phi_enabled": False,
    }


async def list_clinic_intake_links(
    pool: Any,
    clinic_id: str,
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    return await patient_intake_link_repo.list_intake_links_for_clinic(
        pool=pool, clinic_id=clinic_id, status=status, limit=limit
    )


async def list_clinic_intake_submissions(
    pool: Any,
    clinic_id: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    return await patient_intake_link_repo.list_intake_submissions_for_clinic(
        pool=pool, clinic_id=clinic_id, limit=limit
    )


async def revoke_intake_link(
    pool: Any,
    link_id: str,
    clinic_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Optional[Dict[str, Any]]:
    link = await patient_intake_link_repo.revoke_intake_link(
        pool=pool, link_id=link_id, clinic_id=clinic_id
    )
    if link is None:
        raise IntakeLinkNotFoundError(f"Intake link {link_id!r} not found.")
    logger.info(
        "intake_link_revoked link_id=%s actor=%s",
        link_id,
        actor_user.user_id if actor_user else "anonymous",
    )
    return link
