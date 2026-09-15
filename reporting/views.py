from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminOrTeacher

from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.select_related(
        "student__profile__user", "school_class", "generated_by"
    ).all()
    serializer_class = ReportSerializer
    filterset_fields = ["report_type", "student", "school_class"]
    search_fields = ["title"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter reports based on user role."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return Report.objects.none()

        profile = getattr(user, "profile", None)
        if not profile:
            return Report.objects.none()

        # Admins/teachers see all reports
        if profile.role in ["admin", "teacher"]:
            return Report.objects.all()

        # Students see only their own reports
        if profile.role == "student":
            student = getattr(profile, "student", None)
            if student:
                return Report.objects.filter(student=student)
            return Report.objects.none()

        if profile.role == "parent":
            return Report.objects.filter(student__in=profile.children.all())

        return Report.objects.none()
