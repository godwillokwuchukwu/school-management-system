from django.conf import settings
from django.db import models


class AIAuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assistant_type = models.CharField(
        max_length=50
    )  # 'chatbot', 'teacher', 'admin', 'explainer'
    prompt = models.TextField()
    response = models.TextField()
    context_used = models.TextField(blank=True)  # RAG context
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.assistant_type} query by {self.user} at {self.created_at}"
