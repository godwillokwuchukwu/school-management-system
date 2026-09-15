from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient

from public_site.models import AdmissionEnquiry, JobPosting, NewsArticle


@pytest.mark.django_db
def test_school_profile_is_public():
    client = APIClient()
    response = client.get("/api/public/school/")
    assert response.status_code == 200
    assert response.data["name"] == "Riverside Academy"


@pytest.mark.django_db
def test_unpublished_news_is_not_listed():
    NewsArticle.objects.create(
        title="Draft article",
        body="...",
        is_published=False,
        published_at=timezone.now(),
    )
    published = NewsArticle.objects.create(
        title="Published article",
        body="...",
        is_published=True,
        published_at=timezone.now(),
    )

    client = APIClient()
    response = client.get("/api/public/news/")

    assert response.status_code == 200
    titles = [item["title"] for item in response.data["results"]]
    assert published.title in titles
    assert "Draft article" not in titles


@pytest.mark.django_db
def test_admission_enquiry_creates_reference_and_can_be_tracked():
    client = APIClient()
    payload = {
        "student_name": "Ada Lovelace",
        "class_applying_for": "Grade 7",
        "parent_name": "Grace Hopper",
        "parent_email": "grace@example.com",
        "parent_phone": "+1 555-0101",
        "message": "Interested in the STEM program.",
    }

    response = client.post("/api/public/admissions/enquiries/", payload, format="json")
    assert response.status_code == 201
    reference = response.data["reference"]
    assert reference.startswith("BFA-")

    status_response = client.get(f"/api/public/admissions/enquiries/{reference}/")
    assert status_response.status_code == 200
    assert status_response.data["status"] == "new"
    # Public status lookup must not leak the parent's contact details.
    assert "parent_email" not in status_response.data


@pytest.mark.django_db
def test_job_application_requires_valid_resume_type():
    job = JobPosting.objects.create(
        title="Mathematics Teacher", description="Teach math.", is_active=True
    )
    client = APIClient()
    bad_resume = SimpleUploadedFile(
        "resume.exe", b"not-a-real-resume", content_type="application/octet-stream"
    )

    response = client.post(
        "/api/public/careers/apply/",
        {
            "job_slug": job.slug,
            "full_name": "Jordan Applicant",
            "email": "jordan@example.com",
            "resume": bad_resume,
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert "resume" in response.data


@pytest.mark.django_db
def test_job_application_succeeds_with_valid_resume():
    job = JobPosting.objects.create(
        title="Mathematics Teacher", description="Teach math.", is_active=True
    )
    client = APIClient()
    resume = SimpleUploadedFile(
        "resume.pdf", b"%PDF-1.4 fake pdf bytes", content_type="application/pdf"
    )

    response = client.post(
        "/api/public/careers/apply/",
        {
            "job_slug": job.slug,
            "full_name": "Jordan Applicant",
            "email": "jordan@example.com",
            "resume": resume,
        },
        format="multipart",
    )

    assert response.status_code == 201
    assert response.data["reference"].startswith("EMP-")


@pytest.mark.django_db
def test_inactive_job_cannot_be_applied_to():
    job = JobPosting.objects.create(
        title="Old Posting", description="...", is_active=False
    )
    client = APIClient()
    resume = SimpleUploadedFile(
        "resume.pdf", b"%PDF-1.4", content_type="application/pdf"
    )

    response = client.post(
        "/api/public/careers/apply/",
        {
            "job_slug": job.slug,
            "full_name": "Someone",
            "email": "someone@example.com",
            "resume": resume,
        },
        format="multipart",
    )

    assert response.status_code == 400
