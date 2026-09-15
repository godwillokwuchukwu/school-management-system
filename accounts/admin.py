from django.contrib import admin

from .models import AuditLog, Profile, RegistrationInvitation


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "created_at")
    list_filter = ("role",)
    search_fields = ("user__email", "user__username", "phone")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "actor",
        "action",
        "model_name",
        "object_id",
        "ip_address",
    )
    list_filter = ("action", "model_name")
    search_fields = ("object_id", "actor__email")
    readonly_fields = [f.name for f in AuditLog._meta.fields]


@admin.register(RegistrationInvitation)
class RegistrationInvitationAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "role",
        "created_by",
        "created_at",
        "used_at",
        "is_expired",
    ]
    list_filter = ["role"]
    search_fields = ["email"]
