from django.utils import timezone
from rest_framework import serializers

from .models import Fee, FeeStatus


class FeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source="student.profile.user.get_full_name", read_only=True
    )

    class Meta:
        model = Fee
        fields = [
            "id",
            "student",
            "student_name",
            "title",
            "amount",
            "due_date",
            "status",
            "paid_at",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at", "paid_at"]

    def update(self, instance, validated_data):
        if (
            validated_data.get("status") == FeeStatus.PAID
            and instance.status != FeeStatus.PAID
        ):
            validated_data["paid_at"] = timezone.now()
        return super().update(instance, validated_data)
