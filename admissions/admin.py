from django.contrib import admin

from .models import AdmissionApplication, AdmissionDocument, ParentRelationshipRequest


class AdmissionDocumentInline(admin.TabularInline):
    model = AdmissionDocument
    extra = 0
    readonly_fields = ["uploaded_at"]


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "student_first_name",
        "student_last_name",
        "status",
        "class_applying_for",
        "created_at",
    ]
    list_filter = ["status", "academic_session"]
    search_fields = [
        "reference",
        "student_first_name",
        "student_last_name",
        "guardian_email",
    ]
    readonly_fields = ["reference", "created_at", "updated_at", "submitted_at"]
    inlines = [AdmissionDocumentInline]


@admin.register(ParentRelationshipRequest)
class ParentRelationshipRequestAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "child_full_name",
        "student_admission_number",
        "status",
        "created_at",
    ]
    list_filter = ["status"]
    search_fields = [
        "reference",
        "child_full_name",
        "student_admission_number",
        "email",
    ]
    readonly_fields = ["reference", "created_at", "updated_at"]
