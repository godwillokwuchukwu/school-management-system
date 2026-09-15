import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\communications\serializers.py"

new_serializers = """
from rest_framework import serializers
from .models import Announcement, Conversation, ConversationParticipant, Message, MessageAttachment, MessageReadReceipt

class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = Announcement
        fields = [
            "id", "title", "content", "category", "created_by", "created_by_name",
            "target_all", "target_students", "target_teachers", "target_parents",
            "target_class", "target_grade", "created_at", "updated_at"
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        return super().create(validated_data)


class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = ["id", "file", "filename", "file_size", "mime_type", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender", "sender_name", "body", "is_deleted", "created_at", "updated_at", "attachments"]
        read_only_fields = ["sender", "created_at", "updated_at"]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ["id", "subject", "created_at", "updated_at", "is_archived", "messages"]

"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_serializers)
