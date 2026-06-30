-- =============================================================================
-- PraxisMed — PostgreSQL Database Schema
-- Sprint 1 / Module 3
--
-- Design principles:
--   • Multi-tenant: every row is scoped to a clinic via clinic_id.
--   • UUID primary keys throughout (gen_random_uuid() requires pgcrypto or
--     Postgres ≥ 13 where it is built-in).
--   • Immutable audit trail: audit_log rows are never updated or deleted.
--   • All timestamps stored as TIMESTAMPTZ (UTC-normalised).
--   • Schema is idempotent: wrapped in a transaction; use IF NOT EXISTS so
--     re-running against an existing DB is safe during development.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- Enable the pgcrypto extension for gen_random_uuid() on Postgres < 13.
-- On Postgres ≥ 13 this is a no-op because gen_random_uuid() is built-in.
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- A) clinics
--    Root tenant table.  Every other table references this via clinic_id.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clinics (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            TEXT        UNIQUE NOT NULL,
    name            TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'active',
    config_path     TEXT,
    config_version  INTEGER     NOT NULL DEFAULT 1,
    timezone        TEXT        NOT NULL DEFAULT 'Europe/Vienna',
    locale          TEXT        NOT NULL DEFAULT 'de-AT',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- B) clinic_users
--    Staff / admin users belonging to a clinic.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clinic_users (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id   UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    email       TEXT        NOT NULL,
    full_name   TEXT        NOT NULL,
    role        TEXT        NOT NULL,
    status      TEXT        NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (clinic_id, email)
);

-- ---------------------------------------------------------------------------
-- C) clinic_calendar_connections
--    OAuth / API connections to external calendar providers (Google, Microsoft
--    Bookings, etc.).  One clinic may have multiple connections.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clinic_calendar_connections (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id            UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    provider             TEXT        NOT NULL,
    external_calendar_id TEXT        NOT NULL,
    sync_status          TEXT        NOT NULL DEFAULT 'active',
    last_synced_at       TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (clinic_id, provider, external_calendar_id)
);

-- ---------------------------------------------------------------------------
-- D) clinic_calendar_blocks
--    Busy periods the AI booking layer must respect.
--    Sources: calendar sync, manual entry, vacation uploads.
--    Vapi and WhatsApp check this table before proposing appointment slots.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clinic_calendar_blocks (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id        UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    connection_id    UUID        REFERENCES clinic_calendar_connections(id) ON DELETE SET NULL,
    external_event_id TEXT,
    title            TEXT,
    block_type       TEXT        NOT NULL,
    starts_at        TIMESTAMPTZ NOT NULL,
    ends_at          TIMESTAMPTZ NOT NULL,
    is_all_day       BOOLEAN     NOT NULL DEFAULT false,
    source           TEXT        NOT NULL DEFAULT 'calendar_sync',
    raw_payload      JSONB,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT clinic_calendar_blocks_ends_after_starts CHECK (ends_at > starts_at)
);

-- ---------------------------------------------------------------------------
-- E) clinic_calendar_sync_events
--    Append-only log of sync operations triggered by n8n or webhooks.
--    Consumed by the dashboard and by alerting pipelines.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clinic_calendar_sync_events (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id     UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    connection_id UUID        REFERENCES clinic_calendar_connections(id) ON DELETE SET NULL,
    event_type    TEXT        NOT NULL,
    status        TEXT        NOT NULL,
    message       TEXT,
    raw_payload   JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- F) audit_log
--    Immutable compliance trail.  Rows are never updated or deleted.
--    clinic_id may be NULL for system-level actions (before a clinic exists).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_log (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id     UUID        REFERENCES clinics(id) ON DELETE SET NULL,
    actor_type    TEXT        NOT NULL,
    actor_id      TEXT,
    action        TEXT        NOT NULL,
    resource_type TEXT        NOT NULL,
    resource_id   TEXT,
    metadata      JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- Indexes
-- =============================================================================

-- clinics
CREATE INDEX IF NOT EXISTS idx_clinics_slug
    ON clinics (slug);

CREATE INDEX IF NOT EXISTS idx_clinics_status
    ON clinics (status);

-- clinic_users
CREATE INDEX IF NOT EXISTS idx_clinic_users_clinic_id
    ON clinic_users (clinic_id);

-- clinic_calendar_connections
CREATE INDEX IF NOT EXISTS idx_clinic_calendar_connections_clinic_id
    ON clinic_calendar_connections (clinic_id);

-- clinic_calendar_blocks — composite index optimised for time-range availability
-- queries ("is there a block overlapping this slot for this clinic?")
CREATE INDEX IF NOT EXISTS idx_clinic_calendar_blocks_clinic_time
    ON clinic_calendar_blocks (clinic_id, starts_at, ends_at);

CREATE INDEX IF NOT EXISTS idx_clinic_calendar_blocks_clinic_type
    ON clinic_calendar_blocks (clinic_id, block_type);

-- clinic_calendar_sync_events
CREATE INDEX IF NOT EXISTS idx_clinic_calendar_sync_events_clinic_created
    ON clinic_calendar_sync_events (clinic_id, created_at);

-- audit_log
CREATE INDEX IF NOT EXISTS idx_audit_log_clinic_created
    ON audit_log (clinic_id, created_at);

COMMIT;
