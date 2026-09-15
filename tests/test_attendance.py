import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_teacher_can_create_attendance_record():
    client = APIClient()

    teacher = User.objects.create_user(
        username="teacher@example.com",
        email="teacher@example.com",
        first_name="Tara",
        last_name="Teacher",
        password="StrongPass123!",
    )
    teacher.profile.role = "teacher"
    teacher.profile.save(update_fields=["role"])

    student_user = User.objects.create_user(
        username="student@example.com",
        email="student@example.com",
        first_name="Sam",
        last_name="Student",
        password="StrongPass123!",
    )
    student_user.profile.role = "student"
    student_user.profile.save(update_fields=["role"])

    from students.models import Student

    student, _ = Student.objects.get_or_create(
        profile=student_user.profile,
        defaults={"admission_number": "ADM-TEST-001", "dob": "2014-01-01"},
    )
    client.force_authenticate(user=teacher)
    resp = client.post(
        "/api/attendance/records/",
        {"student": student.id, "date": "2026-09-04", "status": "present"},
        format="json",
    )

    assert resp.status_code == 201
    assert resp.data["status"] == "present"
