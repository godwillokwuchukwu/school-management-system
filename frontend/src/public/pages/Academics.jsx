import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { PageHero } from '../ui'

const CURRICULUM_STAGES = [
  {
    id: 'primary',
    name: 'Primary School',
    grades: 'Grades 1–5',
    overview: 'Foundational literacy, numeracy, and curiosity-driven learning in small, nurturing classes designed to spark lifelong curiosity and emotional confidence.',
    subjects: [
      { name: 'English Language & Phonics', code: 'ENG-PRI', desc: 'Reading fluency, creative writing, spelling, and oral expression.' },
      { name: 'Foundational Mathematics', code: 'MTH-PRI', desc: 'Numeracy, mental arithmetic, geometry, patterns, and problem solving.' },
      { name: 'Basic Science & Discovery', code: 'SCI-PRI', desc: 'Exploring natural phenomena, living things, environments, and basic experiments.' },
      { name: 'Social & Cultural Studies', code: 'SOC-PRI', desc: 'Family structures, community awareness, local history, and world geography.' },
      { name: 'Visual Arts & Music', code: 'ART-PRI', desc: 'Creative drawing, color theory, rhythmic notation, and choir singing.' },
      { name: 'Physical & Health Education', code: 'PHE-PRI', desc: 'Fundamental movement, coordination, team sportsmanship, and personal wellness.' },
      { name: 'ICT & Digital Literacy', code: 'ICT-PRI', desc: 'Keyboarding skills, computer parts, basic software, and internet safety.' },
      { name: 'Character & Life Skills', code: 'LIF-PRI', desc: 'Mindfulness, mutual respect, teamwork, and responsible decision making.' },
    ],
  },
  {
    id: 'secondary',
    name: 'Secondary School',
    grades: 'Grades 6–9',
    overview: 'A balanced, rigorous curriculum that deepens critical thinking across sciences, humanities, languages, and technical disciplines.',
    subjects: [
      { name: 'English Literature & Composition', code: 'ENG-SEC', desc: 'Textual analysis, argumentative essays, persuasive speech, and syntax.' },
      { name: 'Mathematics & Pre-Algebra', code: 'MTH-SEC', desc: 'Algebraic functions, Euclidean geometry, probability, and statistics.' },
      { name: 'Integrated Science', code: 'SCI-SEC', desc: 'Hands-on laboratory physics, chemistry foundations, and biological systems.' },
      { name: 'History & Global Civics', code: 'HIS-SEC', desc: 'Modern world history, constitutional law, human rights, and global governance.' },
      { name: 'Computer Science & Coding', code: 'CSC-SEC', desc: 'Algorithmic problem solving, Python basics, web fundamentals, and ethics.' },
      { name: 'Business Studies & Commerce', code: 'BUS-SEC', desc: 'Principles of business, bookkeeping, financial planning, and enterprise.' },
      { name: 'French & Modern Languages', code: 'FRN-SEC', desc: 'Conversational fluency, grammar mastery, and international culture.' },
      { name: 'Performing Arts & Design', code: 'DRM-SEC', desc: 'Stage production, public speaking, studio design, and instrumental music.' },
    ],
  },
  {
    id: 'senior',
    name: 'Senior Secondary',
    grades: 'Grades 10–12',
    overview: 'College-preparatory pathways offering specialized academic tracks in Sciences, Humanities, and Business/Technology with individual university counseling.',
    subjects: [
      { name: 'Advanced Mathematics & Calculus', code: 'MTH-SNR', desc: 'Differential and integral calculus, trigonometry, and complex numbers.' },
      { name: 'Physics & Applied Mechanics', code: 'PHY-SNR', desc: 'Newtonian mechanics, wave theory, electromagnetism, and atomic physics.' },
      { name: 'Chemistry & Biochemistry', code: 'CHM-SNR', desc: 'Chemical kinetics, organic chemistry synthesis, and qualitative analysis.' },
      { name: 'Biology & Genetics', code: 'BIO-SNR', desc: 'Cellular biology, genetics, biotechnology, human physiology, and ecology.' },
      { name: 'Economics & Global Markets', code: 'ECO-SNR', desc: 'Microeconomics, monetary policy, fiscal strategies, and international trade.' },
      { name: 'Financial Accounting', code: 'ACC-SNR', desc: 'Balance sheets, cost accounting, corporate taxation, and internal auditing.' },
      { name: 'Literature in English & Classics', code: 'LIT-SNR', desc: 'World literature, Shakespearean drama, African prose, and literary criticism.' },
      { name: 'Computer Science & Software', code: 'CSC-SNR', desc: 'Data structures, algorithms, SQL databases, and full-stack software development.' },
    ],
  },
]

export default function Academics() {
  const [activeStageId, setActiveStageId] = useState('primary')

  useEffect(() => { document.title = 'Academics & Curriculum — Riverside Academy' }, [])

  const currentStage = CURRICULUM_STAGES.find((s) => s.id === activeStageId) || CURRICULUM_STAGES[0]

  return (
    <>
      <PageHero crumb="Academics" title="A curriculum built for real growth" detail="Structured, rigorous, and designed to meet every learner where they are." />

      <section className="bfa-section bfa-section-alt">
        <div className="bfa-container">
          <div className="bfa-section-head">
            <p className="bfa-eyebrow" style={{ color: 'var(--bfa-navy)' }}>ACADEMIC FRAMEWORK</p>
            <h2>Educational stages at Riverside</h2>
          </div>
          <div className="bfa-grid bfa-grid-3">
            {CURRICULUM_STAGES.map((stage) => (
              <div
                className="bfa-card"
                key={stage.id}
                style={{
                  cursor: 'pointer',
                  borderColor: stage.id === activeStageId ? 'var(--bfa-gold)' : 'var(--bfa-border)',
                  boxShadow: stage.id === activeStageId ? '0 10px 25px rgba(23, 58, 43, 0.08)' : 'none',
                }}
                onClick={() => setActiveStageId(stage.id)}
              >
                <span className="bfa-tag">{stage.grades}</span>
                <h3>{stage.name}</h3>
                <p>{stage.overview}</p>
                <button
                  className="bfa-btn bfa-btn-outline"
                  style={{ marginTop: 14, fontSize: 11, padding: '6px 12px' }}
                  onClick={(e) => { e.stopPropagation(); setActiveStageId(stage.id) }}
                >
                  {stage.id === activeStageId ? 'Active curriculum' : 'View curriculum →'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tabbed Curriculum by Stage */}
      <section className="bfa-section">
        <div className="bfa-container">
          <div className="bfa-section-head left">
            <p className="bfa-eyebrow" style={{ color: 'var(--bfa-navy)' }}>OUR CURRICULUM</p>
            <h2>{currentStage.name} Subjects & Pathways</h2>
            <p>{currentStage.overview}</p>
          </div>

          <div className="bfa-curriculum-tabs">
            {CURRICULUM_STAGES.map((stage) => (
              <button
                key={stage.id}
                className={stage.id === activeStageId ? 'bfa-tab-btn active' : 'bfa-tab-btn'}
                onClick={() => setActiveStageId(stage.id)}
              >
                {stage.name} ({stage.grades})
              </button>
            ))}
          </div>

          <div className="bfa-subject-grid">
            {currentStage.subjects.map((subject) => (
              <div className="bfa-subject-card" key={subject.name}>
                <span className="bfa-badge" style={{ marginBottom: 10 }}>{subject.code}</span>
                <h4>{subject.name}</h4>
                <p>{subject.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bfa-section bfa-section-alt">
        <div className="bfa-container bfa-grid bfa-grid-2">
          <div className="bfa-card">
            <span className="bfa-tag">ASSESSMENT METHODOLOGY</span>
            <h3 style={{ marginTop: 8 }}>Continuous Evaluation & Progress Tracking</h3>
            <p style={{ lineHeight: 1.7 }}>
              Students are evaluated through balanced formative coursework, interactive STEM/Arts projects, collaborative presentations, and end-of-term examinations. Termly report cards are securely published directly to the Student and Parent Portals.
            </p>
          </div>
          <div className="bfa-card">
            <span className="bfa-tag">COLLEGE & CAREER ADVISING</span>
            <h3 style={{ marginTop: 8 }}>Global University Placement</h3>
            <p style={{ lineHeight: 1.7 }}>
              Starting in Grade 9, students receive personalized guidance on course selection, standard testing preparations (SAT, IGCSE, WASSCE), university applications, and extracurricular leadership portfolios.
            </p>
          </div>
        </div>
      </section>

      <section className="bfa-section" style={{ textAlign: 'center' }}>
        <div className="bfa-container">
          <h2 style={{ color: 'var(--bfa-navy)' }}>Ready to begin your journey?</h2>
          <p style={{ color: 'var(--bfa-muted)', marginBottom: 24 }}>Explore admission requirements or submit an online application today.</p>
          <Link to="/admissions/apply" className="bfa-btn bfa-btn-gold">Apply for Admission →</Link>
        </div>
      </section>
    </>
  )
}

