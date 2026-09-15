from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AnnouncementViewSet, ConversationViewSet

router = DefaultRouter()
router.register(r"announcements", AnnouncementViewSet, basename="announcement")
router.register(r"conversations", ConversationViewSet, basename="conversation")

urlpatterns = [
    path("", include(router.urls)),
]
