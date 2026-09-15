import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\admissions\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'student_profile = Profile.objects.create(user=student_user, role="student")',
    'student_profile = student_user.profile\n            student_profile.role = "student"\n            student_profile.save(update_fields=["role"])',
)

content = content.replace(
    'parent_profile = Profile.objects.create(user=parent_user, role="parent")',
    'parent_profile = parent_user.profile\n            parent_profile.role = "parent"\n            parent_profile.save(update_fields=["role"])',
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
