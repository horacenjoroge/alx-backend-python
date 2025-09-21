from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.shortcuts import get_object_or_404


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating conversations with filtering.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['conversation_id', 'created_at']

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

    @action(detail=True, methods=['post'], url_path='add-participant')
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


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and sending messages in conversations with filtering.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['message_id', 'conversation', 'sender', 'recipient', 'sent_at']

    def get_queryset(self):
        """
        Return messages for conversations the authenticated user is part of.
        """
        return Message.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        """
        Send a new message in an existing conversation.
        """
        conversation_id = self.request.data.get('conversation')
        recipient_id = self.request.data.get('recipient')
        
        if not conversation_id or not recipient_id:
            return Response({"error": "conversation and recipient are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        recipient = get_object_or_404(User, user_id=recipient_id)
        
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            return Response({"error": "You are not a participant in this conversation"}, status=status.HTTP_403_FORBIDDEN)
        
        if not conversation.participants.filter(user_id=recipient_id).exists():
            return Response({"error": "Recipient is not a participant in this conversation"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(sender=self.request.user, conversation=conversation, recipient=recipient)