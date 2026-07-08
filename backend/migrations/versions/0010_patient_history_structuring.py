"""Add patient_history_structuring_runs and patient_history_proposals tables — PraxisMed Sprint 20 / Module 153.

Revision ID: 0010_patient_history_structuring
Revises: 0009_patient_intake_links
Create Date: 2026-07-09

Intermediate proposal layer between intake submissions and approved history entries.
Local deterministic demo extraction only — no external LLM, no API keys.
All proposals remain unverified until staff/doctor explicit approval (future module).

No patient_history_* writes in this module. No diagnosis. No medical advice.
No treatment recommendations. No triage scoring. No clinical confidence.
synthetic_demo always true. production_phi_enabled always false.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

from alembic import op

revision = "0010_patient_history_structuring"
down_revision = "0009_patient_intake_links"
branch_labels = None
depends_on = None

_EMPTY_JSONB = "'{}'::jsonb"

_PROVIDER_VALUES = "('local_demo_extractor','claude_haiku_planned','disabled_external_llm')"
_RUN_STATUS_VALUES = "('completed','failed','skipped')"
_LANGUAGE_VALUES = "('de','en','ar')"
_EXTRACTION_MODE_VALUES = "('synthetic_demo','rule_based','external_llm_disabled')"

_PROPOSAL_STATUS_VALUES = "('unverified','rejected','merged','archived_demo')"
_HISTORY_TYPE_VALUES = "('allergies','medications','conditions','procedures','immunizations','family-history','social-history')"
_FHIR_TYPE_VALUES = "('AllergyIntolerance','MedicationStatement','Condition','Procedure','Immunization','FamilyMemberHistory','Observation')"


def upgrade() -> None:
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS patient_history_structuring_runs (
            id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
            intake_submission_id    UUID        NOT NULL REFERENCES patient_intake_submissions(id) ON DELETE CASCADE,
            intake_link_id          UUID        REFERENCES patient_intake_links(id) ON DELETE SET NULL,
            template_id             UUID        REFERENCES anamnesis_templates(id) ON DELETE SET NULL,
            patient_id              UUID        REFERENCES patients(id) ON DELETE SET NULL,
            appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
            consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
            provider                TEXT        NOT NULL DEFAULT 'local_demo_extractor',
            provider_model          TEXT,
            status                  TEXT        NOT NULL DEFAULT 'completed',
            language                TEXT        NOT NULL DEFAULT 'de',
            extraction_mode         TEXT        NOT NULL DEFAULT 'synthetic_demo',
            proposals_count         INTEGER     NOT NULL DEFAULT 0,
            error_message           TEXT,
            pseudonymized_log_ref   TEXT,
            synthetic_demo          BOOLEAN     NOT NULL DEFAULT true,
            production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
            created_by_user_id      UUID,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT structuring_runs_phi_check           CHECK (production_phi_enabled = false),
            CONSTRAINT structuring_runs_demo_check          CHECK (synthetic_demo = true),
            CONSTRAINT structuring_runs_proposals_check     CHECK (proposals_count >= 0),
            CONSTRAINT structuring_runs_provider_check      CHECK (provider IN {_PROVIDER_VALUES}),
            CONSTRAINT structuring_runs_status_check        CHECK (status IN {_RUN_STATUS_VALUES}),
            CONSTRAINT structuring_runs_language_check      CHECK (language IN {_LANGUAGE_VALUES}),
            CONSTRAINT structuring_runs_mode_check          CHECK (extraction_mode IN {_EXTRACTION_MODE_VALUES})
        );
    """)

    for col in ["clinic_id", "intake_submission_id", "patient_id",
                "appointment_request_id", "consent_event_id",
                "provider", "status", "language", "created_at"]:
        op.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_structuring_runs_{col}
                ON patient_history_structuring_runs ({col});
        """)

    op.execute(f"""
        CREATE TABLE IF NOT EXISTS patient_history_proposals (
            id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
            structuring_run_id      UUID        NOT NULL REFERENCES patient_history_structuring_runs(id) ON DELETE CASCADE,
            intake_submission_id    UUID        NOT NULL REFERENCES patient_intake_submissions(id) ON DELETE CASCADE,
            consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
            patient_id              UUID        REFERENCES patients(id) ON DELETE SET NULL,
            appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
            proposal_status         TEXT        NOT NULL DEFAULT 'unverified',
            history_type            TEXT        NOT NULL,
            fhir_resource_type      TEXT        NOT NULL,
            source_question_key     TEXT,
            source_answer_ref       TEXT,
            proposed_fields         JSONB       NOT NULL DEFAULT {_EMPTY_JSONB},
            proposed_fhir_payload   JSONB       NOT NULL DEFAULT {_EMPTY_JSONB},
            extraction_confidence   NUMERIC(4,3),
            confidence_explanation  TEXT,
            staff_review_required   BOOLEAN     NOT NULL DEFAULT true,
            reviewed_by_user_id     UUID,
            reviewed_at             TIMESTAMPTZ,
            review_note             TEXT,
            merged_history_entry_id UUID,
            rejected_reason         TEXT,
            synthetic_demo          BOOLEAN     NOT NULL DEFAULT true,
            production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT proposals_phi_check            CHECK (production_phi_enabled = false),
            CONSTRAINT proposals_demo_check           CHECK (synthetic_demo = true),
            CONSTRAINT proposals_review_required_check CHECK (staff_review_required = true),
            CONSTRAINT proposals_status_check         CHECK (proposal_status IN {_PROPOSAL_STATUS_VALUES}),
            CONSTRAINT proposals_history_type_check   CHECK (history_type IN {_HISTORY_TYPE_VALUES}),
            CONSTRAINT proposals_fhir_type_check      CHECK (fhir_resource_type IN {_FHIR_TYPE_VALUES}),
            CONSTRAINT proposals_confidence_check     CHECK (
                extraction_confidence IS NULL
                OR (extraction_confidence >= 0 AND extraction_confidence <= 1)
            )
        );
    """)

    for col in ["clinic_id", "structuring_run_id", "intake_submission_id",
                "consent_event_id", "patient_id", "appointment_request_id",
                "proposal_status", "history_type", "fhir_resource_type", "created_at"]:
        op.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_proposals_{col}
                ON patient_history_proposals ({col});
        """)


def downgrade() -> None:
    for col in ["clinic_id", "structuring_run_id", "intake_submission_id",
                "consent_event_id", "patient_id", "appointment_request_id",
                "proposal_status", "history_type", "fhir_resource_type", "created_at"]:
        op.execute(f"DROP INDEX IF EXISTS idx_proposals_{col};")
    op.execute("DROP TABLE IF EXISTS patient_history_proposals;")

    for col in ["clinic_id", "intake_submission_id", "patient_id",
                "appointment_request_id", "consent_event_id",
                "provider", "status", "language", "created_at"]:
        op.execute(f"DROP INDEX IF EXISTS idx_structuring_runs_{col};")
    op.execute("DROP TABLE IF EXISTS patient_history_structuring_runs;")
