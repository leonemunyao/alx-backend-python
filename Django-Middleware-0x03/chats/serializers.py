from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'sender_name', 'message_body', 'sent_at', 'conversation']
        read_only_fields = ['sent_at']

    def validate_message_body(self, data):
        if not data.get('message_body', '').strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return data

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    title = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at', 'updated_at', 'participant_count', 'title']
        read_only_fields = ['created_at', 'updated_at']

    def get_participant_count(self, obj):
        return obj.participants.count()

    def validate(self, data):
        participants = self.context.get('participants', [])
        if len(participants) < 2:
            raise serializers.ValidationError("A conversation must have at least two participants.")
        return data

    def create(self, validated_data):
        participants = self.context.get('participants', [])
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        return conversation
