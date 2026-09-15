import { useEffect } from 'react'
import { PageHero } from '../ui'

export default function Privacy() {
  useEffect(() => { document.title = 'Privacy Policy — Riverside Academy' }, [])
  return (
    <>
      <PageHero crumb="Legal" title="Privacy Policy" />
      <section className="bfa-section">
        <div className="bfa-container" style={{ maxWidth: 760, lineHeight: 1.8, color: 'var(--bfa-muted)' }}>
          <p>Riverside Academy collects only the information needed to process admissions, employment, and general enquiries submitted through this website, and to operate the school management system for enrolled students, families, and staff.</p>
          <p>Information submitted through public forms (admissions enquiries, job applications, contact messages) is reviewed by authorized school staff only. It is never sold or shared with third parties for marketing purposes.</p>
          <p>Internal portal accounts (student, teacher, parent, admin) are protected by role-based access controls — each account can only access the records it is authorized to see.</p>
          <p>This is placeholder policy text pending review by school leadership and legal counsel.</p>
        </div>
      </section>
    </>
  )
}
