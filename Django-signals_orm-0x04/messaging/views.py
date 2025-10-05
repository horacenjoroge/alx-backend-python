from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import User, Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer, UserPublicSerializer
from .permissions import (
    IsParticipantOfConversation,
    IsConversationParticipant, 
    IsMessageSenderOrRecipient, 
    CanManageUsers,
    ConversationPermission,
    MessagePermission,
    IsUserSelf
)
from .filters import MessageFilter, ConversationFilter, UserFilter
from .pagination import MessagePagination, ConversationPagination, UserPagination
from django.shortcuts import get_object_or_404


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user registration and management.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'create':
            # Allow registration without authentication
            permission_classes = [AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Users can only manage their own profile, admins can manage any
            permission_classes = [IsAuthenticated, IsUserSelf | CanManageUsers]
        else:
            # For list action, use custom permission
            permission_classes = [IsAuthenticated, CanManageUsers]
        
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Use different serializers based on the action.
        """
        if self.action in ['list', 'retrieve']:
            return UserPublicSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Return users based on permissions and filters.
        """
        if hasattr(self.request.user, 'role') and self.request.user.role == 'admin':
            return User.objects.all()
        elif self.action == 'list':
            # For listing users, return all users (for finding conversation participants)
            return User.objects.all()
        else:
            # For other actions, return only current user
            return User.objects.filter(user_id=self.request.user.user_id)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get current user's information.
        """
        serializer = UserPublicSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Update current user's profile.
        """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserPublicSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating conversations with filtering.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]  # Apply custom permission
    pagination_class = ConversationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return conversations for the authenticated user only.
        """
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new conversation and add the authenticated user as a participant.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        return conversation

    @action(detail=True, methods=['post'], url_path='add-participant', 
            permission_classes=[IsParticipantOfConversation])
    def add_participant(self, request, pk=None):
        """
        Custom action to add a participant to an existing conversation.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(user_id=user_id)
            if conversation.participants.filter(user_id=user_id).exists():
                return Response({"error": "User is already a participant"}, status=status.HTTP_400_BAD_REQUEST)
            
            conversation.participants.add(user)
            return Response({"message": f"User {user.email} added to conversation"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'], url_path='leave',
            permission_classes=[IsParticipantOfConversation])
    def leave_conversation(self, request, pk=None):
        """
        Allow user to leave a conversation.
        """
        conversation = self.get_object()
        conversation.participants.remove(request.user)
        return Response({"message": "You have left the conversation"}, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and sending messages in conversations with filtering and pagination.
    Task 5: Cache applied to message list views for 60 seconds
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation]  # Apply custom permission
    pagination_class = MessagePagination  # 20 messages per page
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MessageFilter  # Apply custom filter
    search_fields = ['message_body', 'sender__email', 'recipient__email']
    ordering_fields = ['sent_at', 'sender__email', 'recipient__email']
    ordering = ['-sent_at']

    @method_decorator(cache_page(60))  # Cache for 60 seconds as per Task 5
    def list(self, request, *args, **kwargs):
        """
        List all messages in conversations with 60-second cache timeout.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return messages for conversations the authenticated user is part of.
        """
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(conversation__in=user_conversations).order_by('-sent_at')

    def perform_create(self, serializer):
        """
        Send a new message in an existing conversation.
        """
        conversation_id = self.request.data.get('conversation')
        recipient_id = self.request.data.get('recipient')
        
        if not conversation_id or not recipient_id:
            return Response(
                {"error": "conversation and recipient are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        recipient = get_object_or_404(User, user_id=recipient_id)
        
        # Check if current user is a participant in the conversation
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            return Response(
                {"error": "You are not a participant in this conversation"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if recipient is a participant in the conversation
        if not conversation.participants.filter(user_id=recipient_id).exists():
            return Response(
                {"error": "Recipient is not a participant in this conversation"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(sender=self.request.user, conversation=conversation, recipient=recipient)

    @action(detail=False, methods=['get'], url_path='my-messages')
    @method_decorator(cache_page(60))  # Cache for 60 seconds
    def my_messages(self, request):
        """
        Get all messages sent by the current user with 60-second cache.
        """
        messages = self.get_queryset().filter(sender=request.user)
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='received-messages')
    @method_decorator(cache_page(60))  # Cache for 60 seconds
    def received_messages(self, request):
        """
        Get all messages received by the current user with 60-second cache.
        """
        messages = self.get_queryset().filter(recipient=request.user)
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)