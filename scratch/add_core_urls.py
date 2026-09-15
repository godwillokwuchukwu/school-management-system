import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\config\urls.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'path("api/accounts/", include("accounts.urls")),',
    'path("api/core/", include("core.urls")),\n    path("api/accounts/", include("accounts.urls")),',
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
