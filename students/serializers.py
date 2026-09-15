import secrets
import string

from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model

from accounts.models import Role
from activities.models import Assignment

from .models import Student

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="profile.user_id", read_only=True)
    email = serializers.EmailField(source="profile.user.email", required=False)
    first_name = serializers.CharField(
        source="profile.user.first_name", required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source="profile.user.last_name", required=False, allow_blank=True
    )
    phone = serializers.CharField(
        source="profile.phone", required=False, allow_blank=True
    )
    full_name = serializers.CharField(
        source="profile.user.get_full_name", read_only=True
    )
    # Only ever populated in the response to the create() call that just
    # generated it (see to_representation) -- never persisted, never
    # available on subsequent reads. Without this, an admin-created
    # student's random temporary password was generated and then
    # discarded nowhere, permanently locking the new account out with no
    # way for anyone to learn the password and log in.
    temporary_password = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "admission_number",
            "dob",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "profile",
            "user_id",
            "temporary_password",
        ]
        read_only_fields = ["id", "full_name", "profile"]

    def get_temporary_password(self, instance):
        return getattr(instance, "_temporary_password", None)

    def validate_email(self, value):
        qs = User.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.profile.user_id)
        if qs.exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    @staticmethod
    def _temporary_password():
        alphabet = string.ascii_letters + string.digits
        return f"Student-{''.join(secrets.choice(alphabet) for _ in range(16))}!"

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop("profile", {})
        email = profile_data.get("user", {}).get("email")
        if not email:
            raise serializers.ValidationError({"email": "This field is required."})
        user_data = profile_data.pop("user", {})
        raw_password = self._temporary_password()
        user = User.objects.create_user(
            username=email,
            email=email,
            password=raw_password,
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
        )
        profile = user.profile
        profile.role = Role.STUDENT
        profile.phone = profile_data.get("phone", "")
        profile.save(update_fields=["role", "phone"])
        student = Student.objects.create(profile=profile, **validated_data)
        student._temporary_password = raw_password
        return student

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        user_data = profile_data.pop("user", {})
        user = instance.profile.user
        for field, value in user_data.items():
            setattr(user, field, value)
        if user_data:
            user.save(update_fields=list(user_data))
        for field, value in profile_data.items():
            setattr(instance.profile, field, value)
        if profile_data:
            instance.profile.save(update_fields=list(profile_data))
        return super().update(instance, validated_data)


class ParentChildSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="profile.user.get_full_name", read_only=True
    )
    email = serializers.EmailField(source="profile.user.email", read_only=True)
    attendance = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    reports = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    grades = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "full_name",
            "email",
            "admission_number",
            "attendance",
            "average_score",
            "reports",
            "teachers",
            "grades",
            "assignments",
        ]

    def get_attendance(self, obj):
        records = list(obj.attendance_records.values_list("status", flat=True))
        present = sum(status in {"present", "late"} for status in records)
        return {
            "total": len(records),
            "present": present,
            "percentage": round(present / len(records) * 100) if records else None,
        }

    def get_average_score(self, obj):
        scores = list(obj.enrollments.values_list("grades__score", flat=True))
        return round(sum(scores) / len(scores), 1) if scores else None

    def get_reports(self, obj):
        return list(obj.reports.values("id", "title", "report_type", "created_at"))

    def get_teachers(self, obj):
        teacher_ids = obj.enrollments.values_list(
            "school_class__class_teacher_id", flat=True
        ).distinct()
        users = get_user_model().objects.filter(id__in=teacher_ids)
        return [
            {"id": user.id, "name": user.get_full_name(), "email": user.email}
            for user in users
        ]

    def get_grades(self, obj):
        return list(
            obj.enrollments.values(
                "grades__id", "grades__score", "grades__subject__name"
            )
        )

    def get_assignments(self, obj):
        class_ids = obj.enrollments.values_list("school_class_id", flat=True)
        return list(
            Assignment.objects.filter(school_class_id__in=class_ids).values(
                "id", "title", "due_date"
            )
        )


class StudentRecipientSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="profile.user_id", read_only=True)
    full_name = serializers.CharField(
        source="profile.user.get_full_name", read_only=True
    )

    class Meta:
        model = Student
        fields = ["id", "user_id", "full_name", "admission_number"]
