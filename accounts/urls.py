from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminNotificationViewSet,
    AuditLogViewSet,
    PortalNotificationViewSet,
    ProfileViewSet,
    ResendVerificationView,
    StudentRegisterView,
    VerifyEmailView,
)

router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profile")
router.register(
    "admin/notifications", AdminNotificationViewSet, basename="admin-notification"
)
router.register(
    "notifications", PortalNotificationViewSet, basename="portal-notification"
)
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("student/register/", StudentRegisterView.as_view(), name="student_register"),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify_email"),
    path(
        "resend-verification/",
        ResendVerificationView.as_view(),
        name="resend_verification",
    ),
] + router.urls
