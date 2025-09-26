from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, exposing basic user information.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'first_name', 'last_name', 'email', 
            'phone_number', 'role', 'created_at', 'password', 'password_confirm'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True},
        }

    def validate_email(self, value):
        """
        Validate that the email is unique.
        """
        if User.objects.filter(email=value).exclude(pk=self.instance.user_id if self.instance else None).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        """
        Validate that password and password_confirm match.
        """
        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        """
        Create a new user with hashed password.
        """
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update user instance, handling password changes.
        """
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for User model - excludes sensitive information.
    """
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'role']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model, including sender and recipient details.
    """
    sender = UserPublicSerializer(read_only=True)
    recipient = UserPublicSerializer(read_only=True)
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
    participants = UserPublicSerializer(many=True, read_only=True)
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