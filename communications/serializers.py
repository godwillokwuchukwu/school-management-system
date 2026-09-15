from rest_framework import serializers
from .models import (
    Announcement,
    Conversation,
    ConversationParticipant,
    Message,
    MessageAttachment,
    MessageReadReceipt,
)


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "content",
            "category",
            "created_by",
            "created_by_name",
            "target_all",
            "target_students",
            "target_teachers",
            "target_parents",
            "target_class",
            "target_grade",
            "created_at",
            "updated_at",
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
        fields = [
            "id",
            "sender",
            "sender_name",
            "body",
            "is_deleted",
            "created_at",
            "updated_at",
            "attachments",
        ]
        read_only_fields = ["sender", "created_at", "updated_at"]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=__import__("django.contrib.auth", fromlist=["get_user_model"])
        .get_user_model()
        .objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Conversation
        fields = [
            "id",
            "subject",
            "created_at",
            "updated_at",
            "is_archived",
            "messages",
            "participant_ids",
        ]

    def create(self, validated_data):
        participant_users = validated_data.pop("participant_ids", [])
        conversation = super().create(validated_data)
        # Always add the creator as a participant
        request = self.context.get("request")
        if request and request.user:
            ConversationParticipant.objects.get_or_create(
                conversation=conversation, user=request.user
            )
        # Add any explicitly specified participants
        for user in participant_users:
            ConversationParticipant.objects.get_or_create(
                conversation=conversation, user=user
            )
        return conversation
