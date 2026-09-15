import { useEffect, useState } from 'react'
import { publicApi } from '../api'
import { Empty, Loading, PageHero } from '../ui'

export default function Programs() {
  const [programs, setPrograms] = useState(null)

  useEffect(() => {
    document.title = 'Programs — Riverside Academy'
    publicApi.programs().then((data) => setPrograms(data.results || data || [])).catch(() => setPrograms([]))
  }, [])

  return (
    <>
      <PageHero crumb="Programs" title="Sports, arts & extracurricular life" detail="Leadership, creativity, and community — the experiences that round out a Riverside education." />
      <section className="bfa-section">
        <div className="bfa-container">
          {programs === null ? (
            <Loading />
          ) : programs.length === 0 ? (
            <Empty label="Program listings will appear here soon." />
          ) : (
            <div className="bfa-grid bfa-grid-3">
              {programs.map((program) => (
                <div className="bfa-card" key={program.slug}>
                  {program.image_url ? (
                    <img src={program.image_url} alt={program.name} className="bfa-card-media" />
                  ) : (
                    <div className="bfa-card-placeholder">✦</div>
                  )}
                  <span className="bfa-tag">{program.category}</span>
                  <h3>{program.name}</h3>
                  <p>{program.description || program.summary}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  )
}
