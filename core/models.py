from django.db import models
from django.utils.text import slugify


class School(models.Model):
    """
    Tenant root. Stage 1 runs a single-school deployment, but every
    school-owned model going forward should carry a FK to this table (see
    GAP_ANALYSIS_AND_ROADMAP.md item #69 / Stage 13.5) so multi-tenancy is
    a matter of *enabling* isolation later, not retrofitting it.

    `is_default` marks the school used when a request/record doesn't
    otherwise specify one -- true multi-tenant routing (subdomain/tenant
    middleware) is explicitly out of scope until Stage 13.
    """

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    domain = models.CharField(
        max_length=200, blank=True, help_text="Reserved for future subdomain routing."
    )
    is_default = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:100]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @classmethod
    def get_default(cls):
        school = cls.objects.filter(is_default=True).first()
        if school:
            return school
        return cls.objects.create(name="Riverside Academy", is_default=True)


import os
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_file_size(value):
    limit = 10 * 1024 * 1024  # 10 MB
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 10 MiB.")


def malware_scan_stub(file):
    # Stubbed malware scanner
    # A real implementation would send the file to an AV engine (e.g. ClamAV)
    return True


class DocumentCategory(models.TextChoices):
    ADMISSION = "admission", "Admission"
    STUDENT_RECORD = "student_record", "Student Record"
    TEACHER_RECORD = "teacher_record", "Teacher Record"
    POLICY = "policy", "Policy"
    REPORT_CARD = "report_card", "Report Card"
    INVOICE = "invoice", "Invoice"
    RECEIPT = "receipt", "Receipt"
    OTHER = "other", "Other"


class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to="documents/%Y/%m/", validators=[validate_file_size]
    )
    category = models.CharField(
        max_length=20, choices=DocumentCategory.choices, default=DocumentCategory.OTHER
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_documents",
        null=True,
        blank=True,
    )
    mime_type = models.CharField(max_length=100, blank=True)
    is_archived = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)

    # Permission scoping
    is_public = models.BooleanField(
        default=False, help_text="Can be accessed by anyone with a signed URL"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} (v{self.version})"

    def clean(self):
        super().clean()
        if self.file:
            # Extension validation
            valid_extensions = [
                ".pdf",
                ".doc",
                ".docx",
                ".png",
                ".jpg",
                ".jpeg",
                ".txt",
            ]
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(
                    f"Unsupported file extension. Allowed: {', '.join(valid_extensions)}"
                )

            # Malware scanning stub
            if not malware_scan_stub(self.file):
                raise ValidationError("File failed malware scan.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
