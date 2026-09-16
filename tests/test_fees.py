import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from academics.models import Class, Enrollment
from fees.models import Fee, FeeSchedule, Payment
from students.models import Student

User = get_user_model()


@pytest.fixture
def admin_client():
    client = APIClient()
    admin = User.objects.create_superuser("admin_fees@example.com", "admin_fees@example.com", "Pass12345!")
    admin.profile.role = "admin"
    admin.profile.save()
    client.force_authenticate(user=admin)
    return client, admin


@pytest.fixture
def student_client():
    client = APIClient()
    student_user = User.objects.create_user("student_fees@example.com", "student_fees@example.com", "Pass12345!")
    student_user.profile.role = "student"
    student_user.profile.save()
    student = Student.objects.create(profile=student_user.profile, admission_number="ADM-FEES-01", dob="2012-01-01")
    client.force_authenticate(user=student_user)
    return client, student_user, student


@pytest.mark.django_db
def test_fee_crud(admin_client, student_client):
    client, admin = admin_client
    s_client, student_user, student = student_client

    create_resp = client.post(
        "/api/fees/fees/",
        {
            "student": student.id,
            "title": "Term 1 Tuition",
            "amount": "50000.00",
            "due_date": "2026-10-01",
        },
        format="json",
    )
    assert create_resp.status_code == 201
    fee_id = create_resp.data["id"]

    # Student views their fee
    list_resp = s_client.get("/api/fees/fees/")
    assert list_resp.status_code == 200
    assert len(list_resp.data["results"]) == 1


@pytest.mark.django_db
def test_bulk_generate_and_webhook(admin_client, student_client):
    client, admin = admin_client
    s_client, student_user, student = student_client

    school_class = Class.objects.create(name="Class 5", code="CLS5", academic_year="2026/2027")
    Enrollment.objects.create(student=student, school_class=school_class, academic_year="2026/2027")

    schedule = FeeSchedule.objects.create(
        title="Term 1 Sports Fee",
        academic_year="2026/2027",
        amount=5000.00,
        due_date="2026-11-01",
    )

    # Bulk generate fees
    gen_resp = client.post(
        "/api/fees/fees/bulk_generate/",
        {"schedule_id": schedule.id, "class_id": school_class.id},
        format="json",
    )
    assert gen_resp.status_code == 200
    assert "Successfully generated 1 invoices" in gen_resp.data["detail"]

    fee = Fee.objects.get(student=student, title="Term 1 Sports Fee (2026/2027)")

    # Webhook payment test
    anon_client = APIClient()
    webhook_resp = anon_client.post(
        "/api/fees/webhook/",
        {
            "invoice_id": fee.id,
            "status": "success",
            "transaction_ref": "TXN-FEES-1001",
        },
        format="json",
    )
    assert webhook_resp.status_code == 200
    fee.refresh_from_db()
    assert fee.status == "paid"

    # Test duplicate transaction
    dup_resp = anon_client.post(
        "/api/fees/webhook/",
        {
            "invoice_id": fee.id,
            "status": "success",
            "transaction_ref": "TXN-FEES-1001",
        },
        format="json",
    )
    assert dup_resp.status_code == 400

