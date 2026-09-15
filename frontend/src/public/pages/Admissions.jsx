import { useState } from 'react'
import { Link } from 'react-router-dom'
import { publicApi } from '../api'
import { ErrorBanner, PageHero, SuccessBanner } from '../ui'

const STEPS = [
  ['1', 'Submit an enquiry or start an application', 'Tell us about your child, or create an applicant account to begin the full application.'],
  ['2', 'Upload documents', 'Birth certificate, previous report, photo, and any required identification.'],
  ['3', 'Application review', 'Our admissions team reviews your application and may schedule an assessment or interview.'],
  ['4', 'Admission decision', "You'll receive a decision — approved, waitlisted, or an admission offer."],
  ['5', 'Enroll', 'Accept your offer, complete enrollment payment, and your child is ready to join Riverside Academy.'],
]

const EMPTY_ENQUIRY = { student_name: '', student_dob: '', class_applying_for: '', academic_session: '2026/2027', parent_name: '', parent_email: '', parent_phone: '', message: '' }

export default function Admissions() {
  const [form, setForm] = useState(EMPTY_ENQUIRY)
  const [error, setError] = useState('')
  const [reference, setReference] = useState('')
  const [saving, setSaving] = useState(false)

  const update = (field, value) => setForm({ ...form, [field]: value })

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      const data = await publicApi.submitAdmissionEnquiry(form)
      setReference(data.reference)
      setForm(EMPTY_ENQUIRY)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHero crumb="Admissions" title="Admissions are open" detail="Start with a quick enquiry, or go straight to the full application." />

      <section className="bfa-section bfa-section-alt">
        <div className="bfa-container">
          <div className="bfa-section-head"><h2>How admissions works</h2></div>
          <div className="bfa-grid bfa-grid-3">
            {STEPS.map(([n, title, detail]) => (
              <div className="bfa-card" key={n}>
                <span className="bfa-tag">STEP {n}</span>
                <h3>{title}</h3>
                <p>{detail}</p>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', marginTop: 36, flexWrap: 'wrap' }}>
            <Link to="/admissions/apply" className="bfa-btn bfa-btn-outline">Start full application →</Link>
            <Link to="/admissions/status" className="bfa-btn bfa-btn-outline">Track my application</Link>
            <Link to="/register/parent" className="bfa-btn bfa-btn-outline">Register as parent/guardian</Link>
          </div>
        </div>
      </section>

      <section className="bfa-section">
        <div className="bfa-container bfa-grid bfa-grid-2">
          <div>
            <h2 style={{ color: 'var(--bfa-navy)' }}>Not ready to apply yet?</h2>
            <p style={{ color: 'var(--bfa-muted)', lineHeight: 1.7 }}>
              Send us a quick enquiry and our admissions team will reach out with more information about
              Riverside Academy before you commit to a full application.
            </p>
          </div>
          <div className="bfa-card">
            {reference ? (
              <SuccessBanner message={`Enquiry received! Your reference is ${reference}. Track it any time from the Admissions status page.`} />
            ) : (
              <form className="bfa-form" onSubmit={submit}>
                <ErrorBanner message={error} />
                <label className="bfa-field">Student's name
                  <input required value={form.student_name} onChange={(e) => update('student_name', e.target.value)} />
                </label>
                <div className="bfa-form-row">
                  <label className="bfa-field">Date of birth
                    <input type="date" value={form.student_dob} onChange={(e) => update('student_dob', e.target.value)} />
                  </label>
                  <label className="bfa-field">Class applying for
                    <input required value={form.class_applying_for} onChange={(e) => update('class_applying_for', e.target.value)} />
                  </label>
                </div>
                <label className="bfa-field">Parent/Guardian name
                  <input required value={form.parent_name} onChange={(e) => update('parent_name', e.target.value)} />
                </label>
                <div className="bfa-form-row">
                  <label className="bfa-field">Email
                    <input required type="email" value={form.parent_email} onChange={(e) => update('parent_email', e.target.value)} />
                  </label>
                  <label className="bfa-field">Phone
                    <input required value={form.parent_phone} onChange={(e) => update('parent_phone', e.target.value)} />
                  </label>
                </div>
                <label className="bfa-field">Message (optional)
                  <textarea value={form.message} onChange={(e) => update('message', e.target.value)} />
                </label>
                <button className="bfa-btn bfa-btn-gold bfa-btn-block" disabled={saving}>{saving ? 'Sending…' : 'Send enquiry'}</button>
              </form>
            )}
          </div>
        </div>
      </section>
    </>
  )
}
