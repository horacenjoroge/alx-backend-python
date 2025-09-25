"""
Custom filters for the messaging app.
"""
import django_filters
from django_filters import rest_framework as filters
from django.db import models
from .models import Message, Conversation, User


class MessageFilter(filters.FilterSet):
    """
    Filter class for Message model to retrieve conversations with specific users 
    or messages within a time range.
    """
    # Filter by conversation ID
    conversation = filters.UUIDFilter(field_name='conversation__conversation_id', lookup_expr='exact')
    
    # Filter by sender
    sender = filters.UUIDFilter(field_name='sender__user_id', lookup_expr='exact')
    sender_email = filters.CharFilter(field_name='sender__email', lookup_expr='icontains')
    
    # Filter by recipient
    recipient = filters.UUIDFilter(field_name='recipient__user_id', lookup_expr='exact')
    recipient_email = filters.CharFilter(field_name='recipient__email', lookup_expr='icontains')
    
    # Filter messages within a time range
    sent_at_after = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_at_before = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    sent_at_range = filters.DateFromToRangeFilter(field_name='sent_at')
    
    # Filter by date (specific day)
    sent_date = filters.DateFilter(field_name='sent_at', lookup_expr='date')
    
    # Filter by message content
    message_body = filters.CharFilter(field_name='message_body', lookup_expr='icontains')
    
    # Filter messages between specific users
    between_users = filters.CharFilter(method='filter_between_users')
    
    class Meta:
        model = Message
        fields = [
            'conversation',
            'sender', 
            'sender_email',
            'recipient',
            'recipient_email',
            'sent_at_after',
            'sent_at_before',
            'sent_at_range',
            'sent_date',
            'message_body',
            'between_users'
        ]
    
    def filter_between_users(self, queryset, name, value):
        """
        Custom filter to get messages between specific users.
        Expected format: 'user1_email,user2_email' or 'user1_id,user2_id'
        """
        if not value:
            return queryset
        
        try:
            user_identifiers = value.split(',')
            if len(user_identifiers) != 2:
                return queryset
            
            user1_identifier, user2_identifier = user_identifiers
            
            # Try to find users by email first, then by user_id
            try:
                if '@' in user1_identifier and '@' in user2_identifier:
                    # Filter by email
                    user1 = User.objects.get(email=user1_identifier.strip())
                    user2 = User.objects.get(email=user2_identifier.strip())
                else:
                    # Filter by user_id
                    user1 = User.objects.get(user_id=user1_identifier.strip())
                    user2 = User.objects.get(user_id=user2_identifier.strip())
                
                # Return messages between these two users (in both directions)
                return queryset.filter(
                    models.Q(sender=user1, recipient=user2) | 
                    models.Q(sender=user2, recipient=user1)
                )
            except User.DoesNotExist:
                return queryset.none()
                
        except (ValueError, AttributeError):
            return queryset


class ConversationFilter(filters.FilterSet):
    """
    Filter class for Conversation model.
    """
    # Filter by participant email
    participant_email = filters.CharFilter(method='filter_by_participant_email')
    
    # Filter by creation date range
    created_at_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    created_date = filters.DateFilter(field_name='created_at', lookup_expr='date')
    
    class Meta:
        model = Conversation
        fields = [
            'participant_email',
            'created_at_after',
            'created_at_before',
            'created_date'
        ]
    
    def filter_by_participant_email(self, queryset, name, value):
        """
        Filter conversations by participant email.
        """
        if not value:
            return queryset
        
        try:
            user = User.objects.get(email=value)
            return queryset.filter(participants=user)
        except User.DoesNotExist:
            return queryset.none()


class UserFilter(filters.FilterSet):
    """
    Filter class for User model.
    """
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    first_name = filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    role = filters.ChoiceFilter(choices=[('guest', 'Guest'), ('host', 'Host'), ('admin', 'Admin')])
    created_at_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = User
        fields = [
            'email',
            'first_name', 
            'last_name',
            'role',
            'created_at_after',
            'created_at_before'
        ]