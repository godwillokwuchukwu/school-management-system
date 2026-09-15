from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Class(models.Model):
    """A section/cohort for one academic year, e.g. 'Grade 8B' / '2026'."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=9)  # e.g. "2025-2026"
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes_led",
    )
    subjects = models.ManyToManyField(Subject, related_name="classes", blank=True)

    class Meta:
        ordering = ["academic_year", "name"]
        # Business rule (Section 3.2 / 5): class code unique per academic_year
        constraints = [
            models.UniqueConstraint(
                fields=["code", "academic_year"], name="uniq_class_code_per_year"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.academic_year})"


class Enrollment(models.Model):
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="enrollments"
    )
    school_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="enrollments"
    )
    academic_year = models.CharField(max_length=9)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Business rule: no duplicate enrollment (student + class + year)
        constraints = [
            models.UniqueConstraint(
                fields=["student", "school_class", "academic_year"],
                name="uniq_enrollment_per_year",
            )
        ]

    def __str__(self):
        return f"{self.student} → {self.school_class} ({self.academic_year})"


class Grade(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="grades"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="grades"
    )
    # Business rule: score 0-100, enforced at DB level and in the serializer
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(score__gte=0) & models.Q(score__lte=100),
                name="grade_score_0_100",
            )
        ]

    @property
    def letter_grade(self):
        s = self.score
        if s >= 90:
            return "A"
        if s >= 80:
            return "B"
        if s >= 70:
            return "C"
        if s >= 60:
            return "D"
        return "F"

    def __str__(self):
        return f"{self.enrollment.student} — {self.subject.code}: {self.score}"


class ClassSchedule(models.Model):
    """
    Timetable entry representing a specific subject scheduled for a class.
    """

    school_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="schedules"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="schedules"
    )
    day_of_week = models.IntegerField(
        choices=[
            (1, "Monday"),
            (2, "Tuesday"),
            (3, "Wednesday"),
            (4, "Thursday"),
            (5, "Friday"),
            (6, "Saturday"),
            (7, "Sunday"),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.school_class} - {self.subject} ({self.get_day_of_week_display()} {self.start_time})"
