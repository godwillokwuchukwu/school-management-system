from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permissions import IsAdminOrTeacher, ReadOnlyOrAdmin

from .models import Class, Enrollment, Grade, Subject, ClassSchedule
from .serializers import (
    ClassSerializer,
    EnrollmentSerializer,
    GradeSerializer,
    SubjectSerializer,
    ClassScheduleSerializer,
)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def get_permissions(self):
        return (
            [AllowAny()]
            if self.request.method in ("GET", "HEAD", "OPTIONS")
            else [ReadOnlyOrAdmin()]
        )

    filterset_fields = ["code"]
    search_fields = ["name", "code"]


class ClassViewSet(viewsets.ModelViewSet):
    queryset = (
        Class.objects.select_related("class_teacher").prefetch_related("subjects").all()
    )
    serializer_class = ClassSerializer
    permission_classes = [ReadOnlyOrAdmin]
    filterset_fields = ["academic_year", "code"]

    @action(detail=True, methods=["get"], permission_classes=[IsAdminOrTeacher])
    def roster(self, request, pk=None):
        school_class = self.get_object()
        enrollments = Enrollment.objects.filter(
            school_class=school_class
        ).select_related("student__profile__user")
        students = [
            {
                "id": e.student.id,
                "first_name": e.student.profile.user.first_name,
                "last_name": e.student.profile.user.last_name,
                "admission_number": e.student.admission_number,
                "dob": str(e.student.dob),
            }
            for e in enrollments
        ]
        return Response(students)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related("student", "school_class").all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["academic_year", "school_class", "student"]

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
        # Any other/new role (e.g. a public "applicant" account, added in
        # Stage 2) has no legitimate reason to see enrollment records --
        # explicit allow-list rather than an implicit "everyone else sees
        # everything" default, which would otherwise silently leak to
        # every future role added to the system.
        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.profile.role not in ("admin", "teacher"):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only staff can create enrollments.")
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.profile.role not in ("admin", "teacher"):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only staff can update enrollments.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.profile.role not in ("admin", "teacher"):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only staff can delete enrollments.")
        instance.delete()


class GradeViewSet(viewsets.ModelViewSet):
    """
    Write access: admins + teachers (grading is a staff action).
    Read access: any authenticated user; students/parents should be scoped
    to their own child via get_queryset once the `students` app's
    guardian-linkage model lands.
    """

    queryset = Grade.objects.select_related("enrollment", "subject", "graded_by").all()
    serializer_class = GradeSerializer
    filterset_fields = ["enrollment", "subject"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        profile = getattr(self.request.user, "profile", None)
        role = getattr(profile, "role", None)
        if role == "student":
            return queryset.filter(
                enrollment__student__profile=self.request.user.profile
            )
        if role == "parent":
            return queryset.filter(enrollment__student__parents=profile)
        if role in ("admin", "teacher"):
            return queryset
        # See the matching comment in EnrollmentViewSet.get_queryset above.
        return queryset.none()


class ClassScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.select_related("school_class", "subject").all()
    serializer_class = ClassScheduleSerializer
    filterset_fields = ["school_class", "subject", "day_of_week"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        profile = getattr(self.request.user, "profile", None)
        role = getattr(profile, "role", None)
        if role == "student":
            return queryset.filter(
                school_class__enrollments__student__profile=self.request.user.profile
            )
        if role == "parent":
            return queryset.filter(school_class__enrollments__student__parents=profile)
        if role in ("admin", "teacher"):
            return queryset
        return queryset.none()
