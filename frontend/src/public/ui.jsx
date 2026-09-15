export function Loading({ label = 'Loading…' }) {
  return <div className="bfa-loading">{label}</div>
}

export function Empty({ label }) {
  return <div className="bfa-empty">{label}</div>
}

export function ErrorBanner({ message }) {
  if (!message) return null
  return <div className="bfa-error">{message}</div>
}

export function SuccessBanner({ message }) {
  if (!message) return null
  return <div className="bfa-success">{message}</div>
}

export function PageHero({ crumb, title, detail }) {
  return (
    <section className="bfa-page-hero">
      <div className="bfa-container">
        {crumb && <p className="bfa-breadcrumb">{crumb}</p>}
        <h1>{title}</h1>
        {detail && <p>{detail}</p>}
      </div>
    </section>
  )
}


