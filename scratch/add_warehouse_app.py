import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\config\settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('"public_site",', '"public_site",\n    "warehouse",')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
