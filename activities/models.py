from django.conf import settings
from django.db import models


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(
        "academics.Subject", on_delete=models.CASCADE, related_name="assignments"
    )
    school_class = models.ForeignKey(
        "academics.Class", on_delete=models.CASCADE, related_name="assignments"
    )
    due_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-due_date", "title"]

    def __str__(self):
        return f"{self.title} ({self.school_class})"


class AssignmentSubmissionStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    LATE = "late", "Late"
    GRADED = "graded", "Graded"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
    )
    content = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=AssignmentSubmissionStatus.choices,
        default=AssignmentSubmissionStatus.SUBMITTED,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"], name="uniq_assignment_submission"
            )
        ]

    def __str__(self):
        return f"{self.student} -> {self.assignment}"


class EventCategory(models.TextChoices):
    ACADEMIC = "academic", "Academic Calendar"
    HOLIDAY = "holiday", "Holiday"
    EXAM = "exam", "Exam"
    MEETING = "meeting", "Meeting"
    DEADLINE = "deadline", "Deadline"
    OTHER = "other", "Other"


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20, choices=EventCategory.choices, default=EventCategory.OTHER
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    school_class = models.ForeignKey(
        "academics.Class",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Target specific class",
    )
    is_school_wide = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.title} ({self.start_time.date()})"


class MeetingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELED = "canceled", "Canceled"
    COMPLETED = "completed", "Completed"


class ParentTeacherMeeting(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_meetings",
    )
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parent_meetings",
    )
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="meetings"
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=MeetingStatus.choices, default=MeetingStatus.PENDING
    )

    video_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"Meeting: {self.teacher} & {self.parent} (for {self.student})"
