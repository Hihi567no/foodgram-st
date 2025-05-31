"""Custom permissions for API endpoints."""
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    Read permissions are allowed for any request.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the object.
        return obj.author == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Read permissions are allowed for any request.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):
    """
    Custom permission to allow unauthenticated users to create accounts,
    but require authentication for other operations.
    """

    def has_permission(self, request, view):
        """Check if user has permission to access the view."""
        # Allow account creation for unauthenticated users
        if request.method == 'POST' and view.action == 'create':
            return True

        # Require authentication for all other operations
        return request.user and request.user.is_authenticated
