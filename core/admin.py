from django.contrib import admin

from .models import School, Document


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_default", "is_active"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "owner",
        "is_public",
        "is_archived",
        "created_at",
    ]
    list_filter = ["category", "is_public", "is_archived"]
    search_fields = ["title"]
