import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\academics\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "from .models import Class, Enrollment, Grade, Subject",
    "from .models import Class, Enrollment, Grade, Subject, ClassSchedule",
)
content = content.replace(
    "from .serializers import ClassSerializer, EnrollmentSerializer, GradeSerializer, SubjectSerializer",
    "from .serializers import ClassSerializer, EnrollmentSerializer, GradeSerializer, SubjectSerializer, ClassScheduleSerializer",
)

new_viewset = """
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
            return queryset.filter(school_class__enrollments__student__profile=self.request.user.profile)
        if role == "parent":
            return queryset.filter(school_class__enrollments__student__parents=profile)
        if role in ("admin", "teacher"):
            return queryset
        return queryset.none()
"""
content += new_viewset

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
