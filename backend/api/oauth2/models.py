from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class OAuth2Client(models.Model):
    """
    OAuth2 client model for OpenEdX integration.
    """
    client_id = models.CharField(max_length=100, unique=True)
    client_secret = models.CharField(max_length=100)
    redirect_uri = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Client {self.client_id}"

    class Meta:
        verbose_name = "OAuth2 Client"
        verbose_name_plural = "OAuth2 Clients"

class OAuth2Token(models.Model):
    """OAuth2 token model."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, unique=True)
    refresh_token = models.CharField(max_length=255, unique=True, null=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'oauth2_token'
        
    def is_expired(self):
        """Check if the token is expired."""
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"Token for {self.user.username}"

    class Meta:
        verbose_name = "OAuth2 Token"
        verbose_name_plural = "OAuth2 Tokens" 