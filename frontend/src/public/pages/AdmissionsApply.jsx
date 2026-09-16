import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { publicApi } from '../api'
import { ErrorBanner, Loading, PageHero, SuccessBanner } from '../ui'
import { formatDate } from '../formatters'
import SchoolCrest from '../components/SchoolCrest'
import '../../auth/StudentAuth.css'

const EMPTY_APPLICATION = {
  student_first_name: '', student_middle_name: '', student_last_name: '', student_dob: '',
  student_gender: '', student_nationality: '', student_phone: '', student_email: '', student_address: '',
  previous_school: '', previous_class: '', class_applying_for: '', academic_session: '2026/2027',
  guardian_full_name: '', guardian_relationship: '', guardian_phone: '', guardian_email: '', guardian_address: '',
}

const DOCUMENT_TYPES = [
  ['birth_certificate', 'Birth Certificate'],
  ['previous_report', 'Previous School Report'],
  ['passport_photo', 'Passport Photograph'],
  ['identification', 'Identification Document'],
  ['medical', 'Medical Document'],
  ['other', 'Other Supporting Document'],
]

function ApplicantAuth({ onSignedIn }) {
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

  // Password Strength Calculation (matches StudentAuth)
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
    <div className="student-portal-wrapper">
      {/* HERO SECTION */}
      <section className="student-portal-hero">
        <div className="student-hero-content">
          <div className="student-hero-text">
            <span className="student-hero-eyebrow">RIVERSIDE ACADEMY • ADMISSIONS</span>
            <h1 className="student-hero-title">Admissions Portal</h1>
            <p className="student-hero-desc">
              Begin your journey at Riverside Academy. Log in to manage your active application, or create an account to start an online enrollment application for your child.
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
          {/* LEFT CARD: APPLICANT LOGIN */}
          <div className="student-card student-login-card" id="applicant-login">
            <div className="student-card-header">
              <div className="student-avatar-badge">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
              </div>
              <div>
                <h2 className="student-card-title">Applicant Sign In</h2>
                <p className="student-card-subtitle">Access your admission application</p>
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
                {loginLoading ? 'Signing in…' : 'Sign in to Application'}
              </button>

              <div className="student-trust-badge">
                <svg className="student-trust-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
                <span>256-Bit SSL Encrypted. Your admissions information is securely transmitted and protected.</span>
              </div>
            </form>
          </div>

          {/* RIGHT CARD: APPLICANT REGISTRATION */}
          <div className="student-card student-register-card" id="applicant-register">
            <div className="student-card-header">
              <div className="student-avatar-badge" style={{ backgroundColor: '#fbf4e6', color: 'var(--bfa-gold-accent)' }}>
                <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                  <path d="M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm-9-2V7H4v3H1v2h3v3h2v-3h3v-2H6zm9 4c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
              </div>
              <div>
                <h2 className="student-card-title">Create Applicant Account</h2>
                <p className="student-card-subtitle">Start your online enrollment application</p>
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
                    <Link to="/privacy">Privacy Policy</Link> for Riverside Academy Admissions.
                  </span>
                </label>
              </div>

              <button
                type="submit"
                className="student-btn student-btn-gold"
                disabled={regLoading}
              >
                {regLoading ? 'Creating account…' : 'Create Account & Begin Application'}
              </button>
            </form>
          </div>
        </div>
      </section>
    </div>
  )
}

function ApplicationForm({ application, onSaved }) {
  const [form, setForm] = useState({ ...EMPTY_APPLICATION, ...application })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const update = (field, value) => setForm({ ...form, [field]: value })

  const save = async (event) => {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      const payload = { ...form }
      delete payload.id; delete payload.reference; delete payload.status; delete payload.submitted_at; delete payload.created_at
      const saved = application.id
        ? await publicApi.updateApplication(application.id, payload)
        : await publicApi.createApplication(payload)
      onSaved(saved)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="bfa-card" style={{ maxWidth: 840, margin: '0 auto' }}>
      <form className="bfa-form" onSubmit={save} style={{ maxWidth: '100%' }}>
        <ErrorBanner message={error} />
        <h3 style={{ margin: '0 0 4px', color: 'var(--bfa-navy)', fontSize: 22 }}>Student Information</h3>
        <p style={{ color: 'var(--bfa-muted)', fontSize: 13, margin: '0 0 16px' }}>
          Personal and background details for the applicant child.
        </p>

        <div className="bfa-form-row">
          <label className="bfa-field">FIRST NAME<input required value={form.student_first_name} onChange={(e) => update('student_first_name', e.target.value)} /></label>
          <label className="bfa-field">LAST NAME<input required value={form.student_last_name} onChange={(e) => update('student_last_name', e.target.value)} /></label>
        </div>
        <div className="bfa-form-row">
          <label className="bfa-field">MIDDLE NAME<input value={form.student_middle_name} onChange={(e) => update('student_middle_name', e.target.value)} /></label>
          <label className="bfa-field">DATE OF BIRTH<input required type="date" value={form.student_dob} onChange={(e) => update('student_dob', e.target.value)} /></label>
        </div>
        <div className="bfa-form-row">
          <label className="bfa-field">GENDER
            <select value={form.student_gender} onChange={(e) => update('student_gender', e.target.value)}>
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </label>
          <label className="bfa-field">NATIONALITY<input value={form.student_nationality} placeholder="e.g. Nigerian" onChange={(e) => update('student_nationality', e.target.value)} /></label>
        </div>
        <div className="bfa-form-row">
          <label className="bfa-field">CLASS APPLYING FOR
            <select required value={form.class_applying_for} onChange={(e) => update('class_applying_for', e.target.value)}>
              <option value="">Select Class</option>
              <option value="Creche">Creche</option>
              <option value="Nursery 1">Nursery 1</option>
              <option value="Nursery 2">Nursery 2</option>
              <option value="Primary 1">Primary 1</option>
              <option value="Primary 2">Primary 2</option>
              <option value="Primary 3">Primary 3</option>
              <option value="Primary 4">Primary 4</option>
              <option value="Primary 5">Primary 5</option>
              <option value="JSS 1">JSS 1</option>
              <option value="JSS 2">JSS 2</option>
              <option value="JSS 3">JSS 3</option>
              <option value="SSS 1">SSS 1</option>
              <option value="SSS 2">SSS 2</option>
              <option value="SSS 3">SSS 3</option>
            </select>
          </label>
          <label className="bfa-field">ACADEMIC SESSION<input required value={form.academic_session} onChange={(e) => update('academic_session', e.target.value)} /></label>
        </div>
        <div className="bfa-form-row">
          <label className="bfa-field">PREVIOUS SCHOOL<input value={form.previous_school} placeholder="School name" onChange={(e) => update('previous_school', e.target.value)} /></label>
          <label className="bfa-field">PREVIOUS CLASS<input value={form.previous_class} placeholder="e.g. Primary 4" onChange={(e) => update('previous_class', e.target.value)} /></label>
        </div>
        <label className="bfa-field">RESIDENTIAL ADDRESS<input value={form.student_address} placeholder="Street address, City, State" onChange={(e) => update('student_address', e.target.value)} /></label>

        <p className="bfa-form-section-title">Parent / Guardian Information</p>
        <div className="bfa-form-row">
          <label className="bfa-field">FULL NAME<input required value={form.guardian_full_name} onChange={(e) => update('guardian_full_name', e.target.value)} /></label>
          <label className="bfa-field">RELATIONSHIP<input required placeholder="Father, Mother, Legal Guardian" value={form.guardian_relationship} onChange={(e) => update('guardian_relationship', e.target.value)} /></label>
        </div>
        <div className="bfa-form-row">
          <label className="bfa-field">PHONE NUMBER<input required value={form.guardian_phone} onChange={(e) => update('guardian_phone', e.target.value)} /></label>
          <label className="bfa-field">EMAIL ADDRESS<input required type="email" value={form.guardian_email} onChange={(e) => update('guardian_email', e.target.value)} /></label>
        </div>
        <label className="bfa-field">GUARDIAN RESIDENTIAL ADDRESS<input value={form.guardian_address} onChange={(e) => update('guardian_address', e.target.value)} /></label>

        <div style={{ display: 'flex', gap: 14, marginTop: 16 }}>
          <button className="bfa-btn bfa-btn-navy" disabled={saving}>
            {saving ? 'Saving…' : 'Save Application Draft'}
          </button>
        </div>
      </form>
    </div>
  )
}

function DocumentUploader({ application, onUploaded }) {
  const [docType, setDocType] = useState(DOCUMENT_TYPES[0][0])
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const upload = async (event) => {
    event.preventDefault()
    if (!file) { setError('Choose a file first.'); return }
    setError('')
    setSaving(true)
    try {
      const body = new FormData()
      body.append('document_type', docType)
      body.append('file', file)
      const doc = await publicApi.uploadApplicationDocument(application.id, body)
      onUploaded(doc)
      setFile(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={upload} style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap', marginTop: 14 }}>
      <ErrorBanner message={error} />
      <label className="bfa-field" style={{ minWidth: 220 }}>DOCUMENT TYPE
        <select value={docType} onChange={(e) => setDocType(e.target.value)}>
          {DOCUMENT_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </label>
      <label className="bfa-field">FILE
        <input type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onChange={(e) => setFile(e.target.files[0])} />
      </label>
      <button className="bfa-btn bfa-btn-outline" disabled={saving}>{saving ? 'Uploading…' : 'Upload File'}</button>
    </form>
  )
}

function ApplicationDetail({ application, onBack, onUpdated }) {
  const [current, setCurrent] = useState(application)
  const [documents, setDocuments] = useState(Array.isArray(application?.documents) ? application.documents : [])
  const [submitMessage, setSubmitMessage] = useState('')
  const [submitError, setSubmitError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const editable = current?.status === 'started'

  useEffect(() => {
    if (!current?.id) return
    publicApi.applicationDocuments(current.id)
      .then((data) => setDocuments(Array.isArray(data) ? data : data?.results || []))
      .catch(() => {})
  }, [current?.id])

  const submit = async () => {
    if (!window.confirm('Are you sure you are ready to submit? Once submitted, your application cannot be edited.')) return
    setSubmitError('')
    setSubmitMessage('')
    setSubmitting(true)
    try {
      const res = await publicApi.submitApplication(current.id)
      setSubmitMessage(`Application submitted successfully! Your application reference number is ${res.reference}.`)
      const refreshed = await publicApi.application(current.id)
      setCurrent(refreshed)
      onUpdated(refreshed)
    } catch (err) {
      setSubmitError(err.message || 'Failed to submit application. Please verify all required fields and documents.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 840, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <button className="bfa-btn bfa-btn-outline" onClick={onBack}>← Back to My Applications</button>
        <span className="bfa-badge bfa-badge-gold" style={{ fontSize: 13, textTransform: 'capitalize' }}>
          Status: {current.status ? current.status.replace(/_/g, ' ') : 'Draft'}
        </span>
      </div>

      <SuccessBanner message={submitMessage} />
      <ErrorBanner message={submitError} />

      {editable ? (
        <ApplicationForm
          application={current}
          onSaved={(saved) => {
            setCurrent(saved)
            onUpdated(saved)
          }}
        />
      ) : (
        <div className="bfa-card" style={{ marginBottom: 24 }}>
          <h3 style={{ color: 'var(--bfa-navy)', fontSize: 20 }}>
            {current.student_first_name} {current.student_last_name}
            {current.reference ? ` · Ref: ${current.reference}` : ''}
          </h3>
          <p style={{ color: 'var(--bfa-muted)', fontSize: 14 }}>
            Applying for <strong>{current.class_applying_for}</strong> ({current.academic_session})
          </p>
          <div className="bfa-form-row" style={{ marginTop: 16 }}>
            <div><strong style={{ color: 'var(--bfa-navy)' }}>Guardian:</strong> {current.guardian_full_name}</div>
            <div><strong style={{ color: 'var(--bfa-navy)' }}>Contact:</strong> {current.guardian_phone} | {current.guardian_email}</div>
          </div>
        </div>
      )}

      {current.id && (
        <div className="bfa-card" style={{ marginTop: 24 }}>
          <h3 style={{ color: 'var(--bfa-navy)', fontSize: 20, marginBottom: 8 }}>Supporting Documents</h3>
          <p style={{ color: 'var(--bfa-muted)', fontSize: 13, marginBottom: 16 }}>
            Upload birth certificates, passport photographs, and previous academic transcripts.
          </p>
          {documents.length === 0 ? (
            <p style={{ color: 'var(--bfa-muted)', fontStyle: 'italic' }}>No documents uploaded yet.</p>
          ) : (
            documents.map((doc) => (
              <div className="bfa-list-row" key={doc.id}>
                <div>
                  <h4>{doc.document_type ? doc.document_type.replace(/_/g, ' ').toUpperCase() : 'DOCUMENT'}</h4>
                  <p>{formatDate(doc.uploaded_at)}</p>
                </div>
                {doc.verified ? (
                  <span className="bfa-badge" style={{ background: '#dcfce7', color: '#15803d' }}>Verified</span>
                ) : (
                  <span className="bfa-badge">Pending Review</span>
                )}
              </div>
            ))
          )}

          {editable && (
            <DocumentUploader
              application={current}
              onUploaded={(doc) => setDocuments((prev) => [...prev, doc])}
            />
          )}

          {editable && (
            <div style={{ marginTop: 28, paddingTop: 20, borderTop: '1px solid var(--bfa-border)' }}>
              <button
                className="bfa-btn bfa-btn-gold"
                style={{ width: '100%', justifyContent: 'center', fontSize: 15, padding: '14px 24px' }}
                onClick={submit}
                disabled={submitting}
              >
                {submitting ? 'Submitting Application…' : 'Submit Final Application →'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function AdmissionsApply() {
  const [signedIn, setSignedIn] = useState(publicApi.isAuthenticated())
  const [applications, setApplications] = useState(null)
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => { document.title = 'Apply — Riverside Academy Admissions' }, [])

  const loadApplications = () => {
    publicApi
      .myApplications()
      .then((data) => setApplications(data.results || data || []))
      .catch((err) => {
        if (err.status === 401 || !publicApi.isAuthenticated()) {
          setSignedIn(false)
        } else {
          setError(err.message)
        }
      })
  }

  useEffect(() => { if (signedIn) loadApplications() }, [signedIn])

  if (!signedIn) {
    return <ApplicantAuth onSignedIn={() => setSignedIn(true)} />
  }

  if (selected) {
    return (
      <>
        <PageHero crumb="Admissions · Apply" title="Admission Application" detail="Manage your application details and uploaded documents." />
        <section className="bfa-section">
          <div className="bfa-container">
            <ApplicationDetail
              application={selected}
              onBack={() => { setSelected(null); loadApplications() }}
              onUpdated={(updated) => setSelected(updated)}
            />
          </div>
        </section>
      </>
    )
  }

  return (
    <>
      <PageHero crumb="Admissions · Apply" title="My Applications" detail="Start a new admission application, or continue one you have already started." />
      <section className="bfa-section">
        <div className="bfa-container" style={{ maxWidth: 840 }}>
          <ErrorBanner message={error} />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
            <button
              className="bfa-btn bfa-btn-gold"
              onClick={() => setSelected({ ...EMPTY_APPLICATION, status: 'started', documents: [] })}
            >
              + Start a New Application
            </button>
            <button
              className="bfa-btn bfa-btn-outline"
              onClick={() => {
                publicApi.logout()
                setSignedIn(false)
              }}
            >
              Sign Out
            </button>
          </div>
          {applications === null ? (
            <Loading />
          ) : applications.length === 0 ? (
            <div className="bfa-card" style={{ textAlign: 'center', padding: '48px 24px' }}>
              <h3 style={{ color: 'var(--bfa-navy)', fontSize: 20 }}>No Active Applications</h3>
              <p style={{ color: 'var(--bfa-muted)', margin: '8px 0 20px' }}>
                You have not started an application yet. Click below to begin your child's enrollment application.
              </p>
              <button
                className="bfa-btn bfa-btn-gold"
                onClick={() => setSelected({ ...EMPTY_APPLICATION, status: 'started', documents: [] })}
              >
                + Start an Application
              </button>
            </div>
          ) : (
            (Array.isArray(applications) ? applications : []).map((app) => (
              <div
                className="bfa-card"
                key={app.id}
                style={{ cursor: 'pointer', marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                onClick={() => publicApi.application(app.id).then(setSelected)}
              >
                <div>
                  <h4 style={{ margin: '0 0 4px', fontSize: 18, color: 'var(--bfa-navy)', fontFamily: "'Playfair Display', Georgia, serif" }}>
                    {app.student_first_name} {app.student_last_name}{app.reference ? ` · Ref: ${app.reference}` : ''}
                  </h4>
                  <p style={{ margin: 0, color: 'var(--bfa-muted)', fontSize: 14 }}>
                    Class: <strong>{app.class_applying_for}</strong> | Session: <strong>{app.academic_session}</strong>
                  </p>
                </div>
                <span className="bfa-badge bfa-badge-gold" style={{ textTransform: 'capitalize', fontSize: 12 }}>
                  {app.status ? app.status.replace(/_/g, ' ') : 'Draft'}
                </span>
              </div>
            ))
          )}
        </div>
      </section>
    </>
  )
}
