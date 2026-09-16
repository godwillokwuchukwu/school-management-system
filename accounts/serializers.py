from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import default_token_generator

from .models import AdminNotification, AuditLog, PortalNotification, Profile, Role
from academics.models import Subject
from students.models import Student

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(
        source="user.first_name", required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source="user.last_name", required=False, allow_blank=True
    )
    teaching_subjects = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), many=True, required=False
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "address",
            "dob",
            "photo",
            "teaching_position",
            "teaching_subjects",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "role", "created_at", "updated_at"]
        # role is intentionally read-only here: role changes are an admin
        # action (separate endpoint), not something a user can self-serve.

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        teaching_subjects = validated_data.pop("teaching_subjects", None)
        request = self.context.get("request")
        request_profile = getattr(getattr(request, "user", None), "profile", None)
        if teaching_subjects is not None and not getattr(
            request_profile, "is_admin", False
        ):
            raise serializers.ValidationError(
                {
                    "teaching_subjects": "Only an administrator can assign teaching subjects."
                }
            )
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save(update_fields=list(user_data) or None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if teaching_subjects is not None:
            instance.teaching_subjects.set(teaching_subjects)
        return instance


class PublicApplicantRegisterSerializer(serializers.Serializer):
    """
    STAGE 2: the only account creation the public, unauthenticated
    `/api/auth/register/` endpoint is allowed to perform. Creates a
    `Profile(role=applicant)` -- an account that can track its own
    admission/employment applications and upload documents, but has no
    reach into any `/portal/*`-equivalent (admin/teacher/student/parent)
    functionality. See `accounts.permissions.IsApplicant` and the
    `admissions` app, which is the only thing that grants this role any
    real capability.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        phone = validated_data.pop("phone", "")
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=password,
        )
        profile = user.profile
        profile.role = Role.APPLICANT
        profile.phone = phone
        profile.save(update_fields=["role", "phone"])
        return user


class RegisterSerializer(serializers.Serializer):
    """
    STAGE 1 FIX (see GAP_ANALYSIS_AND_ROADMAP.md item #2 / Stage 0.3):
    this serializer used to be reachable from the public, unauthenticated
    `/api/auth/register/` endpoint and would mint a *live* portal account
    for any role a client requested -- a direct violation of the platform's
    non-negotiable rule that only an authorized administrator can provision
    an internal account (Stage 1 / Stage 3).

    It is kept here, but is now ONLY reachable through
    `AdminProvisionAccountView`, which requires `IsAdmin`. The public
    `/api/auth/register/` endpoint itself is disabled (see `RegisterView`
    below) until Stage 2 replaces it with a real Applicant Profile flow
    that does not, by itself, grant any portal access.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=Role.choices)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    child_emails = serializers.ListField(
        child=serializers.EmailField(), required=False, write_only=True
    )
    teaching_position = serializers.CharField(
        max_length=100, required=False, allow_blank=True, write_only=True
    )
    subject_ids = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), many=True, required=False, write_only=True
    )
    dob = serializers.DateField(
        required=False, write_only=True, help_text="Required when role is student."
    )

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    def validate(self, attrs):
        if attrs.get("role") == Role.TEACHER:
            attrs["teaching_position"] = attrs.get("teaching_position") or "Teacher"
        if attrs.get("role") == Role.STUDENT and not attrs.get("dob"):
            # Enrollment/Grade/Attendance/Fee all FK to students.Student, not
            # to Profile/User directly. Without a Student row here, a
            # self-registered student is a "ghost" account: it can never be
            # enrolled, graded, marked present/absent, or linked by a parent.
            raise serializers.ValidationError(
                {"dob": "Date of birth is required to register as a student."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data.pop("role")
        phone = validated_data.pop("phone", "")
        child_emails = validated_data.pop("child_emails", [])
        teaching_position = validated_data.pop("teaching_position", "")
        subject_ids = validated_data.pop("subject_ids", [])
        dob = validated_data.pop("dob", None)
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=password,
        )
        # signals.ensure_profile_exists already created a default Profile;
        # update it with the real role/phone rather than creating a second one.
        profile = user.profile
        profile.role = role
        profile.phone = phone
        profile.teaching_position = teaching_position if role == Role.TEACHER else ""
        profile.save(update_fields=["role", "phone", "teaching_position"])
        if role == Role.TEACHER:
            profile.teaching_subjects.set(subject_ids)
        if role == Role.STUDENT:
            # Enrollment/Grade/AttendanceRecord/Fee/AssignmentSubmission all
            # FK to students.Student, not to Profile/User. The admission
            # number is normally assigned by the school; self-registration
            # can't know it yet, so we issue a placeholder the office can
            # correct later via the admin student directory.
            Student.objects.create(
                profile=profile,
                admission_number=f"PENDING-{user.id}",
                dob=dob,
            )
        if role == Role.PARENT and child_emails:
            profile.children.add(
                *Student.objects.filter(profile__user__email__in=child_emails)
            )
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )

    def validate(self, attrs):
        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(attrs["uid"])))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(
                {"token": "This password reset link is invalid or expired."}
            )
        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError(
                {"token": "This password reset link is invalid or expired."}
            )
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class RoleAwareTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Embeds `role` in the JWT payload and supports authentication
    by Email OR Student ID / Admission Number."""

    def validate(self, attrs):
        username = attrs.get(self.username_field)
        if username:
            # 1. Check if identifier is a Student admission number
            student = (
                Student.objects.filter(admission_number__iexact=username)
                .select_related("profile__user")
                .first()
            )
            if student and student.profile and student.profile.user:
                attrs[self.username_field] = student.profile.user.username
            else:
                # 2. Check if identifier is a Profile student_id
                profile = (
                    Profile.objects.filter(student_id__iexact=username)
                    .select_related("user")
                    .first()
                )
                if profile and profile.user:
                    attrs[self.username_field] = profile.user.username
                else:
                    # 3. Check if identifier is an email address
                    user_by_email = User.objects.filter(
                        email__iexact=username
                    ).first()
                    if user_by_email:
                        attrs[self.username_field] = user_by_email.username
        data = super().validate(attrs)
        data["role"] = getattr(getattr(self.user, "profile", None), "role", None)
        data["email"] = self.user.email
        data["user_id"] = self.user.id
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = getattr(getattr(user, "profile", None), "role", None)
        token["email"] = user.email
        return token


class StudentRegisterSerializer(serializers.Serializer):
    """
    Dedicated Student Registration Serializer (Section 9 & 11).
    Validates required fields, password strength, generates 24-hour verification token,
    and sets up Student/Profile.
    """

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    dob = serializers.DateField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    student_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    agree_terms = serializers.BooleanField(required=True)

    def validate_email(self, value):
        val = value.lower().strip()
        if User.objects.filter(email__iexact=val).exists():
            raise serializers.ValidationError(
                "An account with this email address already exists."
            )
        return val

    def validate_student_id(self, value):
        if value and value.strip():
            val = value.strip()
            from accounts.models import Profile

            if Profile.objects.filter(student_id=val).exists():
                raise serializers.ValidationError(
                    "This student ID is already in use."
                )
            if Student.objects.filter(admission_number=val).exists():
                raise serializers.ValidationError(
                    "This student ID is already associated with another account."
                )
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        if not attrs.get("agree_terms"):
            raise serializers.ValidationError(
                {
                    "agree_terms": "You must agree to the Terms of Service and Privacy Policy."
                }
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        import secrets
        from datetime import timedelta
        from django.utils import timezone
        from accounts.models import AdminNotificationType
        from services import email_service, notification_service

        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]
        email = validated_data["email"]
        phone = validated_data["phone"]
        dob = validated_data["dob"]
        password = validated_data["password"]
        student_id = validated_data.get("student_id", "").strip() or None

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        verification_token = secrets.token_urlsafe(32)
        token_expires = timezone.now() + timedelta(hours=24)

        profile = user.profile
        profile.role = Role.STUDENT
        profile.phone = phone
        profile.dob = dob
        profile.student_id = student_id
        profile.email_verification_token = verification_token
        profile.email_verification_token_expires = token_expires
        profile.save()

        # Create or link student record
        admission_num = student_id or f"ADM-{timezone.now().year}-{user.id:04d}"
        Student.objects.get_or_create(
            profile=profile,
            defaults={"admission_number": admission_num, "dob": dob},
        )

        # Notify admin of new student registration
        notification_service.notify_admin(
            title="New Student Registered",
            message=f"{first_name} {last_name} ({email}) created a student account.",
            notification_type=AdminNotificationType.STUDENT_REGISTERED,
            object_instance=user,
            user=user,
        )

        # Dispatch verification email (non-blocking)
        request = self.context.get("request")
        email_service.send_verification_email(user, verification_token, request=request)

        return user


class AdminNotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AdminNotification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "user",
            "user_name",
            "object_id",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username if obj.user else "System"


class PortalNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalNotification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "link",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "actor",
            "actor_name",
            "action",
            "model_name",
            "object_id",
            "description",
            "ip_address",
            "user_agent",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_actor_name(self, obj):
        return (
            obj.actor.get_full_name() or obj.actor.username if obj.actor else "System"
        )
