import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { publicApi } from './api'
import SchoolCrest from './components/SchoolCrest'
import './theme.css'

const NAV_LINKS = [
  ['About', '/about'],
  ['Academics', '/academics'],
  ['Admissions', '/admissions'],
  ['Programs', '/programs'],
  ['News & Events', '/news'],
  ['Careers', '/careers'],
  ['Contact', '/contact'],
]

function SocialIcons({ school }) {
  const fb = school?.facebook_url || 'https://facebook.com'
  const tw = school?.twitter_url || 'https://twitter.com'
  const ig = school?.instagram_url || 'https://instagram.com'
  const li = school?.linkedin_url || 'https://linkedin.com'

  return (
    <div className="bfa-social-links">
      <a href={fb} target="_blank" rel="noopener noreferrer" className="bfa-social-btn" aria-label="Facebook">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" /></svg>
      </a>
      <a href={tw} target="_blank" rel="noopener noreferrer" className="bfa-social-btn" aria-label="X (Twitter)">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z" /></svg>
      </a>
      <a href={ig} target="_blank" rel="noopener noreferrer" className="bfa-social-btn" aria-label="Instagram">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5" /><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" /><line x1="17.5" y1="6.5" x2="17.51" y2="6.5" /></svg>
      </a>
      <a href={li} target="_blank" rel="noopener noreferrer" className="bfa-social-btn" aria-label="LinkedIn">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" /><rect x="2" y="9" width="4" height="12" /><circle cx="4" cy="4" r="2" /></svg>
      </a>
    </div>
  )
}

function Header({ school }) {
  const [open, setOpen] = useState(false)
  const phone = school?.phone || '+1 555 014 2026'
  const email = school?.email || 'hello@riversideacademy.edu'

  return (
    <>
      <div className="bfa-utility">
        <div className="bfa-container">
          <span>{phone} · {email}</span>
          <span>
            <Link to="/faq">FAQ</Link> &nbsp;·&nbsp; <Link to="/admissions/status">Track application</Link>
          </span>
        </div>
      </div>
      <header className="bfa-header">
        <div className="bfa-container">
          <Link to="/" className="bfa-brand">
            <SchoolCrest size={38} />
            <span>{school?.name || 'Riverside Academy'}</span>
          </Link>
          <nav className={open ? 'bfa-nav open' : 'bfa-nav'}>
            {NAV_LINKS.map(([label, to]) => (
              <NavLink key={to} to={to} onClick={() => setOpen(false)}>
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="bfa-header-actions">
            <Link to="/login" className="bfa-btn bfa-btn-gold">Login</Link>
            <Link to="/portal" className="bfa-btn bfa-btn-outline">Portal</Link>
            <button className="bfa-mobile-toggle" onClick={() => setOpen(!open)} aria-label="Toggle navigation">
              {open ? '✕' : '☰'}
            </button>
          </div>
        </div>
      </header>
    </>
  )
}

function Footer({ school }) {
  const name = school?.name || 'Riverside Academy'
  const tagline = school?.tagline || 'Learning with purpose'
  const email = school?.email || 'hello@riversideacademy.edu'
  const phone = school?.phone || '+1 555 014 2026'
  const officeHours = school?.office_hours || 'Mon–Fri · 8am–4pm'

  return (
    <footer className="bfa-footer">
      <div className="bfa-container">
        <div className="bfa-grid bfa-grid-4">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              <SchoolCrest size={34} variant="gold" />
              <h5 style={{ margin: 0, fontSize: 16 }}>{name}</h5>
            </div>
            <p>{tagline} — a warm, ambitious school community preparing students for a changing world.</p>
            <SocialIcons school={school} />
          </div>
          <div>
            <h5>Explore</h5>
            <Link to="/about">About us</Link>
            <Link to="/academics">Academics</Link>
            <Link to="/admissions">Admissions</Link>
            <Link to="/careers">Careers</Link>
          </div>
          <div>
            <h5>Resources</h5>
            <Link to="/news">News & Events</Link>
            <Link to="/faq">FAQ</Link>
            <Link to="/privacy">Privacy Policy</Link>
            <Link to="/terms">Terms of Use</Link>
          </div>
          <div>
            <h5>Visit</h5>
            <p>{email}</p>
            <p>{phone}</p>
            <p>{officeHours}</p>
            {school?.address && <p>{school.address}</p>}
          </div>
        </div>
        <div className="bfa-footer-bottom">
          <span>© {new Date().getFullYear()} {name}. All rights reserved.</span>
          <span>{tagline}</span>
        </div>
      </div>
    </footer>
  )
}

export default function PublicLayout() {
  const [school, setSchool] = useState(null)

  useEffect(() => {
    publicApi.school().then(setSchool).catch(() => setSchool(null))
  }, [])

  return (
    <div className="bfa-public">
      <Header school={school} />
      <Outlet context={{ school }} />
      <Footer school={school} />
    </div>
  )
}

