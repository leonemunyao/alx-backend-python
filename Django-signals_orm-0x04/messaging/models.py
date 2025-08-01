from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
import uuid
from .managers import UnreadMessagesManager


class User(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    """

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("user", "User"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="user",
        help_text="Role of the user in the application",
    )

    def is_admin(self):
        """Check if the user has admin role."""
        return self.role == "admin"

    def is_user(self):
        """Check if the user has user role."""
        return self.role == "user"

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
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
        null=True,
        blank=True,
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )

    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    read = models.BooleanField(default=False)

    # Managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        if self.receiver:
            return f"Message {self.message_id} from {self.sender.username} to {self.receiver.username} in Conversation {self.conversation.id}"
        return f"Message {self.message_id} from {self.sender.username} in Conversation {self.conversation.id}"

    @property
    def is_reply(self):
        """Check if the message is a reply to another message."""
        return self.parent_message is not None

    @property
    def get_thread_root(self):
        """Get the root message of the thread."""
        if self.parent_message:
            return self.parent_message.get_thread_root()
        return self


class MessageHistory(models.Model):
    """
    Model to keep track of message edits.
    """

    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="edit_history"
    )
    old_content = models.TextField()
    edited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="edited_messages"
    )
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-edited_at"]
        verbose_name = "Message Edit History"
        verbose_name_plural = "Message Edit History"

    def __str__(self):
        return f"Edit of Message {self.message.message_id} by {self.edited_by.username} at {self.edited_at}"


class Notification(models.Model):
    """
    Model for user notifications.
    """

    NOTIFICATION_TYPES = [
        ("message", "New Message"),
        ("mention", "Mention"),
        ("like", "Like"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default="message"
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title} - {self.content[:50]}..."
