import { useEffect, useState } from 'react'
import { api } from './api'
import AuthFlow from './AuthFlow'
import ActivateFlow from './ActivateFlow'
import AdmissionsAdmin from './AdmissionsAdmin'
import UserManagement from './UserManagement'
import ParentWorkspace from './ParentWorkspace'
import SchoolCrest from './public/components/SchoolCrest'
import './index.css'

const studentNav = [
  ['Overview', 'grid'],
  ['Profile', 'users'],
  ['Classes', 'book'],
  ['Assignments', 'file'],
  ['Grades', 'chart'],
  ['Attendance', 'check'],
  ['Exams', 'chart'],
  ['Timetable', 'book'],
  ['Payments', 'file'],
  ['Documents', 'file'],
  ['Messages', 'chat'],
]

const teacherNav = [
  ['Overview', 'grid'],
  ['My Classes', 'book'],
  ['Students', 'users'],
  ['Assignments', 'file'],
  ['Grades', 'chart'],
  ['Attendance', 'check'],
  ['Timetable', 'book'],
  ['Materials', 'book'],
  ['Messages', 'chat'],
]

const adminNav = [
  ['Overview', 'grid'],
  ['Students', 'users'],
  ['Teachers', 'users'],
  ['Parents', 'users'],
  ['Staff', 'users'],
  ['Classes', 'book'],
  ['Admissions', 'file'],
  ['Employment', 'file'],
  ['Attendance', 'check'],
  ['Grades', 'chart'],
  ['Fees', 'file'],
  ['Timetable', 'book'],
  ['Calendar', 'book'],
  ['News', 'bell'],
  ['Reports', 'chart'],
  ['Audit Logs', 'file'],
  ['Settings', 'grid'],
]

const parentNav = [
  ['Overview', 'grid'],
  ['Grades', 'chart'],
  ['Attendance', 'check'],
  ['Assignments', 'file'],
  ['Payments', 'file'],
  ['Documents', 'file'],
  ['Messages', 'chat'],
]

const icons = {
  grid: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z',
  users: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75',
  book: 'M4 19.5A2.5 2.5 0 0 1 6.5 17H20M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z',
  check: 'M20 6 9 17l-5-5',
  file: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M8 13h8M8 17h5',
  chat: 'M21 11.5a8.38 8.38 0 0 1-9 8.5 8.9 8.9 0 0 1-3.8-.9L3 21l1.9-4.1A8.3 8.3 0 0 1 3 11.5a8.5 8.5 0 0 1 9-8.5 8.5 8.5 0 0 1 9 8.5z',
  chart: 'M3 3v18h18M7 16v-5M12 16V7M17 16v-8',
  bell: 'M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4',
  search: 'm21 21-4.35-4.35M19 11a8 8 0 1 1-16 0',
  close: 'M6 6l12 12M18 6 6 18',
}

const demo = {
  classes: [],
  enrollments: [],
  attendance: [],
  assignments: [],
  submissions: [],
  announcements: [],
  conversations: [],
  reports: [],
  grades: [],
  subjects: [],
  students: [],
  children: [],
  documents: [],
  events: [],
  meetings: [],
  studentRecipients: [],
  fees: [],
}

function Icon({ name }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d={icons[name] || icons.grid} />
    </svg>
  )
}

function timeGreeting() {
  const hour = new Date().getHours()
  return hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'
}

function userName(profile) {
  return `${profile?.first_name || ''} ${profile?.last_name || ''}`.trim() || profile?.email || 'User'
}

function PageHeader({ eyebrow, title, detail, onBack }) {
  return (
    <div className="content-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="muted">{detail}</p>
      </div>
      {onBack && (
        <button className="secondary-button" onClick={onBack}>
          ← Overview
        </button>
      )}
    </div>
  )
}

function Stat({ icon, label, value, note, onClick }) {
  return (
    <button className="stat-card stat-action" onClick={onClick}>
      <div className={`stat-icon ${icon}`}>
        <Icon name={icon} />
      </div>
      <div className="stat-body">
        <p>{label}</p>
        <strong>{value}</strong>
        <small className="up">{note} →</small>
      </div>
    </button>
  )
}

function ActionRow({ title, detail, action, onClick }) {
  return (
    <div className="attention-item">
      <div className="attention-icon purple">•</div>
      <div>
        <b>{title}</b>
        <span>{detail}</span>
      </div>
      <button onClick={onClick}>{action} →</button>
    </div>
  )
}

function Schedule({ time, title, detail, status }) {
  return (
    <div className="schedule-row">
      <time>{time}</time>
      <div className="schedule-line">
        <b>{title}</b>
        <span>{detail}</span>
      </div>
      <strong className="status upcoming">{status}</strong>
    </div>
  )
}

function Empty({ title, detail }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <span>{detail}</span>
    </div>
  )
}

function App() {
  const [loggedIn, setLoggedIn] = useState(api.isAuthenticated())
  const [role, setRole] = useState('student')
  const [profile, setProfile] = useState(null)
  const [data, setData] = useState(demo)
  const [active, setActive] = useState('Overview')
  const [error, setError] = useState('')
  const [authMode] = useState('login')
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  useEffect(() => {
    if (!loggedIn) return
    api
      .dashboard()
      .then((dashboard) => {
        setProfile(dashboard.profile)
        setRole(dashboard.profile?.role || 'student')
        setData({ ...demo, ...dashboard })
      })
      .catch((requestError) => setError(requestError.message))
  }, [loggedIn])

  useEffect(() => {
    if (loggedIn) document.title = `${timeGreeting()}, ${userName(profile)} · Riverside Academy`
  }, [loggedIn, profile])

  if (!loggedIn) {
    const params = new URLSearchParams(window.location.search)
    const token = params.get('activate_token')
    
    if (token) {
      return (
        <ActivateFlow 
          token={token} 
          onActivated={() => {
            window.location.href = '/portal'
          }} 
        />
      )
    }

    return (
      <AuthFlow
        initialMode={authMode}
        onAuthenticated={(session) => {
          setRole(session.role || 'student')
          setLoggedIn(true)
        }}
      />
    )
  }

  const isStudent = role === 'student'
  const isTeacher = role === 'teacher'
  const isParent = role === 'parent'
  const isAdmin = role === 'admin'

  const nav = isStudent ? studentNav : isTeacher ? teacherNav : isParent ? parentNav : adminNav
  const initials = userName(profile)
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()

  return (
    <div className="app-shell">
      <AIChatbotWidget />
      <aside className={mobileNavOpen ? 'sidebar mobile-open' : 'sidebar'}>
        <div className="brand">
          <SchoolCrest size={28} variant="gold" />
          <span>Riverside Academy</span>
          <button className="mobile-close" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)}>
            <Icon name="close" />
          </button>
        </div>
        <div className="school-switcher">
          <span className="school-dot" />
          <span>Riverside Academy</span>
          <b>⌄</b>
        </div>
        <p className="nav-label">{role.toUpperCase()} WORKSPACE</p>
        <nav>
          {nav.map(([label, icon]) => (
            <button
              key={label}
              className={active === label ? 'nav-item active' : 'nav-item'}
              onClick={() => {
                setActive(label)
                setMobileNavOpen(false)
              }}
            >
              <Icon name={icon} />
              <span>{label}</span>
              {label === 'Messages' && <em>{(data.conversations || []).length || 0}</em>}
            </button>
          ))}
        </nav>
        <div className="sidebar-user">
          <div className="avatar">{initials}</div>
          <div>
            <strong>{userName(profile)}</strong>
            <small>{role}</small>
          </div>
          <button
            aria-label="Sign out"
            onClick={() => {
              api.logout()
              setLoggedIn(false)
            }}
          >
            ↗
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button className="mobile-menu" aria-label="Open navigation" onClick={() => setMobileNavOpen(true)}>
            ☰
          </button>
          <div className="breadcrumbs">
            <span>Workspace</span>
            <b>/</b>
            <strong>{active}</strong>
          </div>
          <div className="top-actions">
            <label className="search">
              <Icon name="search" />
              <input
                placeholder="Search records, students, classes..."
                aria-label="Search anything"
                onChange={(event) => {
                  if (event.target.value.trim()) setActive(isAdmin ? 'Students' : isStudent ? 'Assignments' : 'Students')
                }}
              />
            </label>
            <button className="icon-button" aria-label="Notifications" onClick={() => setActive('Notices')}>
              <Icon name="bell" />
            </button>
            <div className="top-avatar">{initials}</div>
          </div>
        </header>

        <div className="content">
          {isParent ? (
            <ParentWorkspace active={active} setActive={setActive} profile={profile} data={data} />
          ) : isStudent ? (
            <StudentPortal active={active} setActive={setActive} profile={profile} data={data} />
          ) : (
            <StaffWorkspace active={active} setActive={setActive} profile={profile} data={data} role={role} error={error} />
          )}
        </div>
      </main>
    </div>
  )
}

function StudentPortal({ active, setActive, profile, data }) {
  const name = userName(profile)
  const firstName = profile?.first_name || name.split(' ')[0]
  const go = (page) => setActive(page)

  if (active === 'Classes' || active === 'Academics') return <AcademicsPage data={data} onBack={() => go('Overview')} />
  if (active === 'Attendance') return <AttendancePage data={data} onBack={() => go('Overview')} />
  if (active === 'Assignments') return <AssignmentWorkflow data={data} onBack={() => go('Overview')} />
  if (active === 'Grades' || active === 'Exams') return <StudentGradesPage data={data} onBack={() => go('Overview')} />
  if (active === 'Messages') return <MessagesPage data={data} onBack={() => go('Overview')} />
  if (active === 'Reports') return <ReportsPage data={data} onBack={() => go('Overview')} />
  if (active !== 'Overview') return <ModulePage module={active} data={data} onBack={() => go('Overview')} />

  return <StudentHome firstName={firstName} data={data} go={go} />
}

function StudentHome({ firstName, data, go }) {
  const upcoming = data.assignments.slice(0, 3)
  return (
    <>
      <PageHeader
        eyebrow="STUDENT PORTAL"
        title={`${timeGreeting()}, ${firstName}`}
        detail="Your personal school dashboard, updated from your enrolled classes."
      />
      <div className="stats-grid">
        <Stat icon="book" label="Current classes" value={data.enrollments.length || '—'} note="View classes" onClick={() => go('Classes')} />
        <Stat
          icon="check"
          label="Attendance"
          value={
            data.attendance.length
              ? `${Math.round(
                  (data.attendance.filter((item) => ['present', 'late'].includes(item.status)).length /
                    data.attendance.length) *
                    100
                )}%`
              : '—'
          }
          note="View attendance"
          onClick={() => go('Attendance')}
        />
        <Stat icon="file" label="Assignments due" value={upcoming.length} note="View assignments" onClick={() => go('Assignments')} />
        <Stat icon="chart" label="Reports" value={data.reports.length} note="View reports" onClick={() => go('Reports')} />
      </div>
      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Today’s schedule</h2>
              <p className="panel-subtitle">Your enrolled timetable</p>
            </div>
            <button className="text-button" onClick={() => go('Classes')}>
              View timetable →
            </button>
          </div>
          {data.enrollments.length ? (
            data.enrollments.map((enrollment) => (
              <Schedule
                key={enrollment.id}
                time="Today"
                title={`Class #${enrollment.school_class}`}
                detail={`Academic year ${enrollment.academic_year}`}
                status="Enrolled"
              />
            ))
          ) : (
            <Empty title="No timetable yet" detail="Your classes will appear here once you are enrolled." />
          )}
        </section>
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Upcoming work</h2>
              <p className="panel-subtitle">Assignments from your classes</p>
            </div>
            <button className="text-button" onClick={() => go('Assignments')}>
              View all →
            </button>
          </div>
          {upcoming.length ? (
            upcoming.map((assignment) => (
              <ActionRow
                key={assignment.id}
                title={assignment.title}
                detail={`Due ${assignment.due_date}`}
                action="Open"
                onClick={() => go('Assignments')}
              />
            ))
          ) : (
            <Empty title="No upcoming work" detail="You are all caught up." />
          )}
        </section>
      </div>
    </>
  )
}

function StudentGradesPage({ data, onBack }) {
  return (
    <>
      <PageHeader eyebrow="ACADEMIC RESULTS" title="My grades & results" detail="Published examination scores and letter grades." onBack={onBack} />
      <section className="panel page-panel">
        <div className="panel-heading">
          <div>
            <h2>Recorded results</h2>
            <p className="panel-subtitle">Only published grades are displayed</p>
          </div>
        </div>
        {data.grades.length ? (
          data.grades.map((grade) => (
            <ActionRow
              key={grade.id}
              title={grade.subject_name ? `${grade.subject_name}: ${grade.score}` : `Score: ${grade.score}`}
              detail={`Grade ${grade.letter_grade || 'pending'}`}
              action="Details"
              onClick={() => window.print()}
            />
          ))
        ) : (
          <Empty title="No published grades yet" detail="Grades will appear after your teachers publish them." />
        )}
      </section>
    </>
  )
}

function AssignmentWorkflow({ data, onBack }) {
  const [selected, setSelected] = useState(null)
  const [content, setContent] = useState('')
  const [saving, setSaving] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    try {
      await api.createSubmission({ assignment: selected.id, content, status: 'submitted' })
      setSelected(null)
      setContent('')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader eyebrow="ASSIGNMENTS" title="My assignments" detail="Open work, submit responses, and track your progress." onBack={onBack} />
      {selected ? (
        <section className="panel">
          <button className="text-button" onClick={() => setSelected(null)}>
            ← All assignments
          </button>
          <h2>{selected.title}</h2>
          <p className="muted">Due {selected.due_date}</p>
          <p className="assignment-detail">{selected.description || 'Your teacher has not added instructions yet.'}</p>
          <form onSubmit={submit}>
            <label className="workflow-label">
              Your response
              <textarea required value={content} onChange={(event) => setContent(event.target.value)} placeholder="Write your response..." />
            </label>
            <button className="primary-button" disabled={saving}>
              {saving ? 'Submitting…' : 'Submit assignment'} <span>✓</span>
            </button>
          </form>
        </section>
      ) : (
        <section className="panel">
          {data.assignments.length ? (
            data.assignments.map((item) => (
              <ActionRow key={item.id} title={item.title} detail={`Due ${item.due_date}`} action="Open" onClick={() => setSelected(item)} />
            ))
          ) : (
            <Empty title="No assignments" detail="New work from your enrolled classes will appear here." />
          )}
        </section>
      )}
    </>
  )
}

function AttendancePage({ data, onBack }) {
  return (
    <>
      <PageHeader eyebrow="ATTENDANCE" title="My attendance" detail="A private record of your attendance history." onBack={onBack} />
      <section className="panel">
        <div className="student-summary">
          <div>
            <span>Records</span>
            <strong>{data.attendance.length}</strong>
            <small>Personal history</small>
          </div>
          <div>
            <span>Present</span>
            <strong>{data.attendance.filter((item) => item.status === 'present').length}</strong>
            <small className="green-text">On time</small>
          </div>
          <div>
            <span>Late</span>
            <strong>{data.attendance.filter((item) => item.status === 'late').length}</strong>
            <small>Needs attention</small>
          </div>
          <div>
            <span>Absent</span>
            <strong>{data.attendance.filter((item) => item.status === 'absent').length}</strong>
            <small>Review with school</small>
          </div>
        </div>
        {data.attendance.length ? (
          data.attendance.map((item) => (
            <ActionRow key={item.id} title={item.date} detail={item.notes || 'Attendance record'} action={item.status} onClick={() => window.print()} />
          ))
        ) : (
          <Empty title="No attendance records" detail="Your attendance will appear here." />
        )}
      </section>
    </>
  )
}

function AcademicsPage({ data, onBack }) {
  return (
    <>
      <PageHeader eyebrow="ACADEMICS" title="My academics" detail="Your enrolled classes and grades." onBack={onBack} />
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Enrolled classes</h2>
            <p className="panel-subtitle">Only classes linked to your student account</p>
          </div>
        </div>
        {data.enrollments.length ? (
          data.enrollments.map((item) => (
            <ActionRow
              key={item.id}
              title={item.class_name || `Class #${item.school_class}`}
              detail={`Academic year ${item.academic_year}`}
              action="View grades"
              onClick={() => window.print()}
            />
          ))
        ) : (
          <Empty title="No classes found" detail="Ask your administrator to enroll you in a class." />
        )}
      </section>
      <section className="panel page-panel">
        <div className="panel-heading">
          <div>
            <h2>Grades</h2>
            <p className="panel-subtitle">Your recorded results</p>
          </div>
        </div>
        {data.grades.length ? (
          data.grades.map((grade) => (
            <ActionRow
              key={grade.id}
              title={grade.subject_name ? `${grade.subject_name}: ${grade.score}` : `Score: ${grade.score}`}
              detail={`Grade ${grade.letter_grade || 'pending'}`}
              action="Details"
              onClick={() => window.print()}
            />
          ))
        ) : (
          <Empty title="No grades yet" detail="Grades will appear after your teachers publish them." />
        )}
      </section>
    </>
  )
}

function StaffWorkspace({ active, setActive, _profile, data, role, error }) {
  if (role === 'admin' && active === 'Admissions') return <AdmissionsAdmin onBack={() => setActive('Overview')} />
  if (role === 'admin' && ['Students', 'Teachers', 'Parents', 'Staff'].includes(active)) return <UserManagement roleFilter={active} onBack={() => setActive('Overview')} />

  if (active === 'Students') return <StudentManagement data={data} onBack={() => setActive('Overview')} />
  if (active === 'Classes' || active === 'My Classes' || active === 'Academics') {
    return <StaffAcademics data={data} role={role} onBack={() => setActive('Overview')} />
  }
  if (active === 'Attendance') return <AttendanceMarking data={data} onBack={() => setActive('Overview')} />
  if (active === 'Assignments') return <StaffAssignments data={data} onBack={() => setActive('Overview')} />
  if (active === 'Grades') return <StudentGradesPage data={data} onBack={() => setActive('Overview')} />
  if (active === 'Messages') return <MessagesPage data={data} onBack={() => setActive('Overview')} canCompose={role === 'teacher'} />
  if (active === 'Notices' || active === 'News') return <AnnouncementManager data={data} onBack={() => setActive('Overview')} />
  if (active === 'Fees' || active === 'Payments') return <FeePage data={data} role={role} onBack={() => setActive('Overview')} />
  if (active === 'Reports') return <StaffReports data={data} setActive={setActive} onBack={() => setActive('Overview')} />
  if (active !== 'Overview') return <ModulePage module={active} data={data} onBack={() => setActive('Overview')} />
  return <StaffHome role={role} data={data} error={error} go={setActive} />
}

function StaffHome({ role, data, error, go }) {
  const attendance = data.attendance.filter((item) => item.status === 'present').length
  return (
    <>
      <PageHeader
        eyebrow={`${role.toUpperCase()} WORKSPACE`}
        title={`${timeGreeting()}, ${role}`}
        detail={error || 'A secure operational view of the school day, ready for your next action.'}
      />
      <div className="stats-grid">
        <Stat icon="users" label="Students" value={data.students.length || '—'} note="Open directory" onClick={() => go('Students')} />
        <Stat icon="book" label="Classes" value={data.classes.length || '—'} note="View academics" onClick={() => go('Classes')} />
        <Stat
          icon="check"
          label="Attendance"
          value={data.attendance.length ? `${Math.round((attendance / data.attendance.length) * 100)}%` : '—'}
          note="Review register"
          onClick={() => go('Attendance')}
        />
        <Stat icon="chart" label="Reports" value={data.reports.length || '—'} note="Open reporting" onClick={() => go('Reports')} />
      </div>
      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Today at Riverside</h2>
              <p className="panel-subtitle">The operational pulse of your school</p>
            </div>
            <button className="text-button" onClick={() => go('Attendance')}>
              Open register →
            </button>
          </div>
          <Empty title="Your workspace is ready" detail="Use the navigation to manage students, learning, attendance, and reports." />
        </section>
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Quick actions</h2>
              <p className="panel-subtitle">Common tasks for {role}s</p>
            </div>
          </div>
          <ActionRow title="Student directory" detail="Search and update student records" action="Open" onClick={() => go('Students')} />
          <ActionRow title="Assignments" detail="Review work and submissions" action="Open" onClick={() => go('Assignments')} />
        </section>
      </div>
    </>
  )
}

function StudentManagement({ data, onBack }) {
  const [query, setQuery] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [students, setStudents] = useState(data.students)

  const filtered = students.filter((student) =>
    `${student.full_name || ''} ${student.admission_number || ''}`.toLowerCase().includes(query.toLowerCase())
  )

  const remove = async (student) => {
    if (!window.confirm(`Remove ${student.full_name || 'this student'}?`)) return
    await api.deleteStudent(student.id)
    setStudents(students.filter((item) => item.id !== student.id))
  }

  return (
    <>
      <PageHeader eyebrow="STUDENT MANAGEMENT" title="Student directory" detail="Keep enrolment records accurate and easy for staff to scan." onBack={onBack} />
      <section className="panel directory-panel">
        <div className="directory-toolbar">
          <label className="directory-search">
            <Icon name="search" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search students or admission number"
              aria-label="Search students"
            />
          </label>
          <button className="primary-button" onClick={() => setShowForm(true)}>
            Add student <span>+</span>
          </button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>Admission no.</th>
                <th>Email</th>
                <th>Date of birth</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((student) => (
                <tr key={student.id}>
                  <td>
                    <div className="student-cell">
                      <div className="student-avatar">{(student.full_name || 'S').slice(0, 1)}</div>
                      <div>
                        <strong>{student.full_name || 'Unnamed student'}</strong>
                        <span>Student profile</span>
                      </div>
                    </div>
                  </td>
                  <td>{student.admission_number || '—'}</td>
                  <td>{student.email || '—'}</td>
                  <td>{student.dob || '—'}</td>
                  <td>
                    <button className="row-menu" onClick={() => remove(student)} aria-label={`Remove ${student.full_name || 'student'}`}>
                      ×
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!filtered.length && (
            <Empty title="No students found" detail={query ? 'Try a different search.' : 'Student records will appear here.'} />
          )}
        </div>
      </section>
      {showForm && (
        <StudentForm onClose={() => setShowForm(false)} onCreated={(student) => setStudents([...students, student])} />
      )}
    </>
  )
}

function StudentForm({ onClose, onCreated }) {
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', admission_number: '', dob: '' })
  const [saving, setSaving] = useState(false)
  const [created, setCreated] = useState(null)

  const update = (field, value) => setForm({ ...form, [field]: value })

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    try {
      const student = await api.createStudent(form)
      onCreated(student)
      if (student.temporary_password) setCreated(student)
      else onClose()
    } finally {
      setSaving(false)
    }
  }

  if (created) {
    return (
      <div className="modal-backdrop">
        <section className="modal">
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <Icon name="close" />
          </button>
          <p className="eyebrow">ACCOUNT CREATED</p>
          <h2>{created.full_name}'s account is ready</h2>
          <p className="muted">Share this temporary password with the student — it will not be shown again. They should change it after logging in.</p>
          <div className="temp-password-box">
            <code>{created.temporary_password}</code>
          </div>
          <div className="modal-actions">
            <button className="primary-button" onClick={onClose}>
              Done <span>→</span>
            </button>
          </div>
        </section>
      </div>
    )
  }

  return (
    <div className="modal-backdrop">
      <section className="modal">
        <button className="modal-close" onClick={onClose} aria-label="Close">
          <Icon name="close" />
        </button>
        <p className="eyebrow">NEW RECORD</p>
        <h2>Add student</h2>
        <p className="muted">Create a student profile for the school directory.</p>
        <form onSubmit={submit}>
          <div className="form-row">
            <label>
              First name
              <input required value={form.first_name} onChange={(event) => update('first_name', event.target.value)} />
            </label>
            <label>
              Last name
              <input required value={form.last_name} onChange={(event) => update('last_name', event.target.value)} />
            </label>
          </div>
          <label>
            Email
            <input required type="email" value={form.email} onChange={(event) => update('email', event.target.value)} />
          </label>
          <div className="form-row">
            <label>
              Admission number
              <input required value={form.admission_number} onChange={(event) => update('admission_number', event.target.value)} />
            </label>
            <label>
              Date of birth
              <input required type="date" value={form.dob} onChange={(event) => update('dob', event.target.value)} />
            </label>
          </div>
          <div className="modal-actions">
            <button type="button" className="secondary-button" onClick={onClose}>
              Cancel
            </button>
            <button className="primary-button" disabled={saving}>
              {saving ? 'Creating…' : 'Create student'} <span>→</span>
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}

function StaffAcademics({ data, role, onBack }) {
  return (
    <>
      <PageHeader
        eyebrow="ACADEMICS"
        title={role === 'teacher' ? 'My teaching workspace' : 'Academic overview'}
        detail="Classes, subjects, and curriculum results in one focused view."
        onBack={onBack}
      />
      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Classes</h2>
              <p className="panel-subtitle">Current academic year</p>
            </div>
          </div>
          {data.classes.length ? (
            data.classes.map((item) => (
              <ActionRow key={item.id} title={item.name} detail={`${item.code} · ${item.academic_year}`} action="Open" onClick={() => window.print()} />
            ))
          ) : (
            <Empty title="No classes yet" detail="Classes will appear when the academic setup is complete." />
          )}
        </section>
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Subjects</h2>
              <p className="panel-subtitle">Available curriculum areas</p>
            </div>
          </div>
          {data.subjects.length ? (
            data.subjects.map((item) => (
              <ActionRow key={item.id} title={item.name} detail={item.code} action="View" onClick={() => window.print()} />
            ))
          ) : (
            <Empty title="No subjects yet" detail="Add subjects to start planning lessons." />
          )}
        </section>
      </div>
    </>
  )
}

function AttendanceMarking({ data, onBack }) {
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [statuses, setStatuses] = useState({})
  const [saving, setSaving] = useState(false)

  const update = (id, status) => setStatuses({ ...statuses, [id]: status })

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    try {
      await api.bulkMarkAttendance(
        data.students.map((student) => ({
          student: student.id,
          date,
          status: statuses[student.id] || 'present',
        }))
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader eyebrow="ATTENDANCE" title="Mark attendance" detail="Capture the class register in one action." onBack={onBack} />
      <section className="panel">
        <form onSubmit={submit}>
          <label className="workflow-label">
            Date
            <input type="date" value={date} onChange={(event) => setDate(event.target.value)} />
          </label>
          <div className="attendance-list">
            {data.students.length ? (
              data.students.map((student) => (
                <div className="attendance-row" key={student.id}>
                  <strong>{student.full_name}</strong>
                  <select value={statuses[student.id] || 'present'} onChange={(event) => update(student.id, event.target.value)}>
                    <option value="present">Present</option>
                    <option value="late">Late</option>
                    <option value="absent">Absent</option>
                    <option value="excused">Excused</option>
                  </select>
                </div>
              ))
            ) : (
              <Empty title="No assigned students" detail="Students assigned to your classes will appear here." />
            )}
          </div>
          <button className="primary-button" disabled={saving || !data.students.length}>
            {saving ? 'Saving…' : 'Save attendance'} <span>✓</span>
          </button>
        </form>
      </section>
    </>
  )
}

function StaffAssignments({ data, onBack }) {
  const [showForm, setShowForm] = useState(false)
  const [assignments, setAssignments] = useState(data.assignments)

  return (
    <>
      <PageHeader
        eyebrow="ASSIGNMENTS"
        title="Assignment tracker"
        detail="Create work from the subjects you teach and track student progress."
        onBack={onBack}
      />
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Assignments</h2>
            <p className="panel-subtitle">Subject-specific work for enrolled classes</p>
          </div>
          <button className="primary-button" onClick={() => setShowForm(true)}>
            Create assignment <span>+</span>
          </button>
        </div>
        {assignments.length ? (
          assignments.map((item) => (
            <ActionRow
              key={item.id}
              title={item.title}
              detail={`${item.subject_name || `Subject #${item.subject}`} · Due ${item.due_date}`}
              action="Review"
              onClick={() => window.print()}
            />
          ))
        ) : (
          <Empty title="No assignments yet" detail="Create an assignment from your academic workflow." />
        )}
      </section>
      {showForm && (
        <AssignmentForm
          data={data}
          onClose={() => setShowForm(false)}
          onCreated={(assignment) => {
            setAssignments([assignment, ...assignments])
            setShowForm(false)
          }}
        />
      )}
    </>
  )
}

function AssignmentForm({ data, onClose, onCreated }) {
  const [form, setForm] = useState({
    title: '',
    description: '',
    subject: data.subjects[0]?.id || '',
    school_class: data.classes[0]?.id || '',
    due_date: '',
  })
  const [saving, setSaving] = useState(false)

  const update = (field, value) => setForm({ ...form, [field]: value })

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    try {
      onCreated(
        await api.createAssignment({
          ...form,
          subject: Number(form.subject),
          school_class: Number(form.school_class),
        })
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop">
      <section className="modal">
        <button className="modal-close" onClick={onClose} aria-label="Close">
          <Icon name="close" />
        </button>
        <p className="eyebrow">TEACHING WORKFLOW</p>
        <h2>Create assignment</h2>
        <p className="muted">Students in the selected class will see this work in their assignment list.</p>
        <form onSubmit={submit}>
          <label>
            Title
            <input required value={form.title} onChange={(event) => update('title', event.target.value)} />
          </label>
          <label>
            Subject
            <select required value={form.subject} onChange={(event) => update('subject', event.target.value)}>
              {data.subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.name} ({subject.code})
                </option>
              ))}
            </select>
          </label>
          <label>
            Class
            <select required value={form.school_class} onChange={(event) => update('school_class', event.target.value)}>
              {data.classes.map((schoolClass) => (
                <option key={schoolClass.id} value={schoolClass.id}>
                  {schoolClass.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Due date
            <input required type="date" value={form.due_date} onChange={(event) => update('due_date', event.target.value)} />
          </label>
          <label>
            Instructions
            <textarea value={form.description} onChange={(event) => update('description', event.target.value)} />
          </label>
          <div className="modal-actions">
            <button type="button" className="secondary-button" onClick={onClose}>
              Cancel
            </button>
            <button className="primary-button" disabled={saving}>
              {saving ? 'Publishing…' : 'Publish assignment'} <span>→</span>
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}

function AnnouncementManager({ data, onBack }) {
  const [form, setForm] = useState({ title: '', content: '' })
  const [saving, setSaving] = useState(false)

  const update = (field, value) => setForm({ ...form, [field]: value })

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    try {
      await api.createAnnouncement(form)
      setForm({ title: '', content: '' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader eyebrow="NOTICE BOARD" title="Announcements" detail="Publish updates for your school community." onBack={onBack} />
      <section className="panel">
        <form onSubmit={submit} className="workflow-form">
          <label className="workflow-label">
            Title
            <input required value={form.title} onChange={(event) => update('title', event.target.value)} />
          </label>
          <label className="workflow-label">
            Message
            <textarea required value={form.content} onChange={(event) => update('content', event.target.value)} />
          </label>
          <button className="primary-button" disabled={saving}>
            {saving ? 'Publishing…' : 'Publish notice'} <span>→</span>
          </button>
        </form>
      </section>
      <section className="panel page-panel">
        {data.announcements.length ? (
          data.announcements.map((item) => (
            <ActionRow key={item.id} title={item.title} detail={item.content} action="Published" onClick={() => window.print()} />
          ))
        ) : (
          <Empty title="No notices yet" detail="Published announcements will appear here." />
        )}
      </section>
    </>
  )
}

function FeePage({ data, role, onBack }) {
  const [form, setForm] = useState({ student: data.students[0]?.id || '', title: '', amount: '', due_date: '' })
  const [fees, setFees] = useState(data.fees || [])
  const [saving, setSaving] = useState(false)

  const update = (field, value) => setForm({ ...form, [field]: value })

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    try {
      const fee = await api.createFee({ ...form, student: Number(form.student), amount: Number(form.amount) })
      setFees([fee, ...fees])
      setForm({ ...form, title: '', amount: '', due_date: '' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader eyebrow="FEES & INVOICES" title="Fee records" detail="Track invoices, due dates, and payment statuses." onBack={onBack} />
      {role === 'admin' && (
        <section className="panel">
          <form className="workflow-form" onSubmit={submit}>
            <div className="form-row">
              <label className="workflow-label">
                Student
                <select required value={form.student} onChange={(event) => update('student', event.target.value)}>
                  {data.students.map((student) => (
                    <option key={student.id} value={student.id}>
                      {student.full_name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="workflow-label">
                Title
                <input required value={form.title} onChange={(event) => update('title', event.target.value)} />
              </label>
            </div>
            <div className="form-row">
              <label className="workflow-label">
                Amount
                <input required type="number" min="0" step="0.01" value={form.amount} onChange={(event) => update('amount', event.target.value)} />
              </label>
              <label className="workflow-label">
                Due date
                <input required type="date" value={form.due_date} onChange={(event) => update('due_date', event.target.value)} />
              </label>
            </div>
            <button className="primary-button" disabled={saving || !data.students.length}>
              {saving ? 'Creating…' : 'Create invoice'} <span>+</span>
            </button>
          </form>
        </section>
      )}
      <section className="panel page-panel">
        {fees.length ? (
          fees.map((fee) => (
            <ActionRow
              key={fee.id}
              title={fee.title}
              detail={`${fee.student_name || 'Student'} · $${fee.amount} · Due ${fee.due_date}`}
              action={fee.status}
              onClick={() => window.print()}
            />
          ))
        ) : (
          <Empty title="No fee records" detail="Fee invoices will appear here when issued by the finance department." />
        )}
      </section>
    </>
  )
}

function StaffReports({ data, setActive, onBack }) {
  return (
    <>
      <PageHeader eyebrow="REPORTING" title="School reporting" detail="A clear overview of academic progress, attendance, and published report cards." onBack={onBack} />
      <div className="stats-grid">
        <Stat icon="chart" label="Published reports" value={data.reports.length || '—'} note="Review archive" onClick={() => window.print()} />
        <Stat icon="check" label="Attendance records" value={data.attendance.length || '—'} note="View register" onClick={() => setActive('Attendance')} />
        <Stat icon="file" label="Submissions" value={data.submissions.length || '—'} note="Review work" onClick={() => setActive('Assignments')} />
        <Stat icon="users" label="Students" value={data.students.length || '—'} note="Open directory" onClick={() => setActive('Students')} />
      </div>
      <section className="panel">
        {data.reports.length ? (
          data.reports.map((report) => (
            <ActionRow key={report.id} title={report.title} detail={report.report_type} action="Open" onClick={() => window.print()} />
          ))
        ) : (
          <Empty title="No reports published" detail="Academic report cards will appear here once generated." />
        )}
      </section>
    </>
  )
}

function MessagesPage({ data, onBack, canCompose = false }) {
  const [selected, setSelected] = useState(null)
  const [recipient, setRecipient] = useState(null)
  const conversations = data.conversations || []
  const closeComposer = () => setRecipient(null)

  return (
    <>
      <PageHeader eyebrow="MESSAGES" title="My messages" detail="Private communication for your account." onBack={onBack} />
      {canCompose && (
        <div className="message-toolbar">
          <button className="primary-button" onClick={() => setRecipient({})}>
            New message <span>+</span>
          </button>
        </div>
      )}
      <section className="panel">
        {selected ? (
          <>
            <button className="text-button" onClick={() => setSelected(null)}>
              ← Inbox
            </button>
            <h2>{selected.subject || 'Message'}</h2>
            <p className="muted">
              From {selected.sender_name} · To {selected.recipient_name}
            </p>
            <p className="assignment-detail">{selected.body}</p>
            <div className="message-actions">
              <button className="primary-button" onClick={() => setRecipient({ id: selected.sender, name: selected.sender_name })}>
                Reply <span>→</span>
              </button>
              {selected.is_read === false && (
                <button
                  className="secondary-button"
                  onClick={() => {
                    api.markMessageRead?.(selected.id)
                    setSelected(null)
                  }}
                >
                  Mark as read
                </button>
              )}
            </div>
          </>
        ) : conversations.length ? (
          conversations.map((message) => (
            <ActionRow
              key={message.id}
              title={message.subject || 'Message'}
              detail={`${message.sender_name} · ${message.body.slice(0, 70)}`}
              action="Open"
              onClick={() => setSelected(message)}
            />
          ))
        ) : (
          <Empty title="No messages" detail="Your conversations will appear here." />
        )}
      </section>
      {recipient && <MessageComposer data={data} recipient={recipient} onClose={closeComposer} />}
    </>
  )
}

function MessageComposer({ data, recipient, onClose }) {
  const [target, setTarget] = useState(recipient.id || '')
  const [body, setBody] = useState('')
  const [saving, setSaving] = useState(false)
  const recipients = (data.studentRecipients || []).map((student) => ({
    id: student.user_id,
    name: student.full_name,
    detail: student.admission_number,
  }))

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    try {
      if (recipient.id) {
        await api.replyToConversation(recipient.id, body)
      } else {
        await api.createConversation({ title: 'New Conversation', initial_message: body, target: target })
      }
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop">
      <section className="modal">
        <button className="modal-close" onClick={onClose} aria-label="Close">
          <Icon name="close" />
        </button>
        <p className="eyebrow">DIRECT MESSAGE</p>
        <h2>{recipient.name ? `Reply to ${recipient.name}` : 'New message'}</h2>
        <p className="muted">Direct messages are logged and accessible within your workspace.</p>
        <form onSubmit={submit}>
          {!recipient.id && (
            <label>
              Recipient
              <select required value={target} onChange={(event) => setTarget(event.target.value)}>
                <option value="">Select a recipient</option>
                {recipients.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name} · {item.detail}
                  </option>
                ))}
              </select>
            </label>
          )}
          <label>
            Message
            <textarea required value={body} onChange={(event) => setBody(event.target.value)} placeholder="Write your message..." />
          </label>
          <div className="modal-actions">
            <button type="button" className="secondary-button" onClick={onClose}>
              Cancel
            </button>
            <button className="primary-button" disabled={saving}>
              {saving ? 'Sending…' : 'Send message'} <span>→</span>
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}

function ReportsPage({ data, onBack }) {
  return (
    <>
      <PageHeader eyebrow="REPORTS" title="My reports" detail="Reports that belong to your student account only." onBack={onBack} />
      <section className="panel">
        {data.reports.length ? (
          data.reports.map((report) => (
            <ActionRow key={report.id} title={report.title} detail={report.report_type} action="Open" onClick={() => window.print()} />
          ))
        ) : (
          <Empty title="No reports yet" detail="Your academic reports will appear here." />
        )}
      </section>
    </>
  )
}

function ModulePage({ module, data, onBack }) {
  const source =
    module === 'Notices' || module === 'News'
      ? data.announcements
      : module === 'Exams & Grades' || module === 'Grades'
      ? data.grades
      : module === 'Timetable' || module === 'Classes' || module === 'My Classes'
      ? data.classes
      : module === 'Students'
      ? data.students
      : module === 'Fees' || module === 'Payments'
      ? data.fees
      : module === 'Documents' ? data.documents : module === 'Calendar' ? data.events : []

  const labels = {
    'Exams & Grades': 'Published results and assessment records.',
    Grades: 'Published marks and academic grading.',
    Timetable: 'Classes and upcoming academic schedule.',
    Notices: 'Announcements relevant to your school community.',
    News: 'Published school updates and news articles.',
    Fees: 'Invoices, balances, and payment records.',
    Payments: 'Fee payments, receipts, and installment schedules.',
    Documents: 'Uploaded certificates, records, and school forms.',
    Profile: 'Personal details, contact information, and enrollment status.',
    Calendar: 'Academic year milestones, term dates, and school events.',
    Library: 'Borrowed books, catalog, and due dates.',
    Teachers: 'Teacher directory and teaching assignments.',
    Parents: 'Parent directory and verified child links.',
    Staff: 'School administrative and support staff directory.',
    Admissions: 'Review queue of submitted admission applications.',
    Employment: 'Review queue of job applicants and employment offers.',
    'Audit Logs': 'System security, sensitive mutations, and permission logs.',
    Settings: 'School configuration, roles, and administrative preferences.',
    Students: 'Student directory and enrollment records.',
    Materials: 'Subject syllabi, lesson plans, and classroom learning resources.',
  }

  return (
    <>
      <PageHeader eyebrow={module.toUpperCase()} title={module} detail={labels[module] || 'A focused view of this school workspace.'} onBack={onBack} />
      <section className="panel module-panel">
        <div className="panel-heading">
          <div>
            <h2>{module} overview</h2>
            <p className="panel-subtitle">Operational records from your account</p>
          </div>
          <button className="secondary-button" onClick={() => window.print()}>
            Print view
          </button>
        </div>
        {source.length ? (
          source.map((item, index) => (
            <ActionRow
              key={item.id || index}
              title={item.title || item.name || item.full_name || `${module} record ${index + 1}`}
              detail={item.description || item.date || item.code || item.report_type || item.email || 'Available in your workspace'}
              action="View"
              onClick={() => window.print()}
            />
          ))
        ) : (
          <Empty title={`No ${module.toLowerCase()} yet`} detail="This operational area is ready and will display connected school records." />
        )}
      </section>
    </>
  )
}


function AIChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState([{ sender: 'ai', text: 'Hi! I am your AI Assistant. How can I help you today?' }])
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (!prompt.trim()) return
    
    const userMessage = { sender: 'user', text: prompt }
    setMessages((prev) => [...prev, userMessage])
    setPrompt('')
    setLoading(true)
    
    try {
      const data = await api.aiChatbot(userMessage.text)
      setMessages((prev) => [...prev, { sender: 'ai', text: data.response }])
    } catch {
      setMessages((prev) => [...prev, { sender: 'ai', text: 'Error connecting to the assistant.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button 
        className="primary-button" 
        style={{ position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 9999, borderRadius: '50px', padding: '1rem' }}
        onClick={() => setIsOpen(true)}
        aria-label="Open AI Assistant"
      >
        <Icon name="messages" /> Ask AI
      </button>

      {isOpen && (
        <div className="modal-backdrop" style={{ zIndex: 10000 }}>
          <section className="modal" style={{ width: '400px', height: '500px', display: 'flex', flexDirection: 'column' }}>
            <button className="modal-close" onClick={() => setIsOpen(false)} aria-label="Close">
              <Icon name="close" />
            </button>
            <p className="eyebrow">RIVERSIDE ACADEMY</p>
            <h2>AI Assistant</h2>
            
            <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px' }}>
              {messages.map((m, i) => (
                <div key={i} style={{ marginBottom: '1rem', textAlign: m.sender === 'user' ? 'right' : 'left' }}>
                  <span style={{ 
                    display: 'inline-block',
                    padding: '0.5rem 1rem', 
                    borderRadius: '20px', 
                    background: m.sender === 'user' ? '#000' : '#f0f0f0',
                    color: m.sender === 'user' ? '#fff' : '#000',
                  }}>
                    {m.text}
                  </span>
                </div>
              ))}
              {loading && <div style={{ textAlign: 'left' }}><span style={{ display: 'inline-block', padding: '0.5rem', background: '#f0f0f0', borderRadius: '20px' }}>...</span></div>}
            </div>

            <form onSubmit={submit} style={{ display: 'flex', gap: '0.5rem' }}>
              <input 
                type="text" 
                value={prompt} 
                onChange={e => setPrompt(e.target.value)} 
                placeholder="Ask a question..." 
                style={{ flex: 1, padding: '0.5rem' }} 
              />
              <button className="primary-button" disabled={loading}>Send</button>
            </form>
          </section>
        </div>
      )}
    </>
  )
}

export default App
