from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdmin

from .models import Student
from .serializers import (
    ParentChildSerializer,
    StudentRecipientSerializer,
    StudentSerializer,
)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = (
        Student.objects.select_related("profile__user")
        .all()
        .order_by("profile__user__last_name", "profile__user__first_name")
    )
    serializer_class = StudentSerializer
    search_fields = [
        "profile__user__first_name",
        "profile__user__last_name",
        "profile__user__email",
        "admission_number",
    ]
    filterset_fields = ["admission_number", "profile__role"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        role = getattr(self.request.user.profile, "role", None)
        if role == "student":
            return queryset.filter(profile=self.request.user.profile)
        if role == "parent":
            return queryset.filter(parents=self.request.user.profile)
        if role == "teacher":
            return queryset.filter(
                enrollments__school_class__class_teacher=self.request.user
            ).distinct()
        if role == "admin":
            return queryset
        # New/unrecognized roles (e.g. Stage 2's public "applicant" role)
        # get no access by default rather than inheriting admin-level reach.
        return queryset.none()

    @action(detail=False, methods=["get"], url_path="children")
    def children(self, request):
        if getattr(request.user.profile, "role", None) != "parent":
            return Response(
                {"detail": "Only parents can view linked children."}, status=403
            )
        children = self.get_queryset().prefetch_related(
            "attendance_records", "enrollments__grades", "reports"
        )
        return Response(ParentChildSerializer(children, many=True).data)

    @action(detail=False, methods=["get"], url_path="recipients")
    def recipients(self, request):
        if getattr(request.user.profile, "role", None) not in ("admin", "teacher"):
            return Response(
                {"detail": "Only staff can view student recipients."}, status=403
            )
        students = Student.objects.select_related("profile__user").order_by(
            "profile__user__last_name", "profile__user__first_name"
        )
        return Response(StudentRecipientSerializer(students, many=True).data)
