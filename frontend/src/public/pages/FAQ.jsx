import { useEffect, useState } from 'react'
import { publicApi } from '../api'
import { Empty, Loading, PageHero } from '../ui'

export default function FAQ() {
  const [faqs, setFaqs] = useState(null)
  const [openId, setOpenId] = useState(null)

  useEffect(() => {
    document.title = 'FAQ — Riverside Academy'
    publicApi.faqs().then(setFaqs).catch(() => setFaqs([]))
  }, [])

  return (
    <>
      <PageHero crumb="FAQ" title="Frequently asked questions" />
      <section className="bfa-section">
        <div className="bfa-container" style={{ maxWidth: 760 }}>
          {faqs === null ? (
            <Loading />
          ) : faqs.length === 0 ? (
            <Empty label="FAQs will be published here soon." />
          ) : (
            faqs.map((item) => (
              <div className="bfa-card" key={item.id} style={{ marginBottom: 14, cursor: 'pointer' }} onClick={() => setOpenId(openId === item.id ? null : item.id)}>
                <span className="bfa-badge" style={{ marginBottom: 10 }}>{item.category}</span>
                <h3>{item.question}</h3>
                {openId === item.id && <p style={{ marginTop: 10 }}>{item.answer}</p>}
              </div>
            ))
          )}
        </div>
      </section>
    </>
  )
}
