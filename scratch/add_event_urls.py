import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\activities\urls.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "from .views import AssignmentSubmissionViewSet, AssignmentViewSet",
    "from .views import AssignmentSubmissionViewSet, AssignmentViewSet, EventViewSet, ParentTeacherMeetingViewSet",
)
content = content.replace(
    'router.register(r"submissions", AssignmentSubmissionViewSet, basename="assignmentsubmission")',
    'router.register(r"submissions", AssignmentSubmissionViewSet, basename="assignmentsubmission")\nrouter.register(r"events", EventViewSet, basename="event")\nrouter.register(r"meetings", ParentTeacherMeetingViewSet, basename="meeting")',
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
