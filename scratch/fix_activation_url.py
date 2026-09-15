import os

files = [
    r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\accounts\views.py",
    r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\admissions\views.py",
]
for p in files:
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()
    c = c.replace(
        'f"{frontend_url}/?activate_token={invitation.token}"',
        'f"{frontend_url}/portal?activate_token={invitation.token}"',
    )
    with open(p, "w", encoding="utf-8") as f:
        f.write(c)
