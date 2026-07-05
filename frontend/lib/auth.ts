// Auth helpers — PraxisMed Sprint 8 / Module 66
// Updated Sprint 17 / Module 120 — httpOnly cookie session; no sessionStorage.
//
// Session state is owned by the backend: the praximed_session cookie is set on
// POST /auth/login and cleared on POST /auth/logout. The browser never reads
// the cookie value directly (httpOnly). Use getMe() to check session status.

import { apiFetch } from './api'

export interface LoginResult {
  access_token: string
  token_type: string
  expires_in_seconds: number
  user: {
    id: string
    clinic_id: string
    email: string
    role: string
  }
}

export interface CurrentUser {
  user_id: string
  clinic_id: string
  role: string
}

// Calls POST /auth/login. On success the backend sets the praximed_session
// httpOnly cookie. Returns the full login payload for display use.
// Throws on non-2xx response.
export async function loginUser(
  email: string,
  password: string,
  clinicId: string,
): Promise<LoginResult> {
  const resp = await apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password, clinic_id: clinicId }),
  })

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}))
    throw new Error((body as { detail?: string }).detail ?? 'Login failed')
  }

  return resp.json() as Promise<LoginResult>
}

// Calls GET /auth/me using the session cookie. Returns the current user or null
// if the session is missing or expired. Safe to call on any page load.
export async function getMe(): Promise<CurrentUser | null> {
  try {
    const resp = await apiFetch('/auth/me')
    if (!resp.ok) return null
    return resp.json() as Promise<CurrentUser>
  } catch {
    return null
  }
}

// Calls POST /auth/logout to clear the session cookie on the backend.
export async function logout(): Promise<void> {
  await apiFetch('/auth/logout', { method: 'POST' })
}
