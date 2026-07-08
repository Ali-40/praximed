'use client'

// PraxisMed — Patient History Review (Doctor-reviewed merge queue)
// Sprint 20 / Module 154 — AI Structuring Review UI
//
// Synthetic staging only. Proposals remain unverified until staff approval.
// No diagnosis, no medical advice, no PHI. Production PHI remains NO-GO.
// No auto-approval. No automatic confirmation. Staff/doctor review required.
// No browser storage. No token storage.

import { useState } from 'react'
import {
  fetchPatientHistoryReviewQueue,
  fetchPatientHistoryProposalReview,
  approveMergePatientHistoryProposal,
  rejectReviewPatientHistoryProposal,
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

type Proposal = {
  id: string
  history_type: string
  fhir_resource_type: string
  proposal_status: string
  staff_review_required: boolean
  extraction_confidence?: number | null
  source_question_key?: string | null
  source_answer_ref?: string | null
  proposed_fields?: Record<string, unknown>
  proposed_fhir_payload?: Record<string, unknown>
  consent_event_id: string
  intake_submission_id: string
  patient_id?: string | null
  appointment_request_id?: string | null
  production_phi_enabled: boolean
  synthetic_demo: boolean
  created_at?: unknown
  confidence_explanation?: string | null
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ fontSize: '0.7rem', fontWeight: 700, color: MUTED, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
      {children}
    </div>
  )
}

function Field({ label, value, mono }: { label: string; value?: string | null; mono?: boolean }) {
  return (
    <div style={{ marginBottom: '0.6rem' }}>
      <Label>{label}</Label>
      <div style={{ fontSize: '0.8125rem', color: value ? TEXT : MUTED, fontFamily: mono ? 'ui-monospace, monospace' : undefined }}>
        {value || '—'}
      </div>
    </div>
  )
}

function Input({
  label, value, onChange, placeholder, type = 'text',
}: {
  label: string; value: string; onChange: (v: string) => void; placeholder?: string; type?: string
}) {
  return (
    <div style={{ marginBottom: '0.75rem' }}>
      <Label>{label}</Label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%', padding: '0.5rem 0.75rem', borderRadius: 7,
          border: `1px solid ${EDGE}`, background: 'rgba(255,255,255,0.05)',
          color: TEXT, fontSize: '0.8125rem', fontFamily: 'ui-monospace, monospace',
          boxSizing: 'border-box',
        }}
      />
    </div>
  )
}

function Btn({
  label, onClick, disabled, variant = 'primary',
}: {
  label: string; onClick: () => void; disabled?: boolean; variant?: 'primary' | 'danger' | 'muted'
}) {
  const bg = variant === 'danger' ? `rgba(230,57,70,0.15)` : variant === 'muted' ? 'rgba(255,255,255,0.06)' : 'rgba(0,128,128,0.15)'
  const col = variant === 'danger' ? DANGER : variant === 'muted' ? MUTED : ACCENT
  const bdr = variant === 'danger' ? DANGER : variant === 'muted' ? EDGE : ACCENT
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        fontSize: '0.8125rem', fontWeight: 700, padding: '0.5rem 1.25rem',
        borderRadius: 7, border: `1px solid ${bdr}`, background: bg, color: col,
        cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.55 : 1,
        marginRight: '0.5rem', marginBottom: '0.5rem',
      }}
    >
      {label}
    </button>
  )
}

function Alert({ msg, kind }: { msg: string; kind: 'ok' | 'err' | 'warn' }) {
  const c = kind === 'ok' ? GREEN : kind === 'err' ? DANGER : WARN
  return (
    <div style={{ padding: '0.625rem 1rem', borderRadius: 8, border: `1px solid ${c}`, background: `${c}18`, color: c, fontSize: '0.8125rem', marginBottom: '0.75rem' }}>
      {msg}
    </div>
  )
}

export default function HistoryReviewPage() {
  const [clinicId, setClinicId] = useState('')
  const [patientId, setPatientId] = useState('')
  const [historyType, setHistoryType] = useState('all')
  const [queue, setQueue] = useState<Proposal[]>([])
  const [queueMsg, setQueueMsg] = useState<string | null>(null)
  const [queueErr, setQueueErr] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const [selected, setSelected] = useState<Proposal | null>(null)
  const [detailErr, setDetailErr] = useState<string | null>(null)

  const [editedFieldsJson, setEditedFieldsJson] = useState('{}')
  const [reviewNote, setReviewNote] = useState('')
  const [staffReviewConfirmed, setStaffReviewConfirmed] = useState(false)
  const [rejectedReason, setRejectedReason] = useState('')

  const [mergeMsg, setMergeMsg] = useState<string | null>(null)
  const [mergeErr, setMergeErr] = useState<string | null>(null)
  const [rejectMsg, setRejectMsg] = useState<string | null>(null)
  const [rejectErr, setRejectErr] = useState<string | null>(null)

  async function loadQueue() {
    if (!clinicId.trim()) { setQueueErr('Admin session required. Please log in first.'); return }
    setLoading(true); setQueueErr(null); setQueueMsg(null); setQueue([])
    try {
      const items = await fetchPatientHistoryReviewQueue(clinicId.trim(), {
        patientId: patientId.trim() || undefined,
        historyType: historyType !== 'all' ? historyType : undefined,
      })
      setQueue(items as Proposal[])
      if (items.length === 0) setQueueMsg('No unverified proposals found.')
    } catch {
      setQueueErr('Proposal could not be loaded.')
    } finally {
      setLoading(false)
    }
  }

  async function selectProposal(p: Proposal) {
    setDetailErr(null); setMergeMsg(null); setMergeErr(null); setRejectMsg(null); setRejectErr(null)
    setStaffReviewConfirmed(false); setReviewNote(''); setRejectedReason(''); setEditedFieldsJson('{}')
    try {
      const detail = await fetchPatientHistoryProposalReview(p.id, clinicId) as Proposal
      setSelected(detail)
      setEditedFieldsJson(JSON.stringify(detail.proposed_fields ?? {}, null, 2))
    } catch {
      setDetailErr('Proposal could not be loaded.')
    }
  }

  async function handleMerge() {
    if (!selected) return
    if (!staffReviewConfirmed) { setMergeErr('Staff review confirmation is required.'); return }
    setMergeErr(null); setMergeMsg(null)
    let editedFields: Record<string, unknown> = {}
    try { editedFields = JSON.parse(editedFieldsJson) } catch { setMergeErr('Could not merge proposal. Invalid JSON in edited fields.'); return }
    try {
      await approveMergePatientHistoryProposal(selected.id, clinicId, {
        edited_fields: editedFields,
        review_note: reviewNote || undefined,
        confirm_staff_review: true,
      })
      setMergeMsg('Proposal merged into patient history after staff review.')
      setSelected(null)
      await loadQueue()
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      if (msg.includes('not eligible') || msg.includes('not unverified')) setMergeErr('This proposal is not eligible for merge.')
      else setMergeErr('Could not merge proposal.')
    }
  }

  async function handleReject() {
    if (!selected) return
    setRejectErr(null); setRejectMsg(null)
    try {
      await rejectReviewPatientHistoryProposal(selected.id, clinicId, {
        rejected_reason: rejectedReason || undefined,
      })
      setRejectMsg('Proposal rejected.')
      setSelected(null)
      await loadQueue()
    } catch {
      setRejectErr('Could not reject proposal.')
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: INK, color: TEXT, fontFamily: 'Inter, system-ui, sans-serif', padding: '3rem 1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ width: '100%', maxWidth: 860 }}>

        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.625rem', flexWrap: 'wrap' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.01em' }}>
              Patient History Review
            </h1>
            <span style={{ fontSize: '0.6875rem', fontWeight: 700, padding: '2px 10px', borderRadius: 99, background: WARN, color: INK, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              ADMIN / STAGING
            </span>
          </div>
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.75rem' }}>
            Doctor-reviewed merge queue
          </p>
          <div style={{ padding: '0.875rem 1.25rem', borderRadius: 10, background: 'rgba(230,57,70,0.10)', border: `1px solid ${DANGER}`, fontSize: '0.8125rem', color: '#F7A6AC', lineHeight: 1.6 }}>
            <strong style={{ color: '#FFCDD1' }}>Synthetic staging only.</strong>{' '}
            Proposals remain unverified until staff approval. No diagnosis, no medical advice, no PHI.{' '}
            <strong style={{ color: '#FFCDD1' }}>Production PHI remains NO-GO.</strong>{' '}
            No automatic approval. Staff/doctor review required before merging.
          </div>
        </div>

        {/* Filters */}
        <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12, padding: '1.25rem', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: TEXT, marginBottom: '1rem' }}>Load review queue</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <Input label="Clinic ID" value={clinicId} onChange={setClinicId} placeholder="uuid" />
            <Input label="Patient ID (optional)" value={patientId} onChange={setPatientId} placeholder="uuid — leave blank for all" />
          </div>
          <div style={{ marginBottom: '0.75rem' }}>
            <Label>History type filter</Label>
            <select
              value={historyType}
              onChange={e => setHistoryType(e.target.value)}
              style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: 7, border: `1px solid ${EDGE}`, background: 'rgba(255,255,255,0.05)', color: TEXT, fontSize: '0.8125rem' }}
            >
              {['all','allergies','medications','conditions','procedures','immunizations','family-history','social-history'].map(t => (
                <option key={t} value={t} style={{ background: PANEL }}>{t}</option>
              ))}
            </select>
          </div>
          {queueErr && <Alert msg={queueErr} kind="err" />}
          {queueMsg && <Alert msg={queueMsg} kind="warn" />}
          <Btn label={loading ? 'Loading…' : 'Load review queue'} onClick={loadQueue} disabled={loading} />
        </div>

        {/* Queue list */}
        {queue.length > 0 && (
          <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12, padding: '1.25rem', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: TEXT, marginBottom: '1rem' }}>
              Unverified proposals ({queue.length})
            </h3>
            {queue.map(p => (
              <div
                key={p.id}
                onClick={() => selectProposal(p)}
                style={{
                  padding: '0.75rem 1rem', borderRadius: 8, marginBottom: '0.5rem',
                  border: `1px solid ${selected?.id === p.id ? ACCENT : EDGE}`,
                  background: selected?.id === p.id ? 'rgba(0,128,128,0.10)' : 'rgba(255,255,255,0.03)',
                  cursor: 'pointer',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '0.25rem' }}>
                  <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: '0.75rem', color: ACCENT }}>{p.id.slice(0,8)}…</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: TEXT }}>{p.history_type}</span>
                  <span style={{ fontSize: '0.7rem', color: MUTED }}>{p.fhir_resource_type}</span>
                  <span style={{ fontSize: '0.7rem', padding: '1px 6px', borderRadius: 99, background: 'rgba(255,183,3,0.12)', color: WARN, fontWeight: 700 }}>{p.proposal_status}</span>
                  {p.staff_review_required && <span style={{ fontSize: '0.65rem', color: DANGER }}>review required</span>}
                </div>
                {p.extraction_confidence != null && (
                  <div style={{ fontSize: '0.7rem', color: MUTED }}>
                    Extraction confidence: {(p.extraction_confidence * 100).toFixed(0)}% — Extraction confidence only — not a medical judgment.
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Detail + merge/reject panel */}
        {selected && (
          <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12, padding: '1.25rem', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: TEXT, marginBottom: '1rem' }}>
              Proposal detail — {selected.history_type} / {selected.fhir_resource_type}
            </h3>

            {detailErr && <Alert msg={detailErr} kind="err" />}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <Field label="Proposal ID" value={selected.id} mono />
                <Field label="History type" value={selected.history_type} />
                <Field label="FHIR resource type" value={selected.fhir_resource_type} />
                <Field label="Status" value={selected.proposal_status} />
                <Field label="Staff review required" value={selected.staff_review_required ? 'Yes' : 'No'} />
                <Field label="Extraction confidence" value={selected.extraction_confidence != null ? `${(selected.extraction_confidence * 100).toFixed(0)}% — Extraction confidence only — not a medical judgment.` : '—'} />
              </div>
              <div>
                <Field label="Source question key" value={selected.source_question_key} mono />
                <Field label="Intake submission ID" value={selected.intake_submission_id} mono />
                <Field label="Consent event ID" value={selected.consent_event_id} mono />
                <Field label="Patient ID" value={selected.patient_id} mono />
                <Field label="Production PHI enabled" value={String(selected.production_phi_enabled)} />
                <Field label="Synthetic demo" value={String(selected.synthetic_demo)} />
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <Label>Proposed fields (JSON)</Label>
              <pre style={{ background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: 8, fontSize: '0.75rem', color: '#7FD4D4', overflow: 'auto', maxHeight: 160 }}>
                {JSON.stringify(selected.proposed_fields ?? {}, null, 2)}
              </pre>
            </div>

            {/* Merge panel */}
            <div style={{ borderTop: `1px solid ${EDGE}`, paddingTop: '1rem', marginTop: '0.5rem' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: ACCENT, marginBottom: '0.75rem' }}>Approve & merge into patient history</h4>
              <div style={{ marginBottom: '0.75rem' }}>
                <Label>Edit proposed fields (JSON)</Label>
                <textarea
                  value={editedFieldsJson}
                  onChange={e => setEditedFieldsJson(e.target.value)}
                  rows={6}
                  style={{
                    width: '100%', padding: '0.5rem 0.75rem', borderRadius: 7,
                    border: `1px solid ${EDGE}`, background: 'rgba(255,255,255,0.05)',
                    color: TEXT, fontSize: '0.75rem', fontFamily: 'ui-monospace, monospace',
                    boxSizing: 'border-box', resize: 'vertical',
                  }}
                />
              </div>
              <Input label="Review note (optional)" value={reviewNote} onChange={setReviewNote} placeholder="Optional note for the record" />
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', padding: '0.625rem 1rem', borderRadius: 8, border: `1px solid ${EDGE}`, background: 'rgba(255,255,255,0.03)' }}>
                <input
                  type="checkbox"
                  id="staffReviewConfirm"
                  checked={staffReviewConfirmed}
                  onChange={e => setStaffReviewConfirmed(e.target.checked)}
                  style={{ width: 16, height: 16, cursor: 'pointer' }}
                />
                <label htmlFor="staffReviewConfirm" style={{ fontSize: '0.8125rem', color: TEXT, cursor: 'pointer' }}>
                  I confirm staff/doctor review before merging.
                </label>
              </div>
              {mergeMsg && <Alert msg={mergeMsg} kind="ok" />}
              {mergeErr && <Alert msg={mergeErr} kind="err" />}
              <Btn label="Approve & merge into patient history" onClick={handleMerge} disabled={!staffReviewConfirmed} />
            </div>

            {/* Reject panel */}
            <div style={{ borderTop: `1px solid ${EDGE}`, paddingTop: '1rem', marginTop: '1rem' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: DANGER, marginBottom: '0.75rem' }}>Reject proposal</h4>
              <Input label="Rejection reason (optional)" value={rejectedReason} onChange={setRejectedReason} placeholder="Optional reason" />
              {rejectMsg && <Alert msg={rejectMsg} kind="ok" />}
              {rejectErr && <Alert msg={rejectErr} kind="err" />}
              <Btn label="Reject proposal" onClick={handleReject} variant="danger" />
            </div>
          </div>
        )}

        {/* Back */}
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <a href="/developer-console" style={{ fontSize: '0.8125rem', color: MUTED, textDecoration: 'none' }}>
            ← Back to developer console
          </a>
        </div>
      </div>
    </div>
  )
}
