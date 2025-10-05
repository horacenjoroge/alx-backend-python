from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a specific user.
    Task 4: Custom ORM Manager for Unread Messages
    """
    
    def unread_for_user(self, user):
        """
        Returns unread messages for a specific user.
        Uses .only() to retrieve only necessary fields for optimization.
        
        Args:
            user: The user to filter unread messages for
            
        Returns:
            QuerySet of unread messages with only necessary fields
        """
        return self.get_queryset().filter(
            receiver=user, 
            read=False
        ).only('id', 'sender', 'content', 'timestamp')