import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\communications\models.py"

new_models = """
from django.conf import settings
from django.db import models

class AnnouncementCategory(models.TextChoices):
    SCHOOL_WIDE = "school-wide", "School Wide"
    EMERGENCY = "emergency", "Emergency"
    ACADEMIC = "academic", "Academic"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=AnnouncementCategory.choices, default=AnnouncementCategory.SCHOOL_WIDE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="announcements_created")
    
    # Targeting
    target_all = models.BooleanField(default=False)
    target_students = models.BooleanField(default=False)
    target_teachers = models.BooleanField(default=False)
    target_parents = models.BooleanField(default=False)
    target_class = models.ForeignKey("academics.Class", on_delete=models.CASCADE, related_name="announcements", null=True, blank=True)
    target_grade = models.CharField(max_length=20, blank=True) # e.g. "Grade 8"
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.category})"


class Conversation(models.Model):
    subject = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.subject or f"Conversation {self.id}"


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    joined_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["conversation", "user"], name="uniq_conversation_participant")
        ]

    def __str__(self):
        return f"{self.user} in {self.conversation}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent")
    body = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Msg {self.id} by {self.sender}"


class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="message_attachments/")
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class MessageReadReceipt(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="read_receipts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="read_receipts")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["message", "user"], name="uniq_message_read_receipt")
        ]

    def __str__(self):
        return f"{self.user} read {self.message}"

"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_models)
