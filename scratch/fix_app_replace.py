import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\frontend\src\App.jsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the broken demo object
demo_regex = r"const demo = \{[\s\S]*?\n\}"
correct_demo = """const demo = {
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
}"""

content = re.sub(demo_regex, correct_demo, content)

# Now fix the ModulePage that I also broke
module_page_regex = r"const source =\s+module === 'Notices'[\s\S]*?\n\s+\]"
correct_module_page = """const source =
    module === 'Notices' || module === 'News'
      ? data.announcements
      : module === 'Exams & Grades' || module === 'Grades'
      ? data.grades
      : module === 'Timetable' || module === 'Classes' || module === 'My Classes'
      ? data.classes
      : module === 'Students'
      ? data.students
      : module === 'Fees' || module === 'Payments'
      ? data.reports
      : module === 'Documents'
      ? data.documents
      : module === 'Calendar'
      ? data.events
      : []"""

content = re.sub(module_page_regex, correct_module_page, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
