'use client'

// Dashboard page — PraxisMed Sprint 8 / Module 71
// Appointments, Patients, Notifications, and Consultations sections are live.

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { clearToken, getClinicId, getToken, isAuthenticated } from '@/lib/auth'
import {
  fetchAppointmentRequests,
  fetchPatients,
  fetchNotifications,
  fetchConsultations,
  AppointmentRequest,
  Patient,
  Notification,
  ConsultationSession,
} from '@/lib/api'

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

  return (
    <main style={{ minHeight: '100vh', background: 'var(--color-surface)' }}>
      {/* Header */}
      <header
        style={{
          background: '#fff',
          borderBottom: '1px solid var(--color-border)',
          padding: '1rem 2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span
          style={{ fontWeight: 700, fontSize: '1.25rem', color: 'var(--color-brand)' }}
        >
          PraxisMed
        </span>

        <button
          onClick={handleLogout}
          style={{
            fontSize: '0.875rem',
            padding: '0.375rem 0.875rem',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            background: '#fff',
            color: 'var(--color-text-muted)',
            cursor: 'pointer',
          }}
        >
          Logout
        </button>
      </header>

      <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem 1rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem' }}>
          Welcome to PraxisMed
        </h2>

        {/* ---------------------------------------------------------------- */}
        {/* Appointments section (live)                                       */}
        {/* ---------------------------------------------------------------- */}
        <section
          data-section="appointments"
          style={{
            background: '#fff',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            padding: '1.25rem',
            boxShadow: 'var(--shadow-card)',
            marginBottom: '1.5rem',
          }}
        >
          <h3 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>Appointments</h3>

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
            <ul
              data-state="list"
              style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}
            >
              {appointments.map((appt) => (
                <li
                  key={appt.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.5rem 0',
                    borderBottom: '1px solid var(--color-border)',
                    fontSize: '0.875rem',
                  }}
                >
                  <span style={{ flex: 1, fontWeight: 500 }}>
                    {appt.patient_name ?? '—'}
                  </span>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: 4,
                      fontSize: '0.75rem',
                      background: appt.status === 'new' ? '#dbeafe' : 'var(--color-border)',
                      color: appt.status === 'new' ? '#1e40af' : 'var(--color-text-muted)',
                    }}
                  >
                    {appt.status}
                  </span>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>
                    {appt.urgency_level}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Patients section (live)                                           */}
        {/* ---------------------------------------------------------------- */}
        <section
          data-section="patients"
          style={{
            background: '#fff',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            padding: '1.25rem',
            boxShadow: 'var(--shadow-card)',
            marginBottom: '1.5rem',
          }}
        >
          <h3 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>Patients</h3>

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
            <ul
              data-state="list"
              style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}
            >
              {patients.map((patient) => (
                <li
                  key={patient.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.5rem 0',
                    borderBottom: '1px solid var(--color-border)',
                    fontSize: '0.875rem',
                  }}
                >
                  <span style={{ flex: 1, fontWeight: 500 }}>
                    {[patient.first_name, patient.last_name].filter(Boolean).join(' ') || '—'}
                  </span>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: 4,
                      fontSize: '0.75rem',
                      background: patient.status === 'active' ? '#dcfce7' : 'var(--color-border)',
                      color: patient.status === 'active' ? '#166534' : 'var(--color-text-muted)',
                    }}
                  >
                    {patient.status ?? '—'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Notifications section (live)                                      */}
        {/* ---------------------------------------------------------------- */}
        <section
          data-section="notifications"
          style={{
            background: '#fff',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            padding: '1.25rem',
            boxShadow: 'var(--shadow-card)',
            marginBottom: '1.5rem',
          }}
        >
          <h3 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>Notifications</h3>

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
            <ul
              data-state="list"
              style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}
            >
              {notifications.map((notif) => (
                <li
                  key={notif.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.5rem 0',
                    borderBottom: '1px solid var(--color-border)',
                    fontSize: '0.875rem',
                  }}
                >
                  <span style={{ flex: 1, fontWeight: 500 }}>
                    {notif.title ?? '—'}
                  </span>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: 4,
                      fontSize: '0.75rem',
                      background: notif.priority === 'urgent' || notif.priority === 'emergency'
                        ? '#fee2e2'
                        : 'var(--color-border)',
                      color: notif.priority === 'urgent' || notif.priority === 'emergency'
                        ? '#991b1b'
                        : 'var(--color-text-muted)',
                    }}
                  >
                    {notif.priority ?? '—'}
                  </span>
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
        <section
          data-section="consultations"
          style={{
            background: '#fff',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            padding: '1.25rem',
            boxShadow: 'var(--shadow-card)',
            marginBottom: '1.5rem',
          }}
        >
          <h3 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>Consultations</h3>

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
            <ul
              data-state="list"
              style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}
            >
              {consultations.map((consult) => (
                <li
                  key={consult.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.5rem 0',
                    borderBottom: '1px solid var(--color-border)',
                    fontSize: '0.875rem',
                  }}
                >
                  <span style={{ flex: 1, fontWeight: 500 }}>
                    {consult.title ?? '—'}
                  </span>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: 4,
                      fontSize: '0.75rem',
                      background: consult.approval_status === 'approved' ? '#dcfce7' : 'var(--color-border)',
                      color: consult.approval_status === 'approved' ? '#166534' : 'var(--color-text-muted)',
                    }}
                  >
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
      </div>
    </main>
  )
}
