from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Only allows users with the admin role
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'Admin'
        )

class IsStudentRole(BasePermission):
    """
    Only allows users with the student role
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'Student'
        )