"""
Anamnesis Template Engine — PraxisMed Sprint 20 / Module 150.

Clinic-configurable questionnaire templates for consent-first patient intake.
Supports de/en/ar labels. Escalation keywords surface to staff without scoring.

No patient answers stored. No patient history writes. No AI structuring.
No diagnosis. No medical advice. No triage scoring. No treatment recommendations.
production_phi_enabled always False. Synthetic/fake staging only.
Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import anamnesis_template_repo
from backend.app.db.repositories.anamnesis_template_repo import (
    AnamnesisTemplateNotFoundError,
    InvalidAnamnesisTemplateError,
)
from backend.app.services.consent_ledger import ClinicNotFoundError

logger = logging.getLogger(__name__)


class AnamnesisTemplateServiceError(RuntimeError):
    """Base error for anamnesis template service."""


class TemplateValidationError(AnamnesisTemplateServiceError):
    """Raised when template data fails service-level validation."""


# ── Demo template definitions ────────────────────────────────────────────────

_DEMO_TEMPLATES: List[Dict[str, Any]] = [
    {
        "template_key": "demo_gp_basic_history",
        "display_name": "GP / Allgemeinmedizin — Kurzanamnese",
        "specialty": "general_practice",
        "primary_language": "de",
        "supported_languages": ["de", "en", "ar"],
        "status": "active",
        "consent_purpose": "patient_history_collection",
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "escalation_keywords": [
            "starke Schmerzen", "Atemnot", "Brustschmerzen",
            "chest pain", "shortness of breath", "severe pain",
        ],
        "template_schema": {
            "sections": [
                {
                    "section_key": "allergies",
                    "title": {
                        "de": "Allergien und Unverträglichkeiten",
                        "en": "Allergies and Intolerances",
                        "ar": "الحساسية وعدم التحمل",
                    },
                    "description": {
                        "de": "Bitte beantworten Sie nur, was Sie teilen möchten.",
                        "en": "Please answer only what you are comfortable sharing.",
                        "ar": "يرجى الإجابة فقط على ما ترغب في مشاركته.",
                    },
                    "questions": [
                        {
                            "question_key": "known_allergies",
                            "history_target": "allergies",
                            "type": "textarea",
                            "label": {
                                "de": "Haben Sie bekannte Allergien?",
                                "en": "Do you have any known allergies?",
                                "ar": "هل لديك أي حساسية معروفة؟",
                            },
                            "help_text": {
                                "de": "Z.B. Penicillin, Nüsse, Latex. Optional.",
                                "en": "E.g. penicillin, nuts, latex. Optional.",
                                "ar": "مثل البنسلين، المكسرات، اللاتكس. اختياري.",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "AllergyIntolerance",
                        }
                    ],
                },
                {
                    "section_key": "medications",
                    "title": {
                        "de": "Aktuelle Medikamente",
                        "en": "Current Medications",
                        "ar": "الأدوية الحالية",
                    },
                    "questions": [
                        {
                            "question_key": "current_medications",
                            "history_target": "medications",
                            "type": "textarea",
                            "label": {
                                "de": "Nehmen Sie aktuell Medikamente ein?",
                                "en": "Are you currently taking any medications?",
                                "ar": "هل تتناول أي أدوية حالياً؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "MedicationStatement",
                        }
                    ],
                },
                {
                    "section_key": "procedures",
                    "title": {
                        "de": "Frühere Eingriffe",
                        "en": "Prior Procedures",
                        "ar": "الإجراءات السابقة",
                    },
                    "questions": [
                        {
                            "question_key": "prior_procedures",
                            "history_target": "procedures",
                            "type": "textarea",
                            "label": {
                                "de": "Hatten Sie frühere Operationen oder Eingriffe?",
                                "en": "Have you had any previous surgeries or procedures?",
                                "ar": "هل خضعت لعمليات جراحية أو إجراءات سابقة؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "Procedure",
                        }
                    ],
                },
                {
                    "section_key": "family_history",
                    "title": {
                        "de": "Familienanamnese",
                        "en": "Family History",
                        "ar": "التاريخ العائلي",
                    },
                    "questions": [
                        {
                            "question_key": "family_conditions",
                            "history_target": "family-history",
                            "type": "textarea",
                            "label": {
                                "de": "Gibt es relevante Erkrankungen in Ihrer Familie?",
                                "en": "Are there any relevant conditions in your family?",
                                "ar": "هل توجد أمراض ذات صلة في عائلتك؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "FamilyMemberHistory",
                        }
                    ],
                },
                {
                    "section_key": "social_history",
                    "title": {
                        "de": "Soziale Anamnese",
                        "en": "Social History",
                        "ar": "التاريخ الاجتماعي",
                    },
                    "questions": [
                        {
                            "question_key": "smoking_status",
                            "history_target": "social-history",
                            "type": "single_select",
                            "label": {
                                "de": "Rauchen Sie?",
                                "en": "Do you smoke?",
                                "ar": "هل تدخن؟",
                            },
                            "options": [
                                {"value": "never", "label_de": "Nein, nie", "label_en": "No, never", "label_ar": "لا، أبداً"},
                                {"value": "former", "label_de": "Früher", "label_en": "Former smoker", "label_ar": "سابقاً"},
                                {"value": "current", "label_de": "Ja", "label_en": "Yes", "label_ar": "نعم"},
                            ],
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "Observation",
                        }
                    ],
                },
            ]
        },
    },
    {
        "template_key": "demo_dermatology_basic_history",
        "display_name": "Dermatologie — Basisanamnese",
        "specialty": "dermatology",
        "primary_language": "de",
        "supported_languages": ["de", "en", "ar"],
        "status": "active",
        "consent_purpose": "patient_history_collection",
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "escalation_keywords": [
            "Infektionszeichen", "starke Schwellung", "Atemnot",
            "signs of infection", "severe swelling", "shortness of breath",
        ],
        "template_schema": {
            "sections": [
                {
                    "section_key": "reason_context",
                    "title": {
                        "de": "Heutiger Anlass",
                        "en": "Reason for Visit",
                        "ar": "سبب الزيارة",
                    },
                    "questions": [
                        {
                            "question_key": "skin_concern",
                            "history_target": "appointment-context",
                            "type": "textarea",
                            "label": {
                                "de": "Was bringt Sie heute in die Praxis?",
                                "en": "What brings you to the practice today?",
                                "ar": "ما الذي أحضرك إلى العيادة اليوم؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "Observation",
                        }
                    ],
                },
                {
                    "section_key": "allergies",
                    "title": {
                        "de": "Allergien",
                        "en": "Allergies",
                        "ar": "الحساسية",
                    },
                    "questions": [
                        {
                            "question_key": "skin_allergies",
                            "history_target": "allergies",
                            "type": "textarea",
                            "label": {
                                "de": "Bekannte Allergien oder Hautreaktionen?",
                                "en": "Known allergies or skin reactions?",
                                "ar": "حساسية معروفة أو تفاعلات جلدية؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "AllergyIntolerance",
                        }
                    ],
                },
                {
                    "section_key": "medications",
                    "title": {
                        "de": "Aktuelle Medikamente",
                        "en": "Current Medications",
                        "ar": "الأدوية الحالية",
                    },
                    "questions": [
                        {
                            "question_key": "current_topical",
                            "history_target": "medications",
                            "type": "textarea",
                            "label": {
                                "de": "Verwenden Sie aktuell Cremes, Salben oder Medikamente?",
                                "en": "Are you currently using any creams, ointments, or medications?",
                                "ar": "هل تستخدم حالياً أي كريمات أو مراهم أو أدوية؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "MedicationStatement",
                        }
                    ],
                },
                {
                    "section_key": "prior_treatments",
                    "title": {
                        "de": "Frühere Behandlungen (selbst berichtet)",
                        "en": "Previous Treatments (patient-reported)",
                        "ar": "العلاجات السابقة (بتقرير المريض)",
                    },
                    "questions": [
                        {
                            "question_key": "prior_skin_treatments",
                            "history_target": "procedures",
                            "type": "textarea",
                            "label": {
                                "de": "Hatten Sie früher Behandlungen für dieses Hautproblem?",
                                "en": "Have you had previous treatments for this skin concern?",
                                "ar": "هل تلقيت علاجات سابقة لهذه المشكلة الجلدية؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "Procedure",
                        }
                    ],
                },
            ]
        },
    },
    {
        "template_key": "demo_pediatrics_since_birth",
        "display_name": "Pädiatrie — Anamnese seit Geburt",
        "specialty": "pediatrics",
        "primary_language": "de",
        "supported_languages": ["de", "en", "ar"],
        "status": "active",
        "consent_purpose": "patient_history_collection",
        "synthetic_demo": True,
        "production_phi_enabled": False,
        "escalation_keywords": [
            "Fieber über 39", "Krampfanfall", "starke Schmerzen",
            "fever over 39", "seizure", "severe pain",
        ],
        "template_schema": {
            "sections": [
                {
                    "section_key": "immunizations",
                    "title": {
                        "de": "Impfungen",
                        "en": "Immunizations",
                        "ar": "التطعيمات",
                    },
                    "questions": [
                        {
                            "question_key": "vaccination_status",
                            "history_target": "immunizations",
                            "type": "textarea",
                            "label": {
                                "de": "Welche Impfungen hat Ihr Kind erhalten?",
                                "en": "Which immunizations has your child received?",
                                "ar": "ما التطعيمات التي تلقاها طفلك؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "Immunization",
                        }
                    ],
                },
                {
                    "section_key": "allergies",
                    "title": {
                        "de": "Allergien",
                        "en": "Allergies",
                        "ar": "الحساسية",
                    },
                    "questions": [
                        {
                            "question_key": "child_allergies",
                            "history_target": "allergies",
                            "type": "textarea",
                            "label": {
                                "de": "Hat Ihr Kind bekannte Allergien?",
                                "en": "Does your child have any known allergies?",
                                "ar": "هل لدى طفلك أي حساسية معروفة؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "AllergyIntolerance",
                        }
                    ],
                },
                {
                    "section_key": "medications",
                    "title": {
                        "de": "Aktuelle Medikamente",
                        "en": "Current Medications",
                        "ar": "الأدوية الحالية",
                    },
                    "questions": [
                        {
                            "question_key": "child_medications",
                            "history_target": "medications",
                            "type": "textarea",
                            "label": {
                                "de": "Nimmt Ihr Kind aktuell Medikamente?",
                                "en": "Is your child currently taking any medications?",
                                "ar": "هل يتناول طفلك أي أدوية حالياً؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "MedicationStatement",
                        }
                    ],
                },
                {
                    "section_key": "family_history",
                    "title": {
                        "de": "Familienanamnese",
                        "en": "Family History",
                        "ar": "التاريخ العائلي",
                    },
                    "questions": [
                        {
                            "question_key": "family_health",
                            "history_target": "family-history",
                            "type": "textarea",
                            "label": {
                                "de": "Gibt es bekannte Erkrankungen in der Familie?",
                                "en": "Are there known conditions in the family?",
                                "ar": "هل توجد أمراض معروفة في الأسرة؟",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "FamilyMemberHistory",
                        }
                    ],
                },
                {
                    "section_key": "milestones_observation",
                    "title": {
                        "de": "Entwicklungsbeobachtungen (nicht-diagnostisch)",
                        "en": "Developmental Observations (non-diagnostic)",
                        "ar": "ملاحظات النمو (غير تشخيصية)",
                    },
                    "questions": [
                        {
                            "question_key": "developmental_notes",
                            "history_target": "social-history",
                            "type": "textarea",
                            "label": {
                                "de": "Gibt es Entwicklungsbeobachtungen, die Sie teilen möchten?",
                                "en": "Are there developmental observations you would like to share?",
                                "ar": "هل توجد ملاحظات حول النمو تودّ مشاركتها؟",
                            },
                            "help_text": {
                                "de": "Nur selbst berichtete Beobachtungen. Kein Scoring.",
                                "en": "Patient-reported observations only. No scoring.",
                                "ar": "ملاحظات بتقرير المريض فقط. لا يوجد تقييم.",
                            },
                            "required": False,
                            "skip_allowed": True,
                            "maps_to_fhir": "Observation",
                        }
                    ],
                },
            ]
        },
    },
]


def get_demo_templates() -> List[Dict[str, Any]]:
    return list(_DEMO_TEMPLATES)


# ── Service functions ────────────────────────────────────────────────────────


async def _verify_clinic_exists(pool: Any, clinic_id: str) -> None:
    row = await pool.fetchrow("SELECT id FROM clinics WHERE id = $1::uuid", clinic_id)
    if row is None:
        raise ClinicNotFoundError(f"Clinic not found: {clinic_id!r}")


async def create_template(
    pool: Any,
    payload: Dict[str, Any],
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    clinic_id = payload.get("clinic_id")
    if clinic_id:
        await _verify_clinic_exists(pool, clinic_id)

    row = await anamnesis_template_repo.create_anamnesis_template(
        pool=pool,
        template_key=payload["template_key"],
        display_name=payload["display_name"],
        specialty=payload["specialty"],
        template_schema=payload["template_schema"],
        clinic_id=clinic_id,
        version=payload.get("version", 1),
        status=payload.get("status", "draft"),
        primary_language=payload.get("primary_language", "de"),
        supported_languages=payload.get("supported_languages", ["de", "en"]),
        escalation_keywords=payload.get("escalation_keywords", []),
        consent_purpose=payload.get("consent_purpose", "patient_history_collection"),
        synthetic_demo=payload.get("synthetic_demo", True),
        created_by_user_id=actor_user.user_id if actor_user else None,
    )
    row["production_phi_enabled"] = False

    logger.info(
        "anamnesis_template_created key=%s specialty=%s actor=%s",
        payload["template_key"],
        payload["specialty"],
        actor_user.user_id if actor_user else "anonymous",
    )
    return row


async def list_templates(
    pool: Any,
    clinic_id: Optional[str] = None,
    specialty: Optional[str] = None,
    status: Optional[str] = None,
    actor_user: Optional[AuthContext] = None,
) -> List[Dict[str, Any]]:
    rows = await anamnesis_template_repo.list_anamnesis_templates(
        pool=pool,
        clinic_id=clinic_id,
        specialty=specialty,
        status=status,
    )
    for row in rows:
        row["production_phi_enabled"] = False
    return rows


async def get_template(
    pool: Any,
    template_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Optional[Dict[str, Any]]:
    row = await anamnesis_template_repo.get_anamnesis_template_by_id(
        pool=pool,
        template_id=template_id,
    )
    if row is not None:
        row["production_phi_enabled"] = False
    return row


async def activate_template(
    pool: Any,
    template_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    row = await anamnesis_template_repo.update_anamnesis_template_status(
        pool=pool,
        template_id=template_id,
        status="active",
        updated_by_user_id=actor_user.user_id if actor_user else None,
    )
    if row is None:
        raise AnamnesisTemplateNotFoundError(f"Template {template_id!r} not found")
    row["production_phi_enabled"] = False

    logger.info(
        "anamnesis_template_activated id=%s actor=%s",
        template_id,
        actor_user.user_id if actor_user else "anonymous",
    )
    return row


async def archive_template(
    pool: Any,
    template_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    row = await anamnesis_template_repo.archive_anamnesis_template(
        pool=pool,
        template_id=template_id,
        updated_by_user_id=actor_user.user_id if actor_user else None,
    )
    if row is None:
        raise AnamnesisTemplateNotFoundError(f"Template {template_id!r} not found")
    row["production_phi_enabled"] = False

    logger.info(
        "anamnesis_template_archived id=%s actor=%s",
        template_id,
        actor_user.user_id if actor_user else "anonymous",
    )
    return row


async def seed_demo_templates(
    pool: Any,
    actor_user: Optional[AuthContext] = None,
) -> List[Dict[str, Any]]:
    rows = await anamnesis_template_repo.seed_demo_anamnesis_templates(
        pool=pool,
        demo_templates=_DEMO_TEMPLATES,
    )
    for row in rows:
        row["production_phi_enabled"] = False

    logger.info(
        "anamnesis_demo_templates_seeded count=%d actor=%s",
        len(rows),
        actor_user.user_id if actor_user else "anonymous",
    )
    return rows
