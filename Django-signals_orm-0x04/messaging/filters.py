import django_filters
from django.db import models
from .models import Message, Conversation, User

class MessageFilter(django_filters.FilterSet):
    """
    Filter class for Message model to filter by:
    - Specific users(sender)
    - Date range (sent within specific time)
    - Content search
    """

    # Filter by sender (specific user)
    sender = django_filters.ModelChoiceFilter(
        queryset = User.objects.all(),
        field_name = 'sender',
        help_text="Filter messages by the sender ID"
    )

    # Filter by sender username
    sender_username = django_filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains',
        help_text="Filter messages by sender's username"
    )

    # Filter by date range
    send_after = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        help_text="Filter messages sent after this date"
    )

    send_before = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        help_text="Filter messages sent before this date"
    )

    # Filter by content search
    content = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains',
        help_text='Search messages by content'
    )

    # Filter by conversation
    conversation = django_filters.NumberFilter(
        queryset=Conversation.objects.all(),
        field_name='conversation__conversation_id',
        help_text="Filter messages by conversation ID"
    )

    class Meta:
        model = Message
        fields = ['sender', 'sender_username', 'send_after', 'send_before', 'content', 'conversation']


class ConversationFilter(django_filters.FilterSet):
    """Filter class for Conversation model to filter by:
    - Participants
    - Date range
    """

    # Filter conversations with a specific participant
    participant = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants',
        help_text="Filter conversations by participants ID"
    )

    # Filter conversations with specific participant username
    participant_username = django_filters.CharFilter(
        field_name='participants__username',
        lookup_expr='icontains',
        help_text="Fielter conversations by participant's username"
    )

    # Filter by creation date range
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter conversations created after this date"
    )

    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter conversations created before this date"
    )

    class Meta:
        model = Conversation
        fields = ['participants', 'participant_username', 'created_after', 'created_before']

    