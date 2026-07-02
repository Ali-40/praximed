'use client'

// Dashboard page — PraxisMed Sprint 11 / Module 81
// Module 81: Confirm action on appointment request rows (status === 'new' only).
// Module 79: Visual polish — header subtitle, count pills, badge tokens, footer.

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { clearToken, getClinicId, getToken, isAuthenticated } from '@/lib/auth'
import {
  confirmAppointmentRequest,
  fetchAppointmentRequests,
  fetchPatients,
  fetchNotifications,
  fetchConsultations,
  AppointmentRequest,
  Patient,
  Notification,
  ConsultationSession,
} from '@/lib/api'

// ---------------------------------------------------------------------------
// Shared badge helper — keeps badge rendering DRY across all four sections.
// ---------------------------------------------------------------------------

const BADGE_STYLES: Record<string, { background: string; color: string }> = {
  new:       { background: 'var(--badge-blue-bg)',    color: 'var(--badge-blue-text)' },
  active:    { background: 'var(--badge-green-bg)',   color: 'var(--badge-green-text)' },
  approved:  { background: 'var(--badge-green-bg)',   color: 'var(--badge-green-text)' },
  urgent:    { background: 'var(--badge-red-bg)',     color: 'var(--badge-red-text)' },
  emergency: { background: 'var(--badge-red-bg)',     color: 'var(--badge-red-text)' },
}

function badgeStyle(value: string | null | undefined) {
  if (!value) return { background: 'var(--badge-neutral-bg)', color: 'var(--badge-neutral-text)' }
  return BADGE_STYLES[value] ?? { background: 'var(--badge-neutral-bg)', color: 'var(--badge-neutral-text)' }
}

// ---------------------------------------------------------------------------
// Small count pill shown in section headers when data is loaded.
// ---------------------------------------------------------------------------

function CountPill({ count }: { count: number }) {
  return (
    <span
      style={{
        fontSize: '0.7rem',
        fontWeight: 500,
        color: 'var(--color-text-muted)',
        background: 'var(--color-border)',
        padding: '1px 7px',
        borderRadius: 99,
        marginLeft: '0.4rem',
        verticalAlign: 'middle',
      }}
    >
      {count}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Dashboard page
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const router = useRouter()

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

  // Tracks which appointment request IDs have a Confirm call in-flight.
  const [confirmingIds, setConfirmingIds] = useState<Set<string>>(new Set())
  const [apptActionError, setApptActionError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace('/login')
      return
    }

    const token = getToken()
    const clinicId = getClinicId()

    if (!token || !clinicId) {
      router.replace('/login')
      return
    }

    fetchAppointmentRequests(clinicId, token)
      .then((rows) => setAppointments(rows))
      .catch(() => setApptError('Could not load appointment requests. Please try again.'))
      .finally(() => setApptLoading(false))

    fetchPatients(clinicId, token)
      .then((rows) => setPatients(rows))
      .catch(() => setPatientsError('Could not load patients. Please try again.'))
      .finally(() => setPatientsLoading(false))

    fetchNotifications(clinicId, token)
      .then((rows) => setNotifications(rows))
      .catch(() => setNotifError('Could not load notifications. Please try again.'))
      .finally(() => setNotifLoading(false))

    fetchConsultations(clinicId, token)
      .then((rows) => setConsultations(rows))
      .catch(() => setConsultError('Could not load consultations. Please try again.'))
      .finally(() => setConsultLoading(false))
  }, [router])

  function handleLogout() {
    clearToken()
    router.push('/login')
  }

  async function handleConfirm(requestId: string) {
    const token = getToken()
    const clinicId = getClinicId()
    if (!token || !clinicId) return

    setConfirmingIds((prev) => new Set(prev).add(requestId))
    setApptActionError(null)

    try {
      await confirmAppointmentRequest(requestId, clinicId, token)
      const rows = await fetchAppointmentRequests(clinicId, token)
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

  // Shared card style for the four sections
  const cardStyle: React.CSSProperties = {
    background: '#fff',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius)',
    padding: '1.25rem',
    boxShadow: 'var(--shadow-card)',
    marginBottom: '1.5rem',
  }

  const rowStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.5rem 0',
    borderBottom: '1px solid var(--color-border)',
    fontSize: '0.875rem',
  }

  const badgePillStyle = (value: string | null | undefined): React.CSSProperties => ({
    ...badgeStyle(value),
    padding: '2px 8px',
    borderRadius: 4,
    fontSize: '0.75rem',
  })

  return (
    <main style={{ minHeight: '100vh', background: 'var(--color-surface)' }}>
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                               */}
      {/* ------------------------------------------------------------------ */}
      <header
        style={{
          background: '#fff',
          borderBottom: '1px solid var(--color-border)',
          padding: '0.875rem 2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div>
          <span style={{ fontWeight: 700, fontSize: '1.125rem', color: 'var(--color-brand)' }}>
            PraxisMed
          </span>
          <p style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginTop: '1px' }}>
            Clinic Dashboard
          </p>
        </div>

        <button
          onClick={handleLogout}
          style={{
            fontSize: '0.875rem',
            padding: '0.375rem 0.875rem',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            background: '#fff',
            color: 'var(--color-text-muted)',
          }}
        >
          Logout
        </button>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* Page body                                                            */}
      {/* ------------------------------------------------------------------ */}
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem 1rem' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', color: 'var(--color-text)' }}>
          Clinic Overview
        </h2>

        {/* ---------------------------------------------------------------- */}
        {/* Appointments section (live)                                       */}
        {/* ---------------------------------------------------------------- */}
        <section data-section="appointments" style={cardStyle}>
          <h3 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>
            Appointments
            {!apptLoading && !apptError && <CountPill count={appointments.length} />}
          </h3>

          {apptLoading && (
            <p data-state="loading" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              Loading appointment requests…
            </p>
          )}
          {!apptLoading && apptError && (
            <p data-state="error" style={{ fontSize: '0.875rem', color: 'var(--color-danger)' }}>
              {apptError}
            </p>
          )}
          {!apptLoading && !apptError && appointments.length === 0 && (
            <p data-state="empty" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              No appointment requests found.
            </p>
          )}
          {!apptLoading && !apptError && appointments.length > 0 && (
            <ul data-state="list" style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {appointments.map((appt) => (
                <li key={appt.id} style={rowStyle}>
                  <span style={{ flex: 1, fontWeight: 500 }}>
                    {appt.patient_name ?? '—'}
                  </span>
                  <span style={badgePillStyle(appt.status)}>{appt.status}</span>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>
                    {appt.urgency_level}
                  </span>
                  {appt.status === 'new' && (
                    <button
                      data-action="confirm"
                      onClick={() => handleConfirm(appt.id)}
                      disabled={confirmingIds.has(appt.id)}
                      style={{
                        fontSize: '0.75rem',
                        padding: '2px 10px',
                        borderRadius: 4,
                        border: '1px solid var(--badge-green-text)',
                        background: confirmingIds.has(appt.id) ? 'var(--color-border)' : 'var(--badge-green-bg)',
                        color: confirmingIds.has(appt.id) ? 'var(--color-text-muted)' : 'var(--badge-green-text)',
                        cursor: confirmingIds.has(appt.id) ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {confirmingIds.has(appt.id) ? 'Confirming…' : 'Confirm'}
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
          {apptActionError && (
            <p data-state="action-error" style={{ fontSize: '0.875rem', color: 'var(--color-danger)', marginTop: '0.5rem' }}>
              {apptActionError}
            </p>
          )}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Patients section (live)                                           */}
        {/* ---------------------------------------------------------------- */}
        <section data-section="patients" style={cardStyle}>
          <h3 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>
            Patients
            {!patientsLoading && !patientsError && <CountPill count={patients.length} />}
          </h3>

          {patientsLoading && (
            <p data-state="loading" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              Loading patients…
            </p>
          )}
          {!patientsLoading && patientsError && (
            <p data-state="error" style={{ fontSize: '0.875rem', color: 'var(--color-danger)' }}>
              {patientsError}
            </p>
          )}
          {!patientsLoading && !patientsError && patients.length === 0 && (
            <p data-state="empty" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              No patients found.
            </p>
          )}
          {!patientsLoading && !patientsError && patients.length > 0 && (
            <ul data-state="list" style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {patients.map((patient) => (
                <li key={patient.id} style={rowStyle}>
                  <span style={{ flex: 1, fontWeight: 500 }}>
                    {patient.full_name ||
                      [patient.first_name, patient.last_name].filter(Boolean).join(' ') ||
                      'Unnamed patient'}
                  </span>
                  <span style={badgePillStyle(patient.status)}>{patient.status ?? '—'}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Notifications section (live)                                      */}
        {/* ---------------------------------------------------------------- */}
        <section data-section="notifications" style={cardStyle}>
          <h3 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>
            Notifications
            {!notifLoading && !notifError && <CountPill count={notifications.length} />}
          </h3>

          {notifLoading && (
            <p data-state="loading" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              Loading notifications…
            </p>
          )}
          {!notifLoading && notifError && (
            <p data-state="error" style={{ fontSize: '0.875rem', color: 'var(--color-danger)' }}>
              {notifError}
            </p>
          )}
          {!notifLoading && !notifError && notifications.length === 0 && (
            <p data-state="empty" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              No notifications found.
            </p>
          )}
          {!notifLoading && !notifError && notifications.length > 0 && (
            <ul data-state="list" style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {notifications.map((notif) => (
                <li key={notif.id} style={rowStyle}>
                  <span style={{ flex: 1, fontWeight: 500 }}>
                    {notif.title ?? '—'}
                  </span>
                  <span style={badgePillStyle(notif.priority)}>{notif.priority ?? '—'}</span>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>
                    {notif.notification_type ?? '—'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Consultations section (live)                                      */}
        {/* ---------------------------------------------------------------- */}
        <section data-section="consultations" style={cardStyle}>
          <h3 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>
            Consultations
            {!consultLoading && !consultError && <CountPill count={consultations.length} />}
          </h3>

          {consultLoading && (
            <p data-state="loading" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              Loading consultations…
            </p>
          )}
          {!consultLoading && consultError && (
            <p data-state="error" style={{ fontSize: '0.875rem', color: 'var(--color-danger)' }}>
              {consultError}
            </p>
          )}
          {!consultLoading && !consultError && consultations.length === 0 && (
            <p data-state="empty" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              No consultations found.
            </p>
          )}
          {!consultLoading && !consultError && consultations.length > 0 && (
            <ul data-state="list" style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {consultations.map((consult) => (
                <li key={consult.id} style={rowStyle}>
                  <span style={{ flex: 1, fontWeight: 500 }}>
                    {consult.title ?? '—'}
                  </span>
                  <span style={badgePillStyle(consult.approval_status ?? undefined)}>
                    {consult.approval_status ?? consult.status ?? '—'}
                  </span>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>
                    {consult.source ?? '—'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Local-demo footer label                                           */}
        {/* ---------------------------------------------------------------- */}
        <p
          style={{
            textAlign: 'center',
            fontSize: '0.7rem',
            color: 'var(--color-text-muted)',
            marginTop: '1rem',
            paddingBottom: '1rem',
          }}
        >
          Local demo — all data is fake and for development only
        </p>
      </div>
    </main>
  )
}
