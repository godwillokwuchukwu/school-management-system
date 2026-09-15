import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\fees\models.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_models = """

class FeeSchedule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    academic_year = models.CharField(max_length=9)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-due_date"]

    def __str__(self):
        return f"{self.title} ({self.academic_year})"


class Payment(models.Model):
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    transaction_ref = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default="success")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment of {self.amount} for {self.fee} (Ref: {self.transaction_ref})"
"""

content += new_models

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
