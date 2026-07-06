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
// Design tokens (inline-style helpers)
// ---------------------------------------------------------------------------

const BADGE_MAP: Record<string, { bg: string; color: string }> = {
  new:       { bg: 'var(--badge-blue-bg)',    color: 'var(--badge-blue-text)' },
  confirmed: { bg: 'var(--badge-green-bg)',   color: 'var(--badge-green-text)' },
  active:    { bg: 'var(--badge-green-bg)',   color: 'var(--badge-green-text)' },
  approved:  { bg: 'var(--badge-green-bg)',   color: 'var(--badge-green-text)' },
  pending:   { bg: 'var(--badge-amber-bg)',   color: 'var(--badge-amber-text)' },
  urgent:    { bg: 'var(--badge-red-bg)',     color: 'var(--badge-red-text)' },
  emergency: { bg: 'var(--badge-red-bg)',     color: 'var(--badge-red-text)' },
  high:      { bg: 'var(--badge-red-bg)',     color: 'var(--badge-red-text)' },
  normal:    { bg: 'var(--badge-neutral-bg)', color: 'var(--badge-neutral-text)' },
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
    background: found?.bg ?? 'var(--badge-neutral-bg)',
    color: found?.color ?? 'var(--badge-neutral-text)',
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
        background: 'var(--color-card)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-card)',
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
        borderBottom: '1px solid var(--color-border-soft)',
      }}
    >
      <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--color-text)' }}>
        {title}
      </h3>
      {count !== undefined && (
        <span
          style={{
            fontSize: '0.7rem',
            fontWeight: 600,
            color: 'var(--color-text-muted)',
            background: 'var(--color-border)',
            padding: '1px 7px',
            borderRadius: 99,
          }}
        >
          {count}
        </span>
      )}
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div
      data-state="empty"
      style={{
        padding: '2rem 1.25rem',
        textAlign: 'center',
        color: 'var(--color-text-muted)',
        fontSize: '0.875rem',
      }}
    >
      {message}
    </div>
  )
}

function LoadingState({ message }: { message: string }) {
  return (
    <div data-state="loading" style={{ padding: '1.5rem 1.25rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          style={{
            height: 14,
            borderRadius: 6,
            background: 'var(--color-border)',
            width: i === 1 ? '60%' : i === 2 ? '80%' : '45%',
            opacity: 0.7,
          }}
          aria-hidden
        />
      ))}
      <span className="sr-only">{message}</span>
    </div>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <div
      data-state="error"
      style={{
        margin: '1rem 1.25rem',
        padding: '0.75rem 1rem',
        background: 'var(--color-danger-bg)',
        border: '1px solid var(--badge-red-bg)',
        borderRadius: 'var(--radius)',
        fontSize: '0.8125rem',
        color: 'var(--color-danger)',
      }}
    >
      {message}
    </div>
  )
}

function MetricCard({
  label,
  value,
  loading,
}: {
  label: string
  value: number
  loading: boolean
}) {
  return (
    <div
      style={{
        flex: '1 1 120px',
        background: 'var(--color-card)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius)',
        boxShadow: 'var(--shadow-xs)',
        padding: '1rem 1.25rem',
      }}
    >
      <p style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--color-text-muted)', marginBottom: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {label}
      </p>
      {loading ? (
        <div style={{ height: 28, width: 48, background: 'var(--color-border)', borderRadius: 6, opacity: 0.6 }} aria-hidden />
      ) : (
        <p style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-text)', lineHeight: 1 }}>
          {value}
        </p>
      )}
    </div>
  )
}

function TranscriptRecordingPanel() {
  return (
    <div
      data-state="transcript-panel"
      style={{
        margin: '0 1.25rem 1.25rem',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--color-border)',
        background: 'var(--color-bg)',
        padding: '1rem 1.25rem',
      }}
    >
      <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
        Audio Transcript
      </p>
      <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-faint)', fontStyle: 'italic' }}>
        Transcript recording — coming in next module. AI transcription of the intake call will appear here.
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
        .then((rows) => setAppointments(rows))
        .catch(() => setApptError('Could not load appointment requests. Please try again.'))
        .finally(() => setApptLoading(false))

      fetchPatients(user.clinic_id)
        .then((rows) => setPatients(rows))
        .catch(() => setPatientsError('Could not load patients. Please try again.'))
        .finally(() => setPatientsLoading(false))

      fetchNotifications(user.clinic_id)
        .then((rows) => setNotifications(rows))
        .catch(() => setNotifError('Could not load notifications. Please try again.'))
        .finally(() => setNotifLoading(false))

      fetchConsultations(user.clinic_id)
        .then((rows) => setConsultations(rows))
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
      setConfirmingIds((prev) => {
        const next = new Set(prev)
        next.delete(requestId)
        return next
      })
    }
  }

  async function handleViewSummary(appt: AppointmentRequest) {
    if (!clinicId) return
    if (summaryOpenId === appt.id) {
      setSummaryOpenId(null)
      return
    }
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
    <div className="pm-shell">

      {/* ------------------------------------------------------------------ */}
      {/* Header                                                               */}
      {/* ------------------------------------------------------------------ */}
      <header
        style={{
          background: 'var(--color-navy)',
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
            <span style={{ marginLeft: '0.5rem', fontSize: '0.8125rem', color: 'var(--color-navy-600)', fontWeight: 400 }}>
              {clinicDisplayName}
            </span>
            {userRole && (
              <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: 'var(--color-navy-600)' }}>
                · {userRole}
              </span>
            )}
          </div>
          <span
            style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              padding: '2px 8px',
              borderRadius: 99,
              background: 'var(--badge-amber-bg)',
              color: 'var(--badge-amber-text)',
              letterSpacing: '0.03em',
              textTransform: 'uppercase',
            }}
          >
            Staging demo
          </span>
        </div>

        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <a
            href="/onboarding"
            style={{
              fontSize: '0.8125rem',
              fontWeight: 500,
              padding: '0.375rem 0.875rem',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--color-navy-600)',
              textDecoration: 'none',
            }}
          >
            Onboarding
          </a>
          <a
            href="/developer-console"
            style={{
              fontSize: '0.8125rem',
              fontWeight: 500,
              padding: '0.375rem 0.875rem',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--color-navy-600)',
              textDecoration: 'none',
            }}
          >
            Dev Console
          </a>
          <button
            onClick={handleLogout}
            style={{
              fontSize: '0.8125rem',
              fontWeight: 500,
              padding: '0.375rem 0.875rem',
              border: '1px solid rgba(255,255,255,0.12)',
              borderRadius: 'var(--radius-sm)',
              background: 'transparent',
              color: 'rgba(255,255,255,0.7)',
              cursor: 'pointer',
            }}
          >
            Logout
          </button>
        </nav>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* 3-panel application grid                                             */}
      {/* ------------------------------------------------------------------ */}
      <div className="pm-app-grid">

        {/* ---------------------------------------------------------------- */}
        {/* Left panel — AI Intake Queue                                      */}
        {/* ---------------------------------------------------------------- */}
        <aside className="pm-panel-left" data-panel="left">

          {/* Appointment queue */}
          <section data-section="appointments">
            <div style={{ padding: '1.25rem 1rem 0.625rem' }}>
              <h2 style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                AI Intake Queue
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
                      onClick={() => {
                        setSelectedApptId(isSelected ? null : appt.id)
                        if (!isSelected) setSummaryOpenId(null)
                      }}
                      style={{
                        marginBottom: '0.3rem',
                        borderRadius: 8,
                        padding: '0.625rem 0.875rem',
                        cursor: 'pointer',
                        background: isSelected ? 'rgba(13,148,136,0.18)' : 'rgba(255,255,255,0.05)',
                        borderLeft: isSelected
                          ? '3px solid var(--color-teal)'
                          : isNew
                          ? '3px solid rgba(99,102,241,0.55)'
                          : '3px solid transparent',
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
              <h2 style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                Notifications
              </h2>
            </div>

            {notifLoading && (
              <div style={{ padding: '0.25rem 0.75rem' }}>
                {[1, 2].map((i) => (
                  <div key={i} style={{ height: 36, borderRadius: 6, background: 'rgba(255,255,255,0.05)', marginBottom: '0.3rem' }} />
                ))}
              </div>
            )}

            {!notifLoading && notifError && (
              <div style={{ margin: '0.25rem 0.75rem', padding: '0.625rem', borderRadius: 6, background: 'rgba(220,38,38,0.15)', color: '#fca5a5', fontSize: '0.75rem' }}>
                {notifError}
              </div>
            )}

            {!notifLoading && !notifError && notifications.length === 0 && (
              <div style={{ padding: '0.75rem 1rem', fontSize: '0.75rem', color: 'rgba(255,255,255,0.25)' }}>
                No notifications
              </div>
            )}

            {!notifLoading && !notifError && notifications.length > 0 && (
              <ul data-state="list" style={{ listStyle: 'none', padding: '0 0.625rem 1rem' }}>
                {notifications.map((notif) => {
                  const isPending = notif.status === 'pending'
                  const truncatedMsg = notif.message
                    ? notif.message.length > 75
                      ? notif.message.slice(0, 75) + '…'
                      : notif.message
                    : null
                  return (
                    <li
                      key={notif.id}
                      data-notification-status={notif.status}
                      style={{
                        marginBottom: '0.3rem',
                        padding: '0.5rem 0.75rem',
                        borderRadius: 6,
                        background: 'rgba(255,255,255,0.04)',
                        borderLeft: isPending ? '3px solid var(--color-teal)' : '3px solid transparent',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                        <span style={{ flex: 1, fontWeight: 600, fontSize: '0.75rem', color: 'rgba(255,255,255,0.8)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {notif.title ?? '—'}
                        </span>
                        <span style={badge(notif.status)}>{notif.status ?? '—'}</span>
                      </div>
                      {truncatedMsg && (
                        <p
                          data-notification-message
                          style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)', margin: '0.2rem 0 0', lineHeight: 1.4 }}
                        >
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

        {/* ---------------------------------------------------------------- */}
        {/* Center panel — Clinic Overview + Intake Resolution Workspace       */}
        {/* ---------------------------------------------------------------- */}
        <main className="pm-panel-center" data-panel="center">
          <div style={{ padding: '1.5rem 1.5rem 0' }}>
            <h1 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-text)', letterSpacing: '-0.01em' }}>
              Clinic Overview
            </h1>
            <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginTop: '0.2rem' }}>
              Fake-data staging environment — no real patient data
            </p>
          </div>

          {/* Metrics row */}
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', margin: '1rem 1.5rem' }}>
            <MetricCard label="Appointments" value={appointments.length} loading={apptLoading} />
            <MetricCard label="Patients" value={patients.length} loading={patientsLoading} />
            <MetricCard label="Notifications" value={notifications.length} loading={notifLoading} />
            <MetricCard label="Pending" value={pendingCount} loading={apptLoading} />
          </div>

          {/* ---------------------------------------------------------------- */}
          {/* Intake Resolution Workspace                                       */}
          {/* ---------------------------------------------------------------- */}
          <div data-panel="workspace" style={{ margin: '0 1.5rem 1.5rem' }}>
            {!selectedAppt ? (
              <div
                data-state="empty"
                style={{
                  border: '2px dashed var(--color-border)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '3rem 2rem',
                  textAlign: 'center',
                  color: 'var(--color-text-muted)',
                }}
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
                <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--color-border-soft)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-text)' }}>
                      {selectedAppt.patient_name ?? '—'}
                    </h3>
                    <div style={{ display: 'flex', gap: '0.375rem', marginTop: '0.375rem' }}>
                      <span style={badge(selectedAppt.status)}>{selectedAppt.status}</span>
                      <span style={badge(selectedAppt.urgency_level)}>{selectedAppt.urgency_level}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => { setSelectedApptId(null); setSummaryOpenId(null) }}
                    style={{
                      fontSize: '0.75rem',
                      padding: '4px 10px',
                      border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-sm)',
                      background: 'var(--color-card)',
                      color: 'var(--color-text-muted)',
                      cursor: 'pointer',
                    }}
                  >
                    Close
                  </button>
                </div>

                {/* Action buttons */}
                <div style={{ padding: '0.875rem 1.25rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', borderBottom: '1px solid var(--color-border-soft)' }}>
                  <button
                    data-action="view-summary"
                    onClick={() => handleViewSummary(selectedAppt)}
                    style={{
                      fontSize: '0.8125rem',
                      fontWeight: 500,
                      padding: '6px 14px',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      background: summaryOpenId === selectedAppt.id ? 'var(--color-brand-50)' : 'var(--color-card)',
                      color: summaryOpenId === selectedAppt.id ? 'var(--color-brand)' : 'var(--color-text-muted)',
                      cursor: 'pointer',
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
                        fontSize: '0.8125rem',
                        fontWeight: 600,
                        padding: '6px 16px',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-success)',
                        background: confirmingIds.has(selectedAppt.id) ? 'var(--color-border)' : 'var(--color-success-bg)',
                        color: confirmingIds.has(selectedAppt.id) ? 'var(--color-text-muted)' : 'var(--color-success)',
                        cursor: confirmingIds.has(selectedAppt.id) ? 'not-allowed' : 'pointer',
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
                      fontSize: '0.8125rem',
                      fontWeight: 500,
                      padding: '6px 14px',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      background: 'var(--color-bg)',
                      color: 'var(--color-text-faint)',
                      cursor: 'not-allowed',
                      opacity: 0.6,
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
                      style={{
                        margin: '0.875rem 1.25rem',
                        borderRadius: 'var(--radius)',
                        border: '1px solid var(--color-brand-100)',
                        background: 'var(--color-brand-50)',
                        overflow: 'hidden',
                      }}
                    >
                      {summaryEntry === 'loading' && (
                        <div style={{ padding: '1rem 1.25rem' }}>
                          <LoadingState message="Loading summary…" />
                        </div>
                      )}
                      {summaryEntry === 'error' && (
                        <div style={{ padding: '0.75rem 1.25rem', color: 'var(--color-danger)', fontSize: '0.8125rem' }}>
                          Could not load summary. Please try again.
                        </div>
                      )}
                      {summaryEntry && summaryEntry !== 'loading' && summaryEntry !== 'error' && (
                        <div style={{ padding: '1rem 1.25rem' }}>
                          <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-brand)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
                            Pre-appointment Summary
                          </p>
                          <dl
                            style={{
                              display: 'grid',
                              gridTemplateColumns: 'max-content 1fr',
                              columnGap: '1rem',
                              rowGap: '0.4rem',
                              fontSize: '0.8125rem',
                            }}
                          >
                            <dt style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Patient</dt>
                            <dd style={{ margin: 0, color: 'var(--color-text)', fontWeight: 500 }}>{summaryEntry.patient_name}</dd>

                            <dt style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Type</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.patient_type}</dd>

                            <dt style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Reason</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.reason ?? '—'}</dd>

                            <dt style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Urgency</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.urgency_level}</dd>

                            <dt style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Prior visits</dt>
                            <dd style={{ margin: 0 }}>{summaryEntry.previous_request_count}</dd>

                            <dt style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Suggested action</dt>
                            <dd style={{ margin: 0, color: 'var(--color-teal)', fontWeight: 600 }}>{summaryEntry.suggested_next_action}</dd>
                          </dl>

                          <div
                            style={{
                              marginTop: '0.875rem',
                              paddingTop: '0.75rem',
                              borderTop: '1px solid var(--color-brand-100)',
                              fontSize: '0.75rem',
                              color: 'var(--color-text-muted)',
                              display: 'flex',
                              gap: '0.5rem',
                              alignItems: 'flex-start',
                            }}
                          >
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
              <SectionHeader
                title="Consultations"
                count={!consultLoading && !consultError ? consultations.length : undefined}
              />
              {consultLoading && <LoadingState message="Loading consultations…" />}
              {!consultLoading && consultError && <ErrorState message={consultError} />}
              {!consultLoading && !consultError && consultations.length === 0 && (
                <EmptyState message="No consultations on file yet." />
              )}
              {!consultLoading && !consultError && consultations.length > 0 && (
                <ul data-state="list" style={{ listStyle: 'none', padding: '0.25rem 0 0.5rem' }}>
                  {consultations.map((consult, idx) => (
                    <li
                      key={consult.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        padding: '0.625rem 1.25rem',
                        borderBottom: idx < consultations.length - 1 ? '1px solid var(--color-border-soft)' : 'none',
                        fontSize: '0.875rem',
                      }}
                    >
                      <span style={{ flex: 1, fontWeight: 500, color: 'var(--color-text)' }}>
                        {consult.title ?? '—'}
                      </span>
                      <span style={badge(consult.approval_status ?? undefined)}>
                        {consult.approval_status ?? consult.status ?? '—'}
                      </span>
                      <span style={{ color: 'var(--color-text-muted)', fontSize: '0.775rem' }}>
                        {consult.source ?? '—'}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </SectionCard>
          </section>

          <p
            style={{
              textAlign: 'center',
              fontSize: '0.6875rem',
              color: 'var(--color-text-faint)',
              margin: '0 1.5rem 2rem',
              letterSpacing: '0.02em',
            }}
          >
            Staging demo — fake data only · No real patient data · Production PHI: NO-GO
          </p>
        </main>

        {/* ---------------------------------------------------------------- */}
        {/* Right panel — Patient Registry                                    */}
        {/* ---------------------------------------------------------------- */}
        <aside className="pm-panel-right" data-panel="right">
          <div style={{ padding: '1.25rem 1rem 0.75rem', borderBottom: '1px solid var(--color-border-soft)' }}>
            <h2 style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Patient Registry
            </h2>
          </div>

          <section data-section="patients">
            {patientsLoading && <LoadingState message="Loading patients…" />}
            {!patientsLoading && patientsError && <ErrorState message={patientsError} />}
            {!patientsLoading && !patientsError && patients.length === 0 && (
              <EmptyState message="No patients on file yet." />
            )}

            {!patientsLoading && !patientsError && patients.length > 0 && (
              <ul data-state="list" style={{ listStyle: 'none', padding: '0.5rem 0' }}>
                {patients.map((patient) => {
                  const isSelected = selectedPatientId === patient.id
                  const displayName =
                    patient.full_name ||
                    [patient.first_name, patient.last_name].filter(Boolean).join(' ') ||
                    'Unnamed patient'
                  return (
                    <li
                      key={patient.id}
                      onClick={() => setSelectedPatientId(isSelected ? null : patient.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.625rem',
                        padding: '0.625rem 1rem',
                        cursor: 'pointer',
                        background: isSelected ? 'var(--color-teal-bg)' : 'transparent',
                        borderLeft: isSelected ? '3px solid var(--color-teal)' : '3px solid transparent',
                      }}
                    >
                      <span style={{ flex: 1, fontWeight: isSelected ? 600 : 400, fontSize: '0.8125rem', color: 'var(--color-text)' }}>
                        {displayName}
                      </span>
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
              style={{
                margin: '0.75rem',
                padding: '1rem',
                borderRadius: 'var(--radius)',
                border: '1px solid var(--color-teal-light)',
                background: 'var(--color-teal-bg)',
              }}
            >
              <p style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--color-teal)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.625rem' }}>
                Patient Profile
              </p>
              <p style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--color-text)', marginBottom: '0.375rem' }}>
                {selectedPatient.full_name ||
                  [selectedPatient.first_name, selectedPatient.last_name].filter(Boolean).join(' ') ||
                  'Unnamed patient'}
              </p>
              <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }}>
                <span style={badge(selectedPatient.status)}>{selectedPatient.status ?? '—'}</span>
              </div>
              <button
                onClick={() => setSelectedPatientId(null)}
                style={{
                  marginTop: '0.75rem',
                  fontSize: '0.75rem',
                  padding: '3px 10px',
                  border: '1px solid var(--color-teal-light)',
                  borderRadius: 'var(--radius-sm)',
                  background: 'transparent',
                  color: 'var(--color-teal)',
                  cursor: 'pointer',
                }}
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
