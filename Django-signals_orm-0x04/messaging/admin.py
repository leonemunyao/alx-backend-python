from django.contrib import admin
from .models import Notification, User, Conversation, Message

# Register your models here.

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message_body')
    ordering = ('-created_at',)

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"

    actions = [mark_as_read]

