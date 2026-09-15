import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\academics\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

from_block = "from rest_framework import viewsets"
if "from rest_framework.decorators import action" not in content:
    content = content.replace(
        from_block,
        "from rest_framework import viewsets\nfrom rest_framework.decorators import action\nfrom rest_framework.response import Response",
    )

old_class = """class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.select_related("class_teacher").prefetch_related("subjects").all()
    serializer_class = ClassSerializer
    permission_classes = [ReadOnlyOrAdmin]
    filterset_fields = ["academic_year", "code"]"""

new_class = """class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.select_related("class_teacher").prefetch_related("subjects").all()
    serializer_class = ClassSerializer
    permission_classes = [ReadOnlyOrAdmin]
    filterset_fields = ["academic_year", "code"]

    @action(detail=True, methods=["get"], permission_classes=[IsAdminOrTeacher])
    def roster(self, request, pk=None):
        school_class = self.get_object()
        enrollments = Enrollment.objects.filter(school_class=school_class).select_related("student__profile__user")
        students = [
            {
                "id": e.student.id,
                "first_name": e.student.profile.user.first_name,
                "last_name": e.student.profile.user.last_name,
                "admission_number": e.student.admission_number,
                "dob": str(e.student.dob)
            }
            for e in enrollments
        ]
        return Response(students)"""

content = content.replace(old_class, new_class)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
