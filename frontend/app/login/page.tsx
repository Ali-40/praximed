'use client'

// Login page — PraxisMed Sprint 8 / Module 67
// Wires form submission to POST /auth/login via loginUser helper.

import { FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import { loginUser } from '@/lib/auth'

export default function LoginPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const form = e.currentTarget
    const email = (form.elements.namedItem('email') as HTMLInputElement).value
    const password = (form.elements.namedItem('password') as HTMLInputElement).value
    const clinicId = (form.elements.namedItem('clinic_id') as HTMLInputElement).value

    try {
      await loginUser(email, password, clinicId)
      router.push('/dashboard')
    } catch {
      // Generic message only — do not reveal whether email or password was wrong.
      setError('Sign-in failed. Please check your details and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 400,
          background: '#fff',
          borderRadius: 'var(--radius)',
          boxShadow: 'var(--shadow-card)',
          padding: '2rem',
          border: '1px solid var(--color-border)',
        }}
      >
        <h1
          style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            marginBottom: '0.25rem',
            color: 'var(--color-brand)',
          }}
        >
          PraxisMed
        </h1>
        <p
          style={{
            color: 'var(--color-text-muted)',
            marginBottom: '1.5rem',
            fontSize: '0.875rem',
          }}
        >
          Sign in to your clinic dashboard
        </p>

        {error && (
          <p
            role="alert"
            style={{
              color: 'var(--color-danger)',
              fontSize: '0.875rem',
              marginBottom: '1rem',
              padding: '0.5rem 0.75rem',
              background: '#fef2f2',
              borderRadius: 'var(--radius)',
              border: '1px solid #fecaca',
            }}
          >
            {error}
          </p>
        )}

        <form
          onSubmit={handleSubmit}
          style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}
        >
          <div>
            <label
              htmlFor="clinic_id"
              style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 500,
                marginBottom: '0.25rem',
              }}
            >
              Clinic ID
            </label>
            <input
              id="clinic_id"
              name="clinic_id"
              type="text"
              required
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius)',
                fontSize: '0.875rem',
                outline: 'none',
                fontFamily: 'monospace',
              }}
            />
          </div>

          <div>
            <label
              htmlFor="email"
              style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 500,
                marginBottom: '0.25rem',
              }}
            >
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              placeholder="doctor@clinic.at"
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius)',
                fontSize: '1rem',
                outline: 'none',
              }}
            />
          </div>

          <div>
            <label
              htmlFor="password"
              style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 500,
                marginBottom: '0.25rem',
              }}
            >
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius)',
                fontSize: '1rem',
                outline: 'none',
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.625rem',
              background: loading ? 'var(--color-text-muted)' : 'var(--color-brand)',
              color: '#fff',
              border: 'none',
              borderRadius: 'var(--radius)',
              fontSize: '1rem',
              fontWeight: 600,
              marginTop: '0.5rem',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </main>
  )
}
