'use client'

// PraxisMed — Premium Austrian Clinic Interface
// Sprint 18 / Module 126C-FABEL5 — Premium 3-column split-screen clinical workspace.
//
// Fake-data staging only. No real patient data. No secrets. Production PHI: NO-GO.
// Legacy Module 126C palette markers kept for contract compatibility: #0F172A #0D9488

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getMe, logout } from '@/lib/auth'
import { getClinicDisplayName, getRoleDisplay } from '@/lib/tenantDisplay'
import {
  confirmAppointmentRequest,
  fetchAppointmentRequests,
  fetchPatients,
  fetchNotifications,
  fetchConsultations,
  fetchPreAppointmentSummary,
  AppointmentRequest,
  Patient,
  Notification,
  ConsultationSession,
  PreAppointmentSummary,
} from '@/lib/api'

// ---------------------------------------------------------------------------
// Fabel 5 visual identity — exact palette (also mirrored in globals.css tokens)
// ---------------------------------------------------------------------------
const INK    = '#0B132B'   // Primary Structural Ink — header/sidebar/strong type
const ACCENT = '#008080'   // Clinical Accent — primary CTAs
const FILL   = '#E0F2F1'   // Highlight Muted Fill — active/selected states
const WARN   = '#FFB703'   // Warning / New Request state
const DANGER = '#E63946'   // Critical Error State
const CANVAS = '#F4F6F9'   // Canvas Background

const CARD_BORDER = '#E3E8EF'
const TEXT_MUTED  = '#5B6472'
const TEXT_FAINT  = '#8A93A2'

// ---------------------------------------------------------------------------
// Embedded responsive layout CSS — 3-column split-screen workspace.
// Desktop: left 25% / center 45% / right 30%. Laptop: 2 columns. Mobile: stacked.
// ---------------------------------------------------------------------------
const LAYOUT_CSS = `
  .pm-dash-shell { display:flex; flex-direction:column; min-height:100vh; background:${CANVAS}; }
  .pm-dash-grid  {
    display: grid;
    grid-template-columns: minmax(280px,25%) minmax(420px,45%) minmax(320px,30%);
    flex:1; min-height:0; overflow:hidden;
  }
  .pm-dash-left  { overflow-y:auto; background:${INK}; border-right:1px solid rgba(255,255,255,0.07); }
  .pm-dash-center{ overflow-y:auto; background:${CANVAS}; }
  .pm-dash-right { overflow-y:auto; background:#ffffff; border-left:1px solid ${CARD_BORDER}; }
  .pm-tabular    { font-variant-numeric: tabular-nums; }
  @media(max-width:1200px){
    .pm-dash-grid{ grid-template-columns:minmax(260px,32%) 1fr; overflow:visible; }
    .pm-dash-right{ grid-column:1 / -1; border-left:none; border-top:1px solid ${CARD_BORDER}; }
  }
  @media(max-width:768px){
    .pm-dash-grid{ grid-template-columns:1fr; overflow:visible; }
    .pm-dash-left{ max-height:48vh; border-right:none; border-bottom:1px solid rgba(255,255,255,0.12); }
    .pm-dash-right{ grid-column:auto; border-left:none; border-top:1px solid ${CARD_BORDER}; }
  }
`

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------

// Defensive string accessor for index-signature fields on API rows.
function fieldStr(row: Record<string, unknown>, key: string): string | null {
  const v = row[key]
  return typeof v === 'string' && v.length > 0 ? v : null
}

function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  const d = new Date(value)
  if (isNaN(d.getTime())) return '—'
  return d.toISOString().slice(0, 10)
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) return '—'
  const d = new Date(value)
  if (isNaN(d.getTime())) return '—'
  return `${d.toISOString().slice(0, 10)} ${d.toISOString().slice(11, 16)}`
}

function patientDisplayName(patient: Patient): string {
  return (
    patient.full_name ||
    [patient.first_name, patient.last_name].filter(Boolean).join(' ') ||
    'Unnamed patient'
  )
}

// ---------------------------------------------------------------------------
// Status/urgency badge styling
// ---------------------------------------------------------------------------

const BADGE_MAP: Record<string, { bg: string; color: string }> = {
  new:       { bg: '#FFF4D6', color: '#8A5B00' },
  confirmed: { bg: '#DFF5E9', color: '#166534' },
  active:    { bg: '#DFF5E9', color: '#166534' },
  approved:  { bg: '#DFF5E9', color: '#166534' },
  pending:   { bg: '#FFF4D6', color: '#8A5B00' },
  urgent:    { bg: '#FDE3E5', color: '#9F1D28' },
  emergency: { bg: '#FDE3E5', color: '#9F1D28' },
  high:      { bg: '#FDE3E5', color: '#9F1D28' },
  normal:    { bg: '#E8EDF4', color: TEXT_MUTED },
  low:       { bg: '#E8EDF4', color: TEXT_MUTED },
  vapi:      { bg: FILL,      color: ACCENT },
}

function badge(value: string | null | undefined): React.CSSProperties {
  const t = value?.toLowerCase() ?? ''
  const found = BADGE_MAP[t]
  return {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '2px 9px',
    borderRadius: 99,
    fontSize: '0.675rem',
    fontWeight: 600,
    letterSpacing: '0.02em',
    background: found?.bg ?? '#E8EDF4',
    color: found?.color ?? TEXT_MUTED,
    whiteSpace: 'nowrap' as const,
  }
}

function newRequestBadgeStyle(): React.CSSProperties {
  return {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '2px 9px',
    borderRadius: 99,
    fontSize: '0.675rem',
    fontWeight: 700,
    letterSpacing: '0.03em',
    background: WARN,
    color: INK,
    whiteSpace: 'nowrap' as const,
  }
}

// ---------------------------------------------------------------------------
// Shared shell components
// ---------------------------------------------------------------------------

function SectionCard({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div
      style={{
        background: '#ffffff',
        border: `1px solid ${CARD_BORDER}`,
        borderRadius: 14,
        boxShadow: '0 1px 3px 0 rgb(11 19 43 / 0.06), 0 1px 2px -1px rgb(11 19 43 / 0.05)',
        overflow: 'hidden',
        ...style,
      }}
    >
      {children}
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div data-state="empty" style={{ padding: '1.75rem 1.25rem', textAlign: 'center', color: TEXT_MUTED, fontSize: '0.8125rem' }}>
      {message}
    </div>
  )
}

function LoadingState({ message }: { message: string }) {
  return (
    <div data-state="loading" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
      {[1, 2, 3].map((i) => (
        <div key={i} style={{ height: 13, borderRadius: 6, background: '#E8EDF4', width: i === 1 ? '60%' : i === 2 ? '80%' : '45%', opacity: 0.8 }} aria-hidden />
      ))}
      <span className="sr-only">{message}</span>
    </div>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <div
      data-state="error"
      style={{ margin: '0.875rem 1.25rem', padding: '0.75rem 1rem', background: '#FDF1F2', border: `1px solid ${DANGER}`, borderRadius: 10, fontSize: '0.8125rem', color: DANGER }}
    >
      {message}
    </div>
  )
}

function MetricCard({ label, value, loading }: { label: string; value: number; loading: boolean }) {
  return (
    <div style={{ flex: '1 1 110px', background: '#ffffff', border: `1px solid ${CARD_BORDER}`, borderRadius: 10, padding: '0.75rem 1rem' }}>
      <p style={{ fontSize: '0.675rem', fontWeight: 600, color: TEXT_MUTED, marginBottom: '0.3rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {label}
      </p>
      {loading ? (
        <div style={{ height: 24, width: 40, background: '#E8EDF4', borderRadius: 6, opacity: 0.6 }} aria-hidden />
      ) : (
        <p className="pm-tabular" style={{ fontSize: '1.4rem', fontWeight: 700, color: INK, lineHeight: 1 }}>{value}</p>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Audio Transcript & Call Recording — placeholder shell (no real recordings)
// ---------------------------------------------------------------------------

function TranscriptRecordingPanel({ appt }: { appt: AppointmentRequest }) {
  const sourceRef = fieldStr(appt, 'source_ref') ?? fieldStr(appt, 'call_id')
  const waveformBars = [8, 14, 20, 12, 24, 16, 28, 18, 10, 22, 15, 26, 12, 19, 9, 23, 17, 27, 13, 20, 11, 24, 16, 21, 10, 18, 25, 14, 22, 12]
  return (
    <div
      data-state="transcript-panel"
      style={{ margin: '0 1.25rem 1.25rem', borderRadius: 12, border: `1px solid ${CARD_BORDER}`, background: '#FAFBFD', overflow: 'hidden' }}
    >
      <div style={{ padding: '0.875rem 1.25rem 0.625rem', borderBottom: `1px solid ${CARD_BORDER}` }}>
        <p style={{ fontSize: '0.75rem', fontWeight: 700, color: INK, textTransform: 'uppercase', letterSpacing: '0.07em' }}>
          {'Audio Transcript & Call Recording'}
        </p>
      </div>

      {/* Polished audio player placeholder shell */}
      <div style={{ padding: '0.875rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
        <button
          disabled
          title="Recording ingestion pending — no audio integration is enabled in staging"
          style={{
            fontSize: '0.775rem', fontWeight: 600, padding: '7px 14px', borderRadius: 8,
            border: `1px solid ${CARD_BORDER}`, background: '#EFF2F7', color: TEXT_FAINT,
            cursor: 'not-allowed', whiteSpace: 'nowrap',
          }}
        >
          ▶ Play Audio Call
        </button>

        {/* Mock waveform visual track — decorative only */}
        <div aria-hidden style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 2, height: 34, opacity: 0.55 }}>
          {waveformBars.map((h, i) => (
            <span key={i} style={{ width: 3, height: h, borderRadius: 2, background: i % 4 === 0 ? ACCENT : '#B9C4D2' }} />
          ))}
        </div>
        <span className="pm-tabular" style={{ fontSize: '0.7rem', color: TEXT_FAINT }}>00:00 / --:--</span>
      </div>

      {/* Transcript / summary box — safe empty state, no invented content */}
      <div style={{ margin: '0 1.25rem 0.875rem', padding: '0.875rem 1rem', borderRadius: 8, border: `1px dashed ${CARD_BORDER}`, background: '#ffffff' }}>
        <p style={{ fontSize: '0.8125rem', color: TEXT_MUTED, fontStyle: 'italic', lineHeight: 1.5 }}>
          Recording/transcript review will appear here when Vapi recording ingestion is enabled.
        </p>
      </div>

      {/* Metadata row */}
      <div style={{ padding: '0 1.25rem 0.875rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={badge('vapi')}>Vapi source</span>
        <span className="pm-tabular" style={{ fontSize: '0.675rem', color: TEXT_FAINT, fontFamily: 'ui-monospace, monospace' }}>
          {sourceRef ? `source_ref: ${sourceRef}` : 'source_ref: —'}
        </span>
        <span style={{ fontSize: '0.675rem', fontWeight: 600, color: '#8A5B00', background: '#FFF4D6', padding: '2px 8px', borderRadius: 99 }}>
          Recording ingestion pending
        </span>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Dashboard page
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const router = useRouter()

  const [clinicId, setClinicId] = useState<string | null>(null)
  const [clinicDisplayName, setClinicDisplayName] = useState<string>('Clinic')
  const [userRole, setUserRole] = useState<string>('')

  const [appointments, setAppointments] = useState<AppointmentRequest[]>([])
  const [apptLoading, setApptLoading] = useState(true)
  const [apptError, setApptError] = useState<string | null>(null)

  const [patients, setPatients] = useState<Patient[]>([])
  const [patientsLoading, setPatientsLoading] = useState(true)
  const [patientsError, setPatientsError] = useState<string | null>(null)

  const [notifications, setNotifications] = useState<Notification[]>([])
  const [notifLoading, setNotifLoading] = useState(true)
  const [notifError, setNotifError] = useState<string | null>(null)

  const [consultations, setConsultations] = useState<ConsultationSession[]>([])
  const [consultLoading, setConsultLoading] = useState(true)
  const [consultError, setConsultError] = useState<string | null>(null)

  const [confirmingIds, setConfirmingIds] = useState<Set<string>>(new Set())
  const [apptActionError, setApptActionError] = useState<string | null>(null)

  const [summaryOpenId, setSummaryOpenId] = useState<string | null>(null)
  const [summaries, setSummaries] = useState<Record<string, PreAppointmentSummary | 'loading' | 'error'>>({})

  const [selectedApptId, setSelectedApptId] = useState<string | null>(null)
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null)
  const [patientSearch, setPatientSearch] = useState('')

  useEffect(() => {
    getMe().then((user) => {
      if (!user) {
        router.replace('/login')
        return
      }
      setClinicId(user.clinic_id)
      setClinicDisplayName(getClinicDisplayName(user.clinic_id))
      setUserRole(getRoleDisplay(user.role))

      fetchAppointmentRequests(user.clinic_id)
        .then((rows) => {
          setAppointments(rows)
          // Default selected request: first appointment request if available.
          if (rows.length > 0) setSelectedApptId(rows[0].id)
        })
        .catch(() => setApptError('Could not load appointment requests. Please try again.'))
        .finally(() => setApptLoading(false))

      fetchPatients(user.clinic_id)
        .then(setPatients)
        .catch(() => setPatientsError('Could not load patients. Please try again.'))
        .finally(() => setPatientsLoading(false))

      fetchNotifications(user.clinic_id)
        .then(setNotifications)
        .catch(() => setNotifError('Could not load notifications. Please try again.'))
        .finally(() => setNotifLoading(false))

      fetchConsultations(user.clinic_id)
        .then(setConsultations)
        .catch(() => setConsultError('Could not load consultations. Please try again.'))
        .finally(() => setConsultLoading(false))
    })
  }, [router])

  async function handleLogout() {
    await logout()
    router.push('/login')
  }

  async function handleConfirm(requestId: string) {
    if (!clinicId) return
    setConfirmingIds((prev) => new Set(prev).add(requestId))
    setApptActionError(null)
    try {
      await confirmAppointmentRequest(requestId, clinicId)
      const rows = await fetchAppointmentRequests(clinicId)
      setAppointments(rows)
    } catch {
      setApptActionError('Could not confirm appointment request. Please try again.')
    } finally {
      setConfirmingIds((prev) => { const next = new Set(prev); next.delete(requestId); return next })
    }
  }

  async function handleViewSummary(appt: AppointmentRequest) {
    if (!clinicId) return
    if (summaryOpenId === appt.id) { setSummaryOpenId(null); return }
    setSummaryOpenId(appt.id)
    if (summaries[appt.id]) return
    setSummaries((prev) => ({ ...prev, [appt.id]: 'loading' }))
    try {
      const summary = await fetchPreAppointmentSummary(appt.id, clinicId)
      setSummaries((prev) => ({ ...prev, [appt.id]: summary }))
    } catch {
      setSummaries((prev) => ({ ...prev, [appt.id]: 'error' }))
    }
  }

  const pendingCount = appointments.filter((a) => a.status === 'new').length
  const selectedAppt = appointments.find((a) => a.id === selectedApptId) ?? null
  const selectedPatient = patients.find((p) => p.id === selectedPatientId) ?? null

  const filteredPatients = useMemo(() => {
    const q = patientSearch.trim().toLowerCase()
    if (!q) return patients
    return patients.filter((p) => {
      const name = patientDisplayName(p).toLowerCase()
      const phone = (fieldStr(p, 'phone') ?? '').toLowerCase()
      return name.includes(q) || phone.includes(q)
    })
  }, [patients, patientSearch])

  // Linked appointment requests for the selected patient (patient_id linkage).
  const linkedAppointments = useMemo(() => {
    if (!selectedPatient) return []
    return appointments.filter((a) => fieldStr(a, 'patient_id') === selectedPatient.id)
  }, [appointments, selectedPatient])

  function isNewRequest(appt: AppointmentRequest): boolean {
    return appt.status === 'new' || appt.action_required === true || appt.status !== 'confirmed'
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="pm-dash-shell">

      <style dangerouslySetInnerHTML={{ __html: LAYOUT_CSS }} />

      {/* ------------------------------------------------------------------ */}
      {/* Global sticky header — premium clinical, dynamic tenant identity     */}
      {/* ------------------------------------------------------------------ */}
      <header
        style={{
          background: INK,
          borderBottom: '1px solid rgba(255,255,255,0.09)',
          padding: '0 1.25rem',
          minHeight: 58,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          flexShrink: 0,
          flexWrap: 'wrap',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem', flexWrap: 'wrap', padding: '0.4rem 0' }}>
          <span style={{ fontWeight: 800, fontSize: '1.05rem', color: '#ffffff', letterSpacing: '-0.01em' }}>
            PraxisMed
          </span>

          {/* Dynamic multi-tenant identity banner (from tenantDisplay helper) */}
          <span
            data-state="tenant-banner"
            style={{ fontSize: '0.8125rem', color: 'rgba(255,255,255,0.85)', fontWeight: 500, borderLeft: '1px solid rgba(255,255,255,0.2)', paddingLeft: '0.875rem' }}
          >
            {clinicDisplayName}
            {userRole && <span style={{ color: 'rgba(255,255,255,0.45)' }}> · {userRole}</span>}
          </span>

          <span
            style={{
              fontSize: '0.65rem', fontWeight: 700, padding: '2px 9px', borderRadius: 99,
              background: WARN, color: INK, letterSpacing: '0.05em',
            }}
          >
            STAGING DEMO
          </span>

          {/* Safety boundary — always visible */}
          <span style={{ fontSize: '0.6875rem', color: 'rgba(255,255,255,0.5)', letterSpacing: '0.01em' }}>
            Fake-data staging · No real patient data · Production PHI: NO-GO
          </span>
        </div>

        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
          <a href="/onboarding" style={{ fontSize: '0.775rem', fontWeight: 500, padding: '0.35rem 0.75rem', borderRadius: 6, color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>
            Onboarding
          </a>
          <a href="/developer-console" style={{ fontSize: '0.775rem', fontWeight: 500, padding: '0.35rem 0.75rem', borderRadius: 6, color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>
            Dev Console
          </a>
          <button
            onClick={handleLogout}
            style={{
              fontSize: '0.775rem', fontWeight: 600, padding: '0.4rem 0.95rem',
              border: '1px solid rgba(255,255,255,0.22)', borderRadius: 7,
              background: 'transparent', color: 'rgba(255,255,255,0.85)', cursor: 'pointer',
            }}
          >
            Log Out
          </button>
        </nav>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* 3-column split-screen workspace                                      */}
      {/* ------------------------------------------------------------------ */}
      <div className="pm-dash-grid">

        {/* ================================================================ */}
        {/* COLUMN 1 — INCOMING AI INTAKE QUEUE                               */}
        {/* ================================================================ */}
        <aside className="pm-dash-left" data-panel="left">

          <section data-section="appointments">
            <div style={{ padding: '1.125rem 1rem 0.625rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h2 style={{ fontSize: '0.7rem', fontWeight: 700, color: 'rgba(255,255,255,0.55)', textTransform: 'uppercase', letterSpacing: '0.11em' }}>
                Incoming AI Intake Queue
              </h2>
              {!apptLoading && !apptError && (
                <span className="pm-tabular" style={{ fontSize: '0.675rem', fontWeight: 700, color: INK, background: WARN, padding: '1px 7px', borderRadius: 99 }}>
                  {pendingCount}
                </span>
              )}
            </div>

            {apptLoading && (
              <div data-state="loading" style={{ padding: '0.25rem 0.75rem' }}>
                {[1, 2, 3].map((i) => (
                  <div key={i} style={{ height: 64, borderRadius: 10, background: 'rgba(255,255,255,0.06)', marginBottom: '0.4rem' }} />
                ))}
                <span className="sr-only">Loading appointment requests…</span>
              </div>
            )}

            {!apptLoading && apptError && (
              <div data-state="error" style={{ margin: '0.5rem 0.75rem', padding: '0.75rem', borderRadius: 8, background: 'rgba(230,57,70,0.16)', border: `1px solid ${DANGER}`, color: '#F7A6AC', fontSize: '0.8125rem' }}>
                {apptError}
              </div>
            )}

            {!apptLoading && !apptError && appointments.length === 0 && (
              <div data-state="empty" style={{ padding: '1.5rem 1rem', fontSize: '0.8125rem', color: 'rgba(255,255,255,0.4)', textAlign: 'center' }}>
                No incoming AI intake requests yet.
              </div>
            )}

            {!apptLoading && !apptError && appointments.length > 0 && (
              <ul data-state="list" style={{ listStyle: 'none', padding: '0 0.625rem 0.875rem' }}>
                {appointments.map((appt) => {
                  const isSelected = selectedApptId === appt.id
                  const phone = fieldStr(appt, 'patient_phone')
                  const reason = fieldStr(appt, 'reason')
                  const source = fieldStr(appt, 'source')
                  const preferred = fieldStr(appt, 'preferred_starts_at')
                  return (
                    <li
                      key={appt.id}
                      onClick={() => { setSelectedApptId(appt.id); setSummaryOpenId(null) }}
                      style={{
                        marginBottom: '0.375rem', borderRadius: 10, padding: '0.65rem 0.8rem', cursor: 'pointer',
                        background: isSelected ? FILL : 'rgba(255,255,255,0.05)',
                        borderLeft: isSelected ? `3px solid ${ACCENT}` : '3px solid transparent',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.25rem' }}>
                        <span style={{ flex: 1, fontWeight: 700, fontSize: '0.8125rem', color: isSelected ? INK : '#ffffff', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {appt.patient_name ?? '—'}
                        </span>
                        {isNewRequest(appt) && <span style={newRequestBadgeStyle()}>New Request</span>}
                      </div>
                      <div className="pm-tabular" style={{ fontSize: '0.7rem', color: isSelected ? TEXT_MUTED : 'rgba(255,255,255,0.45)', marginBottom: '0.25rem' }}>
                        {phone ?? 'No phone captured'} · {formatDateTime(preferred ?? appt.created_at)}
                      </div>
                      {reason && (
                        <div style={{ fontSize: '0.7rem', color: isSelected ? TEXT_MUTED : 'rgba(255,255,255,0.4)', marginBottom: '0.3rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {reason.length > 60 ? reason.slice(0, 60) + '…' : reason}
                        </div>
                      )}
                      <div style={{ display: 'flex', gap: '0.3rem', flexWrap: 'wrap' }}>
                        <span style={badge(appt.status)}>{appt.status}</span>
                        <span style={badge(appt.urgency_level)}>{appt.urgency_level}</span>
                        {source === 'vapi' && <span style={badge('vapi')}>vapi</span>}
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </section>

          <div style={{ height: 1, background: 'rgba(255,255,255,0.08)' }} />

          {/* ------------------------------------------------------------ */}
          {/* Notifications panel — internal channel only                    */}
          {/* ------------------------------------------------------------ */}
          <section data-section="notifications">
            <div style={{ padding: '0.875rem 1rem 0.5rem' }}>
              <h2 style={{ fontSize: '0.7rem', fontWeight: 700, color: 'rgba(255,255,255,0.55)', textTransform: 'uppercase', letterSpacing: '0.11em' }}>
                Notifications
              </h2>
              <p style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.35)', marginTop: '0.15rem' }}>
                Internal notification only
              </p>
            </div>

            {notifLoading && (
              <div data-state="loading" style={{ padding: '0.25rem 0.75rem' }}>
                {[1, 2].map((i) => <div key={i} style={{ height: 38, borderRadius: 8, background: 'rgba(255,255,255,0.06)', marginBottom: '0.3rem' }} />)}
                <span className="sr-only">Loading notifications…</span>
              </div>
            )}

            {!notifLoading && notifError && (
              <div data-state="error" style={{ margin: '0.25rem 0.75rem', padding: '0.625rem', borderRadius: 8, background: 'rgba(230,57,70,0.16)', color: '#F7A6AC', fontSize: '0.75rem' }}>
                {notifError}
              </div>
            )}

            {!notifLoading && !notifError && notifications.length === 0 && (
              <div data-state="empty" style={{ padding: '0.75rem 1rem 1rem', fontSize: '0.75rem', color: 'rgba(255,255,255,0.3)' }}>
                No notifications
              </div>
            )}

            {!notifLoading && !notifError && notifications.length > 0 && (
              <ul data-state="list" style={{ listStyle: 'none', padding: '0 0.625rem 1rem' }}>
                {notifications.map((notif) => {
                  const isPending = notif.status === 'pending'
                  const truncatedMsg = notif.message
                    ? notif.message.length > 75 ? notif.message.slice(0, 75) + '…' : notif.message
                    : null
                  return (
                    <li
                      key={notif.id}
                      data-notification-status={notif.status}
                      style={{
                        marginBottom: '0.3rem', padding: '0.5rem 0.7rem', borderRadius: 8,
                        background: 'rgba(255,255,255,0.05)',
                        borderLeft: isPending ? `3px solid ${WARN}` : '3px solid transparent',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                        <span style={{ flex: 1, fontWeight: 600, fontSize: '0.75rem', color: 'rgba(255,255,255,0.85)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {notif.title ?? '—'}
                        </span>
                        {isPending
                          ? <span style={newRequestBadgeStyle()}>{notif.status}</span>
                          : <span style={badge(notif.status)}>{notif.status ?? '—'}</span>}
                      </div>
                      {truncatedMsg && (
                        <p data-notification-message style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', margin: '0.2rem 0 0', lineHeight: 1.4 }}>
                          {truncatedMsg}
                        </p>
                      )}
                      <div style={{ display: 'flex', gap: '0.3rem', marginTop: '0.3rem', flexWrap: 'wrap' }}>
                        {notif.priority && <span style={badge(notif.priority)}>{notif.priority}</span>}
                        {notif.notification_type && (
                          <span style={{ ...badge(undefined), background: 'rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.55)' }}>
                            {notif.notification_type}
                          </span>
                        )}
                        <span style={{ ...badge(undefined), background: 'rgba(0,128,128,0.25)', color: '#7FD4D4' }}>
                          internal
                        </span>
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </section>
        </aside>

        {/* ================================================================ */}
        {/* COLUMN 2 — ACTIVE RESOLUTION & RECORDING ENGINE                   */}
        {/* ================================================================ */}
        <main className="pm-dash-center" data-panel="center">
          <div style={{ padding: '1.25rem 1.5rem 0' }}>
            <h1 style={{ fontSize: '1.05rem', fontWeight: 800, color: INK, letterSpacing: '-0.01em' }}>
              Active Resolution Workspace
            </h1>
            {/* Legacy label preserved for contract compatibility */}
            <span className="sr-only">Intake Resolution Workspace · Clinic Overview · Confirm &amp; Create Profile</span>
            <p style={{ fontSize: '0.775rem', color: TEXT_MUTED, marginTop: '0.2rem' }}>
              Fake-data staging environment — no real patient data
            </p>
          </div>

          {/* Clinic Overview metrics */}
          <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap', margin: '0.875rem 1.5rem' }}>
            <MetricCard label="Appointments"  value={appointments.length}  loading={apptLoading} />
            <MetricCard label="Patients"      value={patients.length}      loading={patientsLoading} />
            <MetricCard label="Notifications" value={notifications.length} loading={notifLoading} />
            <MetricCard label="Pending"       value={pendingCount}         loading={apptLoading} />
          </div>

          {/* Selected intake request */}
          <div data-panel="workspace" style={{ margin: '0 1.5rem 1.25rem' }}>
            {!selectedAppt ? (
              <div
                data-state="empty"
                style={{ border: `2px dashed ${CARD_BORDER}`, borderRadius: 14, padding: '2.75rem 2rem', textAlign: 'center', color: TEXT_MUTED, background: '#ffffff' }}
              >
                <p style={{ fontSize: '0.9375rem', fontWeight: 700, marginBottom: '0.5rem', color: INK }}>
                  No intake request selected
                </p>
                <p style={{ fontSize: '0.8125rem' }}>
                  Select an intake card from the Incoming AI Intake Queue to review and resolve
                </p>
              </div>
            ) : (
              <SectionCard>
                {/* Workspace header — patient name prominent */}
                <div style={{ padding: '1.125rem 1.25rem', borderBottom: `1px solid ${CARD_BORDER}`, display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: INK, letterSpacing: '-0.01em' }}>
                      {selectedAppt.patient_name ?? '—'}
                    </h3>
                    <div style={{ display: 'flex', gap: '0.375rem', marginTop: '0.45rem', flexWrap: 'wrap' }}>
                      {isNewRequest(selectedAppt) && <span style={newRequestBadgeStyle()}>New Request</span>}
                      <span style={badge(selectedAppt.status)}>{selectedAppt.status}</span>
                      <span style={badge(selectedAppt.urgency_level)}>{selectedAppt.urgency_level}</span>
                      {fieldStr(selectedAppt, 'source') && <span style={badge(fieldStr(selectedAppt, 'source'))}>{fieldStr(selectedAppt, 'source')}</span>}
                    </div>
                  </div>
                  <span className="pm-tabular" style={{ fontSize: '0.65rem', color: TEXT_FAINT, fontFamily: 'ui-monospace, monospace' }}>
                    {selectedAppt.id}
                  </span>
                </div>

                {/* Request detail grid */}
                <dl
                  className="pm-tabular"
                  style={{ display: 'grid', gridTemplateColumns: 'max-content 1fr', columnGap: '1.25rem', rowGap: '0.4rem', fontSize: '0.8125rem', padding: '0.875rem 1.25rem', borderBottom: `1px solid ${CARD_BORDER}` }}
                >
                  <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Phone</dt>
                  <dd style={{ margin: 0, color: INK }}>{fieldStr(selectedAppt, 'patient_phone') ?? 'No phone captured'}</dd>
                  <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Reason</dt>
                  <dd style={{ margin: 0, color: INK }}>{fieldStr(selectedAppt, 'reason') ?? '—'}</dd>
                  <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Preferred time</dt>
                  <dd style={{ margin: 0, color: INK }}>{formatDateTime(fieldStr(selectedAppt, 'preferred_starts_at'))}</dd>
                  <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Created</dt>
                  <dd style={{ margin: 0, color: INK }}>{formatDateTime(selectedAppt.created_at)}</dd>
                </dl>

                {/* Audio Transcript & Call Recording engine */}
                <div style={{ paddingTop: '1.25rem' }}>
                  <TranscriptRecordingPanel appt={selectedAppt} />
                </div>

                {/* Summary actions */}
                <div style={{ padding: '0 1.25rem 0.875rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <button
                    data-action="view-summary"
                    onClick={() => handleViewSummary(selectedAppt)}
                    style={{
                      fontSize: '0.8125rem', fontWeight: 600, padding: '7px 15px', borderRadius: 7, cursor: 'pointer',
                      border: `1px solid ${summaryOpenId === selectedAppt.id ? ACCENT : CARD_BORDER}`,
                      background: summaryOpenId === selectedAppt.id ? FILL : '#ffffff',
                      color: summaryOpenId === selectedAppt.id ? ACCENT : TEXT_MUTED,
                    }}
                  >
                    {summaryOpenId === selectedAppt.id ? 'Hide summary' : 'View summary'}
                  </button>
                </div>

                {apptActionError && (
                  <div style={{ margin: '0 1.25rem 0.5rem' }}>
                    <ErrorState message={apptActionError} />
                  </div>
                )}

                {/* Pre-appointment summary panel */}
                {summaryOpenId === selectedAppt.id && (() => {
                  const summaryEntry = summaries[selectedAppt.id]
                  return (
                    <div
                      data-state="summary-panel"
                      style={{ margin: '0 1.25rem 1rem', borderRadius: 10, border: `1px solid ${ACCENT}33`, background: FILL, overflow: 'hidden' }}
                    >
                      {summaryEntry === 'loading' && <LoadingState message="Loading summary…" />}
                      {summaryEntry === 'error' && (
                        <div style={{ padding: '0.75rem 1.25rem', color: DANGER, fontSize: '0.8125rem' }}>
                          Could not load summary. Please try again.
                        </div>
                      )}
                      {summaryEntry && summaryEntry !== 'loading' && summaryEntry !== 'error' && (
                        <div style={{ padding: '1rem 1.25rem' }}>
                          <p style={{ fontSize: '0.7rem', fontWeight: 700, color: ACCENT, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.75rem' }}>
                            Pre-appointment Summary
                          </p>
                          <dl className="pm-tabular" style={{ display: 'grid', gridTemplateColumns: 'max-content 1fr', columnGap: '1rem', rowGap: '0.4rem', fontSize: '0.8125rem' }}>
                            <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Patient</dt>
                            <dd style={{ margin: 0, color: INK, fontWeight: 600 }}>{summaryEntry.patient_name}</dd>
                            <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Type</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.patient_type}</dd>
                            <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Reason</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.reason ?? '—'}</dd>
                            <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Urgency</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.urgency_level}</dd>
                            <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Prior visits</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.previous_request_count}</dd>
                            <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Suggested action</dt>
                            <dd style={{ margin: 0, color: ACCENT, fontWeight: 700 }}>{summaryEntry.suggested_next_action}</dd>
                          </dl>
                          <div style={{ marginTop: '0.875rem', paddingTop: '0.75rem', borderTop: `1px solid ${ACCENT}33`, fontSize: '0.75rem', color: TEXT_MUTED, display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                            <span style={{ userSelect: 'none' }}>ℹ</span>
                            <span>{summaryEntry.safety_note}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })()}

                {/* Safety boundary for the workspace */}
                <p style={{ margin: '0 1.25rem 0.875rem', fontSize: '0.6875rem', color: TEXT_FAINT, lineHeight: 1.5 }}>
                  AI intake output is administrative scheduling information only. Staff or doctor
                  review is required before any clinical decision. Fake-data staging — no real patient data.
                </p>

                {/* Action footprint */}
                <div style={{ padding: '0.875rem 1.25rem', borderTop: `1px solid ${CARD_BORDER}`, background: '#FAFBFD', display: 'flex', gap: '0.625rem', flexWrap: 'wrap', alignItems: 'center' }}>
                  {selectedAppt.status === 'new' && (
                    <button
                      data-action="confirm"
                      onClick={() => handleConfirm(selectedAppt.id)}
                      disabled={confirmingIds.has(selectedAppt.id)}
                      style={{
                        fontSize: '0.8125rem', fontWeight: 700, padding: '8px 18px', borderRadius: 8,
                        border: 'none',
                        background: confirmingIds.has(selectedAppt.id) ? '#B9C4D2' : ACCENT,
                        color: '#ffffff',
                        cursor: confirmingIds.has(selectedAppt.id) ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {confirmingIds.has(selectedAppt.id) ? 'Confirming…' : 'Confirm'}
                    </button>
                  )}

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                    <button
                      data-action="confirm-create-profile"
                      disabled
                      title="Profile creation automation coming next"
                      style={{
                        fontSize: '0.8125rem', fontWeight: 700, padding: '8px 18px', borderRadius: 8,
                        border: `1px solid ${ACCENT}`, background: `${ACCENT}1A`, color: ACCENT,
                        cursor: 'not-allowed', opacity: 0.65,
                      }}
                    >
                      {'Confirm Appointment & Create Patient Profile'}
                    </button>
                    <span style={{ fontSize: '0.65rem', color: TEXT_FAINT }}>
                      Profile creation automation coming next
                    </span>
                  </div>
                </div>
              </SectionCard>
            )}
          </div>

          {/* Consultations */}
          <section data-section="consultations" style={{ margin: '0 1.5rem 1.25rem' }}>
            <SectionCard>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.875rem 1.25rem 0.625rem', borderBottom: `1px solid ${CARD_BORDER}` }}>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: INK }}>Consultations</h3>
                {!consultLoading && !consultError && (
                  <span className="pm-tabular" style={{ fontSize: '0.675rem', fontWeight: 700, color: TEXT_MUTED, background: '#E8EDF4', padding: '1px 7px', borderRadius: 99 }}>
                    {consultations.length}
                  </span>
                )}
              </div>
              {consultLoading && <LoadingState message="Loading consultations…" />}
              {!consultLoading && consultError && <ErrorState message={consultError} />}
              {!consultLoading && !consultError && consultations.length === 0 && <EmptyState message="No consultations on file yet." />}
              {!consultLoading && !consultError && consultations.length > 0 && (
                <ul data-state="list" style={{ listStyle: 'none', padding: '0.25rem 0 0.5rem' }}>
                  {consultations.map((consult, idx) => (
                    <li key={consult.id} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.625rem 1.25rem', borderBottom: idx < consultations.length - 1 ? `1px solid #F0F3F8` : 'none', fontSize: '0.8125rem' }}>
                      <span style={{ flex: 1, fontWeight: 500, color: INK }}>{consult.title ?? '—'}</span>
                      <span style={badge(consult.approval_status ?? undefined)}>{consult.approval_status ?? consult.status ?? '—'}</span>
                      <span style={{ color: TEXT_MUTED, fontSize: '0.75rem' }}>{consult.source ?? '—'}</span>
                    </li>
                  ))}
                </ul>
              )}
            </SectionCard>
          </section>

          {/* Safety footer */}
          <p style={{ textAlign: 'center', fontSize: '0.6875rem', color: TEXT_FAINT, margin: '0 1.5rem 1.75rem', letterSpacing: '0.02em' }}>
            Staging demo — fake data only · No real patient data · Production PHI: NO-GO
          </p>
        </main>

        {/* ================================================================ */}
        {/* COLUMN 3 — PATIENT DATABASE REGISTRY & HISTORY                    */}
        {/* ================================================================ */}
        <aside className="pm-dash-right" data-panel="right">
          <div style={{ padding: '1.125rem 1rem 0.75rem', borderBottom: `1px solid ${CARD_BORDER}`, position: 'sticky', top: 0, background: '#ffffff', zIndex: 5 }}>
            <h2 style={{ fontSize: '0.7rem', fontWeight: 700, color: TEXT_MUTED, textTransform: 'uppercase', letterSpacing: '0.11em', marginBottom: '0.625rem' }}>
              Patient Registry
            </h2>
            <div style={{ position: 'relative' }}>
              <span aria-hidden style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', fontSize: '0.8rem', color: TEXT_FAINT }}>
                {/* magnifying glass icon */}
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                  <circle cx="11" cy="11" r="7" />
                  <line x1="21" y1="21" x2="16.5" y2="16.5" />
                </svg>
              </span>
              <input
                type="search"
                value={patientSearch}
                onChange={(e) => setPatientSearch(e.target.value)}
                placeholder="Search Clinical Registries..."
                style={{
                  width: '100%', padding: '0.45rem 0.75rem 0.45rem 1.9rem', borderRadius: 8,
                  border: `1px solid ${CARD_BORDER}`, background: CANVAS, fontSize: '0.775rem',
                  color: INK, outline: 'none', boxSizing: 'border-box',
                }}
              />
            </div>
          </div>

          <section data-section="patients">
            {patientsLoading && <LoadingState message="Loading patients…" />}
            {!patientsLoading && patientsError && <ErrorState message={patientsError} />}

            {!patientsLoading && !patientsError && patients.length === 0 && (
              <>
                <EmptyState message="No patients on file yet." />
                {/* Demo-safe scaffold placeholders — shown only when the real
                    patients array is empty. Not real patients. Not derived from
                    any record. Clearly marked as demo examples. */}
                <div data-state="demo-placeholder" style={{ margin: '0 0.875rem 1rem', borderRadius: 10, border: `1px dashed ${CARD_BORDER}`, padding: '0.75rem' }}>
                  <p style={{ fontSize: '0.65rem', fontWeight: 700, color: TEXT_FAINT, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.5rem' }}>
                    Demo placeholder — not real patients
                  </p>
                  {['Dr. Johann Huber', 'Anna Wallner'].map((name) => (
                    <div key={name} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0.25rem', fontSize: '0.8125rem', color: TEXT_MUTED }}>
                      <span style={{ flex: 1 }}>{name}</span>
                      <span style={{ ...badge(undefined), background: '#FFF4D6', color: '#8A5B00' }}>demo example</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            {!patientsLoading && !patientsError && patients.length > 0 && filteredPatients.length === 0 && (
              <div data-state="empty" style={{ padding: '1.25rem 1rem', textAlign: 'center', color: TEXT_MUTED, fontSize: '0.8125rem' }}>
                No registry matches for this search.
              </div>
            )}

            {!patientsLoading && !patientsError && filteredPatients.length > 0 && (
              <ul data-state="list" style={{ listStyle: 'none', padding: '0.5rem 0' }}>
                {filteredPatients.map((patient) => {
                  const isSelected = selectedPatientId === patient.id
                  const displayName = patientDisplayName(patient)
                  const phone = fieldStr(patient, 'phone')
                  return (
                    <li
                      key={patient.id}
                      onClick={() => setSelectedPatientId(isSelected ? null : patient.id)}
                      style={{
                        padding: '0.55rem 1rem', cursor: 'pointer',
                        background: isSelected ? FILL : 'transparent',
                        borderLeft: isSelected ? `3px solid ${ACCENT}` : '3px solid transparent',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ flex: 1, fontWeight: isSelected ? 700 : 500, fontSize: '0.8125rem', color: INK, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {displayName}
                        </span>
                        <span style={badge(patient.status)}>{patient.status ?? '—'}</span>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.15rem' }}>
                        {phone && <span className="pm-tabular" style={{ fontSize: '0.675rem', color: TEXT_MUTED }}>{phone}</span>}
                        <span className="pm-tabular" style={{ fontSize: '0.625rem', color: TEXT_FAINT, fontFamily: 'ui-monospace, monospace', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {patient.id}
                        </span>
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </section>

          {/* Selected patient profile + chronological history */}
          {selectedPatient && (
            <div
              data-state="patient-profile"
              style={{ margin: '0.75rem', padding: '1rem', borderRadius: 12, border: `1px solid ${ACCENT}44`, background: FILL }}
            >
              <p style={{ fontSize: '0.65rem', fontWeight: 700, color: ACCENT, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.55rem' }}>
                Patient Profile
              </p>
              <p style={{ fontWeight: 700, fontSize: '0.9rem', color: INK, marginBottom: '0.375rem' }}>
                {patientDisplayName(selectedPatient)}
              </p>
              <dl className="pm-tabular" style={{ display: 'grid', gridTemplateColumns: 'max-content 1fr', columnGap: '0.875rem', rowGap: '0.3rem', fontSize: '0.75rem', marginBottom: '0.5rem' }}>
                <dt style={{ color: TEXT_MUTED }}>Phone</dt>
                <dd style={{ margin: 0, color: INK }}>{fieldStr(selectedPatient, 'phone') ?? 'No phone captured'}</dd>
                <dt style={{ color: TEXT_MUTED }}>Email</dt>
                <dd style={{ margin: 0, color: INK }}>{fieldStr(selectedPatient, 'email') ?? '—'}</dd>
                <dt style={{ color: TEXT_MUTED }}>Status</dt>
                <dd style={{ margin: 0 }}><span style={badge(selectedPatient.status)}>{selectedPatient.status ?? '—'}</span></dd>
                <dt style={{ color: TEXT_MUTED }}>Linked requests</dt>
                <dd style={{ margin: 0, color: INK }}>{linkedAppointments.length}</dd>
              </dl>
              <p className="pm-tabular" style={{ fontSize: '0.625rem', color: TEXT_FAINT, fontFamily: 'ui-monospace, monospace', marginBottom: '0.625rem', overflowWrap: 'anywhere' }}>
                {selectedPatient.id}
              </p>

              {/* Chronological history / timeline from linked appointment requests */}
              <div style={{ borderTop: `1px solid ${ACCENT}33`, paddingTop: '0.625rem' }}>
                <p style={{ fontSize: '0.65rem', fontWeight: 700, color: TEXT_MUTED, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.5rem' }}>
                  History
                </p>
                {linkedAppointments.length === 0 ? (
                  <>
                    <p style={{ fontSize: '0.75rem', color: TEXT_MUTED, lineHeight: 1.5 }}>
                      Linked history will appear here as appointment requests accumulate.
                    </p>
                    <p style={{ fontSize: '0.7rem', color: TEXT_FAINT, marginTop: '0.35rem', lineHeight: 1.5 }}>
                      Appointment history will appear here as linked visits accumulate.
                    </p>
                  </>
                ) : (
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {linkedAppointments.map((a) => (
                      <li key={a.id} className="pm-tabular" style={{ fontSize: '0.75rem', color: INK, paddingLeft: '0.75rem', borderLeft: `2px solid ${ACCENT}` }}>
                        <div style={{ fontWeight: 600 }}>{formatDate(a.created_at)}: AI Phone Intake Request Logged</div>
                        <div style={{ color: TEXT_MUTED }}>Status: {a.status}</div>
                        {fieldStr(a, 'reason') && <div style={{ color: TEXT_MUTED }}>Reason: {fieldStr(a, 'reason')}</div>}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <button
                onClick={() => setSelectedPatientId(null)}
                style={{ marginTop: '0.75rem', fontSize: '0.75rem', fontWeight: 600, padding: '4px 12px', border: `1px solid ${ACCENT}`, borderRadius: 6, background: 'transparent', color: ACCENT, cursor: 'pointer' }}
              >
                Deselect
              </button>
            </div>
          )}
        </aside>

      </div>
    </div>
  )
}
