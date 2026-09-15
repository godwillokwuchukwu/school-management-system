from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from accounts.models import Profile


def validate_dob(value):
    today = timezone.now().date()
    min_age_date = today - timezone.timedelta(days=3 * 365)
    if value > min_age_date:
        raise ValidationError("Student must be at least 3 years old.")


class Student(models.Model):
    """
    Minimal placeholder for Phase 1 (academics needs a Student FK for
    Enrollment/Grade). Admission workflow, document uploads, and guardian
    linkage are scoped for the dedicated students-app phase per Section 3.
    """

    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="student"
    )
    parents = models.ManyToManyField(Profile, related_name="children", blank=True)
    admission_number = models.CharField(max_length=32, unique=True)
    dob = models.DateField(validators=[validate_dob])

    class Meta:
        indexes = [models.Index(fields=["admission_number"])]

    def __str__(self):
        return f"{self.profile.user.get_full_name()} ({self.admission_number})"
