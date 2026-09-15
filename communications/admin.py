from django.contrib import admin
from .models import (
    Announcement,
    Conversation,
    ConversationParticipant,
    Message,
    MessageAttachment,
    MessageReadReceipt,
)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_by", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "content")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "created_at")
    list_filter = ("created_at",)
    search_fields = ("body",)


admin.site.register(ConversationParticipant)
admin.site.register(MessageAttachment)
admin.site.register(MessageReadReceipt)
