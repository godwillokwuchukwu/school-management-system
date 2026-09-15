import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\frontend\src\App.jsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add imports
imports = "import AdmissionsAdmin from './AdmissionsAdmin'\nimport UserManagement from './UserManagement'\n"
content = content.replace(
    "import ParentWorkspace from './ParentWorkspace'",
    imports + "import ParentWorkspace from './ParentWorkspace'",
)

# Patch StaffWorkspace
old_staff = """function StaffWorkspace({ active, setActive, _profile, data, role, error }) {
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
}"""

new_staff = """function StaffWorkspace({ active, setActive, _profile, data, role, error }) {
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
}"""

content = content.replace(old_staff, new_staff)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
