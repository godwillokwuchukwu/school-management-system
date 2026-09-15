from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FeeViewSet, PaymentWebhookView

router = DefaultRouter()
router.register(r"fees", FeeViewSet, basename="fee")

urlpatterns = [
    path("webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),
    path("", include(router.urls)),
]
