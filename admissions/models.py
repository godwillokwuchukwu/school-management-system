from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class ApplicationStatus(models.TextChoices):
    """Mirrors Section 20's status list. Not every status is reachable
    through code yet (e.g. ASSESSMENT_SCHEDULED has no scheduling UI) --
    they exist so the status field never needs an incompatible migration
    later, and so the admin action set (see AdmissionApplicationViewSet)
    can grow into the full list without touching this model again."""

    STARTED = "started", "Application Started"
    SUBMITTED = "submitted", "Application Submitted"
    DOCUMENTS_PENDING = "documents_pending", "Documents Pending"
    PAYMENT_PENDING = "payment_pending", "Payment Pending"
    PAYMENT_CONFIRMED = "payment_confirmed", "Payment Confirmed"
    UNDER_REVIEW = "under_review", "Under Review"
    ASSESSMENT_SCHEDULED = "assessment_scheduled", "Assessment Scheduled"
    INTERVIEW_SCHEDULED = "interview_scheduled", "Interview Scheduled"
    INFO_REQUIRED = "info_required", "Additional Information Required"
    WAITLISTED = "waitlisted", "Waitlisted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    ADMISSION_OFFERED = "admission_offered", "Admission Offered"
    ENROLLMENT_PENDING = "enrollment_pending", "Enrollment Pending"
    ENROLLED = "enrolled", "Enrolled"


# Statuses an applicant is allowed to move their own application into.
# Everything else (approve/reject/waitlist/etc.) is an admin-only action.
APPLICANT_EDITABLE_STATUSES = {ApplicationStatus.STARTED}


class AdmissionApplication(models.Model):
    """
    The real, multi-part admission application (Section 19), superseding
    `public_site.AdmissionEnquiry`'s lead-capture role for anyone who has
    registered an Applicant account. `AdmissionEnquiry` remains for
    visitors who just want to ask a question before committing to a full
    application.
    """

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admission_applications",
    )
    reference = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    status = models.CharField(
        max_length=25,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.STARTED,
    )

    # --- Student information ---
    student_first_name = models.CharField(max_length=100)
    student_middle_name = models.CharField(max_length=100, blank=True)
    student_last_name = models.CharField(max_length=100)
    student_dob = models.DateField()
    student_gender = models.CharField(max_length=20, blank=True)
    student_nationality = models.CharField(max_length=100, blank=True)
    student_phone = models.CharField(max_length=30, blank=True)
    student_email = models.EmailField(blank=True)
    student_address = models.CharField(max_length=255, blank=True)
    previous_school = models.CharField(max_length=200, blank=True)
    previous_class = models.CharField(max_length=100, blank=True)
    class_applying_for = models.CharField(max_length=100)
    academic_session = models.CharField(max_length=20)

    # --- Guardian information ---
    guardian_full_name = models.CharField(max_length=200)
    guardian_relationship = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=30)
    guardian_email = models.EmailField()
    guardian_address = models.CharField(max_length=255, blank=True)

    # --- Review ---
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    decision_notes = models.TextField(blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference or '(draft)'} - {self.student_first_name} {self.student_last_name}"

    def generate_reference(self):
        from datetime import date

        year = date.today().year
        count = AdmissionApplication.objects.filter(
            reference__startswith=f"BFA-{year}"
        ).count()
        return f"BFA-{year}-{count + 1:06d}"


class ParentRelationshipStatus(models.TextChoices):
    PENDING = "pending", "Pending Verification"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"


class ParentRelationshipRequest(models.Model):
    """
    Section 2.6 / Section 23: a parent registers publicly identifying the
    student(s) they claim to be guardian of. This creates a PENDING
    relationship only -- it never auto-links to the student record and
    never grants portal access. An admin must verify it (Stage 3 turns a
    verified request into an actual provisioned Parent account, linked to
    the student via `Student.parents`).
    """

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parent_relationship_requests",
    )
    reference = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    student_admission_number = models.CharField(
        max_length=32,
        help_text="Admission number of the already-enrolled student, if known.",
    )
    child_full_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=ParentRelationshipStatus.choices,
        default=ParentRelationshipStatus.PENDING,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    decision_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            from datetime import date

            year = date.today().year
            count = ParentRelationshipRequest.objects.filter(
                reference__startswith=f"PGR-{year}"
            ).count()
            self.reference = f"PGR-{year}-{count + 1:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.reference} - {self.child_full_name} ({self.get_status_display()})"
        )


def admission_document_upload_path(instance, filename):
    return f"admissions/{instance.application.reference or instance.application_id}/{instance.document_type}/{filename}"


class DocumentType(models.TextChoices):
    BIRTH_CERTIFICATE = "birth_certificate", "Birth Certificate"
    PREVIOUS_REPORT = "previous_report", "Previous School Report"
    PASSPORT_PHOTO = "passport_photo", "Passport Photograph"
    IDENTIFICATION = "identification", "Identification Document"
    MEDICAL = "medical", "Medical Document"
    OTHER = "other", "Other Supporting Document"


ALLOWED_DOCUMENT_EXTENSIONS = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
MAX_DOCUMENT_SIZE_MB = 10


class AdmissionDocument(models.Model):
    application = models.ForeignKey(
        AdmissionApplication, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    file = models.FileField(
        upload_to=admission_document_upload_path,
        validators=[FileExtensionValidator(ALLOWED_DOCUMENT_EXTENSIONS)],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.application.reference}"
