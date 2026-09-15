from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("admission_number", "profile", "dob")
    search_fields = (
        "admission_number",
        "profile__user__first_name",
        "profile__user__last_name",
        "profile__user__email",
    )
    filter_horizontal = ("parents",)
