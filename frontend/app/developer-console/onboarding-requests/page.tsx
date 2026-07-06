'use client'

// PraxisMed — Internal Clinic Onboarding Review Console
// Sprint 19 / Module 134A — Crash fix: defensive rendering for nullable/optional fields
// Module 134 — Internal clinic onboarding review console
//
// Admin/staff internal page: list submitted pilot requests, view details, update status.
// Dark developer-console theme. Uses protected GET + PATCH /clinic-onboarding-requests.
// No tenant activation. No PHI. No secrets. Production PHI remains NO-GO.

import { useEffect, useState } from 'react'
import { API_BASE_URL } from '../../../lib/api'

const INK    = '#0B132B'
const PANEL  = '#111C3D'
const EDGE   = 'rgba(255,255,255,0.10)'
const ACCENT = '#008080'
const DANGER = '#E63946'
const WARN   = '#FFB703'
const TEXT   = '#E6EAF2'
const MUTED  = '#93A0B8'
const GREEN  = '#4ADE80'

const ALLOWED_STATUSES = [
  'submitted',
  'reviewed',
  'demo_booked',
  'pilot_approved',
  'rejected',
  'archived',
] as const

type AllowedStatus = typeof ALLOWED_STATUSES[number]

const STATUS_COLORS: Record<AllowedStatus, string> = {
  submitted:      WARN,
  reviewed:       ACCENT,
  demo_booked:    ACCENT,
  pilot_approved: GREEN,
  rejected:       DANGER,
  archived:       MUTED,
}

// supported_languages may arrive as a parsed array, a JSON string, or null
// depending on asyncpg JSONB codec configuration.
interface OnboardingRequest {
  id: string
  clinic_name: string
  clinic_type: string | null
  specialty: string | null
  city: string | null
  address: string | null
  website: string | null
  doctor_name: string
  contact_email: string
  contact_phone: string | null
  preferred_language: string
  fallback_language: string
  supported_languages: string[] | string | null
  workflow_notes: string | null
  estimated_call_volume: string | null
  current_booking_system: string | null
  wants_ai_phone_intake: boolean | null
  wants_dashboard: boolean | null
  wants_notifications: boolean | null
  pilot_interest_level: string | null
  status: string
  source: string | null
  consent_pilot_contact: boolean | null
  acknowledges_no_phi: boolean | null
  production_phi_enabled: boolean | null
  created_at: string | null
  updated_at: string | null
}

type LoadState     = 'idle' | 'loading' | 'loaded' | 'auth_error' | 'error'
type UpdateState   = 'idle' | 'updating' | 'updated' | 'error'
type ProvisionState = 'idle' | 'provisioning' | 'provisioned' | 'error'

interface ProvisionResult {
  ok: boolean
  clinic_id: string
  clinic_name: string
  clinic_slug: string
  preferred_language: string
  production_phi_enabled: boolean
  message: string
  already_provisioned: boolean
}

// ---------------------------------------------------------------------------
// Defensive rendering helpers — guard against null, undefined, and
// unexpected types returned by the backend for optional/JSONB fields.
// ---------------------------------------------------------------------------

function safeText(value: unknown, fallback = '—'): string {
  if (value === null || value === undefined || value === '') return fallback
  return String(value)
}

function safeDate(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—'
  try {
    const d = new Date(String(value))
    if (isNaN(d.getTime())) return '—'
    return d.toLocaleString()
  } catch {
    return '—'
  }
}

function safeBoolean(value: unknown): boolean | null {
  if (value === null || value === undefined) return null
  return Boolean(value)
}

// Handles supported_languages whether the backend delivers it as a parsed
// JSON array, a raw JSON string (asyncpg default JSONB behaviour), or null.
function safeLanguages(value: unknown): string {
  if (value === null || value === undefined) return 'de, en'
  if (Array.isArray(value)) return (value as string[]).join(', ')
  if (typeof value === 'string') {
    try {
      const parsed: unknown = JSON.parse(value)
      if (Array.isArray(parsed)) return (parsed as string[]).join(', ')
    } catch {
      // not JSON — return raw string
    }
    return value
  }
  return '—'
}

// ---------------------------------------------------------------------------
// Display components
// ---------------------------------------------------------------------------

function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLORS[status as AllowedStatus] ?? MUTED
  return (
    <span
      style={{
        display: 'inline-block',
        fontSize: '0.6875rem',
        fontWeight: 700,
        padding: '2px 9px',
        borderRadius: 99,
        background: `${color}22`,
        color,
        border: `1px solid ${color}55`,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        fontFamily: 'ui-monospace, monospace',
      }}
    >
      {safeText(status)}
    </span>
  )
}

function LangBadge({ lang }: { lang: string }) {
  return (
    <span
      style={{
        display: 'inline-block',
        fontSize: '0.6875rem',
        fontWeight: 700,
        padding: '2px 8px',
        borderRadius: 6,
        background: 'rgba(0,128,128,0.15)',
        color: '#7FD4D4',
        fontFamily: 'ui-monospace, monospace',
        letterSpacing: '0.03em',
      }}
    >
      {lang === 'de' ? 'Deutsch-first' : safeText(lang)}
    </span>
  )
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div
      style={{
        display: 'flex',
        gap: '0.75rem',
        padding: '0.45rem 0',
        borderBottom: `1px solid ${EDGE}`,
        fontSize: '0.8125rem',
        alignItems: 'flex-start',
      }}
    >
      <span style={{ flexShrink: 0, width: 180, color: MUTED, fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.02em', paddingTop: 1 }}>
        {label}
      </span>
      <span style={{ flex: 1, color: TEXT, wordBreak: 'break-all' }}>
        {value !== null && value !== undefined && value !== ''
          ? value
          : <span style={{ color: MUTED, fontStyle: 'italic' }}>—</span>}
      </span>
    </div>
  )
}

// Renders boolean fields safely. null/undefined → "—", true → "Yes", false → "No".
function BoolRow({ label, value }: { label: string; value: boolean | null }) {
  if (value === null) {
    return <Row label={label} value={<span style={{ color: MUTED, fontStyle: 'italic' }}>—</span>} />
  }
  return (
    <Row
      label={label}
      value={
        <span style={{ color: value ? GREEN : DANGER, fontWeight: 700 }}>
          {value ? 'Yes' : 'No'}
        </span>
      }
    />
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function OnboardingRequestsPage() {
  const [loadState, setLoadState]           = useState<LoadState>('idle')
  const [requests, setRequests]             = useState<OnboardingRequest[]>([])
  const [selected, setSelected]             = useState<OnboardingRequest | null>(null)
  const [selectedStatus, setSelectedStatus] = useState<string>('')
  const [updateState, setUpdateState]       = useState<UpdateState>('idle')
  const [updateError, setUpdateError]       = useState<string | null>(null)
  const [fetchError, setFetchError]         = useState<string | null>(null)
  const [provisionState, setProvisionState]   = useState<ProvisionState>('idle')
  const [provisionResult, setProvisionResult] = useState<ProvisionResult | null>(null)
  const [provisionError, setProvisionError]   = useState<string | null>(null)

  useEffect(() => { loadRequests() }, [])

  async function loadRequests() {
    setLoadState('loading')
    setFetchError(null)
    try {
      const resp = await fetch(`${API_BASE_URL}/clinic-onboarding-requests`, {
        credentials: 'include',
      })
      if (resp.status === 401 || resp.status === 403) {
        setLoadState('auth_error')
        return
      }
      if (!resp.ok) {
        setFetchError('Failed to load onboarding requests.')
        setLoadState('error')
        return
      }
      const data = await resp.json() as { ok: boolean; requests?: OnboardingRequest[] }
      setRequests(data.requests ?? [])
      setLoadState('loaded')
    } catch {
      setFetchError('A network error occurred. Check your connection.')
      setLoadState('error')
    }
  }

  function selectRequest(req: OnboardingRequest) {
    setSelected(req)
    setSelectedStatus(safeText(req.status, 'submitted'))
    setUpdateState('idle')
    setUpdateError(null)
    setProvisionState('idle')
    setProvisionResult(null)
    setProvisionError(null)
  }

  async function handleStatusUpdate() {
    if (!selected || !selectedStatus) return
    setUpdateState('updating')
    setUpdateError(null)
    try {
      const resp = await fetch(
        `${API_BASE_URL}/clinic-onboarding-requests/${selected.id}/status`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ status: selectedStatus }),
        },
      )
      if (!resp.ok) {
        let msg = 'Status update failed. Please try again.'
        try {
          const errData = await resp.json() as { detail?: string | Array<{ msg: string }> }
          if (typeof errData.detail === 'string') msg = errData.detail
          else if (Array.isArray(errData.detail)) msg = errData.detail.map((d) => d.msg).join(' ')
        } catch { /* keep default */ }
        setUpdateError(msg)
        setUpdateState('error')
        return
      }
      const data = await resp.json() as { ok: boolean; request?: OnboardingRequest }
      const updated = data.request ?? { ...selected, status: selectedStatus }
      setRequests((prev) => prev.map((r) => (r.id === selected.id ? updated : r)))
      setSelected(updated)
      setUpdateState('updated')
    } catch {
      setUpdateError('A network error occurred during status update.')
      setUpdateState('error')
    }
  }

  async function handleProvision() {
    if (!selected) return
    setProvisionState('provisioning')
    setProvisionError(null)
    try {
      const resp = await fetch(
        `${API_BASE_URL}/clinic-onboarding-requests/${selected.id}/provision-clinic-shell`,
        { method: 'POST', credentials: 'include' },
      )
      if (resp.status === 401 || resp.status === 403) {
        setProvisionError('Admin session required.')
        setProvisionState('error')
        return
      }
      if (resp.status === 409) {
        setProvisionError('Request must be pilot_approved before provisioning.')
        setProvisionState('error')
        return
      }
      if (!resp.ok) {
        setProvisionError('Provisioning failed. Please retry or check backend logs.')
        setProvisionState('error')
        return
      }
      const data = await resp.json() as ProvisionResult
      setProvisionResult(data)
      setProvisionState('provisioned')
    } catch {
      setProvisionError('Provisioning failed. Please retry or check backend logs.')
      setProvisionState('error')
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: INK,
        color: TEXT,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '3rem 1.5rem',
        fontFamily: 'Inter, system-ui, sans-serif',
      }}
    >
      <div style={{ width: '100%', maxWidth: 900 }}>

        {/* Header */}
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.625rem' }}>
            <h1 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.01em' }}>
              Clinic Onboarding Requests
            </h1>
            <span
              style={{
                fontSize: '0.6875rem', fontWeight: 700, padding: '2px 10px', borderRadius: 99,
                background: WARN, color: INK, letterSpacing: '0.05em', textTransform: 'uppercase',
              }}
            >
              ADMIN / STAGING
            </span>
          </div>
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.5rem' }}>
            Internal review console — view submitted pilot requests and update review status.
          </p>

          {/* Safety banner */}
          <div
            style={{
              padding: '0.75rem 1rem',
              borderRadius: 9,
              background: 'rgba(230,57,70,0.10)',
              border: `1px solid ${DANGER}`,
              fontSize: '0.775rem',
              color: '#F7A6AC',
              lineHeight: 1.6,
            }}
          >
            <strong style={{ color: '#FFCDD1' }}>No tenant activation.</strong>{' '}
            <strong style={{ color: '#FFCDD1' }}>No PHI.</strong>{' '}
            Approving a request does not create a tenant or unlock production PHI.{' '}
            <strong style={{ color: '#FFCDD1' }}>Production PHI remains NO-GO</strong>{' '}
            until all C3–C8 compliance hardening blockers are resolved.
          </div>
        </div>

        {/* Auth error */}
        {loadState === 'auth_error' && (
          <div
            style={{
              padding: '1.25rem', borderRadius: 10, background: PANEL, border: `1px solid ${DANGER}`,
              color: '#F7A6AC', fontSize: '0.875rem', marginBottom: '1.25rem',
            }}
          >
            Admin session required. Please log in first.{' '}
            <a href="/login" style={{ color: ACCENT, textDecoration: 'underline' }}>Go to login</a>
          </div>
        )}

        {/* Generic error */}
        {loadState === 'error' && fetchError && (
          <div
            style={{
              padding: '1.25rem', borderRadius: 10, background: PANEL, border: `1px solid ${WARN}`,
              color: WARN, fontSize: '0.875rem', marginBottom: '1.25rem',
            }}
          >
            {fetchError}
            <button
              onClick={loadRequests}
              style={{ marginLeft: '1rem', color: ACCENT, background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.875rem' }}
            >
              Retry
            </button>
          </div>
        )}

        {/* Loading */}
        {loadState === 'loading' && (
          <p style={{ color: MUTED, fontSize: '0.875rem', marginBottom: '1rem' }}>Loading onboarding requests…</p>
        )}

        {/* Content */}
        {loadState === 'loaded' && (
          <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start', flexWrap: 'wrap' }}>

            {/* Left: request list */}
            <div style={{ flex: '1 1 300px', minWidth: 0 }}>
              <div
                style={{
                  background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12,
                  overflow: 'hidden',
                }}
              >
                <div style={{ padding: '0.875rem 1.25rem', borderBottom: `1px solid ${EDGE}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT }}>
                    Requests ({requests.length})
                  </span>
                  <button
                    onClick={loadRequests}
                    style={{ fontSize: '0.75rem', color: ACCENT, background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    Refresh
                  </button>
                </div>

                {requests.length === 0 ? (
                  <div style={{ padding: '1.5rem 1.25rem', color: MUTED, fontSize: '0.8125rem', textAlign: 'center' }}>
                    No onboarding requests submitted yet.
                  </div>
                ) : (
                  <div>
                    {requests.map((req) => (
                      <button
                        key={req.id}
                        onClick={() => selectRequest(req)}
                        style={{
                          width: '100%', textAlign: 'left', padding: '0.875rem 1.25rem',
                          borderBottom: `1px solid ${EDGE}`,
                          background: selected?.id === req.id ? 'rgba(0,128,128,0.12)' : 'transparent',
                          border: 'none', cursor: 'pointer',
                          borderLeft: selected?.id === req.id ? `3px solid ${ACCENT}` : '3px solid transparent',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.25rem' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.875rem', color: TEXT }}>
                            {safeText(req.clinic_name)}
                          </span>
                          <StatusBadge status={safeText(req.status, 'submitted')} />
                        </div>
                        <div style={{ fontSize: '0.75rem', color: MUTED, marginBottom: '0.125rem' }}>
                          {safeText(req.doctor_name)}
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.7rem', color: MUTED }}>{safeText(req.contact_email)}</span>
                          <LangBadge lang={safeText(req.preferred_language, 'de')} />
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right: detail panel */}
            {selected ? (
              <div style={{ flex: '1 1 360px', minWidth: 0 }}>
                <div
                  style={{
                    background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12,
                    overflow: 'hidden',
                  }}
                >
                  <div style={{ padding: '0.875rem 1.25rem', borderBottom: `1px solid ${EDGE}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT }}>Request Detail</span>
                    <StatusBadge status={safeText(selected.status, 'submitted')} />
                  </div>

                  <div style={{ padding: '1rem 1.25rem' }}>

                    {/* Clinic */}
                    <p style={{ fontSize: '0.7rem', fontWeight: 700, color: MUTED, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.375rem' }}>Clinic</p>
                    <Row label="clinic_name"  value={safeText(selected.clinic_name)} />
                    <Row label="clinic_type"  value={safeText(selected.clinic_type)} />
                    <Row label="specialty"    value={safeText(selected.specialty)} />
                    <Row label="city"         value={safeText(selected.city)} />
                    <Row label="address"      value={safeText(selected.address)} />
                    <Row label="website"      value={safeText(selected.website)} />

                    {/* Doctor */}
                    <p style={{ fontSize: '0.7rem', fontWeight: 700, color: MUTED, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.375rem', marginTop: '1rem' }}>Doctor / Admin</p>
                    <Row label="doctor_name"   value={safeText(selected.doctor_name)} />
                    <Row label="contact_email" value={safeText(selected.contact_email)} />
                    <Row label="contact_phone" value={safeText(selected.contact_phone)} />

                    {/* Language */}
                    <p style={{ fontSize: '0.7rem', fontWeight: 700, color: MUTED, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.375rem', marginTop: '1rem' }}>Language</p>
                    <Row
                      label="preferred_language"
                      value={
                        <>
                          <code style={{ fontFamily: 'ui-monospace, monospace', color: '#7FD4D4' }}>
                            {safeText(selected.preferred_language)}
                          </code>
                          {selected.preferred_language === 'de' ? ' — Deutsch-first' : ''}
                        </>
                      }
                    />
                    <Row
                      label="fallback_language"
                      value={<code style={{ fontFamily: 'ui-monospace, monospace', color: '#7FD4D4' }}>{safeText(selected.fallback_language)}</code>}
                    />
                    <Row label="supported_languages" value={safeLanguages(selected.supported_languages)} />

                    {/* Workflow */}
                    <p style={{ fontSize: '0.7rem', fontWeight: 700, color: MUTED, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.375rem', marginTop: '1rem' }}>Workflow</p>
                    <Row label="estimated_call_volume"  value={safeText(selected.estimated_call_volume)} />
                    <Row label="current_booking_system" value={safeText(selected.current_booking_system)} />
                    <Row label="workflow_notes"         value={safeText(selected.workflow_notes)} />
                    <BoolRow label="wants_ai_phone_intake" value={safeBoolean(selected.wants_ai_phone_intake)} />
                    <BoolRow label="wants_dashboard"       value={safeBoolean(selected.wants_dashboard)} />
                    <BoolRow label="wants_notifications"   value={safeBoolean(selected.wants_notifications)} />

                    {/* Safety */}
                    <p style={{ fontSize: '0.7rem', fontWeight: 700, color: MUTED, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.375rem', marginTop: '1rem' }}>Safety</p>
                    <BoolRow label="consent_pilot_contact"  value={safeBoolean(selected.consent_pilot_contact)} />
                    <BoolRow label="acknowledges_no_phi"    value={safeBoolean(selected.acknowledges_no_phi)} />
                    <BoolRow label="production_phi_enabled" value={safeBoolean(selected.production_phi_enabled)} />

                    {/* Operational */}
                    <p style={{ fontSize: '0.7rem', fontWeight: 700, color: MUTED, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.375rem', marginTop: '1rem' }}>Operational</p>
                    <Row label="id"     value={<code style={{ fontFamily: 'ui-monospace, monospace', fontSize: '0.75rem', color: '#7FD4D4' }}>{safeText(selected.id)}</code>} />
                    <Row label="source" value={safeText(selected.source)} />
                    <Row label="pilot_interest_level" value={safeText(selected.pilot_interest_level)} />
                    <Row label="created_at" value={safeDate(selected.created_at)} />
                    <Row label="updated_at" value={safeDate(selected.updated_at)} />

                    {/* Activation warning */}
                    <div
                      style={{
                        marginTop: '1rem',
                        padding: '0.625rem 0.875rem',
                        borderRadius: 8,
                        background: 'rgba(255,183,3,0.08)',
                        border: `1px solid rgba(255,183,3,0.35)`,
                        fontSize: '0.775rem',
                        color: WARN,
                        lineHeight: 1.55,
                      }}
                    >
                      Approving a request does not create a tenant or unlock production PHI.
                      Status updates are internal review markers only.
                    </div>

                    {/* Status update */}
                    <div style={{ marginTop: '1rem' }}>
                      <p style={{ fontSize: '0.7rem', fontWeight: 700, color: MUTED, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Update status</p>
                      <div style={{ display: 'flex', gap: '0.625rem', alignItems: 'center', flexWrap: 'wrap' }}>
                        <select
                          value={selectedStatus}
                          onChange={(e) => { setSelectedStatus(e.target.value); setUpdateState('idle') }}
                          style={{
                            flex: '1 1 160px',
                            padding: '0.5rem 0.75rem',
                            borderRadius: 7,
                            border: `1px solid ${EDGE}`,
                            background: 'rgba(255,255,255,0.06)',
                            color: TEXT,
                            fontSize: '0.8125rem',
                            fontFamily: 'ui-monospace, monospace',
                          }}
                        >
                          {ALLOWED_STATUSES.map((s) => (
                            <option key={s} value={s} style={{ background: '#1a2540' }}>{s}</option>
                          ))}
                        </select>
                        <button
                          onClick={handleStatusUpdate}
                          disabled={updateState === 'updating' || selectedStatus === selected.status}
                          style={{
                            padding: '0.5rem 1.25rem',
                            borderRadius: 7,
                            border: `1px solid ${ACCENT}`,
                            background: 'rgba(0,128,128,0.15)',
                            color: ACCENT,
                            fontSize: '0.8125rem',
                            fontWeight: 700,
                            cursor: updateState === 'updating' || selectedStatus === selected.status ? 'not-allowed' : 'pointer',
                            opacity: updateState === 'updating' || selectedStatus === selected.status ? 0.5 : 1,
                          }}
                        >
                          {updateState === 'updating' ? 'Updating…' : 'Update status'}
                        </button>
                      </div>

                      {updateState === 'updated' && (
                        <p style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: GREEN }}>
                          Status updated
                        </p>
                      )}
                      {updateState === 'error' && updateError && (
                        <p style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: DANGER }}>
                          {updateError}
                        </p>
                      )}
                    </div>

                    {/* Clinic Shell Provisioning */}
                    <div style={{ marginTop: '1.25rem' }}>
                      <p style={{ fontSize: '0.7rem', fontWeight: 700, color: MUTED, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                        Clinic Shell Provisioning
                      </p>

                      <div
                        style={{
                          padding: '0.625rem 0.875rem',
                          borderRadius: 8,
                          background: 'rgba(230,57,70,0.06)',
                          border: `1px solid rgba(230,57,70,0.25)`,
                          fontSize: '0.775rem',
                          color: '#F7A6AC',
                          lineHeight: 1.55,
                          marginBottom: '0.75rem',
                        }}
                      >
                        Provisioning does not activate production PHI. It creates a pilot clinic
                        shell only — no Vapi credentials are bound, no patient records are created,
                        and no production PHI is enabled.{' '}
                        <strong style={{ color: '#FFCDD1' }}>Production PHI remains NO-GO.</strong>
                      </div>

                      <button
                        onClick={handleProvision}
                        disabled={selected.status !== 'pilot_approved' || provisionState === 'provisioning'}
                        style={{
                          padding: '0.5rem 1.25rem',
                          borderRadius: 7,
                          border: `1px solid ${selected.status === 'pilot_approved' ? GREEN : EDGE}`,
                          background: selected.status === 'pilot_approved' ? 'rgba(74,222,128,0.12)' : 'rgba(255,255,255,0.04)',
                          color: selected.status === 'pilot_approved' ? GREEN : MUTED,
                          fontSize: '0.8125rem',
                          fontWeight: 700,
                          cursor: (selected.status !== 'pilot_approved' || provisionState === 'provisioning') ? 'not-allowed' : 'pointer',
                          opacity: (selected.status !== 'pilot_approved' || provisionState === 'provisioning') ? 0.5 : 1,
                        }}
                      >
                        {provisionState === 'provisioning' ? 'Provisioning…' : 'Provision Clinic Shell'}
                      </button>

                      {selected.status !== 'pilot_approved' && (
                        <p style={{ marginTop: '0.375rem', fontSize: '0.775rem', color: MUTED, fontStyle: 'italic' }}>
                          Set status to pilot_approved before provisioning.
                        </p>
                      )}

                      {provisionState === 'provisioned' && provisionResult && (
                        <div
                          style={{
                            marginTop: '0.75rem',
                            padding: '0.75rem 0.875rem',
                            borderRadius: 8,
                            background: 'rgba(74,222,128,0.08)',
                            border: `1px solid rgba(74,222,128,0.35)`,
                          }}
                        >
                          {provisionResult.already_provisioned ? (
                            <p style={{ fontSize: '0.8125rem', color: GREEN, margin: 0 }}>
                              Already provisioned. clinic_id:{' '}
                              <code style={{ fontFamily: 'ui-monospace, monospace', fontSize: '0.75rem' }}>
                                {provisionResult.clinic_id}
                              </code>
                            </p>
                          ) : (
                            <div style={{ fontSize: '0.8125rem', color: GREEN }}>
                              <p style={{ margin: '0 0 0.5rem', fontWeight: 700 }}>
                                Clinic shell provisioned. Production PHI remains disabled.
                              </p>
                              <Row
                                label="clinic_id"
                                value={
                                  <code style={{ fontFamily: 'ui-monospace, monospace', fontSize: '0.75rem', color: '#7FD4D4' }}>
                                    {provisionResult.clinic_id}
                                  </code>
                                }
                              />
                              <Row label="clinic_name" value={safeText(provisionResult.clinic_name)} />
                              <Row
                                label="clinic_slug"
                                value={
                                  <code style={{ fontFamily: 'ui-monospace, monospace', fontSize: '0.75rem', color: '#7FD4D4' }}>
                                    {provisionResult.clinic_slug}
                                  </code>
                                }
                              />
                              <Row label="preferred_language" value={safeText(provisionResult.preferred_language)} />
                            </div>
                          )}
                        </div>
                      )}

                      {provisionState === 'error' && provisionError && (
                        <p style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: DANGER }}>
                          {provisionError}
                        </p>
                      )}
                    </div>

                  </div>
                </div>
              </div>
            ) : (
              <div
                style={{
                  flex: '1 1 360px', background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12,
                  padding: '2rem 1.25rem', color: MUTED, fontSize: '0.875rem', textAlign: 'center',
                }}
              >
                Select a request to view details.
              </div>
            )}
          </div>
        )}

        {/* Nav */}
        <div style={{ marginTop: '2rem', display: 'flex', gap: '1.5rem', justifyContent: 'center' }}>
          <a href="/developer-console" style={{ fontSize: '0.8125rem', color: MUTED, textDecoration: 'none' }}>
            ← Developer Console
          </a>
          <a href="/dashboard" style={{ fontSize: '0.8125rem', color: MUTED, textDecoration: 'none' }}>
            ← Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}
