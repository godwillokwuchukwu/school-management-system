import { useState, useEffect } from 'react'
import { api, API_URL } from './api'

export default function UserManagement({ roleFilter, onBack }) {
  const [profiles, setProfiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [provisionEmail, setProvisionEmail] = useState('')
  const [provisionLoading, setProvisionLoading] = useState(false)

  const roleValue = roleFilter === 'Staff' ? 'admin' : roleFilter.toLowerCase().replace(/s$/, '')

  useEffect(() => {
    fetchProfiles()
  }, [roleFilter])

  async function fetchProfiles() {
    try {
      const response = await fetch(`${API_URL}/accounts/profiles/?role=${roleValue}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      if (!response.ok) throw new Error('Failed to fetch profiles')
      const data = await response.json()
      setProfiles(data.results || data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleProvision(e) {
    e.preventDefault()
    if (!provisionEmail) return
    setProvisionLoading(true)
    try {
      await api.adminProvisionAccount({ email: provisionEmail, role: roleValue })
      alert(`Provisioned account for ${provisionEmail}`)
      setProvisionEmail('')
      fetchProfiles()
    } catch (err) {
      alert(`Error provisioning: ${err.message}`)
    } finally {
      setProvisionLoading(false)
    }
  }

  async function toggleSuspend(profile) {
    const isActive = profile.user?.is_active ?? profile.is_active ?? true
    const isSuspended = !isActive
    const action = isSuspended ? 'reactivate' : 'suspend'
    if (!window.confirm(`Are you sure you want to ${action} this account?`)) return

    try {
      if (isSuspended) {
        await api.adminReactivateProfile(profile.id)
      } else {
        await api.adminSuspendProfile(profile.id)
      }
      fetchProfiles()
    } catch (err) {
      alert(`Error: ${err.message}`)
    }
  }

  return (
    <>
      <div className="content-heading">
        <div>
          <p className="eyebrow">USER MANAGEMENT</p>
          <h1>{roleFilter}</h1>
          <p className="muted">Manage and provision {roleFilter.toLowerCase()} accounts.</p>
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
            <h2>Provision New {roleFilter}</h2>
          </div>
        </div>
        <form onSubmit={handleProvision} style={{padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'flex-end'}}>
          <label style={{flex: 1}}>
            Email Address
            <input 
              type="email" 
              value={provisionEmail} 
              onChange={e => setProvisionEmail(e.target.value)} 
              required 
              style={{width: '100%'}}
            />
          </label>
          <button className="primary-button" type="submit" disabled={provisionLoading}>
            {provisionLoading ? 'Provisioning...' : 'Provision Account'}
          </button>
        </form>
      </section>

      <section className="panel page-panel">
        <div className="panel-heading">
          <div>
            <h2>Active Profiles</h2>
          </div>
        </div>
        
        {loading && <p style={{padding: '1rem'}}>Loading...</p>}
        {error && <p className="form-error" style={{padding: '1rem'}}>{error}</p>}
        
        {!loading && !error && profiles.length === 0 && (
          <div className="empty-state">
            <strong>No profiles</strong>
            <span>There are no {roleFilter.toLowerCase()} profiles found.</span>
          </div>
        )}

        {!loading && !error && profiles.map((profile) => {
          const isActive = profile.user?.is_active ?? profile.is_active ?? true
          return (
          <div key={profile.id} className="attention-item" style={{display: 'flex', justifyContent: 'space-between', padding: '1rem', borderBottom: '1px solid var(--border-light)'}}>
            <div>
              <b>{profile.first_name} {profile.last_name}</b>
              <div style={{display: 'flex', gap: '1rem', marginTop: '4px'}}>
                <span className="muted">{profile.email}</span>
                <span className={`status ${!isActive ? 'urgent' : 'upcoming'}`}>
                  {isActive ? 'ACTIVE' : 'SUSPENDED'}
                </span>
              </div>
            </div>
            <button className="secondary-button" onClick={() => toggleSuspend(profile)}>
              {isActive ? 'Suspend' : 'Reactivate'}
            </button>
          </div>
        )})}
      </section>
    </>
  )
}

