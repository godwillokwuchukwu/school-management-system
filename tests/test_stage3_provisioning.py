import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import Profile, RegistrationInvitation
from django.contrib.auth import get_user_model
from admissions.models import AdmissionApplication, ApplicationStatus
from students.models import Student

User = get_user_model()


@pytest.fixture
def admin_user():
    user = User.objects.create_user(
        username="admin2@local", email="admin2@local", password="testpassword"
    )
    user.profile.role = "admin"
    user.profile.save()
    return user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_admissions_provision(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    app = AdmissionApplication.objects.create(
        applicant=admin_user,
        status=ApplicationStatus.APPROVED,
        reference="BFA-2025-000001",
        student_first_name="John",
        student_last_name="Doe",
        student_email="johndoe@test.local",
        student_dob="2010-01-01",
        class_applying_for="Grade 1",
        academic_session="2023",
        guardian_full_name="Jane Doe",
        guardian_email="janedoe@test.local",
        guardian_phone="1234567890",
    )

    url = f"/api/admissions/admin/applications/{app.id}/provision/"
    response = api_client.post(url)
    assert response.status_code == 200, response.data

    student_user = User.objects.get(email="johndoe@test.local")
    assert not student_user.is_active
    assert hasattr(student_user, "profile")
    assert student_user.profile.role == "student"

    student = Student.objects.get(profile=student_user.profile)
    assert student.admission_number == app.reference

    parent_user = User.objects.get(email="janedoe@test.local")
    assert not parent_user.is_active
    assert hasattr(parent_user, "profile")
    assert parent_user.profile.role == "parent"

    assert parent_user.profile in student.parents.all()

    assert RegistrationInvitation.objects.filter(email="johndoe@test.local").exists()
    assert RegistrationInvitation.objects.filter(email="janedoe@test.local").exists()


@pytest.mark.django_db
def test_admin_suspend_reactivate(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    user = User.objects.create_user(
        username="teacher3@local", email="teacher3@local", password="pwd"
    )
    user.profile.role = "teacher"
    user.profile.save()

    url = f"/api/accounts/profiles/{user.profile.id}/suspend/"
    response = api_client.post(url)
    assert response.status_code == 200
    user.refresh_from_db()
    assert not user.is_active

    url = f"/api/accounts/profiles/{user.profile.id}/reactivate/"
    response = api_client.post(url)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_active
