from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUser(BasePermission):
    """
    Grants access only to users with the Admin role.
    Used for: Creating, updating, or deleting courses, modules, and lessons.
    """
    message = "This administrative action requires an elevated Admin role."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, "role", None) == "Admin"
        )


class IsReadOnlyOrAdmin(BasePermission):
    """
    Allows anyone (including unauthenticated users or Students) to view public data,
    but restricts write actions (POST, PUT, PATCH, DELETE) exclusively to Admins.
    Used for: The general course catalog endpoints.
    """
    message = "You do not have permission to modify course content. Administrative privileges required."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, "role", None) == "Admin"
        )


class IsOwnProfileOrAdmin(BasePermission):
    """
    students can only view or modify their own
    personal progress tracking data and profile records. Admins bypass this check.
    Used for: User profiles, enrollment metrics, and lesson completion states.
    """
    message = "Access denied. You cannot view or modify another student's account records."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == "Admin":
            return True

        user_id = getattr(obj, "id", None) or getattr(getattr(obj, "user", None), "id", None)

        return str(request.user.id) == str(user_id)

class IsAdminRole(BasePermission):
    """
    Custom permission to strictly allow only Admin users to access the view.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_admin