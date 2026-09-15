import { useState } from 'react'
import { api } from './api'
import SchoolCrest from './public/components/SchoolCrest'

export default function ActivateFlow({ token, onActivated }) {
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    setLoading(true)
    try {
      await api.activateAccount(token, password)
      setSuccess(true)
      setTimeout(() => {
        onActivated() // Will redirect to login without token
      }, 2000)
    } catch (requestError) {
      setError(requestError.message || 'Activation failed. The token may be expired or invalid.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <main className="auth-page">
        <div className="auth-brand">
          <SchoolCrest size={36} variant="gold" />
          <span>Riverside Academy</span>
        </div>
        <div className="auth-card">
          <h1>Account Activated!</h1>
          <p className="muted">Your account is now ready. Redirecting you to login...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="auth-page">
      <div className="auth-brand">
        <SchoolCrest size={36} variant="gold" />
        <span>Riverside Academy</span>
      </div>
      <div className="auth-card">
        <p className="eyebrow">ACCOUNT SETUP</p>
        <h1>Welcome to Schoolhub.</h1>
        <p className="muted">Set your password to activate your account and access the portal.</p>

        <form onSubmit={submit}>
          <label>New Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          </label>
          <label>Confirm Password
            <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required minLength={8} />
          </label>
          
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button auth-wide" type="submit" disabled={loading}>
            {loading ? 'Activating...' : 'Activate Account'} <span>→</span>
          </button>
        </form>
      </div>
    </main>
  )
}

