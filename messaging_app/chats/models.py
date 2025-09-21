# chats/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extended User model with additional fields for the messaging app.
    """
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]

    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        null=False,
        blank=False,
        default='guest'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'chats_user'
        indexes = [
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['user_id'], name='idx_user_id'),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """
    Model representing a conversation between users.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chats_conversation'
        indexes = [
            models.Index(fields=['conversation_id'], name='idx_conv_id'),
            models.Index(fields=['created_at'], name='idx_conv_created_at'),
        ]

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """
    Model representing a message sent in a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chats_message'
        indexes = [
            models.Index(fields=['message_id'], name='idx_msg_id'),
            models.Index(fields=['sender'], name='idx_msg_sender'),
            models.Index(fields=['conversation'], name='idx_msg_conv'),
            models.Index(fields=['sent_at'], name='idx_msg_sent_at'),
        ]
        ordering = ['-sent_at']

    def __str__(self):
        return f"Message from {self.sender} at {self.sent_at}"