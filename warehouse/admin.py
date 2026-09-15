from django.contrib import admin
from .models import (
    DimStudent,
    DimTeacher,
    DimClass,
    DimSubject,
    DimDate,
    FactAttendance,
    FactAcademicPerformance,
    FactPayment,
    DataQualityScore,
)

admin.site.register(DimStudent)
admin.site.register(DimTeacher)
admin.site.register(DimClass)
admin.site.register(DimSubject)
admin.site.register(DimDate)
admin.site.register(FactAttendance)
admin.site.register(FactAcademicPerformance)
admin.site.register(FactPayment)


@admin.register(DataQualityScore)
class DataQualityScoreAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp",
        "overall_score",
        "student_score",
        "attendance_score",
        "finance_score",
    ]
