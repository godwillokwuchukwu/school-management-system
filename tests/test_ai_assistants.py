import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User as CustomUser
from accounts.models import Profile

pytestmark = pytest.mark.django_db


@pytest.fixture
def student_client():
    client = APIClient()
    user = CustomUser.objects.create_user(
        username="student_ai", email="student_ai@test.com", password="pass"
    )
    user.profile.role = "student"
    user.profile.save()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def teacher_client():
    client = APIClient()
    user = CustomUser.objects.create_user(
        username="teacher_ai", email="teacher_ai@test.com", password="pass"
    )
    user.profile.role = "teacher"
    user.profile.save()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client():
    client = APIClient()
    user = CustomUser.objects.create_user(
        username="admin_ai", email="admin_ai@test.com", password="pass"
    )
    user.profile.role = "admin"
    user.profile.save()
    client.force_authenticate(user=user)
    return client


def test_chatbot_view(student_client):
    response = student_client.post(reverse("ai-chatbot"), {"prompt": "Hello"})
    assert response.status_code == 200
    assert "response" in response.data


def test_teacher_view(teacher_client):
    response = teacher_client.post(
        reverse("ai-teacher"), {"prompt": "plan lesson Math"}
    )
    assert response.status_code == 200


def test_admin_view(admin_client):
    response = admin_client.post(reverse("ai-admin"), {"prompt": "show metrics"})
    assert response.status_code == 200


def test_explainer_view(teacher_client):
    response = teacher_client.post(
        reverse("ai-explainer"), {"prompt": "Explain Student 1"}
    )
    assert response.status_code == 200


def test_ai_role_enforcement(student_client):
    assert (
        student_client.post(reverse("ai-admin"), {"prompt": "metrics"}).status_code
        == 403
    )
    assert (
        student_client.post(reverse("ai-teacher"), {"prompt": "plan"}).status_code
        == 403
    )
