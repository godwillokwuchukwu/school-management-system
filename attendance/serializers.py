from rest_framework import serializers

from .models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "student",
            "date",
            "status",
            "notes",
            "marked_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["marked_by", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["marked_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        validated_data["marked_by"] = request.user
        return super().update(instance, validated_data)
