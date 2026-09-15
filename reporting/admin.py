from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "report_type",
        "student",
        "school_class",
        "generated_by",
        "created_at",
    )
    list_filter = ("report_type",)
    search_fields = (
        "title",
        "student__profile__user__first_name",
        "student__profile__user__last_name",
    )
