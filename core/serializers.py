from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file",
            "category",
            "owner",
            "owner_name",
            "mime_type",
            "is_archived",
            "version",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "mime_type", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["owner"] = request.user

        # Extract mime_type basically from file extension
        import mimetypes

        file_obj = validated_data.get("file")
        if file_obj:
            mime_type, _ = mimetypes.guess_type(file_obj.name)
            validated_data["mime_type"] = mime_type or "application/octet-stream"

        return super().create(validated_data)
