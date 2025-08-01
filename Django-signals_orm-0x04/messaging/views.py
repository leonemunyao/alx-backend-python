from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Conversation, Message, MessageHistory, Conversation
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsMessageOwner
from .pagination import MessagePagination, ConversationPagination
from .filters import MessageFilter, ConversationFilter


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    pagination_class = ConversationPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['participants__username']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['updated_at']

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
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation, IsMessageOwner]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        user_conversations = Conversation.objects.filter(participants=self.request.user)

        if 'conversation_pk' in self.kwargs:
            return Message.objects.filter(conversation_id=self.kwargs['conversation_pk'],
                                          conversation__in=user_conversations)

        elif 'conversation_id' in self.kwargs:
            return Message.objects.filter(conversation_id=self.kwargs['conversation_id'],
                                          conversation__in=user_conversations)
        return Message.objects.filter(conversation__in=user_conversations)

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id') or self.kwargs.get('conversation_pk')

        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
                if self.request.user not in conversation.participants.all():
                    return Response(
                        {"detail": "You are not a participant in this conversation."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                serializer.save(conversation=conversation, sender=self.request.user)
            except Conversation.DoesNotExist:
                return Response(
                    {"detail": "Conversation does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            serializer.save(sender=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Override update to add explicit permission check"""
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {"error": "You do not have permission to update this message."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs) 
    
    def delete(self, request, *args, **kwargs):
        """Override delete to add explicit permission check"""
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {"error": "You do not have permission to delete this message."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Override partial_update to add explicit permission check"""
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {"error": "You do not have permission to partially update this message."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

@login_required
def message_edit_history(request, message_id):
    """
    View to retrieve the edit history of a specific message.
    """
    message = get_object_or_404(Message, id=message_id)
    if request.user not in message.conversation.participants.all():
        return JsonResponse({"error": "You are not a participant in this conversation."}, status=403)

    history = MessageHistory.objects.filter(message=message).order_by('-edited_at')
    history_data = [
        {
            'old_content': entry.old_content,
            'edited_by': entry.edited_by.username,
            'edited_at': entry.edited_at
        } for entry in history
    ]
    return JsonResponse(history_data, safe=False)

@login_required
def message_edit(request, message_id):
    """
    View to edit a message.
    """
    
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return JsonResponse({"error": "You do not have permission to edit this message."}, status=403)

    if request.method == 'POST':
        new_content = request.POST.get('content')
        if new_content:
            message.content = new_content
            message.edited = True
            message.edited_at = timezone.now()
            message.save()
            return JsonResponse({"message": "Message updated successfully."}, status=200)
        return JsonResponse({"error": "Content cannot be empty."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)
