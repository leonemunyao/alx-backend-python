from rest_framework import viewsets, permissions, status, filters
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsOwnerOrReadOnly, IsParticipantReadOnly, IsMessageOwner


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantReadOnly, IsOwnerOrReadOnly, 
                          IsMessageOwner]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        # Only return conversations where the user is a participant.
        return Conversation.objects.filter(participants=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer 
    permission_classes = [permissions.IsAuthenticated, IsMessageOwner]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']

    def get_queryset(self):
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        if 'conversation_id' in self.kwargs:
            return Message.objects.filter(conversation_id=self.kwargs['conversation_id'],
                                          conversation__in=user_conversations)
        return Message.objects.filter(conversation__in=user_conversations)

    def perform_create(self, serializer):
        if 'conversation_id' in self.kwargs:
            conversation = Conversation.objects.get(id=self.kwargs['conversation_id'])
            if self.request.user in conversation.participants.all():
                serializer.save(conversation=conversation, sender=self.request.user)
        else:
            serializer.save(sender=self.request.user)
