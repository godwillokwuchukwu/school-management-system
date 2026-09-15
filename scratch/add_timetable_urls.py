import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\academics\urls.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "from .views import ClassViewSet, EnrollmentViewSet, GradeViewSet, SubjectViewSet",
    "from .views import ClassViewSet, EnrollmentViewSet, GradeViewSet, SubjectViewSet, ClassScheduleViewSet",
)
content = content.replace(
    'router.register("grades", GradeViewSet, basename="grade")',
    'router.register("grades", GradeViewSet, basename="grade")\nrouter.register("schedules", ClassScheduleViewSet, basename="class-schedule")',
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
