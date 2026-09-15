from django.contrib import admin

from .models import Class, Enrollment, Grade, Subject, ClassSchedule

admin.site.register(Subject)
admin.site.register(Class)
admin.site.register(Enrollment)
admin.site.register(Grade)


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "school_class",
        "subject",
        "day_of_week",
        "start_time",
        "end_time",
        "room",
    ]
    list_filter = ["day_of_week", "school_class"]
