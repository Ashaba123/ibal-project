from django.contrib import admin
from .models import ChatSession, Message

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'content', 'is_from_user', 'created_at')
    list_filter = ('is_from_user', 'created_at')
    search_fields = ('content', 'session__user__username') 