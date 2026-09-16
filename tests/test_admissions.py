import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from admissions.models import AdmissionApplication

User = get_user_model()


def _register_applicant(client, email):
    client.post(
        "/api/auth/register/",
        {
            "email": email,
            "password": "SuperSecret123!",
            "first_name": "A",
            "last_name": "Pplicant",
        },
        format="json",
    )
    login = client.post(
        "/api/auth/login/",
        {"username": email, "password": "SuperSecret123!"},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    return User.objects.get(email=email)


VALID_APPLICATION_PAYLOAD = {
    "student_first_name": "Ada",
    "student_last_name": "Lovelace",
    "student_dob": "2013-05-10",
    "class_applying_for": "Grade 6",
    "academic_session": "2026/2027",
    "guardian_full_name": "Grace Hopper",
    "guardian_relationship": "Mother",
    "guardian_phone": "+1 555-0101",
    "guardian_email": "grace@example.com",
}


@pytest.mark.django_db
def test_applicant_can_create_and_submit_application():
    client = APIClient()
    _register_applicant(client, "parent1@example.com")

    create = client.post(
        "/api/admissions/applications/", VALID_APPLICATION_PAYLOAD, format="json"
    )
    assert create.status_code == 201
    app_id = create.data["id"]
    assert create.data["status"] == "started"

    submit = client.post(f"/api/admissions/applications/{app_id}/submit/")
    assert submit.status_code == 200
    assert submit.data["status"] == "submitted"
    assert submit.data["reference"].startswith("BFA-")


@pytest.mark.django_db
def test_incomplete_application_is_rejected_at_creation():
    """
    Guardian/student fields are required at the model level, so an
    incomplete application never even reaches 'started' -- validation
    fails at creation time rather than silently allowing a submit later.
    (submit()'s own completeness re-check exists as defense in depth.)
    """
    client = APIClient()
    _register_applicant(client, "parent2@example.com")

    create = client.post(
        "/api/admissions/applications/",
        {
            "student_first_name": "Ada",
            "student_last_name": "Lovelace",
            "student_dob": "2013-05-10",
            "class_applying_for": "Grade 6",
            "academic_session": "2026/2027",
            "guardian_full_name": "",
            "guardian_relationship": "",
            "guardian_phone": "",
            "guardian_email": "",
        },
        format="json",
    )
    assert create.status_code == 400
    assert "guardian_full_name" in create.data


@pytest.mark.django_db
def test_applicant_cannot_view_or_edit_another_applicants_application():
    client_a = APIClient()
    _register_applicant(client_a, "owner@example.com")
    created = client_a.post(
        "/api/admissions/applications/", VALID_APPLICATION_PAYLOAD, format="json"
    )
    app_id = created.data["id"]

    client_b = APIClient()
    _register_applicant(client_b, "intruder@example.com")

    detail = client_b.get(f"/api/admissions/applications/{app_id}/")
    assert detail.status_code == 404  # filtered out of intruder's own queryset entirely

    patch = client_b.patch(
        f"/api/admissions/applications/{app_id}/",
        {"student_first_name": "Hacked"},
        format="json",
    )
    assert patch.status_code == 404


@pytest.mark.django_db
def test_submitted_application_cannot_be_edited_directly():
    client = APIClient()
    _register_applicant(client, "parent3@example.com")
    created = client.post(
        "/api/admissions/applications/", VALID_APPLICATION_PAYLOAD, format="json"
    )
    app_id = created.data["id"]
    client.post(f"/api/admissions/applications/{app_id}/submit/")

    patch = client.patch(
        f"/api/admissions/applications/{app_id}/",
        {"student_first_name": "Changed"},
        format="json",
    )
    assert patch.status_code == 403


@pytest.mark.django_db
def test_document_upload_validates_extension_and_ownership():
    client = APIClient()
    _register_applicant(client, "parent4@example.com")
    created = client.post(
        "/api/admissions/applications/", VALID_APPLICATION_PAYLOAD, format="json"
    )
    app_id = created.data["id"]

    bad_file = SimpleUploadedFile(
        "virus.exe", b"bad", content_type="application/octet-stream"
    )
    bad = client.post(
        f"/api/admissions/applications/{app_id}/documents/",
        {"document_type": "birth_certificate", "file": bad_file},
        format="multipart",
    )
    assert bad.status_code == 400

    good_file = SimpleUploadedFile(
        "cert.pdf", b"%PDF-1.4", content_type="application/pdf"
    )
    good = client.post(
        f"/api/admissions/applications/{app_id}/documents/",
        {"document_type": "birth_certificate", "file": good_file},
        format="multipart",
    )
    assert good.status_code == 201

    # A different applicant cannot upload to (or even see) someone else's application.
    other_client = APIClient()
    _register_applicant(other_client, "intruder2@example.com")
    intruder_file = SimpleUploadedFile(
        "cert.pdf", b"%PDF-1.4", content_type="application/pdf"
    )
    forbidden = other_client.post(
        f"/api/admissions/applications/{app_id}/documents/",
        {"document_type": "birth_certificate", "file": intruder_file},
        format="multipart",
    )
    assert forbidden.status_code == 403


@pytest.mark.django_db
def test_admin_can_review_and_decide_submitted_applications():
    admin = User.objects.create_user(
        username="admin@example.com",
        email="admin@example.com",
        password="AdminPass123!",
    )
    admin.profile.role = "admin"
    admin.profile.save(update_fields=["role"])

    applicant_client = APIClient()
    _register_applicant(applicant_client, "parent5@example.com")
    created = applicant_client.post(
        "/api/admissions/applications/", VALID_APPLICATION_PAYLOAD, format="json"
    )
    app_id = created.data["id"]
    applicant_client.post(f"/api/admissions/applications/{app_id}/submit/")

    admin_client = APIClient()
    admin_client.force_authenticate(admin)

    listing = admin_client.get("/api/admissions/admin/applications/")
    assert listing.status_code == 200
    assert any(item["id"] == app_id for item in listing.data["results"])

    decide = admin_client.post(
        f"/api/admissions/admin/applications/{app_id}/decide/",
        {
            "status": "under_review",
            "decision_notes": "Looks good, scheduling assessment.",
        },
        format="json",
    )
    assert decide.status_code == 200
    assert decide.data["status"] == "under_review"

    application = AdmissionApplication.objects.get(pk=app_id)
    assert application.reviewed_by == admin

    from accounts.models import AuditLog

    assert AuditLog.objects.filter(
        action="admission_application.status_change", actor=admin
    ).exists()


@pytest.mark.django_db
def test_non_admin_cannot_review_applications():
    applicant_client = APIClient()
    _register_applicant(applicant_client, "parent6@example.com")
    created = applicant_client.post(
        "/api/admissions/applications/", VALID_APPLICATION_PAYLOAD, format="json"
    )
    app_id = created.data["id"]
    applicant_client.post(f"/api/admissions/applications/{app_id}/submit/")

    response = applicant_client.get("/api/admissions/admin/applications/")
    assert response.status_code == 403

    response = applicant_client.post(
        f"/api/admissions/admin/applications/{app_id}/decide/",
        {"status": "approved"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_draft_applications_are_hidden_from_admin_review_queue():
    """An application still being drafted (status=started) shouldn't clutter
    the admin review queue -- only submitted-or-later applications should."""
    admin = User.objects.create_user(
        username="admin2@example.com",
        email="admin2@example.com",
        password="AdminPass123!",
    )
    admin.profile.role = "admin"
    admin.profile.save(update_fields=["role"])

    applicant_client = APIClient()
    _register_applicant(applicant_client, "parent7@example.com")
    applicant_client.post(
        "/api/admissions/applications/", VALID_APPLICATION_PAYLOAD, format="json"
    )

    admin_client = APIClient()
    admin_client.force_authenticate(admin)
    listing = admin_client.get("/api/admissions/admin/applications/")
    assert listing.data["count"] == 0


@pytest.mark.django_db
def test_public_application_status_lookup_hides_guardian_contact_details():
    client = APIClient()
    _register_applicant(client, "parent8@example.com")
    created = client.post(
        "/api/admissions/applications/", VALID_APPLICATION_PAYLOAD, format="json"
    )
    app_id = created.data["id"]
    submitted = client.post(f"/api/admissions/applications/{app_id}/submit/")
    reference = submitted.data["reference"]

    anon_client = APIClient()
    response = anon_client.get(f"/api/admissions/status/{reference}/")

    assert response.status_code == 200
    assert response.data["reference"] == reference
    assert "guardian_email" not in response.data
    assert "guardian_phone" not in response.data


@pytest.mark.django_db
def test_parent_relationship_request_is_pending_and_scoped_to_owner():
    from students.models import Student

    student_user = User.objects.create_user(
        username="child@example.com", email="child@example.com", password="Pass123!"
    )
    student_user.profile.role = "student"
    student_user.profile.save(update_fields=["role"])
    Student.objects.create(
        profile=student_user.profile, admission_number="BFA-0001", dob="2013-01-01"
    )

    parent_client = APIClient()
    _register_applicant(parent_client, "guardian@example.com")
    payload = {
        "student_admission_number": "BFA-0001",
        "child_full_name": "Existing Student",
        "relationship": "Mother",
        "phone": "+1 555-0111",
        "email": "guardian@example.com",
        "message": "I am the mother of this student.",
    }

    create = parent_client.post(
        "/api/admissions/parent-relationships/", payload, format="json"
    )
    assert create.status_code == 201
    assert create.data["status"] == "pending"
    assert create.data["reference"].startswith("PGR-")

    # Not yet a real parent-student link -- verification (Stage 3) hasn't happened.
    student = Student.objects.get(admission_number="BFA-0001")
    assert student.parents.count() == 0


@pytest.mark.django_db
def test_admin_can_verify_parent_relationship_request_and_it_is_audited():
    admin = User.objects.create_user(
        username="admin3@example.com",
        email="admin3@example.com",
        password="AdminPass123!",
    )
    admin.profile.role = "admin"
    admin.profile.save(update_fields=["role"])

    parent_client = APIClient()
    _register_applicant(parent_client, "guardian2@example.com")
    payload = {
        "student_admission_number": "BFA-9999",
        "child_full_name": "Some Student",
        "relationship": "Father",
        "phone": "+1 555-0112",
        "email": "guardian2@example.com",
    }
    created = parent_client.post(
        "/api/admissions/parent-relationships/", payload, format="json"
    )
    request_id = created.data["id"]

    admin_client = APIClient()
    admin_client.force_authenticate(admin)
    listing = admin_client.get("/api/admissions/admin/parent-relationships/")
    assert listing.status_code == 200
    assert listing.data["count"] == 1
    # No student exists with that admission number -- admin should be able to see that before verifying.
    assert listing.data["results"][0]["matching_student_exists"] is False

    decide = admin_client.post(
        f"/api/admissions/admin/parent-relationships/{request_id}/decide/",
        {"status": "rejected", "decision_notes": "No matching student record found."},
        format="json",
    )
    assert decide.status_code == 200
    assert decide.data["status"] == "rejected"

    from accounts.models import AuditLog

    assert AuditLog.objects.filter(
        action="parent_relationship_request.status_change", actor=admin
    ).exists()


@pytest.mark.django_db
def test_applicant_cannot_view_another_applicants_parent_relationship_request():
    owner_client = APIClient()
    _register_applicant(owner_client, "guardian3@example.com")
    created = owner_client.post(
        "/api/admissions/parent-relationships/",
        {
            "student_admission_number": "BFA-0002",
            "child_full_name": "X",
            "relationship": "Mother",
            "phone": "+1 555-0113",
            "email": "guardian3@example.com",
        },
        format="json",
    )
    request_id = created.data["id"]

    intruder_client = APIClient()
    _register_applicant(intruder_client, "intruder3@example.com")
    response = intruder_client.get(
        f"/api/admissions/parent-relationships/{request_id}/"
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_job_application_status_is_publicly_trackable():
    from public_site.models import JobPosting

    job = JobPosting.objects.create(
        title="PE Teacher", description="Teach PE.", is_active=True
    )
    from django.core.files.uploadedfile import SimpleUploadedFile

    client = APIClient()
    resume = SimpleUploadedFile(
        "resume.pdf", b"%PDF-1.4", content_type="application/pdf"
    )
    created = client.post(
        "/api/public/careers/apply/",
        {
            "job_slug": job.slug,
            "full_name": "Jordan Applicant",
            "email": "jordan2@example.com",
            "resume": resume,
        },
        format="multipart",
    )
    reference = created.data["reference"]

    status_response = client.get(f"/api/public/careers/applications/{reference}/")
    assert status_response.status_code == 200
    assert status_response.data["status"] == "submitted"
    assert status_response.data["job_title"] == "PE Teacher"


@pytest.mark.django_db
def test_application_document_upload_and_list():
    client = APIClient()
    user = _register_applicant(client, "doc_applicant@example.com")

    create = client.post(
        "/api/admissions/applications/", VALID_APPLICATION_PAYLOAD, format="json"
    )
    assert create.status_code == 201
    app_id = create.data["id"]

    # Upload document
    pdf_file = SimpleUploadedFile(
        "birth_cert.pdf",
        b"%PDF-1.4 test document content",
        content_type="application/pdf",
    )
    upload_resp = client.post(
        f"/api/admissions/applications/{app_id}/documents/",
        {"document_type": "birth_certificate", "file": pdf_file},
        format="multipart",
    )
    assert upload_resp.status_code == 201
    assert upload_resp.data["document_type"] == "birth_certificate"
    assert "file" in upload_resp.data

    # List documents
    list_resp = client.get(f"/api/admissions/applications/{app_id}/documents/")
    assert list_resp.status_code == 200
    assert len(list_resp.data) == 1
    assert list_resp.data[0]["document_type"] == "birth_certificate"

    # Admin can view documents
    admin_user = User.objects.create_superuser(
        "admin_doc@example.com", "admin_doc@example.com", "Pass12345!"
    )
    admin_user.profile.role = "admin"
    admin_user.profile.save()
    admin_client = APIClient()
    admin_client.force_authenticate(user=admin_user)
    admin_list_resp = admin_client.get(
        f"/api/admissions/applications/{app_id}/documents/"
    )
    assert admin_list_resp.status_code == 200
    assert len(admin_list_resp.data) == 1
