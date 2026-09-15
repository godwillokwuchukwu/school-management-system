import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { publicApi } from '../api'
import { Loading } from '../ui'
import { formatDate } from '../formatters'

const FEATURES = [
  ['Academic Excellence', 'A rigorous, well-rounded curriculum guided by experienced educators.'],
  ['Experienced Teachers', 'Passionate, qualified staff who know every learner by name.'],
  ['Modern Facilities', 'Science labs, libraries, sports fields, and creative studios.'],
  ['Holistic Development', 'Sport, arts, leadership, and community service alongside academics.'],
]

export default function Home() {
  const [school, setSchool] = useState(null)
  const [news, setNews] = useState([])
  const [events, setEvents] = useState([])
  const [testimonials, setTestimonials] = useState([])
  const [programs, setPrograms] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    document.title = 'Riverside Academy — Inspiring excellence, building futures.'
    Promise.allSettled([
      publicApi.school(),
      publicApi.news('?page_size=3'),
      publicApi.events('?when=upcoming'),
      publicApi.testimonials(),
      publicApi.programs(),
    ]).then(([schoolRes, newsRes, eventsRes, testimonialsRes, programsRes]) => {
      if (schoolRes.status === 'fulfilled') setSchool(schoolRes.value)
      if (newsRes.status === 'fulfilled') setNews(newsRes.value.results || newsRes.value || [])
      if (eventsRes.status === 'fulfilled') setEvents((eventsRes.value.results || eventsRes.value || []).slice(0, 3))
      if (testimonialsRes.status === 'fulfilled') setTestimonials(testimonialsRes.value.slice(0, 3))
      if (programsRes.status === 'fulfilled') setPrograms((programsRes.value.results || programsRes.value || []).slice(0, 4))
      setLoading(false)
    })
  }, [])

  if (loading) return <Loading label="Loading Riverside Academy…" />

  return (
    <>
      <section className="bfa-hero">
        <div className="bfa-container">
          <div>
            <p className="bfa-eyebrow">{school?.name || 'Riverside Academy'} · {school?.tagline || 'Learning with purpose'}</p>
            <h1>{school?.hero_heading || 'Inspiring excellence, building futures.'}</h1>
            <p>{school?.hero_subtext || 'Where every learner is seen, challenged, and prepared to make a meaningful difference in the world.'}</p>
            <div className="bfa-hero-actions">
              <Link to="/admissions/apply" className="bfa-btn bfa-btn-gold">Enroll Now →</Link>
              <Link to="/about" className="bfa-btn bfa-btn-outline">Learn More</Link>
            </div>
          </div>
          <div className="bfa-hero-card">
            <p className="bfa-eyebrow" style={{ marginBottom: 18 }}>Riverside Academy at a glance</p>
            <div className="bfa-hero-stats">
              <div><strong>{school?.total_students || '—'}</strong><span>Total students</span></div>
              <div><strong>{school?.total_teachers || '—'}</strong><span>Total teachers</span></div>
              <div><strong>{school?.years_of_excellence ? `${school.years_of_excellence}+` : '—'}</strong><span>Years of excellence</span></div>
              <div><strong>{school?.graduation_rate ? `${school.graduation_rate}%` : '—'}</strong><span>Graduation success</span></div>
            </div>
          </div>
        </div>
      </section>

      <section className="bfa-section bfa-section-alt">
        <div className="bfa-container">
          <div className="bfa-section-head">
            <p className="bfa-eyebrow" style={{ color: 'var(--bfa-navy)' }}>WHY CHOOSE US</p>
            <h2>Everything your child needs to thrive</h2>
          </div>
          <div className="bfa-grid bfa-grid-4">
            {FEATURES.map(([title, detail]) => (
              <div className="bfa-card" key={title}>
                <div className="bfa-card-icon">✦</div>
                <h3>{title}</h3>
                <p>{detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Our School Homepage Teaser */}
      <section className="bfa-section">
        <div className="bfa-container">
          <div className="bfa-teaser-grid">
            <div className="bfa-teaser-img-wrap">
              <img src="/school-campus.jpg" alt="Riverside Academy Campus" className="bfa-teaser-img" />
              <div className="bfa-teaser-badge-overlay">
                <strong>{school?.founded_year ? `Est. ${school.founded_year}` : 'Excellence in Education'}</strong>
                <span>{school?.years_of_excellence ? `${school.years_of_excellence}+ Years of Heritage` : 'Riverside Academy'}</span>
              </div>
            </div>
            <div>
              <p className="bfa-eyebrow" style={{ color: 'var(--bfa-navy)' }}>ABOUT OUR SCHOOL</p>
              <h2>A tradition of excellence, an eye on the future</h2>
              <p style={{ color: 'var(--bfa-muted)', lineHeight: 1.7, fontSize: 14.5, marginBottom: 18 }}>
                {school?.mission || 'At Riverside Academy, we believe every student deserves an education that challenges them academically while nurturing their character and leadership skills. Our dedicated faculty and modern facilities ensure an enriching environment.'}
              </p>
              <div className="bfa-teaser-highlights">
                <div className="bfa-teaser-item"><span>✦</span> Rigorous Academic Tracks</div>
                <div className="bfa-teaser-item"><span>✦</span> Dedicated Faculty Mentors</div>
                <div className="bfa-teaser-item"><span>✦</span> Modern STEM & Arts Labs</div>
                <div className="bfa-teaser-item"><span>✦</span> Athletics & Leadership</div>
              </div>
              <Link to="/about" className="bfa-btn bfa-btn-navy">Learn More About Us →</Link>
            </div>
          </div>
        </div>
      </section>

      {programs.length > 0 && (
        <section className="bfa-section bfa-section-alt">
          <div className="bfa-container">
            <div className="bfa-section-head">
              <p className="bfa-eyebrow" style={{ color: 'var(--bfa-navy)' }}>PROGRAMS</p>
              <h2>Beyond the classroom</h2>
            </div>
            <div className="bfa-grid bfa-grid-4">
              {programs.map((program) => (
                <div className="bfa-card" key={program.slug}>
                  {program.image_url ? (
                    <img src={program.image_url} alt={program.name} className="bfa-card-media" />
                  ) : (
                    <div className="bfa-card-placeholder">✦</div>
                  )}
                  <span className="bfa-tag">{program.category}</span>
                  <h3>{program.name}</h3>
                  <p>{program.summary}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="bfa-stats-band">
        <div className="bfa-container">
          <div className="bfa-grid bfa-grid-4">
            <div><strong>{school?.total_students || '—'}</strong><span>Total students</span></div>
            <div><strong>{school?.total_teachers || '—'}</strong><span>Total teachers</span></div>
            <div><strong>{school?.years_of_excellence ? `${school.years_of_excellence}+` : '—'}</strong><span>Years of excellence</span></div>
            <div><strong>{school?.graduation_rate ? `${school.graduation_rate}%` : '—'}</strong><span>Graduation success rate</span></div>
          </div>
        </div>
      </section>

      {testimonials.length > 0 && (
        <section className="bfa-section bfa-section-alt">
          <div className="bfa-container">
            <div className="bfa-section-head">
              <p className="bfa-eyebrow" style={{ color: 'var(--bfa-navy)' }}>TESTIMONIALS</p>
              <h2>What our community says</h2>
            </div>
            <div className="bfa-grid bfa-grid-3">
              {testimonials.map((item) => (
                <div className="bfa-card" key={item.id}>
                  <p className="bfa-quote">“{item.quote}”</p>
                  <div className="bfa-testimonial-author-row">
                    {item.photo_url ? (
                      <img src={item.photo_url} alt={item.name} className="bfa-testimonial-avatar" />
                    ) : (
                      <div className="bfa-testimonial-avatar-fallback">{item.name.charAt(0)}</div>
                    )}
                    <div>
                      <p className="bfa-quote-author" style={{ margin: 0 }}>{item.name}</p>
                      <p className="bfa-quote-role" style={{ margin: 0 }}>{item.role}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {(news.length > 0 || events.length > 0) && (
        <section className="bfa-section">
          <div className="bfa-container">
            <div className="bfa-grid bfa-grid-2">
              <div>
                <div className="bfa-section-head left">
                  <p className="bfa-eyebrow" style={{ color: 'var(--bfa-navy)' }}>LATEST NEWS</p>
                  <h2>What's happening</h2>
                </div>
                {news.map((item) => (
                  <div className="bfa-list-row" key={item.slug} style={{ gap: 14 }}>
                    {item.cover_image_url && (
                      <img src={item.cover_image_url} alt={item.title} style={{ width: 64, height: 64, objectFit: 'cover', borderRadius: 'var(--bfa-radius)', flexShrink: 0 }} />
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <h4><Link to={`/news/${item.slug}`}>{item.title}</Link></h4>
                      <p>{formatDate(item.published_at)}</p>
                    </div>
                    <span className="bfa-badge">{item.category}</span>
                  </div>
                ))}
                <Link to="/news" className="bfa-btn bfa-btn-navy" style={{ marginTop: 12 }}>All news →</Link>
              </div>
              <div>
                <div className="bfa-section-head left">
                  <p className="bfa-eyebrow" style={{ color: 'var(--bfa-navy)' }}>UPCOMING EVENTS</p>
                  <h2>Save the date</h2>
                </div>
                {events.map((item) => {
                  const d = new Date(item.starts_at)
                  const month = isNaN(d.getTime()) ? 'DATE' : d.toLocaleString('en-US', { month: 'short' })
                  const day = isNaN(d.getTime()) ? '—' : d.getDate()
                  return (
                    <div className="bfa-list-row" key={item.slug} style={{ gap: 14 }}>
                      <div className="bfa-date-badge">
                        <span className="bfa-date-badge-month">{month}</span>
                        <span className="bfa-date-badge-day">{day}</span>
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <h4><Link to={`/events/${item.slug}`}>{item.title}</Link></h4>
                        <p>{formatDate(item.starts_at)}{item.location ? ` · ${item.location}` : ''}</p>
                      </div>
                    </div>
                  )
                })}
                {events.length === 0 && <p className="bfa-empty">No upcoming events scheduled yet.</p>}
              </div>
            </div>
          </div>
        </section>
      )}

      <section className="bfa-section" style={{ paddingTop: 0 }}>
        <div className="bfa-cta-banner">
          <p className="bfa-eyebrow">JOIN OUR NEXT CHAPTER</p>
          <h2>Admissions are open for {school?.founded_year ? new Date().getFullYear() : '2026/2027'}.</h2>
          <p>Come and see what your child can become at Riverside Academy.</p>
          <Link to="/admissions/apply" className="bfa-btn bfa-btn-gold">Start an application →</Link>
        </div>
      </section>
    </>
  )
}
