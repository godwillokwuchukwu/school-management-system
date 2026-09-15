import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\admissions\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'audit.record(request.user, "admission_application.provisioned", application, None, None, request=request)',
    'audit.record(actor=request.user, action="admission_application.provisioned", instance=application, request=request)',
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
