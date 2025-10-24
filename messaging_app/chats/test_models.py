"""
Basic tests for the messaging app models
"""
import pytest
from django.test import TestCase
from chats.models import User, Conversation, Message


@pytest.mark.django_db
class TestUserModel(TestCase):
    """Test cases for User model"""
    
    def test_create_user(self):
        """Test creating a new user"""
        user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='pass123'
        )
        self.assertEqual(str(user), 'John Doe (test@example.com)')


@pytest.mark.django_db
class TestConversationModel(TestCase):
    """Test cases for Conversation model"""
    
    def setUp(self):
        """Set up test users"""
        self.user1 = User.objects.create_user(
            username='user1@example.com',
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2@example.com',
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='pass123'
        )
    
    def test_create_conversation(self):
        """Test creating a conversation"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        
        self.assertEqual(conversation.participants.count(), 2)
        self.assertIn(self.user1, conversation.participants.all())
        self.assertIn(self.user2, conversation.participants.all())


@pytest.mark.django_db
class TestMessageModel(TestCase):
    """Test cases for Message model"""
    
    def setUp(self):
        """Set up test users and conversation"""
        self.user1 = User.objects.create_user(
            username='sender@example.com',
            email='sender@example.com',
            first_name='Sender',
            last_name='User',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='receiver@example.com',
            email='receiver@example.com',
            first_name='Receiver',
            last_name='User',
            password='pass123'
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_create_message(self):
        """Test creating a message"""
        message = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            conversation=self.conversation,
            message_body='Hello, this is a test message!'
        )
        
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.recipient, self.user2)
        self.assertEqual(message.message_body, 'Hello, this is a test message!')
        self.assertIsNotNone(message.sent_at)
    
    def test_message_ordering(self):
        """Test that messages are ordered by sent_at descending"""
        message1 = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            conversation=self.conversation,
            message_body='First message'
        )
        message2 = Message.objects.create(
            sender=self.user2,
            recipient=self.user1,
            conversation=self.conversation,
            message_body='Second message'
        )
        
        messages = Message.objects.all()
        self.assertEqual(messages[0], message2)  # Most recent first
        self.assertEqual(messages[1], message1)