import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { publicApi } from '../public/api'
import './StudentAuth.css'

export default function StudentAuth() {
  const navigate = useNavigate()

  // --- Login State ---
  const [loginIdentifier, setLoginIdentifier] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [showLoginPassword, setShowLoginPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [loginLoading, setLoginLoading] = useState(false)
  const [loginError, setLoginError] = useState('')

  // --- Register State ---
  const [regForm, setRegForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dob: '',
    password: '',
    confirmPassword: '',
    studentId: '',
    agreeTerms: false,
  })
  const [showRegPassword, setShowRegPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [regLoading, setRegLoading] = useState(false)
  const [regError, setRegError] = useState('')
  const [regSuccess, setRegSuccess] = useState('')

  // --- Password Strength Calculation ---
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

  // --- Login Submit ---
  const handleLogin = async (e) => {
    e.preventDefault()
    setLoginError('')
    setLoginLoading(true)
    try {
      const data = await publicApi.login(loginIdentifier.trim(), loginPassword)
      const role = data.role
      if (role === 'student') {
        navigate('/portal')
      } else if (role === 'admin') {
        navigate('/portal')
      } else if (role === 'teacher') {
        navigate('/portal')
      } else if (role === 'parent') {
        navigate('/portal')
      } else {
        navigate('/admissions/apply')
      }
    } catch (err) {
      setLoginError(err.message || 'Unable to sign in. Please verify your email/student ID and password.')
    } finally {
      setLoginLoading(false)
    }
  }

  // --- Register Submit ---
  const handleRegister = async (e) => {
    e.preventDefault()
    setRegError('')
    setRegSuccess('')

    if (regForm.password.length < 10) {
      setRegError('Password must be at least 10 characters long.')
      return
    }
    if (regForm.password !== regForm.confirmPassword) {
      setRegError('Passwords do not match.')
      return
    }
    if (!regForm.agreeTerms) {
      setRegError('You must agree to the Terms of Service and Privacy Policy to register.')
      return
    }

    setRegLoading(true)
    try {
      await publicApi.studentRegister({
        first_name: regForm.firstName.trim(),
        last_name: regForm.lastName.trim(),
        email: regForm.email.trim(),
        phone: regForm.phone.trim(),
        dob: regForm.dob,
        password: regForm.password,
        confirm_password: regForm.confirmPassword,
        student_id: regForm.studentId.trim() || undefined,
        agree_terms: regForm.agreeTerms,
      })

      setRegSuccess(
        `Account created successfully! We sent a 24-hour verification link to ${regForm.email}. Please verify your email address to activate your account.`
      )
      setRegForm({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        dob: '',
        password: '',
        confirmPassword: '',
        studentId: '',
        agreeTerms: false,
      })
    } catch (err) {
      setRegError(err.message || 'Registration could not be completed. Please check your details.')
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
            <span className="student-hero-eyebrow">WELCOME TO RIVERSIDE ACADEMY</span>
            <h1 className="student-hero-title">Student Portal</h1>
            <p className="student-hero-desc">
              Log in to your account or create a new one to access your learning resources, results, attendance, applications, and more.
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
          {/* LEFT CARD: STUDENT LOGIN */}
          <div className="student-card student-login-card" id="student-login">
            <div className="student-card-header">
              <div className="student-avatar-badge">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
              </div>
              <div>
                <h2 className="student-card-title">Student Login</h2>
                <p className="student-card-subtitle">Welcome back! Please login to your account.</p>
              </div>
            </div>

            {loginError && <div className="student-alert student-alert-error">{loginError}</div>}

            <form onSubmit={handleLogin} className="student-form">
              <div className="student-field-group">
                <label className="student-label">Email Address or Student ID</label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                  <input
                    type="text"
                    required
                    className="student-input"
                    placeholder="Enter your email or student ID"
                    value={loginIdentifier}
                    onChange={(e) => setLoginIdentifier(e.target.value)}
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
                <Link to="/contact" className="student-forgot-link">
                  Forgot password?
                </Link>
              </div>

              <button type="submit" className="student-btn student-btn-green" disabled={loginLoading}>
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: 8 }}>
                  <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3" />
                </svg>
                {loginLoading ? 'Signing in…' : 'Log In'}
              </button>

              <div className="student-switch-link">
                Don't have an account?{' '}
                <a href="#student-register" onClick={(e) => { e.preventDefault(); document.getElementById('student-register')?.scrollIntoView({ behavior: 'smooth' }) }}>
                  Create one now
                </a>
              </div>

              {/* SECURITY TRUST BADGE */}
              <div className="student-trust-badge">
                <svg className="student-trust-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
                <span>Your information is secure and will only be used for your academic records.</span>
              </div>
            </form>
          </div>

          {/* RIGHT CARD: CREATE STUDENT ACCOUNT */}
          <div className="student-card student-register-card" id="student-register">
            <div className="student-card-header">
              <div className="student-avatar-badge">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                  <path d="M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm-9-2V7H4v3H1v2h3v3h2v-3h3v-2H6zm9 4c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
              </div>
              <div>
                <h2 className="student-card-title">Create Student Account</h2>
                <p className="student-card-subtitle">Fill in the details below to get started.</p>
              </div>
            </div>

            {regError && <div className="student-alert student-alert-error">{regError}</div>}
            {regSuccess && <div className="student-alert student-alert-success">{regSuccess}</div>}

            <form onSubmit={handleRegister} className="student-form">
              {/* Row 1: Name */}
              <div className="student-form-row">
                <div className="student-field-group">
                  <label className="student-label">First Name *</label>
                  <div className="student-input-wrap">
                    <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                    <input
                      type="text"
                      required
                      className="student-input"
                      placeholder="Enter your first name"
                      value={regForm.firstName}
                      onChange={(e) => updateReg('firstName', e.target.value)}
                    />
                  </div>
                </div>

                <div className="student-field-group">
                  <label className="student-label">Last Name *</label>
                  <div className="student-input-wrap">
                    <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                    <input
                      type="text"
                      required
                      className="student-input"
                      placeholder="Enter your last name"
                      value={regForm.lastName}
                      onChange={(e) => updateReg('lastName', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              {/* Row 2: Email */}
              <div className="student-field-group">
                <label className="student-label">Email Address *</label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                  <input
                    type="email"
                    required
                    className="student-input"
                    placeholder="Enter your email address"
                    value={regForm.email}
                    onChange={(e) => updateReg('email', e.target.value)}
                  />
                </div>
              </div>

              {/* Row 3: Phone & DOB */}
              <div className="student-form-row">
                <div className="student-field-group">
                  <label className="student-label">Phone Number *</label>
                  <div className="student-input-wrap">
                    <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                    </svg>
                    <input
                      type="tel"
                      required
                      className="student-input"
                      placeholder="Enter your phone number"
                      value={regForm.phone}
                      onChange={(e) => updateReg('phone', e.target.value)}
                    />
                  </div>
                </div>

                <div className="student-field-group">
                  <label className="student-label">Date of Birth *</label>
                  <div className="student-input-wrap">
                    <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                      <line x1="16" y1="2" x2="16" y2="6" />
                      <line x1="8" y1="2" x2="8" y2="6" />
                      <line x1="3" y1="10" x2="21" y2="10" />
                    </svg>
                    <input
                      type="date"
                      required
                      className="student-input"
                      value={regForm.dob}
                      onChange={(e) => updateReg('dob', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              {/* Row 4: Password */}
              <div className="student-field-group">
                <label className="student-label">
                  Password * <span className="student-sub-hint">(min. 10 characters with uppercase, lowercase, & number)</span>
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
                    placeholder="Create a password"
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
                        width: `${(passwordStrength.score / 3) * 100}%`,
                        backgroundColor: passwordStrength.color,
                      }}
                    />
                    <span className="student-strength-label" style={{ color: passwordStrength.color }}>
                      Password Strength: {passwordStrength.label}
                    </span>
                  </div>
                )}
              </div>

              {/* Row 5: Confirm Password */}
              <div className="student-field-group">
                <label className="student-label">Confirm Password *</label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    className="student-input"
                    placeholder="Confirm your password"
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
                {passwordsMatch && <span className="student-match-badge match">✓ Passwords match</span>}
                {passwordsMismatch && <span className="student-match-badge mismatch">✕ Passwords do not match</span>}
              </div>

              {/* Row 6: Student ID */}
              <div className="student-field-group">
                <label className="student-label">Student ID (if available)</label>
                <div className="student-input-wrap">
                  <svg className="student-input-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="2" y="3" width="20" height="14" rx="2" />
                    <line x1="2" y1="10" x2="22" y2="10" />
                    <line x1="6" y1="14" x2="10" y2="14" />
                  </svg>
                  <input
                    type="text"
                    className="student-input"
                    placeholder="Enter your student ID"
                    value={regForm.studentId}
                    onChange={(e) => updateReg('studentId', e.target.value)}
                  />
                </div>
              </div>

              {/* Terms checkbox */}
              <div className="student-checkbox-group">
                <label className="student-checkbox-label">
                  <input
                    type="checkbox"
                    required
                    checked={regForm.agreeTerms}
                    onChange={(e) => updateReg('agreeTerms', e.target.checked)}
                  />
                  <span>
                    I agree to the <Link to="/terms" target="_blank">Terms of Service</Link> and <Link to="/privacy" target="_blank">Privacy Policy</Link>.
                  </span>
                </label>
              </div>

              {/* Register Button */}
              <button type="submit" className="student-btn student-btn-gold" disabled={regLoading}>
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: 8 }}>
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <line x1="19" y1="8" x2="19" y2="14" />
                  <line x1="22" y1="11" x2="16" y2="11" />
                </svg>
                {regLoading ? 'Creating account…' : 'Register'}
              </button>

              <div className="student-switch-link">
                Already have an account?{' '}
                <a href="#student-login" onClick={(e) => { e.preventDefault(); document.getElementById('student-login')?.scrollIntoView({ behavior: 'smooth' }) }}>
                  Log in
                </a>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* PORTAL FEATURES HIGHLIGHT (Section 21) */}
      <section className="student-features-section">
        <div className="student-features-container">
          <h3 className="student-features-title">Everything You Need To Succeed</h3>
          <p className="student-features-subtitle">
            Riverside Academy's Student Portal connects you directly to all your academic tools in one unified dashboard.
          </p>
          <div className="student-features-grid">
            <div className="student-feature-box">
              <div className="student-feature-icon">📚</div>
              <h4>Learning Resources</h4>
              <p>Access subject syllabi, class schedules, reading materials, and teacher announcements anytime.</p>
            </div>
            <div className="student-feature-box">
              <div className="student-feature-icon">📊</div>
              <h4>Results & Transcripts</h4>
              <p>View verified continuous assessment marks, term examination scores, and download official report cards.</p>
            </div>
            <div className="student-feature-box">
              <div className="student-feature-icon">🗓️</div>
              <h4>Attendance Records</h4>
              <p>Monitor real-time classroom attendance records, term punctuality statistics, and excused absences.</p>
            </div>
            <div className="student-feature-box">
              <div className="student-feature-icon">💳</div>
              <h4>Fees & Invoices</h4>
              <p>Track academic term fees, check outstanding balances, and download transaction payment receipts.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

