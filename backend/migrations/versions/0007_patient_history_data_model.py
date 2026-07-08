"""Add FHIR-aligned patient history tables — PraxisMed Sprint 20 / Module 149.

Revision ID: 0007_patient_history_data_model
Revises: 0006_consent_events
Create Date: 2026-07-08

Seven FHIR R4-aligned patient history tables:
  patient_history_allergies         AllergyIntolerance
  patient_history_medications       MedicationStatement
  patient_history_conditions        Condition (patient-reported/staff-entered; no diagnosis generated)
  patient_history_procedures        Procedure
  patient_history_immunizations     Immunization
  patient_history_family_history    FamilyMemberHistory
  patient_history_social_history    Observation (social context only)

All tables are tenant-scoped, patient-scoped, consent-linked, append-only/versioned,
and enforce production_phi_enabled=false via DB CHECK constraint.
No DELETE path. Staff/doctor review required (status=unverified default).

Synthetic/fake staging only. No real patient PHI.
No diagnosis generated. No medical advice. No triage scoring.
Production PHI remains NO-GO.
"""

from __future__ import annotations

from alembic import op

revision = "0007_patient_history_data_model"
down_revision = "0006_consent_events"
branch_labels = None
depends_on = None

_STATUS_VALUES = "('unverified','approved','rejected','superseded')"
_SOURCE_TYPE_VALUES = "('staff_console','intake_link','phone_call','ai_proposal','demo_seed','import_demo')"


def _common_cols() -> str:
    return """
            id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
            patient_id              UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
            consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
            version_group_id        UUID        NOT NULL,
            version_number          INTEGER     NOT NULL DEFAULT 1,
            supersedes_entry_id     UUID,
            correction_reason       TEXT,
            status                  TEXT        NOT NULL DEFAULT 'unverified',
            source_type             TEXT        NOT NULL DEFAULT 'staff_console',
            source_ref              TEXT,
            entered_by_user_id      UUID,
            reviewed_by_user_id     UUID,
            reviewed_at             TIMESTAMPTZ,
            review_note             TEXT,
            effective_start_date    DATE,
            effective_end_date      DATE,
            notes                   TEXT,
            fhir_resource_type      TEXT        NOT NULL,
            fhir_payload            JSONB       NOT NULL DEFAULT '{{}}'::jsonb,
            metadata                JSONB       NOT NULL DEFAULT '{{}}'::jsonb,
            production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()"""


def _common_constraints(t: str) -> str:
    return f"""
            CONSTRAINT {t}_phi_check CHECK (production_phi_enabled = false),
            CONSTRAINT {t}_status_check CHECK (status IN {_STATUS_VALUES}),
            CONSTRAINT {t}_source_type_check CHECK (source_type IN {_SOURCE_TYPE_VALUES}),
            CONSTRAINT {t}_version_check CHECK (version_number >= 1),
            UNIQUE (version_group_id, version_number)"""


def _indexes(t: str) -> str:
    cols = [
        "clinic_id", "patient_id", "consent_event_id", "appointment_request_id",
        "status", "source_type", "version_group_id", "created_at", "production_phi_enabled",
    ]
    stmts = "\n".join(
        f"        CREATE INDEX IF NOT EXISTS idx_{t}_{c} ON {t} ({c});"
        for c in cols
    )
    return stmts


def upgrade() -> None:
    # ── patient_history_allergies (AllergyIntolerance) ──────────────────────
    t = "patient_history_allergies"
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {t} ({_common_cols()},
            substance_text          TEXT        NOT NULL,
            reaction_text           TEXT,
            severity                TEXT,
            clinical_status         TEXT,
            verification_status     TEXT,
            category                TEXT,
            criticality             TEXT,
            onset_text              TEXT,
            {_common_constraints(t)}
        );
    """)
    op.execute(_indexes(t))

    # ── patient_history_medications (MedicationStatement) ───────────────────
    t = "patient_history_medications"
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {t} ({_common_cols()},
            medication_text         TEXT        NOT NULL,
            dosage_text             TEXT,
            frequency_text          TEXT,
            route_text              TEXT,
            medication_status       TEXT,
            start_text              TEXT,
            end_text                TEXT,
            reason_text             TEXT,
            {_common_constraints(t)}
        );
    """)
    op.execute(_indexes(t))

    # ── patient_history_conditions (Condition — patient-reported only) ───────
    t = "patient_history_conditions"
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {t} ({_common_cols()},
            condition_text          TEXT        NOT NULL,
            clinical_status         TEXT,
            verification_status     TEXT,
            onset_text              TEXT,
            abatement_text          TEXT,
            body_site_text          TEXT,
            severity_text           TEXT,
            patient_reported        BOOLEAN     NOT NULL DEFAULT true,
            {_common_constraints(t)}
        );
    """)
    op.execute(_indexes(t))

    # ── patient_history_procedures (Procedure) ───────────────────────────────
    t = "patient_history_procedures"
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {t} ({_common_cols()},
            procedure_text          TEXT        NOT NULL,
            performed_text          TEXT,
            body_site_text          TEXT,
            outcome_text            TEXT,
            performer_text          TEXT,
            reason_text             TEXT,
            {_common_constraints(t)}
        );
    """)
    op.execute(_indexes(t))

    # ── patient_history_immunizations (Immunization) ─────────────────────────
    t = "patient_history_immunizations"
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {t} ({_common_cols()},
            vaccine_text            TEXT        NOT NULL,
            occurrence_text         TEXT,
            lot_number              TEXT,
            site_text               TEXT,
            route_text              TEXT,
            dose_number             TEXT,
            series_text             TEXT,
            immunization_status     TEXT,
            {_common_constraints(t)}
        );
    """)
    op.execute(_indexes(t))

    # ── patient_history_family_history (FamilyMemberHistory) ─────────────────
    t = "patient_history_family_history"
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {t} ({_common_cols()},
            relationship_text       TEXT        NOT NULL,
            condition_text          TEXT,
            age_text                TEXT,
            deceased                BOOLEAN,
            note_text               TEXT,
            {_common_constraints(t)}
        );
    """)
    op.execute(_indexes(t))

    # ── patient_history_social_history (Observation — non-diagnostic) ────────
    t = "patient_history_social_history"
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {t} ({_common_cols()},
            observation_category    TEXT        NOT NULL,
            observation_text        TEXT        NOT NULL,
            value_text              TEXT,
            period_text             TEXT,
            {_common_constraints(t)}
        );
    """)
    op.execute(_indexes(t))


def downgrade() -> None:
    tables = [
        "patient_history_social_history",
        "patient_history_family_history",
        "patient_history_immunizations",
        "patient_history_procedures",
        "patient_history_conditions",
        "patient_history_medications",
        "patient_history_allergies",
    ]
    for t in tables:
        cols = [
            "clinic_id", "patient_id", "consent_event_id", "appointment_request_id",
            "status", "source_type", "version_group_id", "created_at", "production_phi_enabled",
        ]
        for c in cols:
            op.execute(f"DROP INDEX IF EXISTS idx_{t}_{c};")
        op.execute(f"DROP TABLE IF EXISTS {t};")
