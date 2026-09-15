import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { publicApi } from '../api'
import { Loading } from '../ui'
import { formatDate } from '../formatters'

export default function NewsDetail() {
  const { slug } = useParams()
  const [article, setArticle] = useState(undefined)

  useEffect(() => {
    let active = true
    publicApi.newsArticle(slug).then((data) => {
      if (active) {
        setArticle(data)
        document.title = `${data.title} — Riverside Academy`
      }
    }).catch(() => {
      if (active) setArticle(null)
    })
    return () => { active = false }
  }, [slug])

  if (article === undefined) return <Loading />
  if (article === null) {
    return (
      <section className="bfa-section">
        <div className="bfa-container">
          <p>That article couldn't be found.</p>
          <Link to="/news" className="bfa-btn bfa-btn-navy">← Back to news</Link>
        </div>
      </section>
    )
  }

  return (
    <section className="bfa-section">
      <div className="bfa-container" style={{ maxWidth: 760 }}>
        <Link to="/news" className="bfa-breadcrumb" style={{ display: 'block', marginBottom: 16 }}>← Back to news</Link>
        <span className="bfa-badge">{article.category}</span>
        <h1 style={{ color: 'var(--bfa-navy)', margin: '14px 0 6px', fontSize: 32 }}>{article.title}</h1>
        <p style={{ color: 'var(--bfa-muted)', marginBottom: 24 }}>{formatDate(article.published_at)}</p>
        {article.cover_image_url && (
          <img src={article.cover_image_url} alt={article.title} className="bfa-article-hero-img" />
        )}
        <div style={{ lineHeight: 1.8, fontSize: 15.5, whiteSpace: 'pre-line' }}>{article.body}</div>
      </div>
    </section>
  )
}
