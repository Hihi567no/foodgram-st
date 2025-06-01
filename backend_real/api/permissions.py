"""Custom permissions for API endpoints."""
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.

    Read permissions are allowed for any request.
    Write permissions are only allowed to the author of the object.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access the object.

        Returns True for safe methods (GET, HEAD, OPTIONS) or if the user
        is the author of the object for unsafe methods.
        """
        return (request.method in permissions.SAFE_METHODS or
                obj.author == request.user)
