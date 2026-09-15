import { useEffect, useState } from 'react'
import { publicApi } from '../api'
import { ErrorBanner, PageHero, SuccessBanner } from '../ui'

const EMPTY = { name: '', email: '', phone: '', topic: 'general', subject: '', message: '' }

export default function Contact() {
  const [school, setSchool] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    document.title = 'Contact & Campus Location — Riverside Academy'
    publicApi.school().then(setSchool).catch(() => setSchool(null))
  }, [])

  const update = (field, value) => setForm({ ...form, [field]: value })

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')
    setSaving(true)
    try {
      const data = await publicApi.submitContact(form)
      setSuccess(data.message || "Thanks for reaching out — we'll be in touch shortly.")
      setForm(EMPTY)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const address = school?.address || '123 Academy Road, Lagos, Nigeria'
  const phone = school?.phone || '+1 555 014 2026'
  const email = school?.email || 'hello@riversideacademy.edu'
  const officeHours = school?.office_hours || 'Monday – Friday, 8:00am – 4:00pm'
  const emergencyPhone = school?.emergency_phone

  // Fallback map embed centered on school location
  const mapUrl = school?.map_embed_url || `https://maps.google.com/maps?q=${encodeURIComponent(address)}&t=&z=15&ie=UTF8&iwloc=&output=embed`

  return (
    <>
      <PageHero crumb="Contact" title="Get in touch" detail="Questions about admissions, academics, or anything else — we're happy to help." />
      <section className="bfa-section">
        <div className="bfa-container bfa-grid bfa-grid-2">
          <form className="bfa-form" onSubmit={submit}>
            <ErrorBanner message={error} />
            <SuccessBanner message={success} />
            <div className="bfa-form-row">
              <label className="bfa-field">Full name
                <input required value={form.name} onChange={(e) => update('name', e.target.value)} />
              </label>
              <label className="bfa-field">Email
                <input required type="email" value={form.email} onChange={(e) => update('email', e.target.value)} />
              </label>
            </div>
            <div className="bfa-form-row">
              <label className="bfa-field">Phone
                <input value={form.phone} onChange={(e) => update('phone', e.target.value)} />
              </label>
              <label className="bfa-field">Topic
                <select value={form.topic} onChange={(e) => update('topic', e.target.value)}>
                  <option value="general">General Enquiry</option>
                  <option value="admissions">Admissions</option>
                  <option value="careers">Careers</option>
                  <option value="support">Parent/Student Support</option>
                </select>
              </label>
            </div>
            <label className="bfa-field">Subject
              <input value={form.subject} onChange={(e) => update('subject', e.target.value)} />
            </label>
            <label className="bfa-field">Message
              <textarea required value={form.message} onChange={(e) => update('message', e.target.value)} />
            </label>
            <button className="bfa-btn bfa-btn-gold bfa-btn-block" disabled={saving}>{saving ? 'Sending…' : 'Send message'}</button>
          </form>
          <div>
            <div className="bfa-card" style={{ marginBottom: 20 }}>
              <h3>Visit us</h3>
              <p>{address}</p>
            </div>
            <div className="bfa-card" style={{ marginBottom: 20 }}>
              <h3>Call or email</h3>
              <p>{phone}</p>
              <p>{email}</p>
              {emergencyPhone && <p style={{ fontSize: 12, color: 'var(--bfa-muted)', marginTop: 6 }}>Emergency: {emergencyPhone}</p>}
            </div>
            <div className="bfa-card">
              <h3>Office hours</h3>
              <p>{officeHours}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Embedded Map Section */}
      <section className="bfa-section" style={{ paddingTop: 0 }}>
        <div className="bfa-container">
          <div className="bfa-section-head left" style={{ marginBottom: 16 }}>
            <p className="bfa-eyebrow" style={{ color: 'var(--bfa-navy)' }}>CAMPUS LOCATION</p>
            <h2>Visit our grounds</h2>
            <p>{address}</p>
          </div>
          <div className="bfa-map-frame">
            <iframe
              title="Riverside Academy Campus Map"
              src={mapUrl}
              className="bfa-map-embed"
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              allowFullScreen
            />
          </div>
        </div>
      </section>
    </>
  )
}

