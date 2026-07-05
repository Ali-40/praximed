'use client'

// Dashboard page — PraxisMed Sprint 11 / Module 81
// Updated Sprint 17 / Module 120 — cookie-based session; no token/sessionStorage.
// Updated Sprint 17 / Module 125 — notifications show message+status; appointments have View summary toggle.
// Updated Sprint 18 / Module 126 — Fabel 5 premium UI/UX polish.

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getMe, logout } from '@/lib/auth'
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

// ---------------------------------------------------------------------------
// Metric card
// ---------------------------------------------------------------------------

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
        flex: '1 1 140px',
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

// ---------------------------------------------------------------------------
// Dashboard page
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const router = useRouter()

  const [clinicId, setClinicId] = useState<string | null>(null)

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

  useEffect(() => {
    getMe().then((user) => {
      if (!user) {
        router.replace('/login')
        return
      }

      setClinicId(user.clinic_id)

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

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)', display: 'flex', flexDirection: 'column' }}>

      {/* ------------------------------------------------------------------ */}
      {/* Header                                                               */}
      {/* ------------------------------------------------------------------ */}
      <header
        style={{
          background: 'var(--color-card)',
          borderBottom: '1px solid var(--color-border)',
          padding: '0 2rem',
          height: 60,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div>
            <span style={{ fontWeight: 700, fontSize: '1.0625rem', color: 'var(--color-text)', letterSpacing: '-0.01em' }}>
              PraxisMed
            </span>
            <span style={{ marginLeft: '0.5rem', fontSize: '0.8125rem', color: 'var(--color-text-muted)', fontWeight: 400 }}>
              Clinic Dashboard
            </span>
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

        <button
          onClick={handleLogout}
          style={{
            fontSize: '0.8125rem',
            fontWeight: 500,
            padding: '0.375rem 0.875rem',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--color-card)',
            color: 'var(--color-text-muted)',
            transition: 'none',
          }}
        >
          Logout
        </button>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* Page body                                                            */}
      {/* ------------------------------------------------------------------ */}
      <main style={{ flex: 1, maxWidth: 1060, margin: '0 auto', width: '100%', padding: '2rem 1.5rem 3rem' }}>

        {/* Page title */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h1 style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--color-text)', letterSpacing: '-0.01em' }}>
            Clinic Overview
          </h1>
          <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginTop: '0.2rem' }}>
            Fake-data staging environment — no real patient data
          </p>
        </div>

        {/* ---------------------------------------------------------------- */}
        {/* Metrics row                                                       */}
        {/* ---------------------------------------------------------------- */}
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1.75rem' }}>
          <MetricCard label="Appointments" value={appointments.length} loading={apptLoading} />
          <MetricCard label="Patients" value={patients.length} loading={patientsLoading} />
          <MetricCard label="Notifications" value={notifications.length} loading={notifLoading} />
          <MetricCard label="Pending confirmations" value={pendingCount} loading={apptLoading} />
        </div>

        {/* ---------------------------------------------------------------- */}
        {/* Appointments — primary section                                    */}
        {/* ---------------------------------------------------------------- */}
        <section data-section="appointments" style={{ marginBottom: '1.5rem' }}>
          <SectionCard>
            <SectionHeader
              title="Appointment Requests"
              count={!apptLoading && !apptError ? appointments.length : undefined}
            />

            {apptLoading && <LoadingState message="Loading appointment requests…" />}
            {!apptLoading && apptError && <ErrorState message={apptError} />}
            {!apptLoading && !apptError && appointments.length === 0 && (
              <EmptyState message="No appointment requests. New requests will appear here after a Vapi call." />
            )}

            {!apptLoading && !apptError && appointments.length > 0 && (
              <ul data-state="list" style={{ listStyle: 'none', padding: '0 0 0.5rem' }}>
                {appointments.map((appt, idx) => {
                  const summaryEntry = summaries[appt.id]
                  const isOpen = summaryOpenId === appt.id
                  const isLast = idx === appointments.length - 1
                  return (
                    <li
                      key={appt.id}
                      style={{
                        borderBottom: isLast ? 'none' : '1px solid var(--color-border-soft)',
                      }}
                    >
                      {/* Row */}
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          flexWrap: 'wrap',
                          gap: '0.5rem',
                          padding: '0.875rem 1.25rem',
                        }}
                      >
                        <span style={{ flex: '1 1 160px', fontWeight: 600, fontSize: '0.9rem', color: 'var(--color-text)' }}>
                          {appt.patient_name ?? '—'}
                        </span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', flexWrap: 'wrap' }}>
                          <span style={badge(appt.status)}>{appt.status}</span>
                          <span style={badge(appt.urgency_level)}>{appt.urgency_level}</span>
                        </div>
                        <div style={{ display: 'flex', gap: '0.375rem' }}>
                          <button
                            data-action="view-summary"
                            onClick={() => handleViewSummary(appt)}
                            style={{
                              fontSize: '0.775rem',
                              fontWeight: 500,
                              padding: '4px 12px',
                              borderRadius: 'var(--radius-sm)',
                              border: '1px solid var(--color-border)',
                              background: isOpen ? 'var(--color-brand-50)' : 'var(--color-card)',
                              color: isOpen ? 'var(--color-brand)' : 'var(--color-text-muted)',
                            }}
                          >
                            {isOpen ? 'Hide summary' : 'View summary'}
                          </button>
                          {appt.status === 'new' && (
                            <button
                              data-action="confirm"
                              onClick={() => handleConfirm(appt.id)}
                              disabled={confirmingIds.has(appt.id)}
                              style={{
                                fontSize: '0.775rem',
                                fontWeight: 600,
                                padding: '4px 14px',
                                borderRadius: 'var(--radius-sm)',
                                border: '1px solid var(--color-success)',
                                background: confirmingIds.has(appt.id) ? 'var(--color-border)' : 'var(--color-success-bg)',
                                color: confirmingIds.has(appt.id) ? 'var(--color-text-muted)' : 'var(--color-success)',
                                cursor: confirmingIds.has(appt.id) ? 'not-allowed' : 'pointer',
                              }}
                            >
                              {confirmingIds.has(appt.id) ? 'Confirming…' : 'Confirm'}
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Summary panel */}
                      {isOpen && (
                        <div
                          data-state="summary-panel"
                          style={{
                            margin: '0 1.25rem 0.875rem',
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
                                <dd style={{ margin: 0, color: 'var(--color-brand)', fontWeight: 600 }}>{summaryEntry.suggested_next_action}</dd>
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
                      )}
                    </li>
                  )
                })}
              </ul>
            )}

            {apptActionError && (
              <div style={{ margin: '0 1.25rem 0.875rem' }}>
                <ErrorState message={apptActionError} />
              </div>
            )}
          </SectionCard>
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Two-column: Patients + Notifications                              */}
        {/* ---------------------------------------------------------------- */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem',
            marginBottom: '1.5rem',
          }}
        >
          {/* Patients */}
          <section data-section="patients">
            <SectionCard style={{ height: '100%' }}>
              <SectionHeader
                title="Patients"
                count={!patientsLoading && !patientsError ? patients.length : undefined}
              />

              {patientsLoading && <LoadingState message="Loading patients…" />}
              {!patientsLoading && patientsError && <ErrorState message={patientsError} />}
              {!patientsLoading && !patientsError && patients.length === 0 && (
                <EmptyState message="No patients on file yet." />
              )}
              {!patientsLoading && !patientsError && patients.length > 0 && (
                <ul data-state="list" style={{ listStyle: 'none', padding: '0.25rem 0 0.5rem' }}>
                  {patients.map((patient, idx) => (
                    <li
                      key={patient.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        padding: '0.625rem 1.25rem',
                        borderBottom: idx < patients.length - 1 ? '1px solid var(--color-border-soft)' : 'none',
                        fontSize: '0.875rem',
                      }}
                    >
                      <span style={{ flex: 1, fontWeight: 500, color: 'var(--color-text)' }}>
                        {patient.full_name ||
                          [patient.first_name, patient.last_name].filter(Boolean).join(' ') ||
                          'Unnamed patient'}
                      </span>
                      <span style={badge(patient.status)}>{patient.status ?? '—'}</span>
                    </li>
                  ))}
                </ul>
              )}
            </SectionCard>
          </section>

          {/* Notifications */}
          <section data-section="notifications">
            <SectionCard style={{ height: '100%' }}>
              <SectionHeader
                title="Notifications"
                count={!notifLoading && !notifError ? notifications.length : undefined}
              />

              {notifLoading && <LoadingState message="Loading notifications…" />}
              {!notifLoading && notifError && <ErrorState message={notifError} />}
              {!notifLoading && !notifError && notifications.length === 0 && (
                <EmptyState message="No notifications." />
              )}
              {!notifLoading && !notifError && notifications.length > 0 && (
                <ul data-state="list" style={{ listStyle: 'none', padding: '0.25rem 0 0.5rem' }}>
                  {notifications.map((notif, idx) => {
                    const isPending = notif.status === 'pending'
                    const truncatedMsg = notif.message
                      ? notif.message.length > 100
                        ? notif.message.slice(0, 100) + '…'
                        : notif.message
                      : null
                    return (
                      <li
                        key={notif.id}
                        data-notification-status={notif.status}
                        style={{
                          padding: '0.75rem 1.25rem',
                          borderBottom: idx < notifications.length - 1 ? '1px solid var(--color-border-soft)' : 'none',
                          borderLeft: isPending ? '3px solid var(--color-brand)' : '3px solid transparent',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: truncatedMsg ? '0.3rem' : 0 }}>
                          <span style={{ flex: 1, fontWeight: 600, fontSize: '0.8125rem', color: 'var(--color-text)' }}>
                            {notif.title ?? '—'}
                          </span>
                          <span style={badge(notif.status)}>{notif.status ?? '—'}</span>
                          <span style={badge(notif.priority)}>{notif.priority ?? '—'}</span>
                        </div>
                        {truncatedMsg && (
                          <p
                            data-notification-message
                            style={{ fontSize: '0.775rem', color: 'var(--color-text-muted)', lineHeight: 1.45, margin: 0 }}
                          >
                            {truncatedMsg}
                          </p>
                        )}
                      </li>
                    )
                  })}
                </ul>
              )}
            </SectionCard>
          </section>
        </div>

        {/* ---------------------------------------------------------------- */}
        {/* Consultations                                                     */}
        {/* ---------------------------------------------------------------- */}
        <section data-section="consultations">
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

        {/* ---------------------------------------------------------------- */}
        {/* Footer                                                            */}
        {/* ---------------------------------------------------------------- */}
        <p
          style={{
            textAlign: 'center',
            fontSize: '0.6875rem',
            color: 'var(--color-text-faint)',
            marginTop: '2rem',
            letterSpacing: '0.02em',
          }}
        >
          Staging demo — fake data only · No real patient data · Production PHI: NO-GO
        </p>
      </main>
    </div>
  )
}
