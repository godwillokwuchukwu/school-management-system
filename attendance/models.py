from django.conf import settings
from django.db import models

from students.models import Student


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    EXCUSED = "excused", "Excused"


class AttendanceRecord(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="attendance_records"
    )
    date = models.DateField()
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_marked",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "student__id"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "date"], name="uniq_attendance_student_day"
            )
        ]

    def __str__(self):
        return f"{self.student} — {self.date}: {self.status}"
