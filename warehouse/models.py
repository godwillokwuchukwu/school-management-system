from django.db import models

# --- Dimensions ---


class DimStudent(models.Model):
    student_id = models.IntegerField(unique=True)  # Source system ID
    admission_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=20, blank=True)
    dob = models.DateField(null=True, blank=True)


class DimTeacher(models.Model):
    teacher_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    employee_id = models.CharField(max_length=50, blank=True)


class DimClass(models.Model):
    class_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=9)


class DimSubject(models.Model):
    subject_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)


class DimDate(models.Model):
    date = models.DateField(unique=True)
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    is_weekend = models.BooleanField()
    term = models.CharField(max_length=50, blank=True)


# --- Facts ---


class FactAttendance(models.Model):
    student = models.ForeignKey(DimStudent, on_delete=models.CASCADE)
    date = models.ForeignKey(DimDate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)  # present, absent, late

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "date"], name="uniq_fact_attendance"
            )
        ]


class FactAcademicPerformance(models.Model):
    student = models.ForeignKey(DimStudent, on_delete=models.CASCADE)
    subject = models.ForeignKey(DimSubject, on_delete=models.CASCADE)
    school_class = models.ForeignKey(DimClass, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    graded_at = models.DateField()


class FactPayment(models.Model):
    student = models.ForeignKey(DimStudent, on_delete=models.CASCADE)
    date = models.ForeignKey(DimDate, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_overdue = models.BooleanField(default=False)


# --- Data Quality ---
class DataQualityScore(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    overall_score = models.DecimalField(max_digits=5, decimal_places=2)  # 0-100
    student_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    attendance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    finance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    notes = models.TextField(blank=True)
