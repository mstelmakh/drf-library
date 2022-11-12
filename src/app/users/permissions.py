from rest_framework.permissions import BasePermission

from users.services import is_librarian, is_user


class IsUser(BasePermission):
    """
    Available only for user.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            is_user(request.user)
        )


class IsLibrarian(BasePermission):
    """
    Available only for librarian.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            is_librarian(request.user)
        )
