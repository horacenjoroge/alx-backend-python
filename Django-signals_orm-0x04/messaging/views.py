from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages as django_messages
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from .models import Message, Notification, MessageHistory


@login_required
def delete_user(request):
    """
    View to allow a user to delete their account.
    Task 2: Use Signals for Deleting User-Related Data
    """
    if request.method == 'POST':
        user = request.user
        
        # Log out the user first
        logout(request)
        
        # Delete the user (signals will handle related data cleanup)
        user.delete()
        
        django_messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    
    return render(request, 'messaging/delete_user_confirm.html')


@login_required
def inbox(request):
    """
    Display inbox with unread messages.
    Task 4: Custom ORM Manager for Unread Messages
    Uses .only() to retrieve only necessary fields for optimization
    """
    # Use custom manager to get unread messages with optimized query using .only()
    unread_messages = Message.unread.unread_for_user(request.user)
    
    # Get all messages for the user with optimization using .only()
    all_messages = Message.objects.filter(
        receiver=request.user
    ).select_related('sender').prefetch_related('history').only(
        'id', 'sender', 'receiver', 'content', 'timestamp', 'read', 'edited'
    )
    
    context = {
        'unread_messages': unread_messages,
        'all_messages': all_messages,
        'unread_count': unread_messages.count()
    }
    
    return render(request, 'messaging/inbox.html', context)


@login_required
@cache_page(60)  # Cache for 60 seconds (Task 5)
def conversation_view(request, conversation_id):
    """
    Display a threaded conversation with caching.
    Task 3: Leverage Advanced ORM Techniques for Threaded Conversations
    Task 5: Implement basic view cache
    """
    # Get the main message with optimized queries
    main_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver')
                      .prefetch_related(
                          Prefetch(
                              'replies',
                              queryset=Message.objects.select_related('sender', 'receiver')
                                                     .prefetch_related('replies')
                          )
                      ),
        id=conversation_id
    )
    
    # Recursively get all replies
    def get_threaded_replies(message):
        """Recursively build threaded reply structure"""
        replies = message.replies.all()
        threaded = []
        for reply in replies:
            threaded.append({
                'message': reply,
                'replies': get_threaded_replies(reply)
            })
        return threaded
    
    threaded_conversation = {
        'message': main_message,
        'replies': get_threaded_replies(main_message)
    }
    
    context = {
        'conversation': threaded_conversation,
        'main_message': main_message
    }
    
    return render(request, 'messaging/conversation.html', context)


@login_required
def message_detail(request, message_id):
    """
    Display message details including edit history.
    Task 1: Display message edit history
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver')
                      .prefetch_related('history'),
        id=message_id
    )
    
    # Ensure user has permission to view this message
    if request.user not in [message.sender, message.receiver]:
        django_messages.error(request, 'You do not have permission to view this message.')
        return redirect('inbox')
    
    # Get edit history
    edit_history = message.history.all().select_related('edited_by')
    
    context = {
        'message': message,
        'edit_history': edit_history
    }
    
    return render(request, 'messaging/message_detail.html', context)


@login_required
def send_message(request):
    """Send a new message"""
    if request.method == 'POST':
        from django.contrib.auth.models import User
        
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        parent_message_id = request.POST.get('parent_message_id')
        
        receiver = get_object_or_404(User, id=receiver_id)
        
        parent_message = None
        if parent_message_id:
            parent_message = get_object_or_404(Message, id=parent_message_id)
        
        # Create message (signal will create notification automatically)
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            parent_message=parent_message
        )
        
        django_messages.success(request, 'Message sent successfully!')
        return redirect('inbox')
    
    from django.contrib.auth.models import User
    users = User.objects.exclude(id=request.user.id)
    
    return render(request, 'messaging/send_message.html', {'users': users})


@login_required
def edit_message(request, message_id):
    """Edit a message"""
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    
    if request.method == 'POST':
        new_content = request.POST.get('content')
        
        # Update message (pre_save signal will log the edit)
        message.content = new_content
        message.save()
        
        django_messages.success(request, 'Message updated successfully!')
        return redirect('message_detail', message_id=message.id)
    
    return render(request, 'messaging/edit_message.html', {'message': message})


@login_required
def notifications_view(request):
    """Display user notifications"""
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related('message').order_by('-timestamp')
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(read=False).count()
    }
    
    return render(request, 'messaging/notifications.html', context)


@login_required
def mark_message_read(request, message_id):
    """Mark a message as read"""
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    message.read = True
    message.save()
    
    return redirect('inbox')