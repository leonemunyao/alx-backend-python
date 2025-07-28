from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
import uuid


class User(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    """

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text="Role of the user in the application"
    )

    def is_admin(self):
        """Check if the user has admin role."""
        return self.role == 'admin'
    
    def is_user(self):
        """Check if the user has user role."""
        return self.role == 'user'

    user_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    username = models.CharField(
        max_length=150, unique=True, help_text="Unique username for login"
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Conversation(models.Model):
    """
    Model representing a conversation between users
    Must contain the conversation ID.
    """
    conversation_id = models.AutoField(primary_key=True)
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.conversation_id} with {self.participants.count()} participants"


class Message(models.Model):
    """Message model containing the sender, conversations."""

    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.receiver:
            return f"Message {self.message_id} from {self.sender.username} to {self.receiver.username} in Conversation {self.conversation.id}"
        return f"Message {self.message_id} from {self.sender.username} in Conversation {self.conversation.id}"



class Notification(models.Model):
    """
    Model for user notifications.
    """
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('mention', 'Mention'),
        ('like', 'Like'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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

    title = models.CharField(max_length=255)
    message_body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title} - {self.message_body[:50]}..."
