import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { publicApi } from '../api'
import { Loading } from '../ui'
import { formatDateTime } from '../formatters'

export default function EventDetail() {
  const { slug } = useParams()
  const [event, setEvent] = useState(undefined)

  useEffect(() => {
    let active = true
    publicApi.event(slug).then((data) => {
      if (active) {
        setEvent(data)
        document.title = `${data.title} — Riverside Academy`
      }
    }).catch(() => {
      if (active) setEvent(null)
    })
    return () => { active = false }
  }, [slug])

  if (event === undefined) return <Loading />
  if (event === null) {
    return (
      <section className="bfa-section">
        <div className="bfa-container">
          <p>That event couldn't be found.</p>
          <Link to="/events" className="bfa-btn bfa-btn-navy">← Back to events</Link>
        </div>
      </section>
    )
  }

  return (
    <section className="bfa-section">
      <div className="bfa-container" style={{ maxWidth: 760 }}>
        <Link to="/events" className="bfa-breadcrumb" style={{ display: 'block', marginBottom: 16 }}>← Back to events</Link>
        <h1 style={{ color: 'var(--bfa-navy)', margin: '4px 0 10px', fontSize: 32 }}>{event.title}</h1>
        <p style={{ color: 'var(--bfa-muted)', marginBottom: 6 }}>{formatDateTime(event.starts_at)}{event.ends_at ? ` – ${formatDateTime(event.ends_at)}` : ''}</p>
        {event.location && <p style={{ color: 'var(--bfa-muted)', marginBottom: 20 }}>📍 {event.location}</p>}
        {event.cover_image_url && (
          <img src={event.cover_image_url} alt={event.title} className="bfa-article-hero-img" />
        )}
        <div style={{ lineHeight: 1.8, fontSize: 15.5, whiteSpace: 'pre-line', marginBottom: 24 }}>{event.description}</div>
        {event.registration_url && (
          <a href={event.registration_url} target="_blank" rel="noreferrer" className="bfa-btn bfa-btn-gold">Register →</a>
        )}
      </div>
    </section>
  )
}
