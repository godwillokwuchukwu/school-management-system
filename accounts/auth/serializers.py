from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from accounts.models import Profile, Role
from students.models import Student

User = get_user_model()


class RoleAwareTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Embeds `role` in the JWT payload and supports authentication
    by Email OR Student ID / Admission Number."""

    def validate(self, attrs):
        username = attrs.get(self.username_field)
        if username:
            student = (
                Student.objects.filter(admission_number__iexact=username)
                .select_related("profile__user")
                .first()
            )
            if student and student.profile and student.profile.user:
                attrs[self.username_field] = student.profile.user.username
            else:
                profile = (
                    Profile.objects.filter(student_id__iexact=username)
                    .select_related("user")
                    .first()
                )
                if profile and profile.user:
                    attrs[self.username_field] = profile.user.username
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
    Dedicated Student Registration Serializer.
    Validates required fields, password strength, generates 24-hour verification token,
    and sets up Student/Profile.
    """

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=30)
    dob = serializers.DateField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    student_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    agree_terms = serializers.BooleanField(required=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        if not attrs.get("agree_terms"):
            raise serializers.ValidationError(
                {"agree_terms": "You must accept the terms and conditions."}
            )
        return attrs


class PublicApplicantRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        user.profile.phone = validated_data.get("phone", "")
        user.profile.role = Role.APPLICANT
        user.profile.save()
        return user


RegisterSerializer = PublicApplicantRegisterSerializer


class AccountActivationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, validators=[validate_password])


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
