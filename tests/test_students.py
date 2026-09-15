import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from students.models import Student

User = get_user_model()


def make_user(email, role):
    user = User.objects.create_user(
        username=email, email=email, password="StrongPass123!"
    )
    user.profile.role = role
    user.profile.save(update_fields=["role"])
    return user


@pytest.mark.django_db
def test_admin_can_create_and_list_students():
    admin = make_user("admin-students@example.com", "admin")
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        "/api/students/students/",
        {
            "email": "newstudent@example.com",
            "first_name": "New",
            "last_name": "Student",
            "admission_number": "ADM-NEW-001",
            "dob": "2014-05-20",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["full_name"] == "New Student"
    assert Student.objects.filter(admission_number="ADM-NEW-001").exists()
    assert client.get("/api/students/students/").status_code == 200


@pytest.mark.django_db
def test_teacher_can_read_but_not_create_students():
    teacher = make_user("teacher-students@example.com", "teacher")
    client = APIClient()
    client.force_authenticate(user=teacher)

    assert client.get("/api/students/students/").status_code == 200
    response = client.post(
        "/api/students/students/",
        {
            "email": "blocked@example.com",
            "admission_number": "ADM-BLOCKED",
            "dob": "2014-05-20",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_student_can_only_read_their_own_record():
    first = make_user("first-student@example.com", "student")
    second = make_user("second-student@example.com", "student")
    Student.objects.create(
        profile=first.profile, admission_number="ADM-FIRST", dob="2014-05-20"
    )
    Student.objects.create(
        profile=second.profile, admission_number="ADM-SECOND", dob="2014-05-20"
    )

    client = APIClient()
    client.force_authenticate(user=first)
    response = client.get("/api/students/students/")

    assert response.status_code == 200
    assert [student["admission_number"] for student in response.data["results"]] == [
        "ADM-FIRST"
    ]
