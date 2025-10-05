from django.db import models
from django.contrib.auth.models import User


class UnreadMessagesManager(models.Manager):
    """Custom manager to filter unread messages for a specific user"""
    
    def unread_for_user(self, user):
        """
        Returns unread messages for a specific user
        Uses .only() to retrieve only necessary fields
        """
        return self.get_queryset().filter(
            receiver=user, 
            read=False
        ).only('id', 'sender', 'content', 'timestamp')


class Message(models.Model):
    """Model representing a message between users"""
    
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Default manager
    objects = models.Manager()
    
    # Custom manager for unread messages
    unread = UnreadMessagesManager()
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['receiver', 'read']),
            models.Index(fields=['parent_message']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
    
    def get_replies(self):
        """
        Recursively get all replies to this message
        Uses select_related and prefetch_related for optimization
        """
        return Message.objects.filter(
            parent_message=self
        ).select_related(
            'sender', 'receiver'
        ).prefetch_related('replies')


class Notification(models.Model):
    """Model to store user notifications"""
    
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('reply', 'Message Reply'),
        ('edit', 'Message Edited'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='message'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Notification for {self.user} - {self.notification_type}"


class MessageHistory(models.Model):
    """Model to store message edit history"""
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_edits'
    )
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message histories'
    
    def __str__(self):
        return f"History of message {self.message.id} edited at {self.edited_at}"