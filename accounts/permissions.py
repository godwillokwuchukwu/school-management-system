from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Role


def _has_role(request, role):
    profile = getattr(request.user, "profile", None)
    return bool(
        request.user
        and request.user.is_authenticated
        and profile
        and profile.role == role
    )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request, Role.ADMIN)


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request, Role.TEACHER)


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request, Role.STUDENT)


class IsParent(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request, Role.PARENT)


class IsApplicant(BasePermission):
    """
    The public applicant role (Stage 2). Deliberately has its own
    permission class rather than reusing IsAuthenticated, so applicant
    access to admissions endpoints is an explicit allow-list decision, not
    an accident of "any logged-in user can reach this."
    """

    def has_permission(self, request, view):
        return _has_role(request, Role.APPLICANT)


class IsAdminOrTeacher(BasePermission):
    """Common combo: staff-facing writes (grades, attendance, assignments)."""

    def has_permission(self, request, view):
        return _has_role(request, Role.ADMIN) or _has_role(request, Role.TEACHER)


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level check for Profile/Student detail endpoints: the owner can
    read/edit their own record, admins can act on any record, everyone
    else is denied. Expects `obj.user` or `obj` itself to be the User.
    """

    def has_object_permission(self, request, view, obj):
        if _has_role(request, Role.ADMIN):
            return True
        owner = getattr(obj, "user", obj)
        return owner == request.user


class ReadOnlyOrAdmin(BasePermission):
    """Anyone authenticated can read; only admins can write. Used for
    reference data like Subject/Class lists that teachers/students browse
    but only admins curate."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return _has_role(request, Role.ADMIN)
