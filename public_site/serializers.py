from rest_framework import serializers

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


class SchoolProfileSerializer(serializers.ModelSerializer):
    years_of_excellence = serializers.ReadOnlyField()

    class Meta:
        model = SchoolProfile
        fields = [
            "name",
            "tagline",
            "hero_heading",
            "hero_subtext",
            "mission",
            "vision",
            "history",
            "core_values",
            "founded_year",
            "years_of_excellence",
            "total_students",
            "total_teachers",
            "graduation_rate",
            "address",
            "phone",
            "email",
            "emergency_phone",
            "office_hours",
            "map_embed_url",
            "facebook_url",
            "twitter_url",
            "instagram_url",
            "linkedin_url",
        ]


class NewsArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "category",
            "cover_image_url",
            "is_featured",
            "published_at",
        ]


class NewsArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "body",
            "category",
            "cover_image_url",
            "is_featured",
            "published_at",
        ]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "category",
            "cover_image_url",
            "location",
            "starts_at",
            "ends_at",
            "registration_url",
        ]


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "summary",
            "description",
            "image_url",
        ]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["id", "name", "role", "quote", "photo_url"]


class FAQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQItem
        fields = ["id", "question", "answer", "category"]


class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = [
            "id",
            "title",
            "slug",
            "department",
            "employment_type",
            "location",
            "description",
            "requirements",
            "application_deadline",
        ]


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    job_slug = serializers.SlugRelatedField(
        source="job",
        slug_field="slug",
        queryset=JobPosting.objects.filter(is_active=True),
    )

    class Meta:
        model = JobApplication
        fields = [
            "reference",
            "job_slug",
            "full_name",
            "email",
            "phone",
            "qualifications",
            "years_of_experience",
            "cover_letter",
            "resume",
        ]
        read_only_fields = ["reference"]

    def validate_resume(self, value):
        max_mb = 10
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"Resume must be smaller than {max_mb}MB."
            )
        allowed_ext = (".pdf", ".doc", ".docx")
        if not value.name.lower().endswith(allowed_ext):
            raise serializers.ValidationError("Resume must be a PDF or Word document.")
        return value


class JobApplicationStatusSerializer(serializers.ModelSerializer):
    """Public, unauthenticated reference lookup for a job application
    (Section 22 / Stage 2.5's 'independent status tracking'), stripped of
    PII beyond the applicant's own name."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "reference",
            "status",
            "status_display",
            "job_title",
            "full_name",
            "created_at",
        ]


class AdmissionEnquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionEnquiry
        fields = [
            "reference",
            "student_name",
            "student_dob",
            "class_applying_for",
            "academic_session",
            "parent_name",
            "parent_email",
            "parent_phone",
            "message",
        ]
        read_only_fields = ["reference"]


class AdmissionEnquiryStatusSerializer(serializers.ModelSerializer):
    """Public-facing status lookup by reference -- deliberately excludes
    contact details of other people and any internal-only fields."""

    class Meta:
        model = AdmissionEnquiry
        fields = [
            "reference",
            "student_name",
            "class_applying_for",
            "status",
            "created_at",
        ]


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "topic", "subject", "message"]
