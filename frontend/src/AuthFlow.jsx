import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from './api'
import SchoolCrest from './public/components/SchoolCrest'

export default function AuthFlow({ initialMode = 'login', onAuthenticated }) {
  const [mode, setMode] = useState(initialMode === 'register' ? 'login' : initialMode)
  const [email, setEmail] = useState(() => localStorage.getItem('bfa_remember_email') || '')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(() => Boolean(localStorage.getItem('bfa_remember_email')))
  const [error, setError] = useState('')
  const [ssoNotice, setSsoNotice] = useState('')

  async function submit(event) {
    event.preventDefault()
    setError('')
    setSsoNotice('')
    try {
      if (mode === 'forgot') {
        await api.requestPasswordReset(email)
        setError('If that email exists, password reset instructions have been sent.')
        return
      }

      if (rememberMe) {
        localStorage.setItem('bfa_remember_email', email)
      } else {
        localStorage.removeItem('bfa_remember_email')
      }

      onAuthenticated(await api.login(email, password))
    } catch (requestError) {
      setError(requestError.message || 'Authentication failed. Please check your credentials.')
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-brand">
        <SchoolCrest size={36} variant="gold" />
        <span>Riverside Academy</span>
      </div>
      <div className="auth-card">
        <Link className="text-button" to="/" style={{ display: 'inline-block', marginBottom: 14 }}>← Back to school website</Link>
        <p className="eyebrow">{mode === 'login' ? 'PORTAL ACCESS' : 'PASSWORD RECOVERY'}</p>
        <h1>{mode === 'login' ? 'Make every school day count.' : 'Reset your password.'}</h1>
        <p className="muted">
          {mode === 'login'
            ? 'Sign in to access your student, teacher, or staff dashboard.'
            : 'Enter your registered email address and we will send reset instructions.'}
        </p>

        {mode === 'login' && (
          <>
            <div className="sso-buttons">
              <button
                type="button"
                className="sso-btn"
                onClick={() => setSsoNotice('Google Workspace sign-in is managed by school IT. Please use your school email and password.')}
              >
                <svg viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.35 24 12 24z"/>
                  <path fill="#FBBC05" d="M5.28 14.27A7.2 7.2 0 0 1 4.9 12c0-.79.14-1.57.38-2.27V6.58H1.25A11.97 11.97 0 0 0 0 12c0 1.92.45 3.74 1.25 5.42l4.03-3.15z"/>
                  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.35 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                </svg>
                Google
              </button>
              <button
                type="button"
                className="sso-btn"
                onClick={() => setSsoNotice('Microsoft 365 sign-in is managed by school IT. Please use your school email and password.')}
              >
                <svg viewBox="0 0 23 23">
                  <path fill="#f35325" d="M1 1h10v10H1z"/>
                  <path fill="#81bc06" d="M12 1h10v10H12z"/>
                  <path fill="#05a6f0" d="M1 12h10v10H1z"/>
                  <path fill="#ffba08" d="M12 12h10v10H12z"/>
                </svg>
                Microsoft
              </button>
            </div>
            {ssoNotice && <p style={{ fontSize: 11, color: '#64748b', margin: '4px 0 12px', lineHeight: 1.4 }}>{ssoNotice}</p>}

            <div className="auth-divider">
              <span>OR SIGN IN WITH EMAIL</span>
            </div>
          </>
        )}

        <form onSubmit={submit}>
          <label>Email address
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          {mode === 'login' && (
            <>
              <label>Password
                <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
              </label>
              <div className="auth-remember-row">
                <label className="auth-remember-label">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span>Remember me</span>
                </label>
                <button type="button" className="auth-forgot-link" onClick={() => { setMode('forgot'); setError(''); setSsoNotice('') }}>
                  Forgot password?
                </button>
              </div>
            </>
          )}
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button auth-wide" type="submit">
            {mode === 'login' ? 'Sign in to portal' : 'Send reset link'} <span>→</span>
          </button>
        </form>

        {mode === 'forgot' && (
          <button className="forgot-link" onClick={() => { setMode('login'); setError(''); setSsoNotice('') }}>
            ← Back to sign in
          </button>
        )}

        <p className="muted" style={{ marginTop: 22, fontSize: 12.5, lineHeight: 1.6 }}>
          Don't have a portal account yet? Student, teacher, and parent accounts are provisioned by the administration after an{' '}
          <Link to="/admissions" style={{ color: 'var(--bfa-gold, #b38848)', fontWeight: 600 }}>admissions</Link> or{' '}
          <Link to="/careers" style={{ color: 'var(--bfa-gold, #b38848)', fontWeight: 600 }}>employment</Link> application is approved.
        </p>
      </div>
    </main>
  )
}

