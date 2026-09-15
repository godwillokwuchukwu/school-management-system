from django.contrib import admin

from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status", "marked_by")
    list_filter = ("status", "date")
    search_fields = (
        "student__profile__user__first_name",
        "student__profile__user__last_name",
    )
