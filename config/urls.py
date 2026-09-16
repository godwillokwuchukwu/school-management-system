from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    AccountActivateView,
    AdminProvisionAccountView,
    LoginView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendVerificationView,
    StudentRegisterView,
    VerifyEmailView,
)

urlpatterns = [
    path("", RedirectView.as_view(url="/api/docs/", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    # --- Auth ---
    path("api/auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path(
        "api/auth/student/register/",
        StudentRegisterView.as_view(),
        name="student_register",
    ),
    path(
        "api/auth/verify-email/<str:token>/",
        VerifyEmailView.as_view(),
        name="api_verify_email",
    ),
    path(
        "api/auth/resend-verification/",
        ResendVerificationView.as_view(),
        name="api_resend_verification",
    ),
    path(
        "accounts/verify-email/<str:token>/",
        VerifyEmailView.as_view(),
        name="web_verify_email",
    ),
    path(
        "accounts/resend-verification/",
        ResendVerificationView.as_view(),
        name="web_resend_verification",
    ),
    path(
        "api/auth/password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset",
    ),
    path(
        "api/auth/password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("api/auth/activate/", AccountActivateView.as_view(), name="account-activate"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Admin-only internal account provisioning (Stage 1 interim; Stage 3 adds
    # the activation-token email flow on top of this).
    path(
        "api/accounts/admin/provision/",
        AdminProvisionAccountView.as_view(),
        name="admin_provision_account",
    ),
    # --- App routers ---
    path("api/ai/", include("ai_assistants.urls")),
    path("api/core/", include("core.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/academics/", include("academics.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/activities/", include("activities.urls")),
    path("api/communications/", include("communications.urls")),
    path("api/reporting/", include("reporting.urls")),
    path("api/fees/", include("fees.urls")),
    path("api/students/", include("students.urls")),
    path("api/public/", include("public_site.urls")),
    path("api/admissions/", include("admissions.urls")),
    # --- API docs ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    # ProfileSerializer.photo returns a /media/... URL, but Django never
    # serves MEDIA_ROOT on its own -- without this, every uploaded photo
    # is a 404 in local/dev use. (In production this is handled by
    # nginx/whatever serves static assets, not Django.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
