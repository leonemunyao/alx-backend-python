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

    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation first
        is_participant = request.user in obj.conversation.participants.all()

        if not is_participant:
            return False
        
        # For read operations, any participant can access
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, only the message owner can access
        return obj.sender == request.user


class IsParticipantOfConversation(permissions.BasePermission):
    """Custom permission to only allow participants of a conversation to access it.
    Handles both conversation and message objects."""

    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()    

        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False
    