import { useEffect } from 'react'
import { PageHero } from '../ui'

export default function Terms() {
  useEffect(() => { document.title = 'Terms of Use — Riverside Academy' }, [])
  return (
    <>
      <PageHero crumb="Legal" title="Terms of Use" />
      <section className="bfa-section">
        <div className="bfa-container" style={{ maxWidth: 760, lineHeight: 1.8, color: 'var(--bfa-muted)' }}>
          <p>By using this website and any associated application or portal, you agree to provide accurate information and to use the site only for its intended purposes: learning about Riverside Academy, submitting applications, and (for authorized users) accessing the school management system.</p>
          <p>Applicant accounts are limited to tracking your own applications and documents. Internal portal accounts are provisioned only by school administrators following an approved admissions or employment process.</p>
          <p>This is placeholder terms text pending review by school leadership and legal counsel.</p>
        </div>
      </section>
    </>
  )
}
