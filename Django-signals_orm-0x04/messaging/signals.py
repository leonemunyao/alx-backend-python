from django.utils import timezone
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory, User

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal handler to create a notification when a new message is created.
    Only creates notifications for direct messages (with receiver fields).
    """
    if created and instance.receiver:
        if instance.sender != instance.receiver:
            Notification.objects.create(
                user=instance.receiver,
                message=instance,
                notification_type='message',
                title=f"New Message from {instance.sender.username}",
                content=f"{instance.sender.username} sent you a message in Conversation {instance.conversation.id}",
            )


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal handler to log message edits.
    Creates a MessageHistory entry before the message is updated.
    Saves the old content to MessageHistory before the new content is saved.
    """

    if instance.pk:
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.content,
                    edited_by=old_message.sender,
                )

                instance.edited = True
                instance.edited_at = timezone.now()
        except Message.DoesNotExist:
            # If the message does not exist, this is a new message, so no history to log.
            pass

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal handler to clean up user data when a user is deleted.
    Deletes all messages, notifications, and message histories associated with the user.
    """
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(edited_by=instance).delete()
