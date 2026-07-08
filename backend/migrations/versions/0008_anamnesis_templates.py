"""Add anamnesis_templates table — PraxisMed Sprint 20 / Module 150.

Revision ID: 0008_anamnesis_templates
Revises: 0007_patient_history_data_model
Create Date: 2026-07-08

Clinic-configurable questionnaire templates for consent-first patient intake.
Templates are reusable, specialty-specific, and support de/en/ar labels.
Escalation keywords surface to staff without medical scoring.

clinic_id NULL = global/demo template available to all clinics.
clinic_id SET = clinic-specific override.

No patient answers stored here. No history writes. No AI structuring.
No diagnosis. No medical advice. No triage scoring. No treatment recommendations.
Synthetic/fake staging only. production_phi_enabled always false.
Production PHI remains NO-GO.
"""

from __future__ import annotations

from alembic import op

revision = "0008_anamnesis_templates"
down_revision = "0007_patient_history_data_model"
branch_labels = None
depends_on = None

_EMPTY_JSONB = "'{}'::jsonb"
_EMPTY_ARRAY_JSONB = "'[]'::jsonb"
_DEFAULT_LANGUAGES_JSONB = """'["de","en"]'::jsonb"""

_STATUS_VALUES = "('draft','active','archived')"
_LANGUAGE_VALUES = "('de','en','ar')"
_CONSENT_PURPOSE_VALUES = "('patient_history_collection','phone_history_questions','demo_seed')"


def upgrade() -> None:
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS anamnesis_templates (
            id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            clinic_id               UUID        REFERENCES clinics(id) ON DELETE CASCADE,
            template_key            TEXT        NOT NULL,
            display_name            TEXT        NOT NULL,
            specialty               TEXT        NOT NULL,
            version                 INTEGER     NOT NULL DEFAULT 1,
            status                  TEXT        NOT NULL DEFAULT 'draft',
            primary_language        TEXT        NOT NULL DEFAULT 'de',
            supported_languages     JSONB       NOT NULL DEFAULT {_DEFAULT_LANGUAGES_JSONB},
            template_schema         JSONB       NOT NULL DEFAULT {_EMPTY_JSONB},
            escalation_keywords     JSONB       NOT NULL DEFAULT {_EMPTY_ARRAY_JSONB},
            consent_purpose         TEXT        NOT NULL DEFAULT 'patient_history_collection',
            synthetic_demo          BOOLEAN     NOT NULL DEFAULT true,
            production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
            created_by_user_id      UUID,
            updated_by_user_id      UUID,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT anamnesis_templates_phi_check CHECK (production_phi_enabled = false),
            CONSTRAINT anamnesis_templates_status_check CHECK (status IN {_STATUS_VALUES}),
            CONSTRAINT anamnesis_templates_language_check CHECK (primary_language IN {_LANGUAGE_VALUES}),
            CONSTRAINT anamnesis_templates_purpose_check CHECK (consent_purpose IN {_CONSENT_PURPOSE_VALUES}),
            CONSTRAINT anamnesis_templates_version_check CHECK (version >= 1)
        );
    """)

    # Indexes
    for col in ["clinic_id", "template_key", "specialty", "status",
                "primary_language", "synthetic_demo", "created_at"]:
        op.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_anamnesis_templates_{col}
                ON anamnesis_templates ({col});
        """)

    # Partial unique: one version per key for global (clinic_id IS NULL)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uidx_anamnesis_templates_global_key_version
            ON anamnesis_templates (template_key, version)
            WHERE clinic_id IS NULL;
    """)

    # Partial unique: one version per key per clinic
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uidx_anamnesis_templates_clinic_key_version
            ON anamnesis_templates (clinic_id, template_key, version)
            WHERE clinic_id IS NOT NULL;
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uidx_anamnesis_templates_clinic_key_version;")
    op.execute("DROP INDEX IF EXISTS uidx_anamnesis_templates_global_key_version;")
    for col in ["clinic_id", "template_key", "specialty", "status",
                "primary_language", "synthetic_demo", "created_at"]:
        op.execute(f"DROP INDEX IF EXISTS idx_anamnesis_templates_{col};")
    op.execute("DROP TABLE IF EXISTS anamnesis_templates;")
