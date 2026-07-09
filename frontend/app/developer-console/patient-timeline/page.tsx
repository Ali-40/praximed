'use client'

// No browser storage. No token storage.

const INK    = '#0B132B'
const PANEL  = '#111C3D'
const EDGE   = 'rgba(255,255,255,0.10)'
const ACCENT = '#008080'
const DANGER = '#E63946'
const WARN   = '#FFB703'
const TEXT   = '#E6EAF2'
const MUTED  = '#93A0B8'
const GREEN  = '#22c55e'

import React, { useState } from 'react'
import {
  fetchPatientTimeline,
  fetchPatientTimelineDelta,
} from '../../../lib/api'

type TimelineItem = {
  id: string
  item_type: string
  item_source: string
  title: string
  summary?: string
  occurred_at?: string
  created_at?: string
  status?: string
  history_type?: string
  fhir_resource_type?: string
  is_approved_history?: boolean
  is_unverified_proposal?: boolean
  consent_event_id?: string
  production_phi_enabled?: boolean
}

type TimelineResult = {
  ok: boolean
  clinic_id: string
  patient_id: string
  items: TimelineItem[]
  total: number
  approved_history_count: number
  unverified_proposal_count: number
  consent_event_count: number
  intake_submission_count: number
  appointment_count: number
  structuring_run_count: number
  include_unverified: boolean
  production_phi_enabled: boolean
  extraction_note: string
}

type DeltaResult = {
  ok: boolean
  clinic_id: string
  patient_id: string
  delta_anchor_status: string
  delta_anchor_at?: string
  items: TimelineItem[]
  total: number
  approved_history_count: number
  unverified_proposal_count: number
  includes_unverified_proposals: boolean
  since?: string
  production_phi_enabled: boolean
  extraction_note: string
}

function ItemTypeBadge({ item }: { item: TimelineItem }) {
  const t = item.item_type
  if (item.is_approved_history) {
    return (
      <span style={{ background: 'rgba(34,197,94,0.18)', color: GREEN, fontWeight: 700, fontSize: '0.65rem', padding: '2px 8px', borderRadius: 99, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        APPROVED HISTORY
      </span>
    )
  }
  if (item.is_unverified_proposal) {
    return (
      <span style={{ background: 'rgba(255,183,3,0.15)', color: WARN, fontWeight: 700, fontSize: '0.65rem', padding: '2px 8px', borderRadius: 99, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        UNVERIFIED PROPOSAL
      </span>
    )
  }
  if (t === 'consent_event') {
    return (
      <span style={{ background: 'rgba(0,128,128,0.18)', color: ACCENT, fontWeight: 700, fontSize: '0.65rem', padding: '2px 8px', borderRadius: 99, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        CONSENT
      </span>
    )
  }
  if (t === 'intake_submission') {
    return (
      <span style={{ background: 'rgba(255,255,255,0.07)', color: MUTED, fontWeight: 700, fontSize: '0.65rem', padding: '2px 8px', borderRadius: 99, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        INTAKE
      </span>
    )
  }
  if (t === 'appointment_request') {
    return (
      <span style={{ background: 'rgba(255,255,255,0.07)', color: MUTED, fontWeight: 700, fontSize: '0.65rem', padding: '2px 8px', borderRadius: 99, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        APPOINTMENT
      </span>
    )
  }
  if (t === 'structuring_run') {
    return (
      <span style={{ background: 'rgba(255,255,255,0.07)', color: MUTED, fontWeight: 700, fontSize: '0.65rem', padding: '2px 8px', borderRadius: 99, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        STRUCTURING
      </span>
    )
  }
  return (
    <span style={{ background: 'rgba(255,255,255,0.05)', color: MUTED, fontWeight: 700, fontSize: '0.65rem', padding: '2px 8px', borderRadius: 99 }}>
      {t.toUpperCase()}
    </span>
  )
}

function TimelineItemRow({ item }: { item: TimelineItem }) {
  const ts = item.occurred_at || item.created_at || '—'
  const border = item.is_approved_history
    ? `1px solid ${GREEN}33`
    : item.is_unverified_proposal
    ? `1px solid ${WARN}44`
    : `1px solid ${EDGE}`

  return (
    <div style={{ background: INK, border, borderRadius: 8, padding: '0.75rem 1rem', marginBottom: '0.5rem', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap', marginBottom: '0.25rem' }}>
          <ItemTypeBadge item={item} />
          <span style={{ color: MUTED, fontSize: '0.72rem' }}>{ts}</span>
        </div>
        <div style={{ color: TEXT, fontSize: '0.875rem', fontWeight: 600 }}>{item.title}</div>
        {item.history_type && (
          <div style={{ color: MUTED, fontSize: '0.75rem', marginTop: 2 }}>
            {item.history_type}
            {item.fhir_resource_type ? ` · ${item.fhir_resource_type}` : ''}
          </div>
        )}
        {item.status && (
          <div style={{ color: MUTED, fontSize: '0.72rem', marginTop: 2 }}>status: {item.status}</div>
        )}
      </div>
    </div>
  )
}

export default function PatientTimelinePage() {
  const [clinicId, setClinicId] = useState('')
  const [patientId, setPatientId] = useState('')
  const [includeUnverified, setIncludeUnverified] = useState(true)

  const [timeline, setTimeline] = useState<TimelineResult | null>(null)
  const [timelineErr, setTimelineErr] = useState<string | null>(null)
  const [timelineLoading, setTimelineLoading] = useState(false)

  const [delta, setDelta] = useState<DeltaResult | null>(null)
  const [deltaErr, setDeltaErr] = useState<string | null>(null)
  const [deltaLoading, setDeltaLoading] = useState(false)

  async function handleLoadTimeline() {
    if (!clinicId.trim() || !patientId.trim()) {
      setTimelineErr('Clinic ID and Patient ID are required.')
      return
    }
    setTimelineLoading(true)
    setTimelineErr(null)
    setTimeline(null)
    try {
      const result = await fetchPatientTimeline(clinicId.trim(), patientId.trim(), { includeUnverified })
      setTimeline(result as TimelineResult)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      if (msg.includes('401') || msg.includes('403')) {
        setTimelineErr('Admin session required. Please log in first.')
      } else if (msg.includes('404')) {
        setTimelineErr('Patient not found or no access.')
      } else {
        setTimelineErr('Patient timeline could not be loaded.')
      }
    } finally {
      setTimelineLoading(false)
    }
  }

  async function handleLoadDelta() {
    if (!clinicId.trim() || !patientId.trim()) {
      setDeltaErr('Clinic ID and Patient ID are required.')
      return
    }
    setDeltaLoading(true)
    setDeltaErr(null)
    setDelta(null)
    try {
      const result = await fetchPatientTimelineDelta(clinicId.trim(), patientId.trim(), { includeUnverified })
      setDelta(result as DeltaResult)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      if (msg.includes('401') || msg.includes('403')) {
        setDeltaErr('Admin session required. Please log in first.')
      } else {
        setDeltaErr('Delta view could not be loaded.')
      }
    } finally {
      setDeltaLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: INK, color: TEXT, fontFamily: 'ui-monospace, monospace', padding: '2rem' }}>

      {/* Header */}
      <div style={{ marginBottom: '1.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <h1 style={{ fontSize: '1.375rem', fontWeight: 800, color: TEXT, letterSpacing: '-0.01em', margin: 0 }}>
            Longitudinal Patient Timeline
          </h1>
          <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '3px 10px', borderRadius: 99, background: 'rgba(230,57,70,0.15)', color: DANGER, letterSpacing: '0.07em', textTransform: 'uppercase' }}>
            ADMIN / STAGING
          </span>
        </div>
        <p style={{ color: MUTED, fontSize: '0.8rem', margin: '0.35rem 0 0' }}>
          Approved history and unverified proposal view
        </p>
        <div style={{ marginTop: '0.875rem', background: 'rgba(230,57,70,0.10)', border: `1px solid ${DANGER}44`, borderRadius: 8, padding: '0.625rem 1rem', fontSize: '0.78rem', color: DANGER }}>
          Synthetic staging only. Approved history appears only after staff review. Unverified proposals are clearly marked. No diagnosis, no medical advice, no PHI. Production PHI remains NO-GO.
        </div>
      </div>

      {/* Inputs */}
      <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 10, padding: '1.25rem', marginBottom: '1.25rem' }}>
        <div style={{ marginBottom: '0.875rem', color: ACCENT, fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          Patient Filters
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.875rem', marginBottom: '0.875rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.72rem', color: MUTED, marginBottom: 4 }}>Clinic ID</label>
            <input
              value={clinicId}
              onChange={e => setClinicId(e.target.value)}
              placeholder="xxxxxxxx-xxxx-4xxx-8xxx-xxxxxxxxxxxx"
              style={{ width: '100%', background: INK, border: `1px solid ${EDGE}`, borderRadius: 6, padding: '0.5rem 0.75rem', color: TEXT, fontSize: '0.82rem', fontFamily: 'inherit', boxSizing: 'border-box' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.72rem', color: MUTED, marginBottom: 4 }}>Patient ID</label>
            <input
              value={patientId}
              onChange={e => setPatientId(e.target.value)}
              placeholder="xxxxxxxx-xxxx-4xxx-8xxx-xxxxxxxxxxxx"
              style={{ width: '100%', background: INK, border: `1px solid ${EDGE}`, borderRadius: 6, padding: '0.5rem 0.75rem', color: TEXT, fontSize: '0.82rem', fontFamily: 'inherit', boxSizing: 'border-box' }}
            />
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <input
            type="checkbox"
            id="includeUnverified"
            checked={includeUnverified}
            onChange={e => setIncludeUnverified(e.target.checked)}
            style={{ accentColor: ACCENT, width: 14, height: 14 }}
          />
          <label htmlFor="includeUnverified" style={{ fontSize: '0.8rem', color: MUTED, cursor: 'pointer' }}>
            Include unverified proposals
          </label>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            onClick={handleLoadTimeline}
            disabled={timelineLoading}
            style={{ background: ACCENT, color: '#fff', border: 'none', borderRadius: 7, padding: '0.5rem 1.25rem', fontSize: '0.82rem', fontWeight: 700, cursor: timelineLoading ? 'not-allowed' : 'pointer', opacity: timelineLoading ? 0.7 : 1 }}
          >
            {timelineLoading ? 'Loading…' : 'Load timeline'}
          </button>
          <button
            onClick={handleLoadDelta}
            disabled={deltaLoading}
            style={{ background: PANEL, color: ACCENT, border: `1px solid ${ACCENT}`, borderRadius: 7, padding: '0.5rem 1.25rem', fontSize: '0.82rem', fontWeight: 700, cursor: deltaLoading ? 'not-allowed' : 'pointer', opacity: deltaLoading ? 0.7 : 1 }}
          >
            {deltaLoading ? 'Loading…' : 'Load delta since last visit'}
          </button>
        </div>
      </div>

      {/* Timeline result */}
      {timelineErr && (
        <div style={{ background: 'rgba(230,57,70,0.10)', border: `1px solid ${DANGER}44`, borderRadius: 8, padding: '0.75rem 1rem', color: DANGER, fontSize: '0.82rem', marginBottom: '1rem' }}>
          {timelineErr}
        </div>
      )}

      {timeline && (
        <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 10, padding: '1.25rem', marginBottom: '1.25rem' }}>
          {/* Summary */}
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ color: ACCENT, fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.625rem' }}>
              Timeline Summary
            </div>
            <div style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap', fontSize: '0.8rem', color: MUTED }}>
              <span>Total: <strong style={{ color: TEXT }}>{timeline.total}</strong></span>
              <span>Approved history: <strong style={{ color: GREEN }}>{timeline.approved_history_count}</strong></span>
              <span>Unverified proposals: <strong style={{ color: WARN }}>{timeline.unverified_proposal_count}</strong></span>
              <span>Consent events: <strong style={{ color: TEXT }}>{timeline.consent_event_count}</strong></span>
              <span>Intake submissions: <strong style={{ color: TEXT }}>{timeline.intake_submission_count}</strong></span>
              <span>Appointments: <strong style={{ color: TEXT }}>{timeline.appointment_count}</strong></span>
              <span>Structuring runs: <strong style={{ color: TEXT }}>{timeline.structuring_run_count}</strong></span>
            </div>
            <div style={{ marginTop: '0.5rem', fontSize: '0.72rem', color: MUTED }}>
              {timeline.extraction_note}
            </div>
            <div style={{ marginTop: '0.25rem', fontSize: '0.72rem', color: MUTED }}>
              production_phi_enabled: {String(timeline.production_phi_enabled)}
            </div>
          </div>

          {/* Item list */}
          <div>
            <div style={{ color: ACCENT, fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.625rem' }}>
              Timeline Events ({timeline.items.length})
            </div>
            {timeline.items.length === 0 && (
              <div style={{ color: MUTED, fontSize: '0.82rem' }}>No timeline events found for this patient.</div>
            )}
            {timeline.items.map((item, idx) => (
              <TimelineItemRow key={item.id || idx} item={item} />
            ))}
          </div>
        </div>
      )}

      {/* Delta result */}
      {deltaErr && (
        <div style={{ background: 'rgba(230,57,70,0.10)', border: `1px solid ${DANGER}44`, borderRadius: 8, padding: '0.75rem 1rem', color: DANGER, fontSize: '0.82rem', marginBottom: '1rem' }}>
          {deltaErr}
        </div>
      )}

      {delta && (
        <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 10, padding: '1.25rem', marginBottom: '1.25rem' }}>
          <div style={{ color: ACCENT, fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
            Delta View
          </div>

          {/* Anchor status */}
          <div style={{ marginBottom: '0.875rem' }}>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap', marginBottom: '0.35rem' }}>
              {delta.delta_anchor_status === 'changed_since_last_visit' ? (
                <span style={{ background: 'rgba(34,197,94,0.12)', color: GREEN, fontWeight: 700, fontSize: '0.7rem', padding: '2px 10px', borderRadius: 99, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  changed_since_last_visit
                </span>
              ) : (
                <span style={{ background: 'rgba(255,183,3,0.12)', color: WARN, fontWeight: 700, fontSize: '0.7rem', padding: '2px 10px', borderRadius: 99, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  no_prior_visit_anchor
                </span>
              )}
              {delta.delta_anchor_at && (
                <span style={{ color: MUTED, fontSize: '0.75rem' }}>since: {delta.delta_anchor_at}</span>
              )}
            </div>
            <div style={{ fontSize: '0.8rem', color: MUTED }}>
              Items changed: <strong style={{ color: TEXT }}>{delta.total}</strong>
              {' '}· Approved history: <strong style={{ color: GREEN }}>{delta.approved_history_count}</strong>
              {' '}· Unverified proposals: <strong style={{ color: WARN }}>{delta.unverified_proposal_count}</strong>
            </div>
          </div>

          {/* Delta items */}
          {delta.items.length === 0 ? (
            <div style={{ color: MUTED, fontSize: '0.82rem' }}>No new events since last visit anchor.</div>
          ) : (
            delta.items.map((item, idx) => (
              <TimelineItemRow key={item.id || idx} item={item} />
            ))
          )}
        </div>
      )}

      {/* Safety panel */}
      <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 10, padding: '1.25rem', marginTop: '1.5rem' }}>
        <div style={{ color: ACCENT, fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
          Safety Boundary
        </div>
        <ul style={{ margin: 0, padding: '0 0 0 1.25rem', color: MUTED, fontSize: '0.78rem', lineHeight: 1.7 }}>
          <li>Approved patient history only after staff review and explicit confirmation.</li>
          <li>Unverified proposals are not merged history — clearly labeled UNVERIFIED PROPOSAL.</li>
          <li>Extraction confidence is not medical judgment — {'"Extraction confidence only — not a medical judgment."'}</li>
          <li>No diagnosis generated or surfaced.</li>
          <li>No medical advice given.</li>
          <li>No treatment recommendations generated.</li>
          <li>No triage scoring performed.</li>
          <li>No real patient data — synthetic/fake staging only.</li>
          <li>production_phi_enabled = false enforced end-to-end.</li>
          <li>Production PHI remains NO-GO.</li>
        </ul>
      </div>
    </div>
  )
}
