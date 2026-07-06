'use client'

import { useEffect, useState } from 'react'
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
// Colour constants — hardcoded so the 3-panel shell renders even when CSS
// variables haven't loaded yet, and so static contract tests can verify them.
// ---------------------------------------------------------------------------
const NAVY   = '#0F172A'   // Deep Midnight Navy
const NAVY_800 = '#1E293B' // Left panel background
const NAVY_600 = '#475569' // Muted text on dark panels
const TEAL   = '#0D9488'   // Crisp Teal

// ---------------------------------------------------------------------------
// Embedded layout CSS — makes the 3-panel grid self-contained.
// Responsive breakpoints can't be expressed as inline styles, so they live
// here, not in globals.css, to guarantee they travel with this component.
// ---------------------------------------------------------------------------
const LAYOUT_CSS = `
  .pm-dash-shell { display:flex; flex-direction:column; min-height:100vh; background:#f1f5f9; }
  .pm-dash-grid  { display:grid; grid-template-columns:264px 1fr 272px; flex:1; min-height:0; overflow:hidden; }
  .pm-dash-left  { overflow-y:auto; background:${NAVY_800}; border-right:1px solid rgba(255,255,255,0.06); }
  .pm-dash-center{ overflow-y:auto; background:#f1f5f9; }
  .pm-dash-right { overflow-y:auto; background:#ffffff; border-left:1px solid #e2e8f0; }
  @media(max-width:1200px){
    .pm-dash-grid{ grid-template-columns:240px 1fr; overflow:visible; }
    .pm-dash-right{ display:none; }
  }
  @media(max-width:768px){
    .pm-dash-grid{ grid-template-columns:1fr; overflow:visible; }
    .pm-dash-left{ max-height:45vh; border-right:none; border-bottom:1px solid rgba(255,255,255,0.1); }
    .pm-dash-right{ display:block; border-left:none; border-top:1px solid #e2e8f0; }
  }
`

// ---------------------------------------------------------------------------
// Design tokens (inline-style helpers)
// ---------------------------------------------------------------------------

const BADGE_MAP: Record<string, { bg: string; color: string }> = {
  new:       { bg: '#dbeafe', color: '#1e40af' },
  confirmed: { bg: '#dcfce7', color: '#166534' },
  active:    { bg: '#dcfce7', color: '#166534' },
  approved:  { bg: '#dcfce7', color: '#166534' },
  pending:   { bg: '#fef3c7', color: '#92400e' },
  urgent:    { bg: '#fee2e2', color: '#991b1b' },
  emergency: { bg: '#fee2e2', color: '#991b1b' },
  high:      { bg: '#fee2e2', color: '#991b1b' },
  normal:    { bg: '#e2e8f0', color: '#64748b' },
}

function badge(value: string | null | undefined): React.CSSProperties {
  const t = value?.toLowerCase() ?? ''
  const found = BADGE_MAP[t]
  return {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '2px 9px',
    borderRadius: 99,
    fontSize: '0.7rem',
    fontWeight: 600,
    letterSpacing: '0.02em',
    background: found?.bg ?? '#e2e8f0',
    color: found?.color ?? '#64748b',
    whiteSpace: 'nowrap' as const,
  }
}

// ---------------------------------------------------------------------------
// Small reusable components
// ---------------------------------------------------------------------------

function SectionCard({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div
      style={{
        background: '#ffffff',
        border: '1px solid #e2e8f0',
        borderRadius: 14,
        boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.07), 0 1px 2px -1px rgb(0 0 0 / 0.05)',
        overflow: 'hidden',
        ...style,
      }}
    >
      {children}
    </div>
  )
}

function SectionHeader({ title, count }: { title: string; count?: number }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '1rem 1.25rem 0.75rem',
        borderBottom: '1px solid #f0f4f8',
      }}
    >
      <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: '#0f172a' }}>
        {title}
      </h3>
      {count !== undefined && (
        <span style={{ fontSize: '0.7rem', fontWeight: 600, color: '#64748b', background: '#e2e8f0', padding: '1px 7px', borderRadius: 99 }}>
          {count}
        </span>
      )}
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div data-state="empty" style={{ padding: '2rem 1.25rem', textAlign: 'center', color: '#64748b', fontSize: '0.875rem' }}>
      {message}
    </div>
  )
}

function LoadingState({ message }: { message: string }) {
  return (
    <div data-state="loading" style={{ padding: '1.5rem 1.25rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
      {[1, 2, 3].map((i) => (
        <div key={i} style={{ height: 14, borderRadius: 6, background: '#e2e8f0', width: i === 1 ? '60%' : i === 2 ? '80%' : '45%', opacity: 0.7 }} aria-hidden />
      ))}
      <span className="sr-only">{message}</span>
    </div>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <div
      data-state="error"
      style={{ margin: '1rem 1.25rem', padding: '0.75rem 1rem', background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: 10, fontSize: '0.8125rem', color: '#dc2626' }}
    >
      {message}
    </div>
  )
}

function MetricCard({ label, value, loading }: { label: string; value: number; loading: boolean }) {
  return (
    <div style={{ flex: '1 1 120px', background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 10, boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.04)', padding: '1rem 1.25rem' }}>
      <p style={{ fontSize: '0.75rem', fontWeight: 500, color: '#64748b', marginBottom: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {label}
      </p>
      {loading ? (
        <div style={{ height: 28, width: 48, background: '#e2e8f0', borderRadius: 6, opacity: 0.6 }} aria-hidden />
      ) : (
        <p style={{ fontSize: '1.75rem', fontWeight: 700, color: '#0f172a', lineHeight: 1 }}>{value}</p>
      )}
    </div>
  )
}

// Audio Transcript & Call Recording placeholder
function TranscriptRecordingPanel() {
  return (
    <div
      data-state="transcript-panel"
      style={{ margin: '0 1.25rem 1.25rem', borderRadius: 10, border: '1px solid #e2e8f0', background: '#f1f5f9', padding: '1rem 1.25rem' }}
    >
      <p style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
        Audio Transcript &amp; Call Recording
      </p>
      <p style={{ fontSize: '0.8125rem', color: '#94a3b8', fontStyle: 'italic' }}>
        Transcript recording — coming in next module. AI transcription of the intake call and audio recording will appear here.
      </p>
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
        .then(setAppointments)
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

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="pm-dash-shell">

      {/* Embedded layout CSS — self-contained, no reliance on globals.css */}
      <style dangerouslySetInnerHTML={{ __html: LAYOUT_CSS }} />

      {/* ------------------------------------------------------------------ */}
      {/* Sticky header                                                        */}
      {/* ------------------------------------------------------------------ */}
      <header
        style={{
          background: NAVY,
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          padding: '0 1.5rem',
          height: 56,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 20,
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
          <div>
            <span style={{ fontWeight: 700, fontSize: '1rem', color: '#ffffff', letterSpacing: '-0.01em' }}>
              PraxisMed
            </span>
            <span style={{ marginLeft: '0.5rem', fontSize: '0.8125rem', color: NAVY_600, fontWeight: 400 }}>
              {clinicDisplayName}
            </span>
            {userRole && (
              <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: NAVY_600 }}>
                · {userRole}
              </span>
            )}
          </div>
          <span
            style={{
              fontSize: '0.6875rem', fontWeight: 600, padding: '2px 8px', borderRadius: 99,
              background: '#fef3c7', color: '#92400e', letterSpacing: '0.03em', textTransform: 'uppercase',
            }}
          >
            Staging demo
          </span>
        </div>

        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <a href="/onboarding" style={{ fontSize: '0.8125rem', fontWeight: 500, padding: '0.375rem 0.875rem', borderRadius: 6, color: NAVY_600, textDecoration: 'none' }}>
            Onboarding
          </a>
          <a href="/developer-console" style={{ fontSize: '0.8125rem', fontWeight: 500, padding: '0.375rem 0.875rem', borderRadius: 6, color: NAVY_600, textDecoration: 'none' }}>
            Dev Console
          </a>
          <button
            onClick={handleLogout}
            style={{
              fontSize: '0.8125rem', fontWeight: 500, padding: '0.375rem 0.875rem',
              border: '1px solid rgba(255,255,255,0.12)', borderRadius: 6,
              background: 'transparent', color: 'rgba(255,255,255,0.75)', cursor: 'pointer',
            }}
          >
            Logout
          </button>
        </nav>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* 3-panel application grid                                             */}
      {/* ------------------------------------------------------------------ */}
      <div className="pm-dash-grid">

        {/* ================================================================ */}
        {/* LEFT PANEL — Incoming AI Intake                                   */}
        {/* ================================================================ */}
        <aside className="pm-dash-left" data-panel="left">

          {/* Appointment intake queue */}
          <section data-section="appointments">
            <div style={{ padding: '1.25rem 1rem 0.625rem' }}>
              <h2 style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>
                Incoming AI Intake
              </h2>
            </div>

            {apptLoading && (
              <div style={{ padding: '0.25rem 0.75rem' }}>
                {[1, 2, 3].map((i) => (
                  <div key={i} style={{ height: 52, borderRadius: 8, background: 'rgba(255,255,255,0.05)', marginBottom: '0.375rem' }} />
                ))}
              </div>
            )}

            {!apptLoading && apptError && (
              <div style={{ margin: '0.5rem 0.75rem', padding: '0.75rem', borderRadius: 8, background: 'rgba(220,38,38,0.15)', color: '#fca5a5', fontSize: '0.8125rem' }}>
                {apptError}
              </div>
            )}

            {!apptLoading && !apptError && appointments.length === 0 && (
              <div style={{ padding: '1.25rem 1rem', fontSize: '0.8125rem', color: 'rgba(255,255,255,0.3)', textAlign: 'center' }}>
                No intake requests
              </div>
            )}

            {!apptLoading && !apptError && appointments.length > 0 && (
              <ul data-state="list" style={{ listStyle: 'none', padding: '0 0.625rem 0.75rem' }}>
                {appointments.map((appt) => {
                  const isSelected = selectedApptId === appt.id
                  const isNew = appt.status === 'new'
                  return (
                    <li
                      key={appt.id}
                      onClick={() => { setSelectedApptId(isSelected ? null : appt.id); if (!isSelected) setSummaryOpenId(null) }}
                      style={{
                        marginBottom: '0.3rem', borderRadius: 8, padding: '0.625rem 0.875rem', cursor: 'pointer',
                        background: isSelected ? 'rgba(13,148,136,0.18)' : 'rgba(255,255,255,0.05)',
                        borderLeft: isSelected ? `3px solid ${TEAL}` : isNew ? '3px solid rgba(99,102,241,0.55)' : '3px solid transparent',
                      }}
                    >
                      <div style={{ fontWeight: 600, fontSize: '0.8125rem', color: '#ffffff', marginBottom: '0.25rem' }}>
                        {appt.patient_name ?? '—'}
                      </div>
                      <div style={{ display: 'flex', gap: '0.3rem', flexWrap: 'wrap' }}>
                        <span style={badge(appt.status)}>{appt.status}</span>
                        <span style={badge(appt.urgency_level)}>{appt.urgency_level}</span>
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </section>

          <div style={{ height: 1, background: 'rgba(255,255,255,0.06)' }} />

          {/* Notifications */}
          <section data-section="notifications">
            <div style={{ padding: '0.875rem 1rem 0.5rem' }}>
              <h2 style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>
                Notifications
              </h2>
            </div>

            {notifLoading && (
              <div style={{ padding: '0.25rem 0.75rem' }}>
                {[1, 2].map((i) => <div key={i} style={{ height: 36, borderRadius: 6, background: 'rgba(255,255,255,0.05)', marginBottom: '0.3rem' }} />)}
              </div>
            )}

            {!notifLoading && notifError && (
              <div style={{ margin: '0.25rem 0.75rem', padding: '0.625rem', borderRadius: 6, background: 'rgba(220,38,38,0.15)', color: '#fca5a5', fontSize: '0.75rem' }}>
                {notifError}
              </div>
            )}

            {!notifLoading && !notifError && notifications.length === 0 && (
              <div style={{ padding: '0.75rem 1rem', fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)' }}>No notifications</div>
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
                        marginBottom: '0.3rem', padding: '0.5rem 0.75rem', borderRadius: 6,
                        background: 'rgba(255,255,255,0.04)',
                        borderLeft: isPending ? `3px solid ${TEAL}` : '3px solid transparent',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                        <span style={{ flex: 1, fontWeight: 600, fontSize: '0.75rem', color: 'rgba(255,255,255,0.8)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {notif.title ?? '—'}
                        </span>
                        <span style={badge(notif.status)}>{notif.status ?? '—'}</span>
                      </div>
                      {truncatedMsg && (
                        <p data-notification-message style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)', margin: '0.2rem 0 0', lineHeight: 1.4 }}>
                          {truncatedMsg}
                        </p>
                      )}
                    </li>
                  )
                })}
              </ul>
            )}
          </section>
        </aside>

        {/* ================================================================ */}
        {/* CENTER PANEL — Clinic Overview + Intake Resolution Workspace       */}
        {/* ================================================================ */}
        <main className="pm-dash-center" data-panel="center">
          <div style={{ padding: '1.5rem 1.5rem 0' }}>
            <h1 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', letterSpacing: '-0.01em' }}>
              Clinic Overview
            </h1>
            <p style={{ fontSize: '0.8125rem', color: '#64748b', marginTop: '0.2rem' }}>
              Fake-data staging environment — no real patient data
            </p>
          </div>

          {/* Metrics row */}
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', margin: '1rem 1.5rem' }}>
            <MetricCard label="Appointments" value={appointments.length} loading={apptLoading} />
            <MetricCard label="Patients"     value={patients.length}     loading={patientsLoading} />
            <MetricCard label="Notifications" value={notifications.length} loading={notifLoading} />
            <MetricCard label="Pending"      value={pendingCount}         loading={apptLoading} />
          </div>

          {/* Intake Resolution Workspace */}
          <div data-panel="workspace" style={{ margin: '0 1.5rem 1.5rem' }}>
            {!selectedAppt ? (
              <div
                data-state="empty"
                style={{ border: '2px dashed #e2e8f0', borderRadius: 14, padding: '3rem 2rem', textAlign: 'center', color: '#64748b' }}
              >
                <p style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                  Intake Resolution Workspace
                </p>
                <p style={{ fontSize: '0.8125rem' }}>
                  Select an intake from the queue on the left to review and resolve
                </p>
              </div>
            ) : (
              <SectionCard>
                {/* Workspace header */}
                <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #f0f4f8', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>{selectedAppt.patient_name ?? '—'}</h3>
                    <div style={{ display: 'flex', gap: '0.375rem', marginTop: '0.375rem' }}>
                      <span style={badge(selectedAppt.status)}>{selectedAppt.status}</span>
                      <span style={badge(selectedAppt.urgency_level)}>{selectedAppt.urgency_level}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => { setSelectedApptId(null); setSummaryOpenId(null) }}
                    style={{ fontSize: '0.75rem', padding: '4px 10px', border: '1px solid #e2e8f0', borderRadius: 6, background: '#ffffff', color: '#64748b', cursor: 'pointer' }}
                  >
                    Close
                  </button>
                </div>

                {/* Action buttons */}
                <div style={{ padding: '0.875rem 1.25rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', borderBottom: '1px solid #f0f4f8' }}>
                  <button
                    data-action="view-summary"
                    onClick={() => handleViewSummary(selectedAppt)}
                    style={{
                      fontSize: '0.8125rem', fontWeight: 500, padding: '6px 14px', borderRadius: 6, cursor: 'pointer',
                      border: '1px solid #e2e8f0',
                      background: summaryOpenId === selectedAppt.id ? '#eff6ff' : '#ffffff',
                      color:      summaryOpenId === selectedAppt.id ? '#1a56db' : '#64748b',
                    }}
                  >
                    {summaryOpenId === selectedAppt.id ? 'Hide summary' : 'View summary'}
                  </button>

                  {selectedAppt.status === 'new' && (
                    <button
                      data-action="confirm"
                      onClick={() => handleConfirm(selectedAppt.id)}
                      disabled={confirmingIds.has(selectedAppt.id)}
                      style={{
                        fontSize: '0.8125rem', fontWeight: 600, padding: '6px 16px', borderRadius: 6,
                        border: '1px solid #059669',
                        background: confirmingIds.has(selectedAppt.id) ? '#e2e8f0' : '#f0fdf4',
                        color:      confirmingIds.has(selectedAppt.id) ? '#64748b' : '#059669',
                        cursor:     confirmingIds.has(selectedAppt.id) ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {confirmingIds.has(selectedAppt.id) ? 'Confirming…' : 'Confirm'}
                    </button>
                  )}

                  <button
                    data-action="confirm-create-profile"
                    disabled
                    title="Patient profile creation — coming in next module"
                    style={{
                      fontSize: '0.8125rem', fontWeight: 500, padding: '6px 14px', borderRadius: 6,
                      border: '1px solid #e2e8f0', background: '#f1f5f9', color: '#94a3b8',
                      cursor: 'not-allowed', opacity: 0.6,
                    }}
                  >
                    Confirm &amp; Create Profile
                  </button>
                </div>

                {apptActionError && (
                  <div style={{ margin: '0.75rem 1.25rem 0' }}>
                    <ErrorState message={apptActionError} />
                  </div>
                )}

                {/* Summary panel */}
                {summaryOpenId === selectedAppt.id && (() => {
                  const summaryEntry = summaries[selectedAppt.id]
                  return (
                    <div
                      data-state="summary-panel"
                      style={{ margin: '0.875rem 1.25rem', borderRadius: 10, border: '1px solid #dbeafe', background: '#eff6ff', overflow: 'hidden' }}
                    >
                      {summaryEntry === 'loading' && <div style={{ padding: '1rem 1.25rem' }}><LoadingState message="Loading summary…" /></div>}
                      {summaryEntry === 'error' && <div style={{ padding: '0.75rem 1.25rem', color: '#dc2626', fontSize: '0.8125rem' }}>Could not load summary. Please try again.</div>}
                      {summaryEntry && summaryEntry !== 'loading' && summaryEntry !== 'error' && (
                        <div style={{ padding: '1rem 1.25rem' }}>
                          <p style={{ fontSize: '0.75rem', fontWeight: 600, color: '#1a56db', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
                            Pre-appointment Summary
                          </p>
                          <dl style={{ display: 'grid', gridTemplateColumns: 'max-content 1fr', columnGap: '1rem', rowGap: '0.4rem', fontSize: '0.8125rem' }}>
                            <dt style={{ color: '#64748b', fontWeight: 500 }}>Patient</dt>
                            <dd style={{ margin: 0, color: '#0f172a', fontWeight: 500 }}>{summaryEntry.patient_name}</dd>
                            <dt style={{ color: '#64748b', fontWeight: 500 }}>Type</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.patient_type}</dd>
                            <dt style={{ color: '#64748b', fontWeight: 500 }}>Reason</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.reason ?? '—'}</dd>
                            <dt style={{ color: '#64748b', fontWeight: 500 }}>Urgency</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.urgency_level}</dd>
                            <dt style={{ color: '#64748b', fontWeight: 500 }}>Prior visits</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.previous_request_count}</dd>
                            <dt style={{ color: '#64748b', fontWeight: 500 }}>Suggested action</dt>
                            <dd style={{ margin: 0, color: TEAL, fontWeight: 600 }}>{summaryEntry.suggested_next_action}</dd>
                          </dl>
                          <div style={{ marginTop: '0.875rem', paddingTop: '0.75rem', borderTop: '1px solid #dbeafe', fontSize: '0.75rem', color: '#64748b', display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                            <span style={{ userSelect: 'none' }}>ℹ</span>
                            <span>{summaryEntry.safety_note}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })()}

                <TranscriptRecordingPanel />
              </SectionCard>
            )}
          </div>

          {/* Consultations */}
          <section data-section="consultations" style={{ margin: '0 1.5rem 1.5rem' }}>
            <SectionCard>
              <SectionHeader title="Consultations" count={!consultLoading && !consultError ? consultations.length : undefined} />
              {consultLoading && <LoadingState message="Loading consultations…" />}
              {!consultLoading && consultError && <ErrorState message={consultError} />}
              {!consultLoading && !consultError && consultations.length === 0 && <EmptyState message="No consultations on file yet." />}
              {!consultLoading && !consultError && consultations.length > 0 && (
                <ul data-state="list" style={{ listStyle: 'none', padding: '0.25rem 0 0.5rem' }}>
                  {consultations.map((consult, idx) => (
                    <li key={consult.id} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.625rem 1.25rem', borderBottom: idx < consultations.length - 1 ? '1px solid #f0f4f8' : 'none', fontSize: '0.875rem' }}>
                      <span style={{ flex: 1, fontWeight: 500, color: '#0f172a' }}>{consult.title ?? '—'}</span>
                      <span style={badge(consult.approval_status ?? undefined)}>{consult.approval_status ?? consult.status ?? '—'}</span>
                      <span style={{ color: '#64748b', fontSize: '0.775rem' }}>{consult.source ?? '—'}</span>
                    </li>
                  ))}
                </ul>
              )}
            </SectionCard>
          </section>

          {/* Safety footer */}
          <p style={{ textAlign: 'center', fontSize: '0.6875rem', color: '#94a3b8', margin: '0 1.5rem 2rem', letterSpacing: '0.02em' }}>
            Staging demo — fake data only · No real patient data · Production PHI: NO-GO
          </p>
        </main>

        {/* ================================================================ */}
        {/* RIGHT PANEL — Patient Registry                                    */}
        {/* ================================================================ */}
        <aside className="pm-dash-right" data-panel="right">
          <div style={{ padding: '1.25rem 1rem 0.75rem', borderBottom: '1px solid #f0f4f8' }}>
            <h2 style={{ fontSize: '0.6875rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.12em' }}>
              Patient Registry
            </h2>
          </div>

          <section data-section="patients">
            {patientsLoading && <LoadingState message="Loading patients…" />}
            {!patientsLoading && patientsError && <ErrorState message={patientsError} />}
            {!patientsLoading && !patientsError && patients.length === 0 && <EmptyState message="No patients on file yet." />}

            {!patientsLoading && !patientsError && patients.length > 0 && (
              <ul data-state="list" style={{ listStyle: 'none', padding: '0.5rem 0' }}>
                {patients.map((patient) => {
                  const isSelected = selectedPatientId === patient.id
                  const displayName = patient.full_name || [patient.first_name, patient.last_name].filter(Boolean).join(' ') || 'Unnamed patient'
                  return (
                    <li
                      key={patient.id}
                      onClick={() => setSelectedPatientId(isSelected ? null : patient.id)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: '0.625rem', padding: '0.625rem 1rem', cursor: 'pointer',
                        background: isSelected ? '#f0fdfa' : 'transparent',
                        borderLeft: isSelected ? `3px solid ${TEAL}` : '3px solid transparent',
                      }}
                    >
                      <span style={{ flex: 1, fontWeight: isSelected ? 600 : 400, fontSize: '0.8125rem', color: '#0f172a' }}>{displayName}</span>
                      <span style={badge(patient.status)}>{patient.status ?? '—'}</span>
                    </li>
                  )
                })}
              </ul>
            )}
          </section>

          {/* Selected patient profile */}
          {selectedPatient && (
            <div
              data-state="patient-profile"
              style={{ margin: '0.75rem', padding: '1rem', borderRadius: 10, border: '1px solid #99f6e4', background: '#f0fdfa' }}
            >
              <p style={{ fontSize: '0.6875rem', fontWeight: 700, color: TEAL, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.625rem' }}>
                Patient Profile
              </p>
              <p style={{ fontWeight: 600, fontSize: '0.875rem', color: '#0f172a', marginBottom: '0.375rem' }}>
                {selectedPatient.full_name || [selectedPatient.first_name, selectedPatient.last_name].filter(Boolean).join(' ') || 'Unnamed patient'}
              </p>
              <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }}>
                <span style={badge(selectedPatient.status)}>{selectedPatient.status ?? '—'}</span>
              </div>
              <button
                onClick={() => setSelectedPatientId(null)}
                style={{ marginTop: '0.75rem', fontSize: '0.75rem', padding: '3px 10px', border: '1px solid #99f6e4', borderRadius: 6, background: 'transparent', color: TEAL, cursor: 'pointer' }}
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
