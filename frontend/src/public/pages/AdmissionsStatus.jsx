import { useState } from 'react'
import { Link } from 'react-router-dom'
import { publicApi } from '../api'
import { ErrorBanner, PageHero } from '../ui'
import { formatDate } from '../formatters'

const STATUS_ORDER = [
  'started', 'submitted', 'documents_pending', 'payment_pending', 'payment_confirmed', 'under_review',
  'assessment_scheduled', 'interview_scheduled', 'waitlisted', 'approved', 'admission_offered',
  'enrollment_pending', 'enrolled',
]
const STATUS_LABEL = {
  started: 'Started', submitted: 'Submitted', documents_pending: 'Documents Pending',
  payment_pending: 'Payment Pending', payment_confirmed: 'Payment Confirmed', under_review: 'Under Review',
  assessment_scheduled: 'Assessment Scheduled', interview_scheduled: 'Interview Scheduled',
  info_required: 'Additional Info Required', waitlisted: 'Waitlisted', approved: 'Approved',
  admission_offered: 'Admission Offered', enrollment_pending: 'Enrollment Pending',
  enrolled: 'Enrolled', rejected: 'Not Offered',
}

export default function AdmissionsStatus() {
  const [reference, setReference] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const lookup = async (event) => {
    event.preventDefault()
    if (!reference.trim()) return
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const data = await publicApi.applicationStatus(reference.trim())
      setResult({ kind: 'application', data })
    } catch {
      try {
        const data = await publicApi.admissionEnquiryStatus(reference.trim())
        setResult({ kind: 'enquiry', data })
      } catch {
        setError('No application or enquiry found with that reference. Double-check the reference and try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const currentIndex = result ? STATUS_ORDER.indexOf(result.data.status) : -1

  return (
    <>
      <PageHero crumb="Admissions" title="Track your application" detail="Enter the reference number you received when you submitted your enquiry or application." />
      <section className="bfa-section">
        <div className="bfa-container" style={{ maxWidth: 620 }}>
          <form className="bfa-form" onSubmit={lookup} style={{ marginBottom: 30 }}>
            <ErrorBanner message={error} />
            <label className="bfa-field">Reference number
              <input required placeholder="BFA-2026-000184" value={reference} onChange={(e) => setReference(e.target.value)} />
            </label>
            <button className="bfa-btn bfa-btn-navy" disabled={loading}>{loading ? 'Searching…' : 'Check status'}</button>
          </form>

          {result && (
            <div className="bfa-card">
              <span className="bfa-status-pill">{STATUS_LABEL[result.data.status] || result.data.status}</span>
              <h3 style={{ marginTop: 14 }}>{result.data.student_first_name ? `${result.data.student_first_name} ${result.data.student_last_name}` : result.data.student_name}</h3>
              <p>{result.data.class_applying_for}</p>
              <p style={{ fontSize: 12.5, color: 'var(--bfa-muted)' }}>Reference {result.data.reference}</p>

              {result.kind === 'application' && (
                <ul className="bfa-timeline" style={{ marginTop: 24 }}>
                  {STATUS_ORDER.filter((s) => !['rejected'].includes(s)).map((status, index) => (
                    <li key={status} className={index < currentIndex ? 'done' : index === currentIndex ? 'current' : ''}>
                      <span className="bfa-timeline-dot" />
                      <div><strong>{STATUS_LABEL[status]}</strong></div>
                    </li>
                  ))}
                </ul>
              )}
              {result.data.submitted_at && <p style={{ fontSize: 12.5, color: 'var(--bfa-muted)', marginTop: 10 }}>Submitted {formatDate(result.data.submitted_at)}</p>}
              {result.kind === 'enquiry' && (
                <p style={{ marginTop: 14, fontSize: 13.5, color: 'var(--bfa-muted)' }}>
                  This is a preliminary enquiry. Ready to move forward? <Link to="/admissions/apply">Start the full application →</Link>
                </p>
              )}
            </div>
          )}
        </div>
      </section>
    </>
  )
}
