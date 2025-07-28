from django.test import TestCase

# Create your tests here.

from .models import User, Message, Conversation, Notification


class MessageNotificationSignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create(
            username='sender',
            email='sender@example.com',
            password='password'
        )
        self.recipient = User.objects.create(
            username='recipient',
            email='recipient@example.com',
            password='password'
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.sender, self.recipient)

    def test_create_message_notification(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.recipient,
            conversation=self.conversation,
            message_body='Hello!'
        )
        notification = Notification.objects.filter(user=self.recipient, message=message).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, 'message')
        self.assertEqual(notification.title, f"New Message from {self.sender.username}")
        self.assertFalse(notification.is_read)


