import os

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\admissions\views.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('@action(detail=True, methods=["post"])') and lines[
        i + 1
    ].startswith("    def provision"):
        lines[i] = "    " + line
        break

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)
