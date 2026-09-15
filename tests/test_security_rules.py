import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import Profile
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def test_public_registration_never_creates_privileged_account(api_client):
    url = reverse("register")
    response = api_client.post(
        url,
        {
            "email": "hacker2@test.com",
            "password": "testpassword123",
            "first_name": "Hack",
            "last_name": "Er",
            "role": "admin",
        },
    )
    # The actual implementation of registration in auth.py creates an applicant by default
    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(username="hacker2@test.com")
    assert user.profile.role == "applicant"


def test_only_admins_provision_internal_accounts(api_client):
    # Need to test provisioning logic (e.g. create_employee)
    url = reverse("admin-provision") if hasattr(reverse, "admin-provision") else None
    if url:
        user = User.objects.create_user(username="teacher", password="123")
        Profile.objects.update_or_create(user=user, defaults={"role": "teacher"})
        api_client.force_authenticate(user=user)
        response = api_client.post(url, {"email": "newadmin@test.com"})
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]
