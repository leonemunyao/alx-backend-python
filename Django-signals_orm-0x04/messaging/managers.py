from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager for filtering unread messages for a specific user.
    """

    def unread_for_user(self, user):
        """
        Get all unread messages for a specific user.
        Includes messages where the user is the receiver and messages in conversations they participate in.
        """
        return (
            self.get_queryset()
            .filter(
                models.Q(receiver=user, read=False)
                | models.Q(conversation__participants=user, read=False)
            )
            .exclude(sender=user)
            .distinct()
        )

    def unread_direct_messages(self, user):
        """
        Get unread direct messages where the user is the receiver.
        """
        return (
            self.get_queryset()
            .filter(receiver=user, read=False)
            .only("message_id", "sender__username", "content", "timestamp")
        )

    def unread_in_conversation(self, user, conversation):
        """
        Get unread messages in a specific conversation for a user.
        """
        return (
            self.get_queryset()
            .filter(conversation=conversation, read=False)
            .exclude(sender=user)
            .only("message_id", "sender__username", "content", "timestamp")
        )

    def mark_as_read(self, user, message_ids=None):
        """
        Mark messages as read for a user.
        If message_ids is provided, mark only those messages.
        Otherwise, mark all unread messages for the user.
        """
        queryset = self.unread_for_user(user)
        if message_ids:
            queryset = queryset.filter(message_id__in=message_ids)
        return queryset.update(read=True)
