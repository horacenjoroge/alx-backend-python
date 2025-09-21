from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, exposing basic user information.
    """
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at']
        read_only_fields = ['user_id', 'created_at']

    def validate_email(self, value):
        """
        Validate that the email is unique.
        """
        if User.objects.filter(email=value).exclude(pk=self.instance.user_id if self.instance else None).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model, including sender and recipient details.
    """
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    message_body = serializers.CharField(required=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'recipient', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']

    def validate(self, data):
        """
        Ensure the recipient is part of the conversation.
        """
        conversation = data.get('conversation')
        recipient = data.get('recipient')
        if recipient and conversation and not conversation.participants.filter(pk=recipient.user_id).exists():
            raise serializers.ValidationError("Recipient must be a participant in the conversation.")
        return data


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model, including participants and nested messages.
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']

    def get_messages(self, obj):
        """
        Retrieve all messages for the conversation, ordered by sent_at.
        """
        messages = obj.messages.order_by('-sent_at')
        return MessageSerializer(messages, many=True).data