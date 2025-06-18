from django.contrib import admin
from .models import OAuth2Client, OAuth2Token

@admin.register(OAuth2Client)
class OAuth2ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'redirect_uri', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('client_id', 'redirect_uri')
    readonly_fields = ('created_at',)

@admin.register(OAuth2Token)
class OAuth2TokenAdmin(admin.ModelAdmin):
    """Admin configuration for OAuth2Token model."""
    list_display = ('user', 'access_token', 'refresh_token', 'expires_at', 'created_at')
    list_filter = ('expires_at', 'created_at')
    search_fields = ('user__username', 'user__email', 'access_token', 'refresh_token')
    readonly_fields = ('access_token', 'refresh_token', 'created_at') 