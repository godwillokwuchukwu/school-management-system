from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(
        source="generated_by.get_full_name", read_only=True
    )
    report_type_display = serializers.CharField(
        source="get_report_type_display", read_only=True
    )

    class Meta:
        model = Report
        fields = [
            "id",
            "title",
            "report_type",
            "report_type_display",
            "student",
            "school_class",
            "generated_by",
            "generated_by_name",
            "data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["generated_by", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["generated_by"] = request.user
        return super().create(validated_data)
