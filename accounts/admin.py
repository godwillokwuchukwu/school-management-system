from django.contrib import admin

from .models import (
    AdminNotification,
    AuditLog,
    PortalNotification,
    Profile,
    RegistrationInvitation,
)


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "notification_type", "user", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message", "user__email")
    actions = ["mark_as_read"]

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Mark selected notifications as read"


@admin.register(PortalNotification)
class PortalNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message", "user__email")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "student_id",
        "phone",
        "email_verified_at",
        "created_at",
    )
    list_filter = ("role",)
    search_fields = ("user__email", "user__username", "student_id", "phone")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "actor",
        "action",
        "model_name",
        "object_id",
        "description",
        "ip_address",
    )
    list_filter = ("action", "model_name")
    search_fields = ("object_id", "actor__email", "description")
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
