from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class FeeStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"


class Fee(models.Model):
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="fees"
    )
    title = models.CharField(max_length=200)
    # Business rule: a fee owed can't be negative, enforced at DB level and
    # in the serializer (mirrors Grade.score's pattern in academics/models.py).
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    due_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=FeeStatus.choices, default=FeeStatus.PENDING
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fees_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "due_date", "title"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0), name="fee_amount_non_negative"
            ),
        ]

    def __str__(self):
        return f"{self.title} for {self.student}"


class FeeSchedule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    academic_year = models.CharField(max_length=9)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-due_date"]

    def __str__(self):
        return f"{self.title} ({self.academic_year})"


class Payment(models.Model):
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    transaction_ref = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default="success")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment of {self.amount} for {self.fee} (Ref: {self.transaction_ref})"
