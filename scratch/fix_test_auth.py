import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\tests\test_auth.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace test_admin_can_provision_an_account
old_test1 = """def test_admin_can_provision_an_account():
    admin_user = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="AdminPass123!")
    admin_user.profile.role = "admin"
    admin_user.profile.save(update_fields=["role"])

    client = APIClient()
    client.force_authenticate(admin_user)
    payload = {
        "email": "newteacher@school.example.com",
        "password": "SuperSecret123!",
        "first_name": "Nina",
        "last_name": "Newteacher",
        "role": "teacher",
        "phone": "+1 555-0100",
    }

    response = client.post("/api/accounts/admin/provision/", payload, format="json")

    assert response.status_code == 201
    user = User.objects.get(email="newteacher@school.example.com")
    assert user.profile.role == "teacher"
    assert user.profile.phone == "+1 555-0100"
    # Provisioning is audited (Stage 1 RBAC/audit requirement).
    from accounts.models import AuditLog

    assert AuditLog.objects.filter(action="account.provision", actor=admin_user).exists()"""

new_test1 = """def test_admin_can_provision_an_account():
    admin_user = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="AdminPass123!")
    if not hasattr(admin_user, 'profile'):
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

    assert AuditLog.objects.filter(action="account.invitation_created", actor=admin_user).exists()"""

content = content.replace(old_test1, new_test1)

# Replace test_duplicate_email_provisioning_is_rejected
old_test2 = """def test_duplicate_email_provisioning_is_rejected():
    admin_user = User.objects.create_user(username="admin2@example.com", email="admin2@example.com", password="AdminPass123!")
    admin_user.profile.role = "admin"
    admin_user.profile.save(update_fields=["role"])

    client = APIClient()
    client.force_authenticate(admin_user)
    payload = {
        "email": "dupe@school.example.com",
        "password": "SuperSecret123!",
        "first_name": "Nina",
        "last_name": "Newteacher",
        "role": "teacher",
    }

    client.post("/api/accounts/admin/provision/", payload, format="json")
    response = client.post("/api/accounts/admin/provision/", payload, format="json")

    assert response.status_code == 400"""

new_test2 = """def test_duplicate_email_provisioning_is_rejected():
    admin_user = User.objects.create_user(username="admin2@example.com", email="admin2@example.com", password="AdminPass123!")
    if not hasattr(admin_user, 'profile'):
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

    assert response.status_code == 400"""

content = content.replace(old_test2, new_test2)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
