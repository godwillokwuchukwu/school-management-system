import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_public_self_registration_only_creates_an_applicant_account():
    """
    STAGE 1/2 FIX: public registration must never mint a live portal
    account. It's restricted to the Applicant role -- and even a client
    that tries to smuggle a different role in the payload cannot get one,
    since the public serializer has no `role` field to set at all.
    See GAP_ANALYSIS_AND_ROADMAP.md item #2.
    """
    client = APIClient()
    payload = {
        "email": "prospect@example.com",
        "password": "SuperSecret123!",
        "first_name": "Priya",
        "last_name": "Prospect",
        "phone": "+1 555-0100",
        "role": "admin",  # attempted privilege escalation -- must be ignored
    }

    response = client.post("/api/auth/register/", payload, format="json")

    assert response.status_code == 201
    user = User.objects.get(email="prospect@example.com")
    assert user.profile.role == "applicant"


@pytest.mark.django_db
def test_applicant_account_cannot_reach_portal_endpoints():
    client = APIClient()
    client.post(
        "/api/auth/register/",
        {
            "email": "prospect2@example.com",
            "password": "SuperSecret123!",
            "first_name": "Priya",
            "last_name": "Prospect",
        },
        format="json",
    )
    login = client.post(
        "/api/auth/login/",
        {"username": "prospect2@example.com", "password": "SuperSecret123!"},
        format="json",
    )
    assert login.status_code == 200
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    response = client.get("/api/students/students/")
    # Reachable (any authenticated user can hit the list endpoint), but the
    # object-level scoping means an applicant sees nothing -- this is the
    # queryset.none() fallback added alongside the applicant role.
    assert response.status_code == 200
    assert response.data["results"] == []

    create_response = client.post(
        "/api/students/students/",
        {"admission_number": "X-001", "dob": "2012-01-01"},
        format="json",
    )
    assert create_response.status_code == 403


@pytest.mark.django_db
def test_admin_can_provision_an_account():
    admin_user = User.objects.create_user(
        username="admin@example.com",
        email="admin@example.com",
        password="AdminPass123!",
    )
    if not hasattr(admin_user, "profile"):
        from accounts.models import Profile

        Profile.objects.create(user=admin_user, role="admin")
    else:
        admin_user.profile.role = "admin"
        admin_user.profile.save(update_fields=["role"])

    client = APIClient()
    client.force_authenticate(admin_user)
    payload = {
        "email": "newteacher@school.example.com",
        "first_name": "Nina",
        "last_name": "Newteacher",
        "role": "teacher",
        "phone": "+1 555-0100",
    }

    response = client.post("/api/accounts/admin/provision/", payload, format="json")

    assert response.status_code == 201

    from accounts.models import RegistrationInvitation, AuditLog

    inv = RegistrationInvitation.objects.get(email="newteacher@school.example.com")
    assert inv.role == "teacher"

    assert AuditLog.objects.filter(
        action="account.invitation_created", actor=admin_user
    ).exists()


@pytest.mark.django_db
def test_non_admin_cannot_provision_an_account():
    teacher = User.objects.create_user(
        username="teacher@example.com", email="teacher@example.com", password="Pass123!"
    )
    teacher.profile.role = "teacher"
    teacher.profile.save(update_fields=["role"])

    client = APIClient()
    client.force_authenticate(teacher)
    payload = {
        "email": "newstudent@school.example.com",
        "password": "SuperSecret123!",
        "first_name": "Sam",
        "last_name": "Newstudent",
        "role": "student",
        "dob": "2012-01-01",
    }

    response = client.post("/api/accounts/admin/provision/", payload, format="json")

    assert response.status_code == 403
    assert not User.objects.filter(email="newstudent@school.example.com").exists()


@pytest.mark.django_db
def test_duplicate_email_provisioning_is_rejected():
    admin_user = User.objects.create_user(
        username="admin2@example.com",
        email="admin2@example.com",
        password="AdminPass123!",
    )
    if not hasattr(admin_user, "profile"):
        from accounts.models import Profile

        Profile.objects.create(user=admin_user, role="admin")
    else:
        admin_user.profile.role = "admin"
        admin_user.profile.save(update_fields=["role"])

    client = APIClient()
    client.force_authenticate(admin_user)
    payload = {
        "email": "dupe@school.example.com",
        "first_name": "Nina",
        "last_name": "Newteacher",
        "role": "teacher",
    }

    client.post("/api/accounts/admin/provision/", payload, format="json")
    response = client.post("/api/accounts/admin/provision/", payload, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_password_reset_request_and_confirmation():
    user = User.objects.create_user(
        username="reset@example.com",
        email="reset@example.com",
        password="OldPassword123!",
    )
    client = APIClient()

    request = client.post(
        "/api/auth/password-reset/", {"email": user.email}, format="json"
    )
    assert request.status_code == 202

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    confirm = client.post(
        "/api/auth/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "NewPassword123!"},
        format="json",
    )

    assert confirm.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NewPassword123!")
