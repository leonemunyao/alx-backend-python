from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal handler to create a notification when a new message is created.
    Only creates notifications for direct messages (with receiver fields).
    """
    if created and instance.receiver:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='message',
            title=f"New Message from {instance.sender.username}",
        )
