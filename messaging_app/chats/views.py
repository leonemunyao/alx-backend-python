from rest_framework import viewsets, permissions, status, filters
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer 
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']

    def get_queryset(self):
        if 'conversation_id' in self.kwargs:
            return Message.objects.filter(conversation_id=self.kwargs['conversation_id'])
        return Message.objects.all()

    def perform_create(self, serializer):
        if 'conversation_id' in self.kwargs:
            conversation = Conversation.objects.get(id=self.kwargs['conversation_id'])
            serializer.save(conversation=conversation, sender=self.request.user)
        else:
            serializer.save(sender=self.request.user)
