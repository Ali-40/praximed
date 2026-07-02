import { redirect } from 'next/navigation'

// Root route: redirect unauthenticated users to /login.
// Authenticated redirect to /dashboard is handled in Module 67 (login flow integration).
export default function Home() {
  redirect('/login')
}
