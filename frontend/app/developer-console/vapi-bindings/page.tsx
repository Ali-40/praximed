'use client'

// PraxisMed — Admin Vapi Binding Metadata UI
// Sprint 19 / Module 146 — Internal secret-reference configuration.
//
// Protected: requires admin session cookie. Uses lib/api helpers which apply
// NEXT_PUBLIC_API_BASE_URL and credentials: "include" on every request.
//
// Reference names only. No Vapi secrets are stored or transmitted.
// No live Vapi API calls. No webhook secret values. No PHI. No patient data.
// No production activation. Production PHI remains NO-GO.

import { useState } from 'react'
import {
  fetchClinicVapiBindings,
  createClinicVapiBinding,
  updateClinicVapiBindingStatus,
  ClinicVapiBinding,
} from '../../../lib/api'

const INK    = '#0B132B'
const PANEL  = '#111C3D'
const EDGE   = 'rgba(255,255,255,0.10)'
const ACCENT = '#008080'
const DANGER = '#E63946'
const WARN   = '#FFB703'
const TEXT   = '#E6EAF2'
const MUTED  = '#93A0B8'
const GREEN  = '#4ADE80'

// Reference names must look like environment-variable names — this guard
// blocks anything resembling an actual secret value on the client side too.
const SECRET_REF_PATTERN = /^[A-Z][A-Z0-9_]{2,99}$/

const LANGUAGE_MODES = ['german_first', 'english_first', 'bilingual_auto'] as const
const BINDING_STATUSES = ['draft', 'configured', 'disabled', 'revoked'] as const

type LoadState = 'idle' | 'loading' | 'loaded' | 'not_found' | 'auth_error' | 'clinic_error' | 'error'
type SubmitState = 'idle' | 'submitting' | 'submitted' | 'error'

const labelStyle = {
  display: 'block',
  fontSize: '0.7rem',
  fontWeight: 700 as const,
  color: MUTED,
  letterSpacing: '0.05em',
  textTransform: 'uppercase' as const,
  marginBottom: '0.3rem',
}

const inputStyle = {
  width: '100%',
  padding: '0.5rem 0.75rem',
  borderRadius: 7,
  border: `1px solid ${EDGE}`,
  background: 'rgba(255,255,255,0.04)',
  color: TEXT,
  fontSize: '0.8125rem',
  fontFamily: 'ui-monospace, monospace',
  boxSizing: 'border-box' as const,
  outline: 'none',
}

const selectStyle = { ...inputStyle, fontFamily: 'inherit' }

const buttonStyle = {
  fontSize: '0.8125rem',
  fontWeight: 700 as const,
  padding: '0.5rem 1.25rem',
  borderRadius: 7,
  border: `1px solid ${ACCENT}`,
  background: 'rgba(0,128,128,0.15)',
  color: ACCENT,
  cursor: 'pointer',
}

function SectionPanel({ title, badge, children }: { title: string; badge?: string; children: React.ReactNode }) {
  return (
    <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12, overflow: 'hidden', marginBottom: '1.25rem' }}>
      <div style={{ padding: '0.75rem 1.25rem', borderBottom: `1px solid ${EDGE}`, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span aria-hidden style={{ width: 7, height: 7, borderRadius: 99, background: ACCENT }} />
        <span style={{ flex: 1, fontSize: '0.875rem', fontWeight: 700, color: TEXT }}>{title}</span>
        {badge && (
          <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '2px 9px', borderRadius: 99, background: 'rgba(255,183,3,0.15)', color: WARN, border: '1px solid rgba(255,183,3,0.4)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            {badge}
          </span>
        )}
      </div>
      <div style={{ padding: '1rem 1.25rem' }}>{children}</div>
    </div>
  )
}

function FieldRow({ label, value, mono }: { label: string; value: React.ReactNode; mono?: boolean }) {
  return (
    <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', padding: '0.375rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '0.8125rem' }}>
      <span style={{ flexShrink: 0, width: 190, color: MUTED, fontSize: '0.75rem', fontWeight: 600 }}>{label}</span>
      <span style={{ flex: 1, color: TEXT, fontFamily: mono ? 'ui-monospace, monospace' : 'inherit', wordBreak: 'break-all' }}>
        {value ?? '—'}
      </span>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const color =
    status === 'configured' ? GREEN :
    status === 'draft' ? WARN :
    status === 'revoked' ? DANGER : MUTED
  return (
    <span style={{ display: 'inline-flex', padding: '2px 10px', borderRadius: 99, fontSize: '0.7rem', fontWeight: 700, border: `1px solid ${color}`, color, letterSpacing: '0.03em', textTransform: 'uppercase' }}>
      {status}
    </span>
  )
}

export default function VapiBindingMetadataPage() {
  const [clinicId, setClinicId] = useState('')
  const [loadState, setLoadState] = useState<LoadState>('idle')
  const [loadMessage, setLoadMessage] = useState<string | null>(null)
  const [binding, setBinding] = useState<ClinicVapiBinding | null>(null)

  // Create form — reference names only, never secret values.
  const [apiKeyRef, setApiKeyRef] = useState('')
  const [webhookRef, setWebhookRef] = useState('')
  const [languageMode, setLanguageMode] = useState<string>('german_first')
  const [submitState, setSubmitState] = useState<SubmitState>('idle')
  const [submitMessage, setSubmitMessage] = useState<string | null>(null)

  // Status update
  const [newStatus, setNewStatus] = useState<string>('draft')
  const [statusState, setStatusState] = useState<SubmitState>('idle')
  const [statusMessage, setStatusMessage] = useState<string | null>(null)

  function resetMessages() {
    setLoadMessage(null)
    setSubmitMessage(null)
    setStatusMessage(null)
  }

  async function handleLoad() {
    if (!clinicId.trim()) {
      setLoadState('error')
      setLoadMessage('Please enter a clinic_id first.')
      return
    }
    resetMessages()
    setBinding(null)
    setSubmitState('idle')
    setStatusState('idle')
    setLoadState('loading')
    try {
      const result = await fetchClinicVapiBindings(clinicId.trim())
      if (result.ok && result.binding) {
        setBinding(result.binding)
        setNewStatus(result.binding.status)
        setLoadState('loaded')
      } else if (result.status === 401 || result.status === 403) {
        setLoadState('auth_error')
        setLoadMessage('Admin session required. Please log in first.')
      } else if (result.status === 404 && result.detail?.toLowerCase().includes('no vapi binding')) {
        setLoadState('not_found')
        setLoadMessage('No Vapi binding found for this clinic.')
      } else if (result.status === 404) {
        setLoadState('clinic_error')
        setLoadMessage('Clinic not found or no access.')
      } else {
        setLoadState('error')
        setLoadMessage('Could not load Vapi binding metadata.')
      }
    } catch {
      setLoadState('error')
      setLoadMessage('Could not load Vapi binding metadata.')
    }
  }

  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    resetMessages()
    if (!clinicId.trim()) {
      setSubmitState('error')
      setSubmitMessage('Please enter and load a clinic_id first.')
      return
    }
    if (!SECRET_REF_PATTERN.test(apiKeyRef.trim()) || !SECRET_REF_PATTERN.test(webhookRef.trim())) {
      setSubmitState('error')
      setSubmitMessage(
        'Secret values are not allowed. Enter environment-variable reference names only, never secret values — e.g. VAPI_API_KEY_REF_CLINIC_DEMO.',
      )
      return
    }
    setSubmitState('submitting')
    try {
      const result = await createClinicVapiBinding(clinicId.trim(), {
        api_key_secret_ref: apiKeyRef.trim(),
        webhook_secret_ref: webhookRef.trim(),
        language_mode: languageMode,
      })
      if (result.ok && result.binding) {
        setBinding(result.binding)
        setNewStatus(result.binding.status)
        setLoadState('loaded')
        setSubmitState('submitted')
        setSubmitMessage('Vapi binding metadata saved. Reference names stored — no secret values.')
      } else if (result.status === 401 || result.status === 403) {
        setSubmitState('error')
        setSubmitMessage('Admin session required. Please log in first.')
      } else if (result.status === 404) {
        setSubmitState('error')
        setSubmitMessage('Clinic not found or no access.')
      } else if (result.status === 400 || result.status === 422) {
        setSubmitState('error')
        setSubmitMessage(
          result.detail ??
          'Secret values are not allowed. Enter environment-variable reference names only, never secret values.',
        )
      } else {
        setSubmitState('error')
        setSubmitMessage('Could not save Vapi binding metadata.')
      }
    } catch {
      setSubmitState('error')
      setSubmitMessage('Could not save Vapi binding metadata.')
    }
  }

  async function handleStatusUpdate() {
    if (!binding) return
    resetMessages()
    setStatusState('submitting')
    try {
      const result = await updateClinicVapiBindingStatus(binding.id, newStatus)
      if (result.ok && result.binding) {
        setBinding(result.binding)
        setStatusState('submitted')
        setStatusMessage('Binding status updated.')
      } else if (result.status === 401 || result.status === 403) {
        setStatusState('error')
        setStatusMessage('Admin session required. Please log in first.')
      } else {
        setStatusState('error')
        setStatusMessage(result.detail ?? 'Could not update binding status.')
      }
    } catch {
      setStatusState('error')
      setStatusMessage('Could not update binding status.')
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: INK, color: TEXT, display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '3rem 1.5rem', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div style={{ width: '100%', maxWidth: 760 }}>

        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.01em' }}>
              Vapi Binding Metadata
            </h1>
            <span style={{ fontSize: '0.6875rem', fontWeight: 700, padding: '2px 10px', borderRadius: 99, background: WARN, color: INK, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              ADMIN / STAGING
            </span>
          </div>
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.75rem' }}>
            Internal secret-reference configuration
          </p>

          {/* Red guardrail */}
          <div
            data-state="security-boundary"
            style={{ padding: '0.875rem 1.25rem', borderRadius: 10, background: 'rgba(230,57,70,0.12)', border: `1px solid ${DANGER}`, fontSize: '0.8125rem', color: '#F7A6AC', lineHeight: 1.6 }}
          >
            Reference names only. No Vapi secrets are stored or transmitted. No live Vapi API calls.{' '}
            <strong style={{ color: '#FFCDD1' }}>Production PHI remains NO-GO.</strong>
          </div>
        </div>

        {/* 1. Load bindings */}
        <SectionPanel title="Load Binding Metadata" badge="Read">
          <label style={labelStyle} htmlFor="clinic-id-input">Clinic ID</label>
          <input
            id="clinic-id-input"
            type="text"
            value={clinicId}
            onChange={(e) => setClinicId(e.target.value)}
            placeholder="clinic_id (UUID)"
            style={{ ...inputStyle, marginBottom: '0.375rem' }}
          />
          <p style={{ fontSize: '0.7rem', color: MUTED, marginBottom: '0.75rem' }}>
            Paste a provisioned clinic_id or the staging clinic_id, e.g.{' '}
            <code style={{ fontFamily: 'ui-monospace, monospace', color: '#7FD4D4' }}>
              1a5bbc75-c1b0-4488-94aa-64b3f1c50056
            </code>
          </p>
          <button onClick={handleLoad} disabled={loadState === 'loading'} style={{ ...buttonStyle, opacity: loadState === 'loading' ? 0.6 : 1 }}>
            {loadState === 'loading' ? 'Loading…' : 'Load bindings'}
          </button>

          {loadMessage && (
            <div
              data-state={loadState}
              style={{
                marginTop: '0.875rem', padding: '0.625rem 1rem', borderRadius: 8, fontSize: '0.775rem',
                background: loadState === 'not_found' ? 'rgba(255,183,3,0.10)' : 'rgba(230,57,70,0.12)',
                border: `1px solid ${loadState === 'not_found' ? 'rgba(255,183,3,0.4)' : DANGER}`,
                color: loadState === 'not_found' ? WARN : '#F7A6AC',
              }}
            >
              {loadMessage}
            </div>
          )}
        </SectionPanel>

        {/* 2. Existing binding */}
        {binding && (
          <SectionPanel title="Current Binding" badge="Metadata only">
            <div style={{ marginBottom: '0.5rem' }}>
              <StatusBadge status={binding.status} />
            </div>
            <FieldRow label="Binding ID" value={binding.id} mono />
            <FieldRow label="clinic_id" value={binding.clinic_id} mono />
            <FieldRow label="api_key_secret_ref" value={binding.api_key_secret_ref} mono />
            <FieldRow label="webhook_secret_ref" value={binding.webhook_secret_ref} mono />
            <FieldRow label="language_mode" value={binding.language_mode} />
            <FieldRow label="assistant_id" value={binding.assistant_id} mono />
            <FieldRow label="phone_number_id" value={binding.phone_number_id} mono />
            <FieldRow label="vapi_project_id" value={binding.vapi_project_id} mono />
            <FieldRow label="assistant_config_version" value={binding.assistant_config_version} mono />
            <FieldRow label="production_phi_enabled" value={String(binding.production_phi_enabled)} mono />
            <FieldRow label="created_at" value={binding.created_at} mono />
            <p style={{ fontSize: '0.7rem', color: MUTED, marginTop: '0.625rem' }}>
              Secret reference names only — the actual values live in secure environment
              variables and are never shown here. assistant_id / phone_number_id are set by a
              later live-binding module, not this page.
            </p>

            {/* Status update */}
            <div style={{ marginTop: '0.875rem', paddingTop: '0.875rem', borderTop: `1px solid ${EDGE}` }}>
              <label style={labelStyle} htmlFor="status-select">Update status</label>
              <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap', alignItems: 'center' }}>
                <select id="status-select" value={newStatus} onChange={(e) => setNewStatus(e.target.value)} style={{ ...selectStyle, width: 220 }}>
                  {BINDING_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
                <button onClick={handleStatusUpdate} disabled={statusState === 'submitting'} style={{ ...buttonStyle, opacity: statusState === 'submitting' ? 0.6 : 1 }}>
                  {statusState === 'submitting' ? 'Updating…' : 'Update status'}
                </button>
              </div>
              {statusMessage && (
                <p style={{ marginTop: '0.625rem', fontSize: '0.775rem', color: statusState === 'submitted' ? GREEN : '#F7A6AC' }}>
                  {statusMessage}
                </p>
              )}
            </div>
          </SectionPanel>
        )}

        {/* 3. Create binding */}
        {!binding && (loadState === 'not_found' || loadState === 'idle' || loadState === 'error' || loadState === 'clinic_error') && (
          <SectionPanel title="Create Binding Metadata" badge="Reference names only">
            <p style={{ fontSize: '0.775rem', color: MUTED, marginBottom: '0.875rem' }}>
              Enter environment-variable reference names only, never secret values.
              Secret values are not allowed and are rejected by both this form and the backend.
            </p>
            <form onSubmit={handleCreate}>
              <div style={{ marginBottom: '0.75rem' }}>
                <label style={labelStyle} htmlFor="api-key-ref">api_key_secret_ref (required)</label>
                <input
                  id="api-key-ref"
                  type="text"
                  value={apiKeyRef}
                  onChange={(e) => setApiKeyRef(e.target.value)}
                  placeholder="VAPI_API_KEY_REF_CLINIC_DEMO"
                  style={inputStyle}
                />
              </div>
              <div style={{ marginBottom: '0.75rem' }}>
                <label style={labelStyle} htmlFor="webhook-ref">webhook_secret_ref (required)</label>
                <input
                  id="webhook-ref"
                  type="text"
                  value={webhookRef}
                  onChange={(e) => setWebhookRef(e.target.value)}
                  placeholder="VAPI_WEBHOOK_SECRET_REF_CLINIC_DEMO"
                  style={inputStyle}
                />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={labelStyle} htmlFor="language-mode">language_mode</label>
                <select id="language-mode" value={languageMode} onChange={(e) => setLanguageMode(e.target.value)} style={{ ...selectStyle, width: 260 }}>
                  {LANGUAGE_MODES.map((m) => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>
              <button type="submit" disabled={submitState === 'submitting'} style={{ ...buttonStyle, opacity: submitState === 'submitting' ? 0.6 : 1 }}>
                {submitState === 'submitting' ? 'Saving…' : 'Save binding metadata'}
              </button>
            </form>
            <p style={{ fontSize: '0.7rem', color: MUTED, marginTop: '0.75rem' }}>
              New bindings start with status <code style={{ color: '#7FD4D4' }}>draft</code>.
              Later statuses: configured, disabled, revoked. No live Vapi call is made by saving.
            </p>
            {submitMessage && (
              <div
                data-state={submitState}
                style={{
                  marginTop: '0.875rem', padding: '0.625rem 1rem', borderRadius: 8, fontSize: '0.775rem',
                  background: submitState === 'submitted' ? 'rgba(74,222,128,0.10)' : 'rgba(230,57,70,0.12)',
                  border: `1px solid ${submitState === 'submitted' ? GREEN : DANGER}`,
                  color: submitState === 'submitted' ? GREEN : '#F7A6AC',
                }}
              >
                {submitMessage}
              </div>
            )}
          </SectionPanel>
        )}

        {/* 4. Safety boundary */}
        <SectionPanel title="Safety Boundary" badge="Hard rules">
          {[
            'No live Vapi API calls are made from this page.',
            'No Vapi secrets — reference names only.',
            'No webhook secret values are accepted or displayed.',
            'No PHI. No patient data.',
            'No production activation. Production PHI remains NO-GO.',
            'Actual credentials are managed via secure environment variables, never in the browser.',
          ].map((line, i, arr) => (
            <div key={i} style={{ display: 'flex', gap: '0.625rem', alignItems: 'flex-start', padding: '0.5rem 0', borderBottom: i < arr.length - 1 ? `1px solid ${EDGE}` : 'none', fontSize: '0.8125rem', color: TEXT }}>
              <span style={{ flexShrink: 0, color: DANGER, fontWeight: 700 }}>!</span>
              <span>{line}</span>
            </div>
          ))}
        </SectionPanel>

        {/* Back link */}
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <a href="/developer-console" style={{ fontSize: '0.8125rem', color: MUTED, textDecoration: 'none' }}>
            ← Back to developer console
          </a>
        </div>
      </div>
    </div>
  )
}
