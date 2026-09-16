from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.auth.views import (
    ActivateAccountView,
    LoginView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendVerificationView,
    StudentRegisterView,
    VerifyEmailView,
)

app_name = "auth"

urlpatterns = [
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("student/register/", StudentRegisterView.as_view(), name="student_register"),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify_email"),
    path(
        "resend-verification/",
        ResendVerificationView.as_view(),
        name="resend_verification",
    ),
    path("activate/", ActivateAccountView.as_view(), name="activate"),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
