"""
Riverside Academy - Unified Authentication & Portal Login Module
Consolidates all login, registration, verification, password reset,
and portal authentication views, serializers, and forms in one single module.
"""

from accounts.views import (
    LoginView,
    StudentRegisterView,
    VerifyEmailView,
    ResendVerificationView,
    RegisterView,
    PublicApplicantRegisterView,
    AccountActivateView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

ActivateAccountView = AccountActivateView

from accounts.serializers import (
    RoleAwareTokenObtainPairSerializer,
    StudentRegisterSerializer,
    PublicApplicantRegisterSerializer,
    RegisterSerializer,
    AccountActivationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)

from accounts.forms import (
    StudentLoginForm,
    StudentRegistrationForm,
)

__all__ = [
    # Views
    "LoginView",
    "StudentRegisterView",
    "VerifyEmailView",
    "ResendVerificationView",
    "RegisterView",
    "PublicApplicantRegisterView",
    "ActivateAccountView",
    "AccountActivateView",
    "PasswordResetRequestView",
    "PasswordResetConfirmView",
    # Serializers
    "RoleAwareTokenObtainPairSerializer",
    "StudentRegisterSerializer",
    "PublicApplicantRegisterSerializer",
    "RegisterSerializer",
    "AccountActivationSerializer",
    "PasswordResetRequestSerializer",
    "PasswordResetConfirmSerializer",
    # Forms
    "StudentLoginForm",
    "StudentRegistrationForm",
]
