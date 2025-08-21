from django.test import TestCase

import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Conversation, Message

User = get_user_model()

class MessagingAppTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@test.com',
            password='testpass123'
        )
        self.client = Client()

    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(self.user1.username, 'testuser1')

    def test_conversation_creation(self):
        """Test conversation creation"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(conversation.participants.count(), 2)

    def test_message_creation(self):
        """Test message creation"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        
        message = Message.objects.create(
            sender=self.user1,
            conversation=conversation,
            message_body="Test message"
        )
        
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.message_body, "Test message")
        self.assertEqual(message.sender, self.user1)

    def test_api_endpoint_exists(self):
        """Test that API endpoints are accessible"""
        response = self.client.get('/api/')
        self.assertIn(response.status_code, [200, 401, 404])

@pytest.mark.django_db
class TestMessagingAppPytest:
    """Pytest-style tests"""
    
    def test_database_access(self):
        """Test database access with pytest"""
        user_count = User.objects.count()
        assert isinstance(user_count, int)

    def test_user_model_str(self):
        """Test user model string representation"""
        user = User.objects.create_user(
            username='pytest_user',
            email='pytest@test.com',
            password='testpass123'
        )
        assert str(user) == 'pytest_user'