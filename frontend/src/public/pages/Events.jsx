import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { publicApi } from '../api'
import { Empty, Loading, PageHero } from '../ui'
import { formatDateTime } from '../formatters'

export default function Events() {
  const [events, setEvents] = useState(null)
  const [when, setWhen] = useState('upcoming')

  useEffect(() => { document.title = 'Events — Riverside Academy' }, [])

  useEffect(() => {
    let active = true
    publicApi.events(`?when=${when}`).then((data) => {
      if (active) setEvents(data.results || data || [])
    }).catch(() => {
      if (active) setEvents([])
    })
    return () => { active = false }
  }, [when])

  return (
    <>
      <PageHero crumb="Events" title="School calendar & events" />
      <section className="bfa-section">
        <div className="bfa-container">
          <div style={{ display: 'flex', gap: 10, marginBottom: 28 }}>
            {['upcoming', 'past'].map((option) => (
              <button
                key={option}
                onClick={() => { setWhen(option); setEvents(null) }}
                className={option === when ? 'bfa-btn bfa-btn-navy' : 'bfa-btn bfa-btn-outline'}
                style={option !== when ? { color: 'var(--bfa-navy)', borderColor: 'var(--bfa-border)' } : {}}
              >
                {option === 'upcoming' ? 'Upcoming' : 'Past'}
              </button>
            ))}
          </div>
          {events === null ? (
            <Loading />
          ) : events.length === 0 ? (
            <Empty label={`No ${when} events right now.`} />
          ) : (
            <div className="bfa-grid bfa-grid-3">
              {events.map((item) => (
                <Link to={`/events/${item.slug}`} className="bfa-card" key={item.slug}>
                  {item.cover_image_url ? (
                    <img src={item.cover_image_url} alt={item.title} className="bfa-card-media" />
                  ) : (
                    <div className="bfa-card-placeholder">📅</div>
                  )}
                  <span className="bfa-badge-gold bfa-badge">{item.category || 'Event'}</span>
                  <h3 style={{ marginTop: 12 }}>{item.title}</h3>
                  <p style={{ color: 'var(--bfa-muted)', fontSize: 13, marginTop: 4 }}>
                    {formatDateTime(item.starts_at)}{item.location ? ` · 📍 ${item.location}` : ''}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  )
}
