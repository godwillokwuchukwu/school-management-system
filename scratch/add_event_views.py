import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\activities\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "from .models import Assignment, AssignmentSubmission",
    "from .models import Assignment, AssignmentSubmission, Event, ParentTeacherMeeting",
)
content = content.replace(
    "from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer",
    "from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer, EventSerializer, ParentTeacherMeetingSerializer",
)

new_views = """
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
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content + new_views)
