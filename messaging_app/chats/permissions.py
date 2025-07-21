from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.sender == request.user

class IsParticipantReadOnly(permissions.BasePermission):
    """Custom permission to only allow conversation particpants to access the conversation."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to participants of the conversation.
        return request.user in obj.participants.all()


class IsMessageOwner(permissions.BasePermission):
    """Custom permission to only allow the owner of the message to access it."""

    def has_object_permission(self, request, view, obj):
        # User can access if they are the sender or participant in the conversation
        return (obj.sender == request.user or
                request.user in obj.conversation.participants.all())
