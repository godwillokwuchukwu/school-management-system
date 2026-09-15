import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\accounts\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix suspend
content = content.replace(
    'audit.record(request.user, "account.suspend", profile, None, request)',
    'audit.record(actor=request.user, action="account.suspend", instance=profile, request=request)',
)
# Fix reactivate
content = content.replace(
    'audit.record(request.user, "account.reactivate", profile, None, request)',
    'audit.record(actor=request.user, action="account.reactivate", instance=profile, request=request)',
)
# Fix force_reset
content = content.replace(
    'audit.record(request.user, "account.force_reset", profile, None, request)',
    'audit.record(actor=request.user, action="account.force_reset", instance=profile, request=request)',
)
# Fix revoke_sessions
content = content.replace(
    'audit.record(request.user, "account.sessions_revoked", profile, None, request)',
    'audit.record(actor=request.user, action="account.sessions_revoked", instance=profile, request=request)',
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
