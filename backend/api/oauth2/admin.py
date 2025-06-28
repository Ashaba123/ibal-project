from django.contrib import admin
from .models import OAuth2Client

@admin.register(OAuth2Client)
class OAuth2ClientAdmin(admin.ModelAdmin):
    list_display = ("client_id", "client_secret", "redirect_uri", "is_active", "created_at")
    search_fields = ("client_id",) 