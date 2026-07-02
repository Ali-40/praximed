// Auth helpers — PraxisMed Sprint 8 / Module 66
//
// Token storage uses sessionStorage (local development only).
// For production: replace with httpOnly cookies set by the backend
// /auth/session endpoint — do not store JWTs in localStorage or
// sessionStorage in a production deployment.

import { apiFetch } from './api'

const TOKEN_KEY = 'praximed_access_token'

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

// Calls POST /auth/login and returns the token payload.
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

export function storeToken(token: string): void {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem(TOKEN_KEY, token)
  }
}

export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return sessionStorage.getItem(TOKEN_KEY)
  }
  return null
}

export function clearToken(): void {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(TOKEN_KEY)
  }
}

export function isAuthenticated(): boolean {
  return getToken() !== null
}

// Decodes the clinic_id claim from the stored JWT payload without verifying
// the signature (verification happens on the backend for every request).
export function getClinicId(): string | null {
  const token = getToken()
  if (!token) return null
  try {
    const b64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    const payload = JSON.parse(atob(b64)) as Record<string, unknown>
    return typeof payload.clinic_id === 'string' ? payload.clinic_id : null
  } catch {
    return null
  }
}
