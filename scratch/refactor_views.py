import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\communications\views.py"

new_views = """
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from accounts.permissions import IsAdmin, IsAdminOrTeacher

from .models import Announcement, Conversation, ConversationParticipant, Message
from .serializers import AnnouncementSerializer, ConversationSerializer, MessageSerializer

class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    filterset_fields = ["category", "target_class"]
    search_fields = ["title", "content"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, "role", None) if hasattr(user, "profile") else None
        
        if role == "admin":
            return Announcement.objects.all()
            
        qs = Announcement.objects.all()
        q_filter = Q(target_all=True)
        
        if role == "teacher":
            q_filter |= Q(target_teachers=True)
            q_filter |= Q(created_by=user)
        elif role == "student":
            q_filter |= Q(target_students=True)
            # Would add logic for specific class/grade
        elif role == "parent":
            q_filter |= Q(target_parents=True)
            
        return qs.filter(q_filter).distinct()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            participants__user=self.request.user, 
            participants__is_deleted=False
        ).distinct()

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        conversation = self.get_object()
        body = request.data.get("body")
        if not body:
            return Response({"detail": "Body is required"}, status=400)
            
        msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=body
        )
        return Response(MessageSerializer(msg).data)
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_views)
