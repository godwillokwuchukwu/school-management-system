from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentSubmissionViewSet,
    AssignmentViewSet,
    EventViewSet,
    ParentTeacherMeetingViewSet,
)

router = DefaultRouter()
router.register(r"assignments", AssignmentViewSet, basename="assignment")
router.register(r"submissions", AssignmentSubmissionViewSet, basename="submission")
router.register(r"events", EventViewSet, basename="event")
router.register(r"meetings", ParentTeacherMeetingViewSet, basename="meeting")

urlpatterns = [
    path("", include(router.urls)),
]
