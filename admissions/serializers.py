from rest_framework import serializers

from .models import (
    MAX_DOCUMENT_SIZE_MB,
    AdmissionApplication,
    AdmissionDocument,
    ApplicationStatus,
    ParentRelationshipRequest,
    ParentRelationshipStatus,
)


class AdmissionDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionDocument
        fields = ["id", "document_type", "file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]

    def validate_file(self, value):
        if value.size > MAX_DOCUMENT_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f"File must be smaller than {MAX_DOCUMENT_SIZE_MB}MB."
            )
        return value


class AdmissionApplicationWriteSerializer(serializers.ModelSerializer):
    """Used by the applicant to create/update their OWN application while
    it's still a draft (status=started). Status/reference/review fields
    are never settable here -- see AdmissionApplicationDecisionSerializer
    for the admin-only counterpart."""

    class Meta:
        model = AdmissionApplication
        fields = [
            "id",
            "reference",
            "status",
            "student_first_name",
            "student_middle_name",
            "student_last_name",
            "student_dob",
            "student_gender",
            "student_nationality",
            "student_phone",
            "student_email",
            "student_address",
            "previous_school",
            "previous_class",
            "class_applying_for",
            "academic_session",
            "guardian_full_name",
            "guardian_relationship",
            "guardian_phone",
            "guardian_email",
            "guardian_address",
            "submitted_at",
            "created_at",
        ]
        read_only_fields = ["reference", "status", "submitted_at", "created_at"]


class AdmissionApplicationDetailSerializer(serializers.ModelSerializer):
    documents = AdmissionDocumentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AdmissionApplication
        fields = [
            "id",
            "reference",
            "status",
            "status_display",
            "student_first_name",
            "student_middle_name",
            "student_last_name",
            "student_dob",
            "student_gender",
            "student_nationality",
            "student_phone",
            "student_email",
            "student_address",
            "previous_school",
            "previous_class",
            "class_applying_for",
            "academic_session",
            "guardian_full_name",
            "guardian_relationship",
            "guardian_phone",
            "guardian_email",
            "guardian_address",
            "documents",
            "submitted_at",
            "created_at",
            "updated_at",
        ]


class AdmissionApplicationAdminListSerializer(serializers.ModelSerializer):
    applicant_email = serializers.EmailField(source="applicant.email", read_only=True)

    class Meta:
        model = AdmissionApplication
        fields = [
            "id",
            "reference",
            "status",
            "applicant_email",
            "student_first_name",
            "student_last_name",
            "class_applying_for",
            "academic_session",
            "submitted_at",
            "created_at",
        ]


class AdmissionApplicationPublicStatusSerializer(serializers.ModelSerializer):
    """Public, unauthenticated reference lookup (Section 20). Deliberately
    excludes guardian contact details and any other PII beyond the
    student's name -- same principle as public_site.AdmissionEnquiryStatusSerializer."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AdmissionApplication
        fields = [
            "reference",
            "status",
            "status_display",
            "student_first_name",
            "student_last_name",
            "class_applying_for",
            "submitted_at",
        ]


class AdmissionApplicationDecisionSerializer(serializers.Serializer):
    """Admin-only status transition, e.g. Under Review -> Approved."""

    status = serializers.ChoiceField(choices=ApplicationStatus.choices)
    decision_notes = serializers.CharField(required=False, allow_blank=True)


class ParentRelationshipRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentRelationshipRequest
        fields = [
            "id",
            "reference",
            "status",
            "student_admission_number",
            "child_full_name",
            "relationship",
            "phone",
            "email",
            "message",
            "created_at",
        ]
        read_only_fields = ["reference", "status", "created_at"]


class ParentRelationshipRequestAdminSerializer(serializers.ModelSerializer):
    applicant_email = serializers.EmailField(source="applicant.email", read_only=True)
    # Surfaced so an admin can see at a glance whether the admission number
    # actually matches an enrolled student before verifying -- verification
    # is still a human decision, this is just supporting information.
    matching_student_exists = serializers.SerializerMethodField()

    class Meta:
        model = ParentRelationshipRequest
        fields = [
            "id",
            "reference",
            "status",
            "applicant_email",
            "student_admission_number",
            "child_full_name",
            "relationship",
            "phone",
            "email",
            "message",
            "matching_student_exists",
            "decision_notes",
            "created_at",
        ]

    def get_matching_student_exists(self, obj):
        from students.models import Student

        return Student.objects.filter(
            admission_number=obj.student_admission_number
        ).exists()


class ParentRelationshipRequestDecisionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ParentRelationshipStatus.choices)
    decision_notes = serializers.CharField(required=False, allow_blank=True)
