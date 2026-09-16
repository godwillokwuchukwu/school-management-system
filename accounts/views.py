from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
import logging

from . import audit
from .models import (
    AdminNotification,
    AuditLog,
    PortalNotification,
    Profile,
    RegistrationInvitation,
)
from .permissions import IsAdmin, IsOwnerOrAdmin
from .serializers import (
    AdminNotificationSerializer,
    AuditLogSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PortalNotificationSerializer,
    ProfileSerializer,
    PublicApplicantRegisterSerializer,
    RegisterSerializer,
    RoleAwareTokenObtainPairSerializer,
    StudentRegisterSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    serializer_class = RoleAwareTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            from services import email_service

            identifier = request.data.get("username", "")
            user = (
                User.objects.filter(username__iexact=identifier).first()
                or User.objects.filter(email__iexact=identifier).first()
            )
            if not user:
                from students.models import Student

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


class RegisterView(generics.CreateAPIView):
    """
    STAGE 1 FIX + STAGE 2: public self-registration used to create a live,
    fully-functional portal account for whatever role the client
    requested -- a direct violation of the platform's non-negotiable rule
    that only an authorized administrator can provision an internal
    account (see GAP_ANALYSIS_AND_ROADMAP.md item #2).

    It is now restricted to creating an *Applicant* account only --
    tracking-only access to the public admissions/employment application
    flow (`accounts.permissions.IsApplicant`, the `admissions` app), never
    Student/Teacher/Parent/Admin. Real internal accounts are only ever
    created through `AdminProvisionAccountView` below.
    """

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


class AdminProvisionAccountView(generics.CreateAPIView):
    # This was the old provisioning view. Now it just creates invitations if used directly.
    permission_classes = [IsAdmin]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "admin_sensitive"

    def post(self, request):
        email = request.data.get("email")
        role = request.data.get("role")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        if not email or not role:
            return Response({"detail": "Email and role required."}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"detail": "User already exists."}, status=400)

        if RegistrationInvitation.objects.filter(email=email).exists():
            return Response(
                {"detail": "An invitation for this email already exists."}, status=400
            )

        invitation = RegistrationInvitation.objects.create(
            email=email,
            role=role,
            token=RegistrationInvitation.generate_token(),
            first_name=first_name,
            last_name=last_name,
            created_by=request.user,
        )

        frontend_url = getattr(settings, "FRONTEND_URL", "http://127.0.0.1:5173")
        activation_url = f"{frontend_url}/portal?activate_token={invitation.token}"

        try:
            send_mail(
                "Activate your Schoolhub Account",
                f"An administrator has provisioned an account for you. Use this link to activate it and set your password: {activation_url}",
                settings.DEFAULT_FROM_EMAIL,
                [invitation.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception("Failed to send activation email to %s", invitation.email)

        audit.record(
            actor=request.user,
            action="account.invitation_created",
            instance=invitation,
            new_value={"email": email, "role": role},
            request=request,
        )
        return Response(
            {"detail": "Invitation sent.", "token": invitation.token}, status=201
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"], is_active=True
        ).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = getattr(settings, "FRONTEND_URL", "http://127.0.0.1:5173")
            reset_url = f"{frontend_url}/?reset_uid={uid}&reset_token={token}"
            try:
                send_mail(
                    "Reset your Schoolhub password",
                    f"Use this link to reset your password: {reset_url}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception:
                # Keep the response identical either way (never reveal
                # whether the account/delivery succeeded to the client),
                # but a delivery failure should be visible to operators --
                # silently losing every reset email was invisible before.
                logger.exception(
                    "Failed to send password reset email to user id=%s", user.id
                )
        return Response(
            {
                "detail": "If an account exists for that email, reset instructions have been sent."
            },
            status=202,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Your password has been reset. You can now sign in."}
        )


class ProfileViewSet(viewsets.ModelViewSet):
    """
    /api/accounts/profiles/         admin: list all profiles
    /api/accounts/profiles/me/      any authenticated user: their own profile
    /api/accounts/profiles/{id}/    owner or admin: retrieve/update
    """

    serializer_class = ProfileSerializer
    queryset = Profile.objects.select_related("user").all()

    def get_permissions(self):
        if self.action == "me":
            return [IsAuthenticated()]
        if self.action == "list":
            return [IsAdmin()]
        return [IsOwnerOrAdmin()]

    def get_queryset(self):
        profile = self.request.user.profile
        if profile.role == "admin":
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        profile = request.user.profile
        if request.method == "PATCH":
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(self.get_serializer(profile).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def suspend(self, request, pk=None):
        profile = self.get_object()
        user = profile.user
        user.is_active = False
        user.save()
        audit.record(
            actor=request.user,
            action="account.suspend",
            instance=profile,
            request=request,
        )
        return Response({"detail": "Account suspended."})

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def reactivate(self, request, pk=None):
        profile = self.get_object()
        user = profile.user
        user.is_active = True
        user.save()
        audit.record(
            actor=request.user,
            action="account.reactivate",
            instance=profile,
            request=request,
        )
        return Response({"detail": "Account reactivated."})

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def force_reset(self, request, pk=None):
        profile = self.get_object()
        user = profile.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend_url = getattr(settings, "FRONTEND_URL", "http://127.0.0.1:5173")
        reset_url = f"{frontend_url}/?reset_uid={uid}&reset_token={token}"
        try:
            send_mail(
                "Schoolhub Admin Password Reset",
                f"An administrator has requested a password reset for your account. Use this link to reset it: {reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception:
            pass
        audit.record(
            actor=request.user,
            action="account.force_reset",
            instance=profile,
            request=request,
        )
        return Response({"detail": "Password reset email sent."})

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def revoke_sessions(self, request, pk=None):
        profile = self.get_object()
        user = profile.user
        audit.record(request.user, "account.revoke_sessions", profile, None, request)
        return Response({"detail": "Sessions revoked (stub)."})


from .models import RegistrationInvitation
from django.utils import timezone


class AccountActivateView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        token = request.data.get("token")
        password = request.data.get("password")
        if not token or not password:
            return Response(
                {"detail": "Token and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation = RegistrationInvitation.objects.filter(token=token).first()
        if not invitation or not invitation.is_valid:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find user by email
        user = User.objects.filter(email=invitation.email).first()
        if not user:
            # Create user if it doesn't exist
            user = User.objects.create_user(
                username=invitation.email,
                email=invitation.email,
                password=password,
                first_name=invitation.first_name,
                last_name=invitation.last_name,
            )
            Profile.objects.create(user=user, role=invitation.role)
        else:
            # Set password and activate
            user.set_password(password)
            user.is_active = True
            user.save()

        # Mark as used
        invitation.used_at = timezone.now()
        invitation.save()

        # Log
        audit.record(
            user,
            "account.activate",
            user.profile,
            {"email": user.email, "role": invitation.role},
            request,
        )

        return Response({"detail": "Account activated successfully."})


class StudentRegisterView(generics.CreateAPIView):
    """
    Dedicated Student Portal Registration endpoint.
    Creates an account, sets role=student, issues 24-hour verification token,
    and sends verification email.
    """

    serializer_class = StudentRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Account created successfully. Please check your email to verify your account.",
                "id": user.id,
                "email": user.email,
                "role": user.profile.role,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    """
    Email verification endpoint.
    GET /api/auth/verify-email/<token>/
    Validates token and activates account.
    """

    permission_classes = [AllowAny]

    def get(self, request, token):
        from django.utils import timezone

        profile = (
            Profile.objects.filter(email_verification_token=token)
            .select_related("user")
            .first()
        )
        if not profile:
            return Response(
                {
                    "status": "invalid",
                    "detail": "This verification link is invalid or no longer available.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if (
            profile.email_verification_token_expires
            and timezone.now() > profile.email_verification_token_expires
        ):
            return Response(
                {
                    "status": "expired",
                    "detail": "This verification link has expired. Please request a new verification email.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile.email_verified_at = timezone.now()
        profile.email_verification_token = None
        profile.email_verification_token_expires = None
        profile.save(
            update_fields=[
                "email_verified_at",
                "email_verification_token",
                "email_verification_token_expires",
            ]
        )

        profile.user.is_active = True
        profile.user.save(update_fields=["is_active"])

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
                "message": "Your email address has been successfully verified. Your account is now active.",
            },
            status=status.HTTP_200_OK,
        )


class ResendVerificationView(APIView):
    """
    Resend verification email endpoint.
    Rate limited, does not reveal account existence.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        import secrets
        from datetime import timedelta
        from django.utils import timezone
        from services import email_service

        email = request.data.get("email", "").lower().strip()
        user = User.objects.filter(email__iexact=email).first()
        if user and hasattr(user, "profile") and not user.profile.email_verified_at:
            token = secrets.token_urlsafe(32)
            user.profile.email_verification_token = token
            user.profile.email_verification_token_expires = timezone.now() + timedelta(
                hours=24
            )
            user.profile.save(
                update_fields=[
                    "email_verification_token",
                    "email_verification_token_expires",
                ]
            )
            email_service.send_verification_email(user, token, request=request)

        return Response(
            {
                "message": "If an unverified account exists with that email address, a verification link has been sent."
            },
            status=status.HTTP_200_OK,
        )


class AdminNotificationViewSet(viewsets.ModelViewSet):
    """
    Admin Notification management.
    List, unread count, mark read, mark all read.
    """

    queryset = AdminNotification.objects.all()
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        ntype = self.request.query_params.get("type")
        if ntype:
            qs = qs.filter(notification_type=ntype)
        unread_only = self.request.query_params.get("unread")
        if unread_only == "true":
            qs = qs.filter(is_read=False)
        return qs

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = AdminNotification.objects.filter(is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        return Response({"status": "marked_read"})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        AdminNotification.objects.filter(is_read=False).update(is_read=True)
        return Response({"status": "all_marked_read"})


class PortalNotificationViewSet(viewsets.ModelViewSet):
    """
    In-portal notifications for authenticated users (Students/Parents).
    """

    serializer_class = PortalNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PortalNotification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        return Response({"status": "marked_read"})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Audit Log viewer for administrators.
    """

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        action_param = self.request.query_params.get("action")
        if action_param:
            qs = qs.filter(action__icontains=action_param)
        return qs
