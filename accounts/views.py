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
from .models import Profile
from .permissions import IsAdmin, IsOwnerOrAdmin
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
    PublicApplicantRegisterSerializer,
    RegisterSerializer,
    RoleAwareTokenObtainPairSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    serializer_class = RoleAwareTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


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
