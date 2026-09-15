from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminOrTeacher

from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related(
        "student__profile__user", "marked_by"
    ).all()
    serializer_class = AttendanceRecordSerializer
    filterset_fields = ["student", "date", "status"]
    search_fields = ["notes"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrTeacher()]
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

    @action(detail=False, methods=["post"], permission_classes=[IsAdminOrTeacher])
    def bulk_mark(self, request):
        records = request.data.get("records", [])
        if not isinstance(records, list) or not records:
            return Response(
                {"records": "Provide a non-empty list of attendance records."},
                status=400,
            )
        marked = []
        with transaction.atomic():
            for record in records:
                serializer = self.get_serializer(data=record)
                serializer.is_valid(raise_exception=True)
                values = serializer.validated_data
                instance, _ = AttendanceRecord.objects.update_or_create(
                    student=values["student"],
                    date=values["date"],
                    defaults={
                        "status": values["status"],
                        "notes": values.get("notes", ""),
                        "marked_by": request.user,
                    },
                )
                marked.append(instance)
        return Response(self.get_serializer(marked, many=True).data)
