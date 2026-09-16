from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    TEACHER = "teacher", "Teacher"
    STUDENT = "student", "Student"
    PARENT = "parent", "Parent"
    APPLICANT = "applicant", "Applicant"


phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-()]{7,20}$",
    message="Enter a valid phone number.",
)


class Profile(models.Model):
    """
    Extends the built-in User with role + contact info.
    One-to-one keeps Django's stock auth (admin, password reset,
    permission plumbing) untouched while giving us the role field
    every permission class in this project keys off of.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    school = models.ForeignKey(
        "core.School",
        on_delete=models.PROTECT,
        related_name="profiles",
        null=True,
        blank=True,
        help_text="Multi-tenancy scaffolding (Stage 13.5). Single-school deployments can leave this null; "
        "it is resolved to the default school on save.",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    teaching_position = models.CharField(max_length=100, blank=True)
    teaching_subjects = models.ManyToManyField(
        "academics.Subject", blank=True, related_name="teachers"
    )
    phone = models.CharField(max_length=20, validators=[phone_validator], blank=True)
    address = models.CharField(max_length=255, blank=True)
    dob = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)
    student_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text="Custom student identifier if assigned before enrollment",
    )
    email_verification_token = models.CharField(
        max_length=64, blank=True, null=True, unique=True
    )
    email_verification_token_expires = models.DateTimeField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["student_id"]),
            models.Index(fields=["email_verification_token"]),
        ]

    def save(self, *args, **kwargs):
        if self.school_id is None:
            from core.models import School

            self.school = School.get_default()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_username()} ({self.role})"

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_teacher(self):
        return self.role == Role.TEACHER

    @property
    def is_student(self):
        return self.role == Role.STUDENT

    @property
    def is_parent(self):
        return self.role == Role.PARENT


class AuditLog(models.Model):
    """
    Generic audit trail for sensitive mutations (grades, attendance,
    message deletions, logins, admissions).
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(
        max_length=100
    )  # e.g. "auth.login", "admission.move_to_payment"
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["model_name", "object_id"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.model_name}#{self.object_id} by {self.actor}"


class AdminNotificationType(models.TextChoices):
    STUDENT_REGISTERED = "student_registered", "Student Registered"
    APPLICATION_SUBMITTED = "application_submitted", "Application Submitted"
    DOCUMENT_UPLOADED = "document_uploaded", "Document Uploaded"
    PAYMENT_COMPLETED = "payment_completed", "Payment Completed"
    APPLICATION_UPDATED = "application_updated", "Application Updated"
    INFO = "info", "Information"


class AdminNotification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=AdminNotificationType.choices,
        default=AdminNotificationType.INFO,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_notifications",
    )
    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.CharField(max_length=64, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_read", "-created_at"]),
            models.Index(fields=["notification_type"]),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.title}"


class PortalNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portal_notifications",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, default="general")
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"Notification for {self.user}: {self.title}"


class RegistrationInvitation(models.Model):
    """
    Activation-token model for admin-triggered account provisioning
    (Stage 3: "Internal Account Provisioning"). This existed in the DB
    schema (migration 0003) but had been dropped from models.py in a prior
    version of this codebase without ever being wired to a view -- found
    while working the Stage 1 gap analysis. Restored here rather than
    deleted, since it's exactly the shape Stage 3 needs: an admin
    generates one of these for an approved applicant, emails the token,
    and the recipient uses it once to set their own password and activate
    the account. Not yet wired to any endpoint -- that's Stage 3's job.
    """

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    token = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registration_invitations",
    )
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "used" if self.used_at else "pending"
        return f"{self.email} ({self.role}, {status})"

    @property
    def is_expired(self):
        from django.utils import timezone
        from datetime import timedelta

        return timezone.now() > self.created_at + timedelta(days=7)

    @property
    def is_valid(self):
        return not self.used_at and not self.is_expired

    @classmethod
    def generate_token(cls):
        import secrets

        return secrets.token_urlsafe(32)
