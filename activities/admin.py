from django.contrib import admin

from .models import Assignment, AssignmentSubmission, Event, ParentTeacherMeeting


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "school_class", "due_date", "created_by")
    list_filter = ("subject", "school_class", "due_date")
    search_fields = ("title", "description")


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "status", "submitted_at")
    list_filter = ("status",)
    search_fields = (
        "student__profile__user__first_name",
        "student__profile__user__last_name",
        "assignment__title",
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "start_time", "end_time", "is_school_wide"]
    list_filter = ["category", "is_school_wide"]
    search_fields = ["title"]


@admin.register(ParentTeacherMeeting)
class ParentTeacherMeetingAdmin(admin.ModelAdmin):
    list_display = ["teacher", "parent", "student", "start_time", "status"]
    list_filter = ["status"]
