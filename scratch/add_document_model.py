import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\core\models.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_models = """

import os
from django.conf import settings
from django.core.exceptions import ValidationError

def validate_file_size(value):
    limit = 10 * 1024 * 1024 # 10 MB
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 10 MiB.')

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
    file = models.FileField(upload_to="documents/%Y/%m/", validators=[validate_file_size])
    category = models.CharField(max_length=20, choices=DocumentCategory.choices, default=DocumentCategory.OTHER)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_documents", null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    is_archived = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)
    
    # Permission scoping
    is_public = models.BooleanField(default=False, help_text="Can be accessed by anyone with a signed URL")
    
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
            valid_extensions = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.txt']
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(f"Unsupported file extension. Allowed: {', '.join(valid_extensions)}")
            
            # Malware scanning stub
            if not malware_scan_stub(self.file):
                raise ValidationError("File failed malware scan.")
                
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
"""

content += new_models

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
