from django.conf import settings
from django.db import models


class ReportType(models.TextChoices):
    GRADE = "grade", "Grade Report"
    ATTENDANCE = "attendance", "Attendance Report"
    PERFORMANCE = "performance", "Performance Report"


class Report(models.Model):
    """
    Base model for generating and storing various reports on student performance,
    attendance, and academics.
    """

    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=ReportType.choices)
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
        help_text="If null, report is school-wide or for a class.",
    )
    school_class = models.ForeignKey(
        "academics.Class",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports_generated",
    )
    # JSON data for flexible report content
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["report_type", "student"]),
            models.Index(fields=["school_class"]),
        ]

    def __str__(self):
        target = f"for {self.student}" if self.student else f"for {self.school_class}"
        return f"{self.get_report_type_display()} {target}"
