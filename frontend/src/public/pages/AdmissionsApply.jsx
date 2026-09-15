import { useEffect, useState } from 'react'
import { publicApi } from '../api'
import { ErrorBanner, Loading, PageHero, SuccessBanner } from '../ui'
import { formatDate } from '../formatters'

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
      if (mode === 'register') {
        await publicApi.register(form)
      }
      await publicApi.login(form.email, form.password)
      onSignedIn()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="bfa-section">
      <div className="bfa-container" style={{ maxWidth: 480 }}>
        <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
          <button className={mode === 'register' ? 'bfa-btn bfa-btn-navy' : 'bfa-btn bfa-btn-outline'} style={mode !== 'register' ? { color: 'var(--bfa-navy)', borderColor: 'var(--bfa-border)' } : {}} onClick={() => setMode('register')}>Create account</button>
          <button className={mode === 'login' ? 'bfa-btn bfa-btn-navy' : 'bfa-btn bfa-btn-outline'} style={mode !== 'login' ? { color: 'var(--bfa-navy)', borderColor: 'var(--bfa-border)' } : {}} onClick={() => setMode('login')}>Sign in</button>
        </div>
        <p style={{ color: 'var(--bfa-muted)', marginBottom: 20, fontSize: 14 }}>
          {mode === 'register'
            ? 'Create an applicant account to start and track a full admission application. This account only lets you manage your own applications — it does not grant access to the school portal.'
            : 'Sign in to continue an application you already started.'}
        </p>
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
    </section>
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
    <form className="bfa-form" onSubmit={save} style={{ maxWidth: 720 }}>
      <ErrorBanner message={error} />
      <p className="bfa-form-section-title" style={{ borderTop: 'none', paddingTop: 0 }}>Student information</p>
      <div className="bfa-form-row">
        <label className="bfa-field">First name<input required value={form.student_first_name} onChange={(e) => update('student_first_name', e.target.value)} /></label>
        <label className="bfa-field">Last name<input required value={form.student_last_name} onChange={(e) => update('student_last_name', e.target.value)} /></label>
      </div>
      <div className="bfa-form-row">
        <label className="bfa-field">Middle name<input value={form.student_middle_name} onChange={(e) => update('student_middle_name', e.target.value)} /></label>
        <label className="bfa-field">Date of birth<input required type="date" value={form.student_dob} onChange={(e) => update('student_dob', e.target.value)} /></label>
      </div>
      <div className="bfa-form-row">
        <label className="bfa-field">Gender<input value={form.student_gender} onChange={(e) => update('student_gender', e.target.value)} /></label>
        <label className="bfa-field">Nationality<input value={form.student_nationality} onChange={(e) => update('student_nationality', e.target.value)} /></label>
      </div>
      <div className="bfa-form-row">
        <label className="bfa-field">Class applying for<input required value={form.class_applying_for} onChange={(e) => update('class_applying_for', e.target.value)} /></label>
        <label className="bfa-field">Academic session<input required value={form.academic_session} onChange={(e) => update('academic_session', e.target.value)} /></label>
      </div>
      <div className="bfa-form-row">
        <label className="bfa-field">Previous school<input value={form.previous_school} onChange={(e) => update('previous_school', e.target.value)} /></label>
        <label className="bfa-field">Previous class<input value={form.previous_class} onChange={(e) => update('previous_class', e.target.value)} /></label>
      </div>
      <label className="bfa-field">Student address<input value={form.student_address} onChange={(e) => update('student_address', e.target.value)} /></label>

      <p className="bfa-form-section-title">Parent / Guardian information</p>
      <div className="bfa-form-row">
        <label className="bfa-field">Full name<input required value={form.guardian_full_name} onChange={(e) => update('guardian_full_name', e.target.value)} /></label>
        <label className="bfa-field">Relationship<input required value={form.guardian_relationship} onChange={(e) => update('guardian_relationship', e.target.value)} /></label>
      </div>
      <div className="bfa-form-row">
        <label className="bfa-field">Phone<input required value={form.guardian_phone} onChange={(e) => update('guardian_phone', e.target.value)} /></label>
        <label className="bfa-field">Email<input required type="email" value={form.guardian_email} onChange={(e) => update('guardian_email', e.target.value)} /></label>
      </div>
      <label className="bfa-field">Address<input value={form.guardian_address} onChange={(e) => update('guardian_address', e.target.value)} /></label>

      <button className="bfa-btn bfa-btn-navy" disabled={saving}>{saving ? 'Saving…' : 'Save draft'}</button>
    </form>
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
    <form onSubmit={upload} style={{ display: 'flex', gap: 10, alignItems: 'flex-end', flexWrap: 'wrap', marginTop: 14 }}>
      <ErrorBanner message={error} />
      <label className="bfa-field" style={{ minWidth: 220 }}>Document type
        <select value={docType} onChange={(e) => setDocType(e.target.value)}>
          {DOCUMENT_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </label>
      <label className="bfa-field">File
        <input type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onChange={(e) => setFile(e.target.files[0])} />
      </label>
      <button className="bfa-btn bfa-btn-outline" style={{ color: 'var(--bfa-navy)', borderColor: 'var(--bfa-border)' }} disabled={saving}>{saving ? 'Uploading…' : 'Upload'}</button>
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
    if (!current?.id) {
      setSubmitError('Please save the application draft first before submitting.')
      return
    }
    setSubmitError('')
    setSubmitting(true)
    try {
      const updated = await publicApi.submitApplication(current.id)
      setCurrent(updated)
      onUpdated(updated)
      setSubmitMessage('Application submitted! Your reference is ' + updated.reference + '.')
    } catch (err) {
      setSubmitError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const docList = Array.isArray(documents) ? documents : []

  return (
    <div>
      <button className="bfa-btn bfa-btn-outline" style={{ color: 'var(--bfa-navy)', borderColor: 'var(--bfa-border)', marginBottom: 20 }} onClick={onBack}>← My applications</button>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 10 }}>
        <div>
          <h2 style={{ color: 'var(--bfa-navy)', margin: 0 }}>{current?.student_first_name} {current?.student_last_name}</h2>
          {current?.reference && <p style={{ color: 'var(--bfa-muted)', fontSize: 13.5 }}>Reference {current.reference}</p>}
        </div>
        <span className="bfa-status-pill">{current?.status?.replace(/_/g, ' ') || 'started'}</span>
      </div>

      <SuccessBanner message={submitMessage} />
      <ErrorBanner message={submitError} />

      {editable ? (
        <ApplicationForm application={current} onSaved={(saved) => { setCurrent(saved); onUpdated(saved) }} />
      ) : (
        <p style={{ color: 'var(--bfa-muted)' }}>This application has been submitted and can no longer be edited. Contact admissions if anything needs to change.</p>
      )}

      <p className="bfa-form-section-title">Documents</p>
      {docList.length === 0 ? (
        <p style={{ color: 'var(--bfa-muted)', fontSize: 14 }}>No documents uploaded yet.</p>
      ) : (
        docList.map((doc) => (
          <div className="bfa-list-row" key={doc.id}>
            <div><h4>{DOCUMENT_TYPES.find(([v]) => v === doc.document_type)?.[1] || doc.document_type}</h4><p>Uploaded {formatDate(doc.uploaded_at)}</p></div>
          </div>
        ))
      )}
      {editable && current?.id ? (
        <DocumentUploader application={current} onUploaded={(doc) => setDocuments((prev) => [doc, ...(Array.isArray(prev) ? prev : [])])} />
      ) : editable ? (
        <p style={{ color: 'var(--bfa-muted)', fontSize: 13, marginTop: 10 }}>Please save the application draft above first to enable document uploads.</p>
      ) : null}

      {editable && (
        <button className="bfa-btn bfa-btn-gold" style={{ marginTop: 26 }} onClick={submit} disabled={submitting || !current?.id}>
          {submitting ? 'Submitting…' : 'Review & submit application →'}
        </button>
      )}
    </div>
  )
}

export default function AdmissionsApply() {
  const [signedIn, setSignedIn] = useState(publicApi.isAuthenticated())
  const [applications, setApplications] = useState(null)
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => { document.title = 'Apply — Riverside Academy' }, [])

  const loadApplications = () => {
    publicApi.myApplications().then((data) => setApplications(data.results || data || [])).catch((err) => setError(err.message))
  }

  useEffect(() => { if (signedIn) loadApplications() }, [signedIn])

  if (!signedIn) {
    return (
      <>
        <PageHero crumb="Admissions" title="Start your application" detail="Sign in or create an applicant account to begin." />
        <ApplicantAuth onSignedIn={() => setSignedIn(true)} />
      </>
    )
  }

  if (selected) {
    return (
      <>
        <PageHero crumb="Admissions · Apply" title="Admission application" />
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
      <PageHero crumb="Admissions · Apply" title="My applications" detail="Start a new admission application, or continue one you've already begun." />
      <section className="bfa-section">
        <div className="bfa-container" style={{ maxWidth: 760 }}>
          <ErrorBanner message={error} />
          <button
            className="bfa-btn bfa-btn-gold"
            style={{ marginBottom: 24 }}
            onClick={() => setSelected({ ...EMPTY_APPLICATION, status: 'started', documents: [] })}
          >
            + Start a new application
          </button>
          {applications === null ? (
            <Loading />
          ) : applications.length === 0 ? (
            <p style={{ color: 'var(--bfa-muted)' }}>You haven't started an application yet.</p>
          ) : (
            (Array.isArray(applications) ? applications : []).map((app) => (
              <div className="bfa-list-row" key={app.id} style={{ cursor: 'pointer' }} onClick={() => publicApi.application(app.id).then(setSelected)}>
                <div>
                  <h4>{app.student_first_name} {app.student_last_name}{app.reference ? ` · ${app.reference}` : ''}</h4>
                  <p>{app.class_applying_for} · {app.academic_session}</p>
                </div>
                <span className="bfa-status-pill">{app.status.replace(/_/g, ' ')}</span>
              </div>
            ))
          )}
        </div>
      </section>
    </>
  )
}
