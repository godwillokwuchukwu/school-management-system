from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminOrTeacher

from .models import Assignment, AssignmentSubmission, Event, ParentTeacherMeeting
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    EventSerializer,
    ParentTeacherMeetingSerializer,
)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related(
        "subject", "school_class", "created_by"
    ).all()
    serializer_class = AssignmentSerializer
    filterset_fields = ["subject", "school_class", "due_date"]
    search_fields = ["title", "description"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        profile = getattr(self.request.user, "profile", None)
        role = getattr(profile, "role", None)
        if role == "student":
            return queryset.filter(
                school_class__enrollments__student__profile=self.request.user.profile
            ).distinct()
        if role == "parent":
            return queryset.filter(
                school_class__enrollments__student__parents=profile
            ).distinct()
        if role in ("admin", "teacher"):
            return queryset
        return queryset.none()


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.select_related(
        "assignment", "student__profile__user"
    ).all()
    serializer_class = AssignmentSubmissionSerializer
    filterset_fields = ["assignment", "student", "status"]
    search_fields = ["content"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        profile = getattr(self.request.user, "profile", None)
        role = getattr(profile, "role", None)
        if role == "student":
            return queryset.filter(student__profile=self.request.user.profile)
        if role == "parent":
            return queryset.filter(student__parents=profile)
        if role in ("admin", "teacher"):
            return queryset
        return queryset.none()


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = ["category", "school_class", "is_school_wide"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]


class ParentTeacherMeetingViewSet(viewsets.ModelViewSet):
    queryset = ParentTeacherMeeting.objects.all()
    serializer_class = ParentTeacherMeetingSerializer
    filterset_fields = ["status", "teacher", "parent"]

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        role = getattr(user.profile, "role", None) if hasattr(user, "profile") else None

        if role == "admin":
            return qs
        elif role == "teacher":
            return qs.filter(teacher=user)
        elif role == "parent":
            return qs.filter(parent=user)
        return qs.none()
