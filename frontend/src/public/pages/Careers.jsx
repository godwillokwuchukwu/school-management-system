import { useEffect, useState } from 'react'
import { publicApi } from '../api'
import { Empty, ErrorBanner, Loading, PageHero, SuccessBanner } from '../ui'
import { formatDate } from '../formatters'

const EMPLOYMENT_TYPE_LABEL = { full_time: 'Full Time', part_time: 'Part Time', contract: 'Contract' }

function ApplyForm({ job, onClose }) {
  const [form, setForm] = useState({ full_name: '', email: '', phone: '', qualifications: '', years_of_experience: '', cover_letter: '' })
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')
  const [reference, setReference] = useState('')
  const [saving, setSaving] = useState(false)

  const update = (field, value) => setForm({ ...form, [field]: value })

  const submit = async (event) => {
    event.preventDefault()
    if (!file) { setError('Please attach your resume (PDF or Word document).'); return }
    setError('')
    setSaving(true)
    try {
      const body = new FormData()
      body.append('job_slug', job.slug)
      Object.entries(form).forEach(([key, value]) => body.append(key, value))
      body.append('resume', file)
      const data = await publicApi.applyForJob(body)
      setReference(data.reference)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (reference) {
    return (
      <div className="bfa-card" style={{ marginTop: 16 }}>
        <SuccessBanner message={`Application received! Your reference is ${reference}. Our HR team will follow up by email.`} />
        <button className="bfa-btn bfa-btn-navy" style={{ marginTop: 14 }} onClick={onClose}>Close</button>
      </div>
    )
  }

  return (
    <form className="bfa-form" onSubmit={submit} style={{ marginTop: 16, maxWidth: 100 + '%' }}>
      <ErrorBanner message={error} />
      <div className="bfa-form-row">
        <label className="bfa-field">Full name<input required value={form.full_name} onChange={(e) => update('full_name', e.target.value)} /></label>
        <label className="bfa-field">Email<input required type="email" value={form.email} onChange={(e) => update('email', e.target.value)} /></label>
      </div>
      <div className="bfa-form-row">
        <label className="bfa-field">Phone<input value={form.phone} onChange={(e) => update('phone', e.target.value)} /></label>
        <label className="bfa-field">Years of experience<input type="number" min="0" value={form.years_of_experience} onChange={(e) => update('years_of_experience', e.target.value)} /></label>
      </div>
      <label className="bfa-field">Qualifications<textarea value={form.qualifications} onChange={(e) => update('qualifications', e.target.value)} /></label>
      <label className="bfa-field">Cover letter<textarea value={form.cover_letter} onChange={(e) => update('cover_letter', e.target.value)} /></label>
      <label className="bfa-field">Resume (PDF or Word, max 10MB)
        <input required type="file" accept=".pdf,.doc,.docx" onChange={(e) => setFile(e.target.files[0])} />
      </label>
      <div style={{ display: 'flex', gap: 10 }}>
        <button className="bfa-btn bfa-btn-gold" disabled={saving}>{saving ? 'Submitting…' : 'Submit application'}</button>
        <button type="button" className="bfa-btn bfa-btn-outline" style={{ color: 'var(--bfa-navy)', borderColor: 'var(--bfa-border)' }} onClick={onClose}>Cancel</button>
      </div>
    </form>
  )
}

export default function Careers() {
  const [jobs, setJobs] = useState(null)
  const [applyingTo, setApplyingTo] = useState(null)

  useEffect(() => {
    document.title = 'Careers — Riverside Academy'
    publicApi.jobs().then((data) => setJobs(data.results || data || [])).catch(() => setJobs([]))
  }, [])

  return (
    <>
      <PageHero crumb="Careers" title="Join our team" detail="We're always looking for passionate educators and staff who share our mission." />
      <section className="bfa-section">
        <div className="bfa-container" style={{ maxWidth: 820 }}>
          {jobs === null ? (
            <Loading />
          ) : jobs.length === 0 ? (
            <Empty label="No open positions right now — check back soon." />
          ) : (
            jobs.map((job) => (
              <div className="bfa-card" key={job.slug} style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                  <div>
                    <h3>{job.title}</h3>
                    <p>{job.department} · {EMPLOYMENT_TYPE_LABEL[job.employment_type] || job.employment_type} · {job.location}</p>
                  </div>
                  {applyingTo?.slug !== job.slug && (
                    <button className="bfa-btn bfa-btn-navy" onClick={() => setApplyingTo(job)}>Apply →</button>
                  )}
                </div>
                <p style={{ marginTop: 12 }}>{job.description}</p>
                {job.requirements && <p style={{ marginTop: 8 }}><strong>Requirements:</strong> {job.requirements}</p>}
                {job.application_deadline && <p style={{ marginTop: 8, fontSize: 12.5 }}>Apply by {formatDate(job.application_deadline)}</p>}
                {applyingTo?.slug === job.slug && <ApplyForm job={job} onClose={() => setApplyingTo(null)} />}
              </div>
            ))
          )}
        </div>
      </section>
    </>
  )
}
