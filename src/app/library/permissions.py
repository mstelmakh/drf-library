from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.services import is_librarian, is_user


UPDATE_METHODS = ("PUT", "PATCH")


class IsNotUpdateMethod(BasePermission):
    """
    Allows any method except PUT or PATH.
    """
    def has_permission(self, request, view):
        return bool(
            request.method not in UPDATE_METHODS
        )


class IsNotDeleteMethod(BasePermission):
    """
    Allows any method except DELETE.
    """
    def has_permission(self, request, view):
        return bool(
            not request.method == "DELETE"
        )


class IsAdminOrReadOnly(BasePermission):
    """
    The request is authenticated as a staff user, or is a read-only request.
    """
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


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


class IsReserveeOrBorrower(BasePermission):
    """
    Available only for book reservee or borrower.
    """
    def has_object_permission(self, request, view, obj):
        return bool(
            obj.borrower == request.user
        )
