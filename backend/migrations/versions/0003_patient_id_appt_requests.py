"""Add patient_id to appointment_requests — PraxisMed Sprint 17 / Module 121.

Revision ID: 0003_patient_id_appt_requests
Revises: 0002_password_hash
Create Date: 2026-07-05

Links appointment_requests rows to the patients table so that each captured
request can be tied to a single patient identity within the clinic. The
column is nullable: rows created before this migration (and staff-entered
requests without patient lookup) retain NULL patient_id.

The FK references patients(id) ON DELETE SET NULL so that archiving a patient
record does not cascade-delete appointment requests.
"""

from __future__ import annotations

from alembic import op

revision = "0003_patient_id_appt_requests"
down_revision = "0002_password_hash"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE appointment_requests
            ADD COLUMN IF NOT EXISTS patient_id UUID
            REFERENCES patients(id) ON DELETE SET NULL;
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_appointment_requests_clinic_patient
            ON appointment_requests (clinic_id, patient_id);
    """)


def downgrade() -> None:
    op.execute(
        "DROP INDEX IF EXISTS idx_appointment_requests_clinic_patient;"
    )
    op.execute(
        "ALTER TABLE appointment_requests DROP COLUMN IF EXISTS patient_id;"
    )
