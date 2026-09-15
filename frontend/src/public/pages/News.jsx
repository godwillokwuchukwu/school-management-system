import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { publicApi } from '../api'
import { Empty, Loading, PageHero } from '../ui'
import { formatDate } from '../formatters'

const TABS = [
  { id: 'all', label: 'All Updates' },
  { id: 'news', label: 'News' },
  { id: 'events', label: 'Events' },
  { id: 'announcements', label: 'Announcements' },
]

export default function News() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialTab = searchParams.get('tab') || 'all'
  const [activeTab, setActiveTab] = useState(initialTab)
  const [articles, setArticles] = useState(null)
  const [events, setEvents] = useState(null)

  useEffect(() => {
    document.title = 'News & Events — Riverside Academy'
    Promise.allSettled([
      publicApi.news('?page_size=20'),
      publicApi.events('?page_size=20'),
    ]).then(([newsRes, eventsRes]) => {
      if (newsRes.status === 'fulfilled') {
        setArticles(newsRes.value.results || newsRes.value || [])
      } else {
        setArticles([])
      }
      if (eventsRes.status === 'fulfilled') {
        setEvents(eventsRes.value.results || eventsRes.value || [])
      } else {
        setEvents([])
      }
    })
  }, [])

  const handleTabChange = (tabId) => {
    setActiveTab(tabId)
    setSearchParams(tabId === 'all' ? {} : { tab: tabId })
  }

  if (articles === null || events === null) {
    return (
      <>
        <PageHero crumb="News & Events" title="School news & calendar" detail="Stay informed on school happenings, achievements, and upcoming events." />
        <section className="bfa-section"><div className="bfa-container"><Loading label="Loading news and events…" /></div></section>
      </>
    )
  }

  // Filter items based on active tab
  let displayItems = []
  if (activeTab === 'all') {
    const newsFormatted = articles.map((a) => ({ ...a, itemType: 'news', date: new Date(a.published_at) }))
    const eventsFormatted = events.map((e) => ({ ...e, itemType: 'event', date: new Date(e.starts_at) }))
    displayItems = [...newsFormatted, ...eventsFormatted].sort((a, b) => b.date - a.date)
  } else if (activeTab === 'news') {
    displayItems = articles.map((a) => ({ ...a, itemType: 'news', date: new Date(a.published_at) }))
  } else if (activeTab === 'events') {
    displayItems = events.map((e) => ({ ...e, itemType: 'event', date: new Date(e.starts_at) }))
  } else if (activeTab === 'announcements') {
    displayItems = articles.filter((a) => a.category === 'announcement').map((a) => ({ ...a, itemType: 'news', date: new Date(a.published_at) }))
  }

  return (
    <>
      <PageHero crumb="News & Events" title="School news & calendar" detail="Stay informed on campus life, academic achievements, announcements, and events." />
      <section className="bfa-section">
        <div className="bfa-container">
          <div className="bfa-hub-filter-bar">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={activeTab === tab.id ? 'bfa-btn bfa-btn-navy' : 'bfa-btn bfa-btn-outline'}
                style={activeTab !== tab.id ? { color: 'var(--bfa-navy)', borderColor: 'var(--bfa-border)' } : {}}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {displayItems.length === 0 ? (
            <Empty label={`No entries found in ${activeTab}.`} />
          ) : (
            <div className="bfa-grid bfa-grid-3">
              {displayItems.map((item) => {
                const isEvent = item.itemType === 'event'
                const linkTo = isEvent ? `/events/${item.slug}` : `/news/${item.slug}`

                return (
                  <Link to={linkTo} className="bfa-card" key={`${item.itemType}-${item.slug}`}>
                    {item.cover_image_url ? (
                      <img src={item.cover_image_url} alt={item.title} className="bfa-card-media" />
                    ) : (
                      <div className="bfa-card-placeholder">
                        {isEvent ? '📅' : '📰'}
                      </div>
                    )}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className={isEvent ? 'bfa-badge-gold bfa-badge' : 'bfa-badge'}>
                        {isEvent ? 'Event' : item.category || 'News'}
                      </span>
                      <span style={{ fontSize: 11.5, color: 'var(--bfa-muted)' }}>
                        {isEvent ? formatDate(item.starts_at) : formatDate(item.published_at)}
                      </span>
                    </div>
                    <h3 style={{ marginTop: 12, marginBottom: 8, fontSize: 16 }}>{item.title}</h3>
                    <p style={{ fontSize: 13, color: 'var(--bfa-muted)', lineClamp: 2 }}>
                      {isEvent ? (item.location ? `📍 ${item.location}` : item.description?.slice(0, 100)) : item.excerpt || item.body?.slice(0, 100)}
                    </p>
                  </Link>
                )
              })}
            </div>
          )}
        </div>
      </section>
    </>
  )
}

