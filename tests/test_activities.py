import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academics.models import Class, Subject
from students.models import Student

User = get_user_model()


@pytest.mark.django_db
def test_teacher_can_create_assignment():
    client = APIClient()

    teacher = User.objects.create_user(
        username="teacher2@example.com",
        email="teacher2@example.com",
        first_name="Tara",
        last_name="Teacher",
        password="StrongPass123!",
    )
    teacher.profile.role = "teacher"
    teacher.profile.save(update_fields=["role"])

    student_user = User.objects.create_user(
        username="student2@example.com",
        email="student2@example.com",
        first_name="Sam",
        last_name="Student",
        password="StrongPass123!",
    )
    student_user.profile.role = "student"
    student_user.profile.save(update_fields=["role"])

    student, _ = Student.objects.get_or_create(
        profile=student_user.profile,
        defaults={"admission_number": "ADM-TEST-002", "dob": "2014-05-20"},
    )

    subject = Subject.objects.create(
        name="Science", code="SCI101", description="Lab work"
    )
    teacher.profile.teaching_subjects.add(subject)
    school_class = Class.objects.create(
        name="Grade 8B", code="G8B2", academic_year="2025-2026", class_teacher=teacher
    )
    school_class.subjects.add(subject)

    client.force_authenticate(user=teacher)
    response = client.post(
        "/api/activities/assignments/",
        {
            "title": "Lab Report",
            "description": "Write a 500-word lab report.",
            "subject": subject.id,
            "school_class": school_class.id,
            "due_date": "2026-09-15",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["title"] == "Lab Report"


@pytest.mark.django_db
def test_student_can_submit_assignment():
    client = APIClient()

    teacher = User.objects.create_user(
        username="teacher3@example.com",
        email="teacher3@example.com",
        first_name="Tori",
        last_name="Teacher",
        password="StrongPass123!",
    )
    teacher.profile.role = "teacher"
    teacher.profile.save(update_fields=["role"])

    student_user = User.objects.create_user(
        username="student3@example.com",
        email="student3@example.com",
        first_name="Mia",
        last_name="Student",
        password="StrongPass123!",
    )
    student_user.profile.role = "student"
    student_user.profile.save(update_fields=["role"])

    student, _ = Student.objects.get_or_create(
        profile=student_user.profile,
        defaults={"admission_number": "ADM-TEST-003", "dob": "2014-08-15"},
    )

    subject = Subject.objects.create(name="Biology", code="BIO101", description="Cells")
    school_class = Class.objects.create(
        name="Grade 8A", code="G8A1", academic_year="2025-2026", class_teacher=teacher
    )
    school_class.subjects.add(subject)

    assignment = school_class.assignments.create(
        title="Plant Observation",
        description="Observe a bean seed germination.",
        subject=subject,
        due_date="2026-09-20",
        created_by=teacher,
    )

    client.force_authenticate(user=student_user)
    response = client.post(
        "/api/activities/submissions/",
        {
            "assignment": assignment.id,
            "student": student.id,
            "content": "The seed sprouted after several days.",
            "status": "submitted",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["status"] == "submitted"
