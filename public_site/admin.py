from django.contrib import admin

from .models import (
    AdmissionEnquiry,
    ContactMessage,
    Event,
    FAQItem,
    JobApplication,
    JobPosting,
    NewsArticle,
    Program,
    SchoolProfile,
    Testimonial,
)


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SchoolProfile.objects.exists()


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_featured", "is_published", "published_at"]
    list_filter = ["category", "is_featured", "is_published"]
    search_fields = ["title", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "starts_at", "location", "is_published"]
    list_filter = ["is_published"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_published", "order"]
    list_filter = ["category", "is_published"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "is_published", "order"]


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ["question", "category", "is_published", "order"]
    list_filter = ["category", "is_published"]


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "department",
        "employment_type",
        "is_active",
        "application_deadline",
    ]
    list_filter = ["department", "employment_type", "is_active"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ["reference", "full_name", "job", "status", "created_at"]
    list_filter = ["status", "job"]
    readonly_fields = ["reference", "created_at"]


@admin.register(AdmissionEnquiry)
class AdmissionEnquiryAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "student_name",
        "class_applying_for",
        "status",
        "created_at",
    ]
    list_filter = ["status"]
    readonly_fields = ["reference", "created_at"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "topic", "subject", "is_read", "created_at"]
    list_filter = ["topic", "is_read"]
