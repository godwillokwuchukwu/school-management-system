import { Link } from 'react-router-dom'
import { PageHero } from '../ui'

export default function NotFound() {
  return (
    <>
      <PageHero crumb="404" title="Page not found" detail="The page you're looking for doesn't exist or has moved." />
      <section className="bfa-section" style={{ textAlign: 'center' }}>
        <Link to="/" className="bfa-btn bfa-btn-navy">← Back to homepage</Link>
      </section>
    </>
  )
}
