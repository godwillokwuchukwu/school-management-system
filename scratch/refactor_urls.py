import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\communications\urls.py"

new_urls = """
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AnnouncementViewSet, ConversationViewSet

router = DefaultRouter()
router.register(r"announcements", AnnouncementViewSet, basename="announcement")
router.register(r"conversations", ConversationViewSet, basename="conversation")

urlpatterns = [
    path("", include(router.urls)),
]
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_urls)
