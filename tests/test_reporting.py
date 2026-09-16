import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from reporting.models import Report
from students.models import Student

User = get_user_model()


@pytest.fixture
def teacher_client():
    client = APIClient()
    teacher = User.objects.create_user("teacher_rep@example.com", "teacher_rep@example.com", "Pass12345!")
    teacher.profile.role = "teacher"
    teacher.profile.save()
    client.force_authenticate(user=teacher)
    return client, teacher


@pytest.fixture
def student_client():
    client = APIClient()
    student_user = User.objects.create_user("student_rep@example.com", "student_rep@example.com", "Pass12345!")
    student_user.profile.role = "student"
    student_user.profile.save()
    student = Student.objects.create(profile=student_user.profile, admission_number="ADM-REP-01", dob="2011-01-01")
    client.force_authenticate(user=student_user)
    return client, student_user, student


@pytest.mark.django_db
def test_report_crud_and_role_access(teacher_client, student_client):
    t_client, teacher = teacher_client
    s_client, student_user, student = student_client

    create_resp = t_client.post(
        "/api/reporting/reports/",
        {
            "title": "Term 1 Report Card",
            "report_type": "academic",
            "student": student.id,
            "generated_by": teacher.id,
            "data": {"overall_grade": "A", "attendance": "98%"},
        },
        format="json",
    )
    assert create_resp.status_code == 201

    # Student reads their report
    s_resp = s_client.get("/api/reporting/reports/")
    assert s_resp.status_code == 200
    assert len(s_resp.data["results"]) == 1

