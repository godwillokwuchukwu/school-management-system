import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test.utils import setup_test_environment

# Outside pytest/manage.py test, Django never adds "testserver" to
# ALLOWED_HOSTS, so APIClient requests 400 with DisallowedHost as soon as
# a real ALLOWED_HOSTS value is configured (e.g. via .env). This mirrors
# what the pytest-django/manage.py test runners do automatically.
setup_test_environment()

from rest_framework.test import APIClient

client = APIClient()

print("--- Register (new teacher) ---")
resp = client.post(
    "/api/auth/register/",
    {
        "email": "newteacher@school.example.com",
        "password": "SuperSecret123!",
        "first_name": "Nina",
        "last_name": "Newteacher",
        "role": "teacher",
        "phone": "+1 555-0100",
    },
    format="json",
)
print(resp.status_code, resp.json())

print("\n--- Register duplicate email (should 400) ---")
resp = client.post(
    "/api/auth/register/",
    {
        "email": "newteacher@school.example.com",
        "password": "SuperSecret123!",
        "first_name": "Nina",
        "last_name": "Newteacher",
        "role": "teacher",
    },
    format="json",
)
print(resp.status_code, resp.json())

print("\n--- Login ---")
resp = client.post(
    "/api/auth/login/",
    {"username": "newteacher@school.example.com", "password": "SuperSecret123!"},
    format="json",
)
print(resp.status_code)
tokens = resp.json()
print({k: (v[:30] + "...") for k, v in tokens.items()})
access = tokens["access"]

print("\n--- GET /api/accounts/profiles/me/ without token (should 401) ---")
resp = client.get("/api/accounts/profiles/me/")
print(resp.status_code)

print("\n--- GET /api/accounts/profiles/me/ with token ---")
client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
resp = client.get("/api/accounts/profiles/me/")
print(resp.status_code, resp.json())

print("\n--- Teacher tries to list all profiles (admin-only, should 403) ---")
resp = client.get("/api/accounts/profiles/")
print(resp.status_code, resp.json())

print("\n--- Teacher creates a Subject (should 403, admin-only write) ---")
resp = client.post(
    "/api/academics/subjects/", {"name": "Physics", "code": "PHYS101"}, format="json"
)
print(resp.status_code, resp.json())

# --- Log in as seeded admin and exercise academics business rules ---
print("\n--- Login as admin ---")
resp = client.post(
    "/api/auth/login/",
    {"username": "admin@school.example.com", "password": "ChangeMe123!"},
    format="json",
)
print(resp.status_code)
admin_access = resp.json()["access"]
client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_access}")

print("\n--- Admin creates duplicate class code in same year (should 400) ---")
resp = client.post(
    "/api/academics/classes/",
    {"name": "Grade 8B Again", "code": "G8B", "academic_year": "2025-2026"},
    format="json",
)
print(resp.status_code, resp.json())

print("\n--- Admin lists classes ---")
resp = client.get("/api/academics/classes/")
print(resp.status_code, resp.json())

print("\n--- Login as teacher, create out-of-range grade (should 400) ---")
resp = client.post(
    "/api/auth/login/",
    {"username": "teacher@school.example.com", "password": "ChangeMe123!"},
    format="json",
)
teacher_access = resp.json()["access"]
client.credentials(HTTP_AUTHORIZATION=f"Bearer {teacher_access}")

from academics.models import Class, Enrollment
from students.models import Student

student = Student.objects.first()
school_class = Class.objects.get(code="G8B", academic_year="2025-2026")
enrollment, _ = Enrollment.objects.get_or_create(
    student=student, school_class=school_class, academic_year="2025-2026"
)
subject_id = school_class.subjects.first().id

resp = client.post(
    "/api/academics/grades/",
    {"enrollment": enrollment.id, "subject": subject_id, "score": 150},
    format="json",
)
print(resp.status_code, resp.json())

print("\n--- Teacher creates valid grade ---")
resp = client.post(
    "/api/academics/grades/",
    {"enrollment": enrollment.id, "subject": subject_id, "score": 87.5},
    format="json",
)
print(resp.status_code, resp.json())

from accounts.models import AuditLog

print("\n--- Audit log entries ---")
for log in AuditLog.objects.all():
    print(log.action, log.model_name, log.object_id, log.old_value, "->", log.new_value)

print(
    "\n--- Student self-registers, then submits an assignment (the app's real payload has no `student` field) ---"
)
resp = client.post(
    "/api/auth/register/",
    {
        "email": "smoketest.student@school.example.com",
        "password": "SuperSecret123!",
        "first_name": "Smoke",
        "last_name": "Tester",
        "role": "student",
        "dob": "2012-01-01",
    },
    format="json",
)
assert (
    resp.status_code == 201
), f"student self-registration failed: {resp.status_code} {resp.json()}"
resp = client.post(
    "/api/auth/login/",
    {"username": "smoketest.student@school.example.com", "password": "SuperSecret123!"},
    format="json",
)
client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.json()['access']}")

from activities.models import Assignment

assignment, _ = Assignment.objects.get_or_create(
    title="Smoke test HW",
    subject_id=subject_id,
    school_class=school_class,
    due_date="2026-12-01",
    defaults={"created_by": None},
)
resp = client.post(
    "/api/activities/submissions/",
    {"assignment": assignment.id, "content": "my homework", "status": "submitted"},
    format="json",
)
assert (
    resp.status_code == 201
), f"self-registered student could not submit an assignment: {resp.status_code} {resp.json()}"
print(resp.status_code, resp.json())

print("\n--- Public registration cannot mint an admin account ---")
client.credentials()  # anonymous
resp = client.post(
    "/api/auth/register/",
    {
        "email": "shouldfail@evil.example.com",
        "password": "SuperSecret123!",
        "first_name": "No",
        "last_name": "Admin",
        "role": "admin",
    },
    format="json",
)
assert (
    resp.status_code == 400
), f"admin self-registration should be rejected but got {resp.status_code}"
print(resp.status_code, resp.json())

print("\nALL SMOKE TESTS RAN")
