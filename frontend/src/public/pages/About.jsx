import { useEffect, useState } from 'react'
import { publicApi } from '../api'
import { Loading, PageHero } from '../ui'

export default function About() {
  const [school, setSchool] = useState(null)

  useEffect(() => {
    document.title = 'About Us — Riverside Academy'
    publicApi.school().then(setSchool).catch(() => setSchool({}))
  }, [])

  if (!school) return <Loading />

  const values = (school.core_values || '').split('\n').map((v) => v.trim()).filter(Boolean)

  return (
    <>
      <PageHero crumb="About us" title="A school built on trust and ambition" detail={school.tagline} />
      <section className="bfa-section bfa-section-alt">
        <div className="bfa-container bfa-grid bfa-grid-2">
          <div>
            <h2 style={{ color: 'var(--bfa-navy)' }}>Our history</h2>
            <p style={{ color: 'var(--bfa-muted)', lineHeight: 1.7 }}>
              {school.history || `Riverside Academy was founded${school.founded_year ? ` in ${school.founded_year}` : ''} with a simple belief: every student deserves an education that challenges them academically while nurturing who they are becoming.`}
            </p>
          </div>
          <div className="bfa-card">
            <h3>School culture</h3>
            <p>A safe, supportive, and inspiring environment where every student can learn, grow, and achieve — academically, socially, and personally.</p>
          </div>
        </div>
      </section>
      <section className="bfa-section">
        <div className="bfa-container bfa-grid bfa-grid-2">
          <div className="bfa-card">
            <span className="bfa-tag">MISSION</span>
            <p style={{ color: 'var(--bfa-text)', lineHeight: 1.7 }}>
              {school.mission || 'To provide a well-rounded, high-quality education that equips every student with the knowledge, character, and confidence to succeed.'}
            </p>
          </div>
          <div className="bfa-card">
            <span className="bfa-tag">VISION</span>
            <p style={{ color: 'var(--bfa-text)', lineHeight: 1.7 }}>
              {school.vision || 'To be a leading center of academic excellence and holistic development, preparing the next generation of confident, capable leaders.'}
            </p>
          </div>
        </div>
      </section>
      {values.length > 0 && (
        <section className="bfa-section bfa-section-alt">
          <div className="bfa-container">
            <div className="bfa-section-head"><h2>Our core values</h2></div>
            <div className="bfa-grid bfa-grid-4">
              {values.map((value) => (
                <div className="bfa-card" key={value}><h3>{value}</h3></div>
              ))}
            </div>
          </div>
        </section>
      )}
    </>
  )
}
