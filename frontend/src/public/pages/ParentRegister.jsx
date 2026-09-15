import { useEffect, useState } from 'react'
import { publicApi } from '../api'
import { ErrorBanner, Loading, PageHero } from '../ui'
import { formatDate } from '../formatters'

function ApplicantAuthInline({ onSignedIn }) {
  const [mode, setMode] = useState('register')
  const [form, setForm] = useState({ email: '', password: '', first_name: '', last_name: '', phone: '' })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const update = (field, value) => setForm({ ...form, [field]: value })

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      if (mode === 'register') await publicApi.register(form)
      await publicApi.login(form.email, form.password)
      onSignedIn()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="bfa-card" style={{ maxWidth: 480 }}>
      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        <button className={mode === 'register' ? 'bfa-btn bfa-btn-navy' : 'bfa-btn bfa-btn-outline'} style={mode !== 'register' ? { color: 'var(--bfa-navy)', borderColor: 'var(--bfa-border)' } : {}} onClick={() => setMode('register')}>Create account</button>
        <button className={mode === 'login' ? 'bfa-btn bfa-btn-navy' : 'bfa-btn bfa-btn-outline'} style={mode !== 'login' ? { color: 'var(--bfa-navy)', borderColor: 'var(--bfa-border)' } : {}} onClick={() => setMode('login')}>Sign in</button>
      </div>
      <form className="bfa-form" onSubmit={submit}>
        <ErrorBanner message={error} />
        {mode === 'register' && (
          <div className="bfa-form-row">
            <label className="bfa-field">First name<input required value={form.first_name} onChange={(e) => update('first_name', e.target.value)} /></label>
            <label className="bfa-field">Last name<input required value={form.last_name} onChange={(e) => update('last_name', e.target.value)} /></label>
          </div>
        )}
        <label className="bfa-field">Email<input required type="email" value={form.email} onChange={(e) => update('email', e.target.value)} /></label>
        <label className="bfa-field">Password <span style={{ fontSize: 11, fontWeight: 400, color: 'var(--bfa-muted)' }}>(min. 10 characters)</span>
          <input required type="password" minLength={10} placeholder="At least 10 characters" value={form.password} onChange={(e) => update('password', e.target.value)} />
        </label>
        <button className="bfa-btn bfa-btn-gold bfa-btn-block" disabled={saving}>{saving ? 'Please wait…' : mode === 'register' ? 'Create account & continue' : 'Sign in'}</button>
      </form>
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

  return (
    <>
      <PageHero
        crumb="Register as Parent/Guardian"
        title="Connect with your child's record"
        detail="Identify the student you're the parent or guardian of. An administrator verifies this before any portal access is granted — it's never automatic."
      />
      <section className="bfa-section">
        <div className="bfa-container">
          {!signedIn ? (
            <ApplicantAuthInline onSignedIn={() => setSignedIn(true)} />
          ) : (
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
          )}
        </div>
      </section>
    </>
  )
}
