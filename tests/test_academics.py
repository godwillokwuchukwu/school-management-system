import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from academics.models import Subject, Class, Enrollment, Grade, ClassSchedule
from students.models import Student

User = get_user_model()


@pytest.fixture
def admin_client():
    client = APIClient()
    admin = User.objects.create_superuser(
        "admin_acad@example.com", "admin_acad@example.com", "Pass12345!"
    )
    admin.profile.role = "admin"
    admin.profile.save()
    client.force_authenticate(user=admin)
    return client, admin


@pytest.fixture
def teacher_client():
    client = APIClient()
    teacher = User.objects.create_user(
        "teacher_acad@example.com", "teacher_acad@example.com", "Pass12345!"
    )
    teacher.profile.role = "teacher"
    teacher.profile.save()
    client.force_authenticate(user=teacher)
    return client, teacher


@pytest.fixture
def student_client():
    client = APIClient()
    student_user = User.objects.create_user(
        "student_acad@example.com", "student_acad@example.com", "Pass12345!"
    )
    student_user.profile.role = "student"
    student_user.profile.save()
    student = Student.objects.create(
        profile=student_user.profile, admission_number="ADM-ACAD-01", dob="2010-01-01"
    )
    client.force_authenticate(user=student_user)
    return client, student_user, student


@pytest.mark.django_db
def test_subject_crud(admin_client):
    client, _ = admin_client
    resp = client.post(
        "/api/academics/subjects/",
        {"name": "Mathematics", "code": "MTH101", "description": "Core Math"},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["code"] == "MTH101"

    list_resp = client.get("/api/academics/subjects/")
    assert list_resp.status_code == 200
    assert len(list_resp.data["results"]) >= 1


@pytest.mark.django_db
def test_class_crud_and_roster(admin_client, teacher_client, student_client):
    client, _ = admin_client
    subj = Subject.objects.create(name="English", code="ENG101")
    cls_resp = client.post(
        "/api/academics/classes/",
        {
            "name": "Grade 10A",
            "code": "G10A",
            "academic_year": "2026/2027",
            "subjects": [subj.id],
        },
        format="json",
    )
    assert cls_resp.status_code == 201
    class_id = cls_resp.data["id"]

    _, _, student = student_client
    enroll_resp = client.post(
        "/api/academics/enrollments/",
        {
            "student": student.id,
            "school_class": class_id,
            "academic_year": "2026/2027",
        },
        format="json",
    )
    assert enroll_resp.status_code == 201

    # Test roster action
    t_client, _ = teacher_client
    roster_resp = t_client.get(f"/api/academics/classes/{class_id}/roster/")
    assert roster_resp.status_code == 200
    assert len(roster_resp.data) == 1
    assert roster_resp.data[0]["admission_number"] == "ADM-ACAD-01"


@pytest.mark.django_db
def test_grades_and_schedules(teacher_client, student_client):
    t_client, teacher = teacher_client
    s_client, student_user, student = student_client

    subj = Subject.objects.create(name="Biology", code="BIO101")
    school_class = Class.objects.create(
        name="Grade 11B", code="G11B", academic_year="2026/2027"
    )
    enrollment = Enrollment.objects.create(
        student=student, school_class=school_class, academic_year="2026/2027"
    )

    # Teacher creates grade
    grade_resp = t_client.post(
        "/api/academics/grades/",
        {
            "enrollment": enrollment.id,
            "subject": subj.id,
            "score": 92.5,
            "comments": "Excellent",
            "graded_by": teacher.id,
        },
        format="json",
    )
    assert grade_resp.status_code == 201

    # Student views their grades
    s_grade_resp = s_client.get("/api/academics/grades/")
    assert s_grade_resp.status_code == 200
    assert len(s_grade_resp.data["results"]) == 1

    # Teacher creates schedule
    sched_resp = t_client.post(
        "/api/academics/schedules/",
        {
            "school_class": school_class.id,
            "subject": subj.id,
            "day_of_week": 1,
            "start_time": "08:00:00",
            "end_time": "09:00:00",
            "room": "Lab 1",
        },
        format="json",
    )
    assert sched_resp.status_code == 201

    # Student views schedule
    s_sched_resp = s_client.get("/api/academics/schedules/")
    assert s_sched_resp.status_code == 200
