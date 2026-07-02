'use client'

// Dashboard page — PraxisMed Sprint 8 / Module 68
// Wires Appointments section to GET /appointment-requests.
// Patients / Notifications / Consultations remain as placeholders (Module 69+).

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { clearToken, getClinicId, getToken, isAuthenticated } from '@/lib/auth'
import { fetchAppointmentRequests, AppointmentRequest } from '@/lib/api'

const PLACEHOLDER_SECTIONS = [
  {
    key: 'patients',
    label: 'Patients',
    description: 'Browse and search registered patients.',
  },
  {
    key: 'notifications',
    label: 'Notifications',
    description: 'Review clinic alerts and urgent call notifications.',
  },
  {
    key: 'consultations',
    label: 'Consultations',
    description: 'Access consultation sessions and clinical summaries.',
  },
]

export default function DashboardPage() {
  const router = useRouter()

  const [appointments, setAppointments] = useState<AppointmentRequest[]>([])
  const [apptLoading, setApptLoading] = useState(true)
  const [apptError, setApptError] = useState<string | null>(null)

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
        {/* Appointments section (live data)                                  */}
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

          {/* Loading state */}
          {apptLoading && (
            <p
              data-state="loading"
              style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}
            >
              Loading appointment requests…
            </p>
          )}

          {/* Error state */}
          {!apptLoading && apptError && (
            <p
              data-state="error"
              style={{ fontSize: '0.875rem', color: 'var(--color-danger)' }}
            >
              {apptError}
            </p>
          )}

          {/* Empty state */}
          {!apptLoading && !apptError && appointments.length === 0 && (
            <p
              data-state="empty"
              style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}
            >
              No appointment requests found.
            </p>
          )}

          {/* Appointment list */}
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
        {/* Placeholder cards for remaining sections                          */}
        {/* ---------------------------------------------------------------- */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: '1rem',
          }}
        >
          {PLACEHOLDER_SECTIONS.map((section) => (
            <div
              key={section.key}
              data-section={section.key}
              style={{
                background: '#fff',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius)',
                padding: '1.25rem',
                boxShadow: 'var(--shadow-card)',
                opacity: 0.7,
                cursor: 'not-allowed',
              }}
            >
              <h3 style={{ fontWeight: 600, marginBottom: '0.4rem' }}>{section.label}</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                {section.description}
              </p>
              <span
                style={{
                  display: 'inline-block',
                  marginTop: '0.75rem',
                  fontSize: '0.7rem',
                  background: 'var(--color-border)',
                  borderRadius: 4,
                  padding: '2px 6px',
                  color: 'var(--color-text-muted)',
                }}
              >
                Coming soon
              </span>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
