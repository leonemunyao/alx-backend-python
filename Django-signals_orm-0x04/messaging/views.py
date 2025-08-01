from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from .models import Conversation, Message, MessageHistory, Conversation
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsMessageOwner
from .pagination import MessagePagination, ConversationPagination
from .filters import MessageFilter, ConversationFilter


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsParticipantOfConversation,
    ]
    pagination_class = ConversationPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ConversationFilter
    search_fields = ["participants__username"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["updated_at"]

    def get_queryset(self):
        # Only return conversations where the user is a participant.
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        # When creating a conversarion, add the creater as a participant.
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsParticipantOfConversation,
        IsMessageOwner,
    ]
    pagination_class = MessagePagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = MessageFilter
    search_fields = ["content", "sender__username"]  # Fixed field name
    ordering_fields = ["timestamp"]  # Fixed field name
    ordering = ["-timestamp"]  # Fixed field name

    def get_queryset(self):
        user_conversations = Conversation.objects.filter(
            participants=self.request.user
        )

        # Base queryset with optimizations
        base_queryset = Message.objects.select_related(
            "sender", "receiver", "conversation", "parent_message"
        ).prefetch_related("replies")

        if "conversation_pk" in self.kwargs:
            return base_queryset.filter(
                conversation_id=self.kwargs["conversation_pk"],
                conversation__in=user_conversations,
            )

        elif "conversation_id" in self.kwargs:
            return base_queryset.filter(
                conversation_id=self.kwargs["conversation_id"],
                conversation__in=user_conversations,
            )
        return base_queryset.filter(conversation__in=user_conversations)

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get(
            "conversation_id"
        ) or self.kwargs.get("conversation_pk")

        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
                if self.request.user not in conversation.participants.all():
                    return Response(
                        {
                            "detail": "You are not a participant in this conversation."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                serializer.save(
                    conversation=conversation, sender=self.request.user
                )
            except Conversation.DoesNotExist:
                return Response(
                    {"detail": "Conversation does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            serializer.save(sender=self.request.user)

    def update(self, request, *args, **kwargs):
        """Override update to add explicit permission check"""
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {
                    "error": "You do not have permission to update this message."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Override delete to add explicit permission check"""
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {
                    "error": "You do not have permission to delete this message."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().delete(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Override partial_update to add explicit permission check"""
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {
                    "error": "You do not have permission to partially update this message."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)


@login_required
def message_edit_history(request, message_id):
    """
    View to retrieve the edit history of a specific message.
    """
    message = get_object_or_404(Message, id=message_id)
    if request.user not in message.conversation.participants.all():
        return JsonResponse(
            {"error": "You are not a participant in this conversation."},
            status=403,
        )

    history = MessageHistory.objects.filter(message=message).order_by(
        "-edited_at"
    )
    history_data = [
        {
            "old_content": entry.old_content,
            "edited_by": entry.edited_by.username,
            "edited_at": entry.edited_at,
        }
        for entry in history
    ]
    return JsonResponse(history_data, safe=False)


@login_required
def message_edit(request, message_id):
    """
    View to edit a message.
    """

    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return JsonResponse(
            {"error": "You do not have permission to edit this message."},
            status=403,
        )

    if request.method == "POST":
        new_content = request.POST.get("content")
        if new_content:
            message.content = new_content
            message.edited = True
            message.edited_at = timezone.now()
            message.save()
            return JsonResponse(
                {"message": "Message updated successfully."}, status=200
            )
        return JsonResponse({"error": "Content cannot be empty."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@cache_page(60)  # Cache for 60 seconds
@login_required
def threaded_conversation(request, conversation_id):
    """
    View to retrieve a conversation with threaded messages using optimized queries.
    """
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse(
                {"error": "You are not a participant in this conversation."},
                status=403,
            )

        messages = (
            Message.objects.filter(
                conversation=conversation, parent_message__isnull=True
            )
            .select_related("sender", "receiver")
            .prefetch_related(
                Prefetch(
                    "replies",
                    queryset=MessageHistory.objects.order_by("-edited_at"),
                )
            )
            .order_by("timestamp")
        )

        messages_data = []
        for message in messages:
            message_data = {
                "message_id": message.message_id,
                "sender": message.sender.username,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "edited": message.edited,
                "replies": [],
            }

            for reply in message.replies.all():
                reply_data = {
                    "message_id": reply.message_id,
                    "sender": reply.sender.username,
                    "content": reply.content,
                    "timestamp": reply.timestamp.isoformat(),
                    "edited": reply.edited,
                    "parent_message_id": (
                        reply.parent_message.message_id
                        if reply.parent_message
                        else None
                    ),
                }
                message_data["replies"].append(reply_data)

            messages_data.append(message_data)

        return JsonResponse(
            {
                "conversation_id": conversation.conversation_id,
                "messages": messages_data,
            }
        )
    except Conversation.DoesNotExist:
        return JsonResponse(
            {"error": "Conversation does not exist."}, status=404
        )


@login_required
def create_reply(request, message_id):
    """
    View to create a reply to a specific message.
    """

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        parent_message = Message.objects.select_related(
            "conversation", "sender"
        ).get(message_id=message_id)

        if request.user not in parent_message.conversation.participants.all():
            return JsonResponse(
                {"error": "You are not a participant in this conversation."},
                status=403,
            )

        content = request.POST.get("content", "").strip()
        if not content:
            return JsonResponse(
                {"error": "Content cannot be empty."}, status=400
            )

        reply = Message.objects.create(
            sender=request.user,
            conversation=parent_message.conversation,
            content=content,
            parent_message=parent_message,
        )

        return JsonResponse(
            {
                "message_id": reply.message_id,
                "sender": reply.sender.username,
                "content": reply.content,
                "timestamp": reply.timestamp.isoformat(),
                "edited": reply.edited,
                "parent_message_id": parent_message.message_id,
            },
            status=201,
        )
    except Message.DoesNotExist:
        return JsonResponse({"error": "Message does not exist."}, status=404)


@cache_page(60)  # Cache for 60 seconds
@login_required
def message_thread(request, message_id):
    """
    View to get all messages in a thread (recursive query).
    """

    try:
        message = Message.objects.select_related("sender", "conversation").get(
            message_id=message_id
        )

        if request.user not in message.conversation.participants.all():
            return JsonResponse(
                {"error": "You are not a participant in this conversation."},
                status=403,
            )

        root_message = message.get_thread_root()

        def get_message_with_replies(msg):
            """
            Recursive function to get a message and its replies.
            """

            replies = (
                Message.objects.filter(parent_message=msg)
                .select_related("sender")
                .order_by("timestamp")
            )

            message_data = {
                "message_id": msg.message_id,
                "sender": msg.sender.username,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "edited": msg.edited,
                "is_reply": msg.is_reply,
                "replies": [
                    get_message_with_replies(reply) for reply in replies
                ],
            }

            for reply in replies:
                message_data["replies"].append(get_message_with_replies(reply))

            return message_data

        thread_data = get_message_with_replies(root_message)

        return JsonResponse(
            {
                "thread": thread_data,
                "total_messages_in_thread": count_message_in_thread(
                    root_message
                ),
            }
        )

    except Message.DoesNotExist:
        return JsonResponse({"error": "Message does not exist."}, status=404)


def count_message_in_thread(root_message):
    """
    Count all messages in a thread, including replies.
    """
    count = 1  # Count the root message
    replies = Message.objects.filter(parent_message=root_message)
    for reply in replies:
        count += count_message_in_thread(reply)
    return count


@login_required
def delete_user(request):
    """
    View to delete the current user.
    """
    user = request.user
    if request.method == "POST":
        user.delete()
        return JsonResponse(
            {"message": "User deleted successfully."}, status=200
        )
    return JsonResponse({"error": "Invalid request method."}, status=405)


@cache_page(60)  # Cache for 60 seconds
@login_required
def unread_messages_inbox(request):
    """
    View to display all unread messages for the current user using custom manager.
    Optimized with .only() to retrieve only necessary fields.
    """
    # Get unread messages using custom manager with optimizations
    unread_messages = (
        Message.unread.unread_for_user(request.user)
        .only(
            "message_id",
            "content",
            "timestamp",
            "sender__username",
            "conversation__conversation_id",
        )
        .select_related("sender", "conversation")
        .order_by("-timestamp")
    )

    messages_data = []
    for message in unread_messages:
        messages_data.append(
            {
                "message_id": message.message_id,
                "sender": message.sender.username,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "conversation_id": message.conversation.conversation_id,
            }
        )

    return JsonResponse(
        {"unread_count": len(messages_data), "messages": messages_data}
    )


@login_required
def unread_direct_messages(request):
    """
    View to display unread direct messages for the current user.
    """
    unread_direct = Message.unread.unread_direct_messages(
        request.user
    ).select_related("sender")

    messages_data = []
    for message in unread_direct:
        messages_data.append(
            {
                "message_id": message.message_id,
                "sender": message.sender.username,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
            }
        )

    return JsonResponse(
        {"unread_direct_count": len(messages_data), "messages": messages_data}
    )


@login_required
def unread_in_conversation(request, conversation_id):
    """
    View to display unread messages in a specific conversation.
    """
    try:
        conversation = get_object_or_404(
            Conversation, conversation_id=conversation_id
        )

        # Check if user is participant
        if request.user not in conversation.participants.all():
            return JsonResponse(
                {"error": "You are not a participant in this conversation."},
                status=403,
            )

        unread_messages = Message.unread.unread_in_conversation(
            request.user, conversation
        ).select_related("sender")

        messages_data = []
        for message in unread_messages:
            messages_data.append(
                {
                    "message_id": message.message_id,
                    "sender": message.sender.username,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                }
            )

        return JsonResponse(
            {
                "conversation_id": conversation.conversation_id,
                "unread_count": len(messages_data),
                "messages": messages_data,
            }
        )

    except Conversation.DoesNotExist:
        return JsonResponse({"error": "Conversation not found."}, status=404)


@login_required
def mark_messages_as_read(request):
    """
    View to mark messages as read for the current user.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    message_ids = request.POST.getlist("message_ids[]")

    if message_ids:
        # Mark specific messages as read
        updated_count = Message.unread.mark_as_read(request.user, message_ids)
    else:
        # Mark all unread messages as read
        updated_count = Message.unread.mark_as_read(request.user)

    return JsonResponse(
        {
            "message": f"{updated_count} messages marked as read.",
            "updated_count": updated_count,
        }
    )


@login_required
def unread_count(request):
    """
    View to get the count of unread messages for the current user.
    """
    count = Message.unread.unread_for_user(request.user).count()

    return JsonResponse({"unread_count": count})
