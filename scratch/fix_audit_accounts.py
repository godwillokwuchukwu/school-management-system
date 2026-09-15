import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\accounts\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'audit.record(request.user, "account.invitation_created", None, {"email": email, "role": role}, request)',
    'audit.record(actor=request.user, action="account.invitation_created", instance=invitation, new_value={"email": email, "role": role}, request=request)',
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
