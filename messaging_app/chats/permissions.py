"""
Custom permission classes for the messaging app.
"""
from rest_framework import permissions
from .models import Conversation, Message


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.sender == request.user


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow conversation participants to access conversation data.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        elif isinstance(obj, Message):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        return False

    def has_permission(self, request, view):
        # Allow authenticated users to access the view
        return request.user and request.user.is_authenticated


class IsMessageSenderOrRecipient(permissions.BasePermission):
    """
    Custom permission to only allow message sender or recipient to access message data.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Message):
            # User must be either the sender or recipient of the message
            return (obj.sender == request.user or 
                   obj.recipient == request.user or
                   obj.conversation.participants.filter(user_id=request.user.user_id).exists())
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admin users to access/modify data.
    """

    def has_object_permission(self, request, view, obj):
        # Allow if user is the owner or has admin role
        if hasattr(obj, 'sender'):
            return obj.sender == request.user or request.user.role == 'admin'
        elif hasattr(obj, 'user_id'):
            return obj.user_id == request.user.user_id or request.user.role == 'admin'
        return request.user.role == 'admin'


class CanCreateConversation(permissions.BasePermission):
    """
    Permission to control who can create conversations.
    """

    def has_permission(self, request, view):
        # Only authenticated users with 'host' or 'admin' roles can create conversations
        if request.user and request.user.is_authenticated:
            if request.method == 'POST':
                return request.user.role in ['host', 'admin']
            return True
        return False


class CanSendMessage(permissions.BasePermission):
    """
    Permission to control who can send messages.
    """

    def has_permission(self, request, view):
        # All authenticated users can send messages
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Users can only send messages in conversations they participate in
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        return True


class IsUserSelf(permissions.BasePermission):
    """
    Permission to only allow users to access their own user data.
    """

    def has_object_permission(self, request, view, obj):
        # Allow users to only access/modify their own profile
        return obj == request.user


class CanManageUsers(permissions.BasePermission):
    """
    Permission for user management - only admins can manage other users.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':  # Registration is allowed for everyone
            return True
        
        if request.user and request.user.is_authenticated:
            # Admin can manage all users, others can only access their own data
            if request.user.role == 'admin':
                return True
            # Non-admin users can only access user list for finding conversation participants
            return request.method in permissions.SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        # Admin can access any user, users can only access their own data
        if request.user.role == 'admin':
            return True
        return obj == request.user


class ConversationPermission(permissions.BasePermission):
    """
    Combined permission class for conversation operations.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        if isinstance(obj, Conversation):
            is_participant = obj.participants.filter(user_id=request.user.user_id).exists()
            
            # For deletion, only allow if user is admin or conversation creator
            if request.method == 'DELETE':
                return request.user.role == 'admin'
            
            return is_participant
        return False


class MessagePermission(permissions.BasePermission):
    """
    Combined permission class for message operations.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Message):
            # Users can access messages in conversations they participate in
            is_participant = obj.conversation.participants.filter(user_id=request.user.user_id).exists()
            
            # For modification/deletion, only sender or admin can modify
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return obj.sender == request.user or request.user.role == 'admin'
            
            return is_participant
        return False