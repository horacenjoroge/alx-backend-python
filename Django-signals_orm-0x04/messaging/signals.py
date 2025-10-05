from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


@receiver(post_save, sender=Message)
def notify_user_on_new_message(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a new message is created.
    Task 0: Implement Signals for User Notifications
    
    This signal listens for new messages and automatically creates a notification
    for the receiving user using post_save signal.
    """
    if created:
        # Get the message object
        message = instance
        
        # Determine notification type based on whether it's a reply
        notification_type = 'reply' if message.parent_message else 'message'
        
        # Create notification content
        if notification_type == 'reply':
            content = f"{message.sender.username} replied to your message"
        else:
            content = f"You have a new message from {message.sender.username}"
        
        # Automatically create notification for the receiver
        Notification.objects.create(
            user=message.receiver,
            message=message,
            notification_type=notification_type,
            content=content
        )


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal handler that logs message edits before saving.
    Task 1: Create a Signal for Logging Message Edits
    
    Uses pre_save signal to log the old content of a message before it's updated.
    """
    # Only log if the message already exists (is being edited, not created)
    if instance.pk:
        try:
            # Get the old version of the message
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has changed
            if old_message.content != instance.content:
                # Save the old content to MessageHistory
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender
                )
                
                # Mark message as edited
                instance.edited = True
                
                # Create notification for receiver about the edit
                Notification.objects.create(
                    user=instance.receiver,
                    message=instance,
                    notification_type='edit',
                    content=f"{instance.sender.username} edited their message"
                )
        except Message.DoesNotExist:
            # Message doesn't exist yet, so this is a new message
            pass


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Signal handler that cleans up user-related data when a user is deleted.
    Task 2: Use Signals for Deleting User-Related Data
    
    Note: This signal will be triggered when a User is deleted.
    Related data (messages, notifications, message histories) will be 
    automatically deleted due to CASCADE foreign keys, but this signal
    can be used for additional cleanup or logging.
    """
    # Log the deletion
    print(f"User {instance.username} deleted. Cleaning up related data...")
    
    # Get counts before deletion (for logging purposes)
    sent_messages_count = instance.sent_messages.count()
    received_messages_count = instance.received_messages.count()
    notifications_count = instance.notifications.count()
    
    print(f"Deleted {sent_messages_count} sent messages")
    print(f"Deleted {received_messages_count} received messages")
    print(f"Deleted {notifications_count} notifications")
    
    # Note: Actual deletion happens automatically via CASCADE
    # Additional custom cleanup logic can be added here if needed