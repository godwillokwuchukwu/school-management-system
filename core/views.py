from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["category", "is_public", "is_archived"]
    search_fields = ["title", "owner__first_name", "owner__last_name"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, "role", None) if hasattr(user, "profile") else None

        qs = Document.objects.filter(is_archived=False)
        if role in ["admin", "teacher"]:
            return qs

        # Students and parents can only see their own documents or public ones
        return qs.filter(owner=user) | qs.filter(is_public=True)
