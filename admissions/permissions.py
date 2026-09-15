from rest_framework.permissions import BasePermission


class IsApplicationOwner(BasePermission):
    """Object-level: an applicant may only ever touch their own application."""

    def has_object_permission(self, request, view, obj):
        return obj.applicant_id == request.user.id
