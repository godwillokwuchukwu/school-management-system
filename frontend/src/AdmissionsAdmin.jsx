import { useState, useEffect, useCallback } from 'react'
import { API_URL } from './api'

export default function AdmissionsAdmin({ onBack }) {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchApplications = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/admissions/admin/applications/`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      if (!response.ok) throw new Error('Failed to fetch applications')
      const data = await response.json()
      setApplications(data.results || data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchApplications()
  }, [fetchApplications])

  async function provision(id) {
    if (!window.confirm("Are you sure you want to provision accounts for this application?")) return;
    try {
      const response = await fetch(`${API_URL}/admissions/admin/applications/${id}/provision/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to provision')
      }
      alert('Provisioned successfully!')
      fetchApplications()
    } catch (err) {
      alert(`Error provisioning: ${err.message}`)
    }
  }

  return (
    <>
      <div className="content-heading">
        <div>
          <p className="eyebrow">ADMINISTRATION</p>
          <h1>Admissions</h1>
          <p className="muted">Manage and provision approved admission applications.</p>
        </div>
        {onBack && (
          <button className="secondary-button" onClick={onBack}>
            ← Overview
          </button>
        )}
      </div>

      <section className="panel page-panel">
        <div className="panel-heading">
          <div>
            <h2>Applications</h2>
          </div>
        </div>
        
        {loading && <p style={{padding: '1rem'}}>Loading...</p>}
        {error && <p className="form-error" style={{padding: '1rem'}}>{error}</p>}
        
        {!loading && !error && applications.length === 0 && (
          <div className="empty-state">
            <strong>No applications</strong>
            <span>There are no admission applications found.</span>
          </div>
        )}

        {!loading && !error && applications.map((app) => (
          <div key={app.id} className="attention-item" style={{display: 'flex', justifyContent: 'space-between', padding: '1rem', borderBottom: '1px solid var(--border-light)'}}>
            <div>
              <b>{app.reference} - {app.student_first_name} {app.student_last_name}</b>
              <div style={{display: 'flex', gap: '1rem', marginTop: '4px'}}>
                <span className={`status ${app.status === 'approved' ? 'upcoming' : ''}`}>{app.status.toUpperCase()}</span>
                <span className="muted">{app.class_applying_for}</span>
              </div>
            </div>
            {app.status === 'approved' && (
              <button className="primary-button" onClick={() => provision(app.id)}>
                Provision Accounts
              </button>
            )}
          </div>
        ))}
      </section>
    </>
  )
}

