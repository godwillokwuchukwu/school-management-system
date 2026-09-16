import uuid
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts import audit
from accounts.models import (
    AdminNotification,
    AdminNotificationType,
    Profile,
    RegistrationInvitation,
    Role,
)
from accounts.auth.serializers import (
    AccountActivationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PublicApplicantRegisterSerializer,
    RoleAwareTokenObtainPairSerializer,
    StudentRegisterSerializer,
)
from services import email_service, notification_service
from students.models import Student

User = get_user_model()


class LoginView(TokenObtainPairView):
    """
    Standard and Student Portal Login.
    Supports Email or Student ID / Admission Number.
    """

    serializer_class = RoleAwareTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            identifier = request.data.get("username", "")
            user = (
                User.objects.filter(username__iexact=identifier).first()
                or User.objects.filter(email__iexact=identifier).first()
            )
            if not user:
                student = (
                    Student.objects.filter(admission_number__iexact=identifier)
                    .select_related("profile__user")
                    .first()
                )
                if student and student.profile:
                    user = student.profile.user
            if user:
                audit.record(
                    actor=user,
                    action="auth.login",
                    instance=user,
                    description=f"Successful login for {user.username}",
                    request=request,
                )
                email_service.send_login_notification(user, request=request)
        return response


class StudentRegisterView(APIView):
    """
    Student Self-Registration Portal View.
    Validates info, sets profile, sends verification email, creates admin notification.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.create_user(
            username=data["email"],
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        verification_token = str(uuid.uuid4())
        token_expires = timezone.now() + timedelta(hours=24)

        profile = user.profile
        profile.role = Role.STUDENT
        profile.phone = data["phone"]
        profile.student_id = (
            data.get("student_id", "") or f"RVS-{timezone.now().year}-{user.id:04d}"
        )
        profile.email_verification_token = verification_token
        profile.email_verification_token_expires = token_expires
        profile.save()

        Student.objects.get_or_create(
            profile=profile,
            defaults={
                "dob": data["dob"],
                "admission_number": profile.student_id,
            },
        )

        audit.record(
            actor=user,
            action="auth.student_registered",
            instance=user,
            description=f"Student registration for {user.get_full_name()} ({user.email})",
            request=request,
        )

        email_service.send_verification_email(user, verification_token, request=request)

        notification_service.notify_admin(
            notification_type=AdminNotificationType.STUDENT_REGISTERED,
            message=f"New student registration: {user.get_full_name()} ({user.email}, ID: {profile.student_id})",
            user=user,
        )

        return Response(
            {
                "status": "success",
                "message": "Account created successfully. Please check your email to verify your account within 24 hours.",
                "user_id": user.id,
                "email": user.email,
                "student_id": profile.student_id,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    """Verifies student email via 24-hour token."""

    permission_classes = [AllowAny]

    def get(self, request, token):
        profile = (
            Profile.objects.filter(email_verification_token=token)
            .select_related("user")
            .first()
        )
        if not profile:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid or already used verification token.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            profile.email_verification_token_expires
            and timezone.now() > profile.email_verification_token_expires
        ):
            return Response(
                {
                    "status": "expired",
                    "message": "Verification token has expired. Please request a new verification link.",
                    "email": profile.user.email,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile.email_verified_at = timezone.now()
        profile.email_verification_token = None
        profile.email_verification_token_expires = None
        profile.save()

        audit.record(
            actor=profile.user,
            action="auth.email_verified",
            instance=profile.user,
            description=f"Email verified for {profile.user.email}",
            request=request,
        )

        return Response(
            {
                "status": "success",
                "message": "Email verified successfully. You can now log in to the student portal.",
            },
            status=status.HTTP_200_OK,
        )


class ResendVerificationView(APIView):
    """Resends email verification token."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        if not email:
            return Response(
                {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email__iexact=email).first()
        if not user or not hasattr(user, "profile"):
            return Response(
                {
                    "status": "success",
                    "message": "If an account exists with this email, a verification link has been sent.",
                },
                status=status.HTTP_200_OK,
            )

        if user.profile.email_verified_at:
            return Response(
                {
                    "status": "already_verified",
                    "message": "This account email has already been verified. You can log in directly.",
                },
                status=status.HTTP_200_OK,
            )

        verification_token = str(uuid.uuid4())
        user.profile.email_verification_token = verification_token
        user.profile.email_verification_token_expires = timezone.now() + timedelta(
            hours=24
        )
        user.profile.save()

        email_service.send_verification_email(user, verification_token, request=request)

        return Response(
            {
                "status": "success",
                "message": "A new verification link has been sent to your email address.",
            },
            status=status.HTTP_200_OK,
        )


class RegisterView(generics.CreateAPIView):
    """Public Applicant Register View."""

    serializer_class = PublicApplicantRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"id": user.id, "email": user.email, "role": user.profile.role},
            status=status.HTTP_201_CREATED,
        )


PublicApplicantRegisterView = RegisterView


class ActivateAccountView(APIView):
    """Activates invited accounts."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AccountActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            invitation = RegistrationInvitation.objects.get(token=token)
        except RegistrationInvitation.DoesNotExist:
            return Response(
                {"detail": "Invalid activation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if invitation.is_expired:
            return Response(
                {"detail": "This activation link has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=invitation.email,
            email=invitation.email,
            password=password,
            first_name=invitation.first_name,
            last_name=invitation.last_name,
        )
        user.profile.role = invitation.role
        user.profile.save()

        invitation.mark_used()
        audit.record(
            actor=user,
            action="account.activated",
            instance=user,
            description=f"Account activated for {user.email} with role {user.profile.role}",
            request=request,
        )

        return Response(
            {"detail": "Account activated successfully."}, status=status.HTTP_200_OK
        )


AccountActivateView = ActivateAccountView


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        user = User.objects.filter(email__iexact=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            frontend_url = getattr(settings, "FRONTEND_URL", "http://127.0.0.1:5173")
            reset_url = f"{frontend_url}/reset-password?uid={uid}&token={token}"
            try:
                send_mail(
                    "Password Reset Request",
                    f"Use this link to reset your password: {reset_url}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception:
                pass

        return Response(
            {
                "detail": "If the email is registered, you will receive password reset instructions."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = urlsafe_base64_decode(serializer.validated_data["uidb64"]).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response(
                {"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST
            )

        token = serializer.validated_data["token"]
        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        audit.record(
            actor=user,
            action="account.password_reset",
            instance=user,
            description=f"Password reset completed for {user.email}",
            request=request,
        )
        return Response(
            {"detail": "Password reset successful. You can now log in."},
            status=status.HTTP_200_OK,
        )
