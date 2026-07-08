"""Add patient_intake_links and patient_intake_submissions tables — PraxisMed Sprint 20 / Module 151.

Revision ID: 0009_patient_intake_links
Revises: 0008_anamnesis_templates
Create Date: 2026-07-08

Demo-only intake link flow. Raw token never stored — only token_hash.
Consent step required before submission.
No patient history writes in this module.
No AI structuring. No diagnosis. No medical advice. No triage scoring.
Synthetic/fake staging only. production_phi_enabled always false.
Production PHI remains NO-GO.
"""

from __future__ import annotations

from alembic import op

revision = "0009_patient_intake_links"
down_revision = "0008_anamnesis_templates"
branch_labels = None
depends_on = None

_EMPTY_JSONB = "'{}'::jsonb"
_EMPTY_ARRAY_JSONB = "'[]'::jsonb"

_LINK_STATUS_VALUES = "('active','submitted','expired','revoked')"
_PURPOSE_VALUES = "('patient_history_collection','phone_history_questions','demo_seed')"
_LANGUAGE_VALUES = "('de','en','ar')"
_SUBMISSION_STATUS_VALUES = "('submitted','review_pending','archived_demo')"


def upgrade() -> None:
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS patient_intake_links (
            id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
            patient_id              UUID        REFERENCES patients(id) ON DELETE SET NULL,
            appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
            template_id             UUID        NOT NULL REFERENCES anamnesis_templates(id) ON DELETE RESTRICT,
            token_hash              TEXT        NOT NULL UNIQUE,
            token_prefix            TEXT        NOT NULL,
            status                  TEXT        NOT NULL DEFAULT 'active',
            purpose                 TEXT        NOT NULL DEFAULT 'patient_history_collection',
            language                TEXT        NOT NULL DEFAULT 'de',
            expires_at              TIMESTAMPTZ NOT NULL,
            max_submissions         INTEGER     NOT NULL DEFAULT 1,
            submission_count        INTEGER     NOT NULL DEFAULT 0,
            synthetic_demo          BOOLEAN     NOT NULL DEFAULT true,
            production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
            created_by_user_id      UUID,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT patient_intake_links_phi_check         CHECK (production_phi_enabled = false),
            CONSTRAINT patient_intake_links_demo_check        CHECK (synthetic_demo = true),
            CONSTRAINT patient_intake_links_status_check      CHECK (status IN {_LINK_STATUS_VALUES}),
            CONSTRAINT patient_intake_links_purpose_check     CHECK (purpose IN {_PURPOSE_VALUES}),
            CONSTRAINT patient_intake_links_language_check    CHECK (language IN {_LANGUAGE_VALUES}),
            CONSTRAINT patient_intake_links_max_sub_check     CHECK (max_submissions >= 1),
            CONSTRAINT patient_intake_links_sub_count_check   CHECK (submission_count >= 0)
        );
    """)

    for col in ["clinic_id", "patient_id", "appointment_request_id", "template_id",
                "status", "language", "expires_at", "created_at"]:
        op.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_patient_intake_links_{col}
                ON patient_intake_links ({col});
        """)

    op.execute(f"""
        CREATE TABLE IF NOT EXISTS patient_intake_submissions (
            id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            intake_link_id          UUID        NOT NULL REFERENCES patient_intake_links(id) ON DELETE CASCADE,
            clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
            patient_id              UUID        REFERENCES patients(id) ON DELETE SET NULL,
            appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
            template_id             UUID        NOT NULL REFERENCES anamnesis_templates(id) ON DELETE RESTRICT,
            consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
            language                TEXT        NOT NULL DEFAULT 'de',
            answers                 JSONB       NOT NULL DEFAULT {_EMPTY_JSONB},
            skipped_questions       JSONB       NOT NULL DEFAULT {_EMPTY_ARRAY_JSONB},
            escalation_matches      JSONB       NOT NULL DEFAULT {_EMPTY_ARRAY_JSONB},
            status                  TEXT        NOT NULL DEFAULT 'submitted',
            synthetic_demo          BOOLEAN     NOT NULL DEFAULT true,
            production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
            submitted_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT patient_intake_submissions_phi_check     CHECK (production_phi_enabled = false),
            CONSTRAINT patient_intake_submissions_demo_check    CHECK (synthetic_demo = true),
            CONSTRAINT patient_intake_submissions_status_check  CHECK (status IN {_SUBMISSION_STATUS_VALUES}),
            CONSTRAINT patient_intake_submissions_language_check CHECK (language IN {_LANGUAGE_VALUES})
        );
    """)

    for col in ["intake_link_id", "clinic_id", "patient_id", "appointment_request_id",
                "template_id", "consent_event_id", "status", "language",
                "submitted_at", "created_at"]:
        op.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_{col}
                ON patient_intake_submissions ({col});
        """)


def downgrade() -> None:
    for col in ["intake_link_id", "clinic_id", "patient_id", "appointment_request_id",
                "template_id", "consent_event_id", "status", "language",
                "submitted_at", "created_at"]:
        op.execute(f"DROP INDEX IF EXISTS idx_patient_intake_submissions_{col};")
    op.execute("DROP TABLE IF EXISTS patient_intake_submissions;")

    for col in ["clinic_id", "patient_id", "appointment_request_id", "template_id",
                "status", "language", "expires_at", "created_at"]:
        op.execute(f"DROP INDEX IF EXISTS idx_patient_intake_links_{col};")
    op.execute("DROP TABLE IF EXISTS patient_intake_links;")
