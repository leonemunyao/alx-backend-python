from django.test import TestCase

# Create your tests here.

from .models import User, Message, Conversation, Notification


class MessageNotificationSignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create(
            username="sender", email="sender@example.com", password="password"
        )
        self.recipient = User.objects.create(
            username="recipient",
            email="recipient@example.com",
            password="password",
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.sender, self.recipient)

    def test_create_message_notification(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.recipient,
            conversation=self.conversation,
            content="Hello!",
        )
        notification = Notification.objects.filter(
            user=self.recipient, message=message
        ).first()

        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, "message")
        self.assertEqual(
            notification.title, f"New Message from {self.sender.username}"
        )
        self.assertFalse(notification.is_read)


class UnreadMessagesManagerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="password"
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_for_user_returns_unread_messages(self):
        """Test that for_user returns only unread messages for the specified user"""
        # Create read and unread messages
        read_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            conversation=self.conversation,
            content="Read message",
            read=True,
        )

        unread_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            conversation=self.conversation,
            content="Unread message",
            read=False,
        )

        # Test custom manager
        unread_messages = Message.unread.unread_for_user(self.user2)

        self.assertIn(unread_message, unread_messages)
        self.assertNotIn(read_message, unread_messages)
        self.assertEqual(unread_messages.count(), 1)

    def test_unread_direct_messages(self):
        """Test unread direct messages manager method"""
        direct_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            conversation=self.conversation,
            content="Direct message",
            read=False,
        )

        # Test with .only() optimization
        unread_direct = Message.unread.unread_direct_messages(self.user2)

        self.assertEqual(unread_direct.count(), 1)
        self.assertEqual(
            unread_direct.first().message_id, direct_message.message_id
        )

    def test_unread_in_conversation(self):
        """Test unread messages in specific conversation"""
        message1 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            content="Message 1",
            read=False,
        )

        message2 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            content="Message 2",
            read=True,
        )

        unread_in_conv = Message.unread.unread_in_conversation(
            self.user2, self.conversation
        )

        self.assertEqual(unread_in_conv.count(), 1)
        self.assertEqual(
            unread_in_conv.first().message_id, message1.message_id
        )

    def test_mark_as_read(self):
        """Test marking messages as read"""
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            conversation=self.conversation,
            content="Message 1",
            read=False,
        )

        message2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            conversation=self.conversation,
            content="Message 2",
            read=False,
        )

        # Mark specific message as read
        updated_count = Message.unread.mark_as_read(
            self.user2, [message1.message_id]
        )

        self.assertEqual(updated_count, 1)
        message1.refresh_from_db()
        message2.refresh_from_db()
        self.assertTrue(message1.read)
        self.assertFalse(message2.read)

    def test_mark_all_as_read(self):
        """Test marking all messages as read for a user"""
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            conversation=self.conversation,
            content="Message 1",
            read=False,
        )

        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            conversation=self.conversation,
            content="Message 2",
            read=False,
        )

        # Mark all as read
        updated_count = Message.unread.mark_as_read(self.user2)

        self.assertEqual(updated_count, 2)
        self.assertEqual(
            Message.objects.filter(receiver=self.user2, read=False).count(), 0
        )

    def test_excludes_sender_messages(self):
        """Test that manager excludes messages sent by the user"""
        # User sends message to themselves
        self_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user1,
            conversation=self.conversation,
            content="Message to self",
            read=False,
        )

        unread_messages = Message.unread.unread_for_user(self.user1)

        self.assertNotIn(self_message, unread_messages)
        self.assertEqual(unread_messages.count(), 0)
