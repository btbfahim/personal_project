from rest_framework import permissions

class IsManagerUser(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit and delete.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'manager')