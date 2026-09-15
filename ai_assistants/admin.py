from django.contrib import admin
from .models import AIAuditLog


@admin.register(AIAuditLog)
class AIAuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "assistant_type", "created_at"]
    list_filter = ["assistant_type"]
    search_fields = ["prompt"]
