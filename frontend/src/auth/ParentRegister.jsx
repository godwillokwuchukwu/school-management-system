import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { publicApi } from '../public/api'
import { ErrorBanner, Loading, PageHero } from '../public/ui'
import { formatDate } from '../public/formatters'
import './StudentAuth.css'

function ApplicantAuthInline({ onSignedIn }) {
  // Login State
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [showLoginPassword, setShowLoginPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [loginLoading, setLoginLoading] = useState(false)
  const [loginError, setLoginError] = useState('')

  // Register State
  const [regForm, setRegForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false,
  })
  const [showRegPassword, setShowRegPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [regLoading, setRegLoading] = useState(false)
  const [regError, setRegError] = useState('')

  // Password Strength Calculation
  const calculateStrength = (pass) => {
    if (!pass) return { score: 0, label: '', color: '' }
    let score = 0
    if (pass.length >= 10) score += 1
    if (/[A-Z]/.test(pass)) score += 1
    if (/[a-z]/.test(pass)) score += 1
    if (/[0-9]/.test(pass)) score += 1
    if (/[^A-Za-z0-9]/.test(pass)) score += 1

    if (score <= 2) return { score: 1, label: 'Weak', color: '#dc2626' }
    if (score <= 4) return { score: 2, label: 'Medium', color: '#d97706' }
    return { score: 3, label: 'Strong', color: '#16a34a' }
  }

  const passwordStrength = calculateStrength(regForm.password)
  const passwordsMatch = regForm.confirmPassword && regForm.password === regForm.confirmPassword
  const passwordsMismatch = regForm.confirmPassword && regForm.password !== regForm.confirmPassword

  const updateReg = (field, value) => {
    setRegForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoginError('')
    setLoginLoading(true)
    try {
      await publicApi.login(loginEmail, loginPassword)
      onSignedIn()
    } catch (err) {
      setLoginError(err.message || 'Authentication failed. Please check your credentials.')
    } finally {
      setLoginLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setRegError('')
    if (regForm.password !== regForm.confirmPassword) {
      setRegError('Passwords do not match.')
      return
    }
    if (!regForm.agreeTerms) {
      setRegError('You must accept the terms and conditions.')
      return
    }
    setRegLoading(true)
    try {
      await publicApi.register({
        first_name: regForm.firstName,
        last_name: regForm.lastName,
        email: regForm.email,
        phone: regForm.phone,
        password: regForm.password,
      })
      await publicApi.login(regForm.email, regForm.password)
      onSignedIn()
    } catch (err) {
      setRegError(err.message || 'Registration failed. Please try again.')
    } finally {
      setRegLoading(false)
    }
  }

  return (
    <div className="student-portal-wrapper" style={{ minHeight: 'auto' }}>
      {/* HERO SECTION */}
      <section className="student-portal-hero">
        <div className="student-hero-content">
          <div className="student-hero-text">
            <span className="student-hero-eyebrow">RIVERSIDE ACADEMY • PARENT & GUARDIAN</span>
            <h1 className="student-hero-title">Parent Registration Portal</h1>
            <p className="student-hero-desc">
              Connect with your child's academic journey. Sign in to check relationship verification status or create a new parent account to link with a student record.
            </p>
          </div>
          <div className="student-hero-decor">
            <div className="student-hero-motto">
              <span>Learn • Grow • Succeed</span>
              <svg className="student-motto-curve" viewBox="0 0 160 20" fill="none">
                <path d="M5 15 C 50 2, 110 2, 155 15" stroke="#c5a059" strokeWidth="2.5" strokeLinecap="round" />
              </svg>
            </div>
            <div className="student-hero-image-frame">
              <img src="/school-campus.jpg" alt="Riverside Academy Campus" className="student-hero-img" />
            </div>
          </div>
        </div>
        {/* Wave Divider */}
        <div className="student-hero-wave">
          <svg viewBox="0 0 1440 80" fill="none" preserveAspectRatio="none">
            <path
              d="M0,40 C320,85 720,5 1100,60 C1250,75 1380,50 1440,40 L1440,80 L0,80 Z"
              fill="#faf7f2"
            />
          </svg>
        </div>
      </section>

      {/* AUTHENTICATION CARDS SECTION */}
      <section className="student-auth-section">
        <div className="student-auth-container">
          {/* LEFT CARD: PARENT LOGIN */}
          <div className="student-card student-login-card" id="parent-login">
            <div className="student-card-header">
              <div className="student-avatar-badge">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
              </div>
              <div>
                <h2 className="student-card-title">Parent Sign In</h2>
                <p className="student-card-subtitle">Access your connected children's portal</p>
              </div>
            </div>

            {loginError && <div className="student-alert student-alert-error">{loginError}</div>}

            <form onSubmit={handleLogin} className="student-form">
              <div className="student-field-group">
                <label className="student-label">Email Address</label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                  <input
                    type="email"
                    required
                    className="student-input"
                    placeholder="parent@example.com"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                  />
                </div>
              </div>

              <div className="student-field-group">
                <label className="student-label">Password</label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                  <input
                    type={showLoginPassword ? 'text' : 'password'}
                    required
                    className="student-input"
                    placeholder="Enter your password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    className="student-eye-toggle"
                    onClick={() => setShowLoginPassword(!showLoginPassword)}
                    aria-label="Toggle password visibility"
                  >
                    {showLoginPassword ? (
                      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" /><line x1="1" y1="1" x2="23" y2="23" /></svg>
                    ) : (
                      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>
                    )}
                  </button>
                </div>
              </div>

              <div className="student-auth-options">
                <label className="student-checkbox-label">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span>Remember me</span>
                </label>
                <Link to="/portal" className="student-forgot-link">Forgot password?</Link>
              </div>

              <button
                type="submit"
                className="student-btn student-btn-green"
                disabled={loginLoading}
              >
                {loginLoading ? 'Signing in…' : 'Sign in to Portal'}
              </button>

              <div className="student-trust-badge">
                <svg className="student-trust-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
                <span>256-Bit SSL Encrypted. Official Riverside Academy parent portal access.</span>
              </div>
            </form>
          </div>

          {/* RIGHT CARD: PARENT REGISTRATION */}
          <div className="student-card student-register-card" id="parent-register">
            <div className="student-card-header">
              <div className="student-avatar-badge" style={{ backgroundColor: '#fbf4e6', color: 'var(--bfa-gold-accent)' }}>
                <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                  <path d="M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm-9-2V7H4v3H1v2h3v3h2v-3h3v-2H6zm9 4c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
              </div>
              <div>
                <h2 className="student-card-title">Create Parent Account</h2>
                <p className="student-card-subtitle">Connect with your child's school record</p>
              </div>
            </div>

            {regError && <div className="student-alert student-alert-error">{regError}</div>}

            <form onSubmit={handleRegister} className="student-form">
              <div className="student-form-row">
                <div className="student-field-group">
                  <label className="student-label">First Name</label>
                  <div className="student-input-wrap">
                    <input
                      type="text"
                      required
                      className="student-input"
                      style={{ paddingLeft: 14 }}
                      placeholder="e.g. Sarah"
                      value={regForm.firstName}
                      onChange={(e) => updateReg('firstName', e.target.value)}
                    />
                  </div>
                </div>

                <div className="student-field-group">
                  <label className="student-label">Last Name</label>
                  <div className="student-input-wrap">
                    <input
                      type="text"
                      required
                      className="student-input"
                      style={{ paddingLeft: 14 }}
                      placeholder="e.g. Jenkins"
                      value={regForm.lastName}
                      onChange={(e) => updateReg('lastName', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="student-field-group">
                <label className="student-label">Email Address</label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                  <input
                    type="email"
                    required
                    className="student-input"
                    placeholder="parent@example.com"
                    value={regForm.email}
                    onChange={(e) => updateReg('email', e.target.value)}
                  />
                </div>
              </div>

              <div className="student-field-group">
                <label className="student-label">Phone Number</label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                  </svg>
                  <input
                    type="tel"
                    className="student-input"
                    placeholder="+1 (555) 000-0000"
                    value={regForm.phone}
                    onChange={(e) => updateReg('phone', e.target.value)}
                  />
                </div>
              </div>

              <div className="student-field-group">
                <label className="student-label">
                  Password <span className="student-sub-hint">(min. 10 characters)</span>
                </label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                  <input
                    type={showRegPassword ? 'text' : 'password'}
                    required
                    minLength={10}
                    className="student-input"
                    placeholder="Create a strong password"
                    value={regForm.password}
                    onChange={(e) => updateReg('password', e.target.value)}
                  />
                  <button
                    type="button"
                    className="student-eye-toggle"
                    onClick={() => setShowRegPassword(!showRegPassword)}
                    aria-label="Toggle password visibility"
                  >
                    {showRegPassword ? (
                      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" /><line x1="1" y1="1" x2="23" y2="23" /></svg>
                    ) : (
                      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>
                    )}
                  </button>
                </div>
                {regForm.password && (
                  <div className="student-strength-bar-wrap">
                    <div
                      className="student-strength-bar"
                      style={{
                        width: passwordStrength.score === 1 ? '33%' : passwordStrength.score === 2 ? '66%' : '100%',
                        backgroundColor: passwordStrength.color,
                      }}
                    />
                    <span className="student-strength-label" style={{ color: passwordStrength.color }}>
                      Password Strength: {passwordStrength.label}
                    </span>
                  </div>
                )}
              </div>

              <div className="student-field-group">
                <label className="student-label">Confirm Password</label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    className="student-input"
                    placeholder="Repeat your password"
                    value={regForm.confirmPassword}
                    onChange={(e) => updateReg('confirmPassword', e.target.value)}
                  />
                  <button
                    type="button"
                    className="student-eye-toggle"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    aria-label="Toggle confirm password visibility"
                  >
                    {showConfirmPassword ? (
                      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" /><line x1="1" y1="1" x2="23" y2="23" /></svg>
                    ) : (
                      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>
                    )}
                  </button>
                </div>
                {passwordsMatch && (
                  <span className="student-match-badge match">✓ Passwords match</span>
                )}
                {passwordsMismatch && (
                  <span className="student-match-badge mismatch">✗ Passwords do not match</span>
                )}
              </div>

              <div className="student-checkbox-group">
                <label className="student-checkbox-label">
                  <input
                    type="checkbox"
                    required
                    checked={regForm.agreeTerms}
                    onChange={(e) => updateReg('agreeTerms', e.target.checked)}
                  />
                  <span>
                    I agree to the <Link to="/terms">Terms & Conditions</Link> and{' '}
                    <Link to="/privacy">Privacy Policy</Link> for Riverside Academy Parent Portal.
                  </span>
                </label>
              </div>

              <button
                type="submit"
                className="student-btn student-btn-gold"
                disabled={regLoading}
              >
                {regLoading ? 'Creating account…' : 'Create Account & Continue'}
              </button>
            </form>
          </div>
        </div>
      </section>
    </div>
  )
}

const EMPTY_REQUEST = { student_admission_number: '', child_full_name: '', relationship: '', phone: '', email: '', message: '' }

export default function ParentRegister() {
  const [signedIn, setSignedIn] = useState(publicApi.isAuthenticated())
  const [requests, setRequests] = useState(null)
  const [form, setForm] = useState(EMPTY_REQUEST)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => { document.title = 'Parent/Guardian Registration — Riverside Academy' }, [])

  const load = () => publicApi.myParentRelationshipRequests().then((data) => setRequests(data.results || data || [])).catch(() => setRequests([]))
  useEffect(() => { if (signedIn) load() }, [signedIn])

  const update = (field, value) => setForm({ ...form, [field]: value })

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      await publicApi.createParentRelationshipRequest(form)
      setForm(EMPTY_REQUEST)
      load()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (!signedIn) {
    return <ApplicantAuthInline onSignedIn={() => setSignedIn(true)} />
  }

  return (
    <>
      <PageHero
        crumb="Register as Parent/Guardian"
        title="Connect with your child's record"
        detail="Identify the student you're the parent or guardian of. An administrator verifies this before any portal access is granted — it's never automatic."
      />
      <section className="bfa-section">
        <div className="bfa-container">
          <div className="bfa-grid bfa-grid-2">
            <form className="bfa-form" onSubmit={submit}>
              <ErrorBanner message={error} />
              <label className="bfa-field">Student's admission number
                <input required placeholder="e.g. BFA-0001" value={form.student_admission_number} onChange={(e) => update('student_admission_number', e.target.value)} />
                </label>
                <label className="bfa-field">Student's full name
                  <input required value={form.child_full_name} onChange={(e) => update('child_full_name', e.target.value)} />
                </label>
                <label className="bfa-field">Your relationship to the student
                  <input required value={form.relationship} onChange={(e) => update('relationship', e.target.value)} placeholder="e.g. Mother, Father, Guardian" />
                </label>
                <div className="bfa-form-row">
                  <label className="bfa-field">Phone<input required value={form.phone} onChange={(e) => update('phone', e.target.value)} /></label>
                  <label className="bfa-field">Email<input required type="email" value={form.email} onChange={(e) => update('email', e.target.value)} /></label>
                </div>
                <label className="bfa-field">Anything else we should know? (optional)
                  <textarea value={form.message} onChange={(e) => update('message', e.target.value)} />
                </label>
                <button className="bfa-btn bfa-btn-gold" disabled={saving}>{saving ? 'Submitting…' : 'Submit for verification'}</button>
              </form>

              <div>
                <h3 style={{ color: 'var(--bfa-navy)', marginTop: 0 }}>Your requests</h3>
                {requests === null ? (
                  <Loading />
                ) : requests.length === 0 ? (
                  <p style={{ color: 'var(--bfa-muted)' }}>You haven't submitted a relationship request yet.</p>
                ) : (
                  requests.map((req) => (
                    <div className="bfa-list-row" key={req.id}>
                      <div>
                        <h4>{req.child_full_name} · {req.reference}</h4>
                        <p>{req.relationship} · submitted {formatDate(req.created_at)}</p>
                      </div>
                      <span className="bfa-status-pill">{req.status}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
        </div>
      </section>
    </>
  )
}
