from django.db import models
from django.conf import settings


# this model class is for oauth2 openedx
class OAuth2Client(models.Model):
    client_id = models.CharField(max_length=255, unique=True)
    client_secret = models.CharField(max_length=255)
    redirect_uri = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "OAuth2 Client"
        verbose_name_plural = "OAuth2 Clients"

    def __str__(self):
        return self.client_id

class OAuth2AuthorizationCode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client = models.ForeignKey(OAuth2Client, on_delete=models.CASCADE)
    redirect_uri = models.URLField(default="")

    class Meta:
        verbose_name = "OAuth2 Authorization Code"
        verbose_name_plural = "OAuth2 Authorization Codes"

    def __str__(self):
        return self.code

class OAuth2Token(models.Model):
    access_token = models.CharField(max_length=255, unique=True)
    refresh_token = models.CharField(max_length=255, unique=True, null=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "OAuth2 Token"
        verbose_name_plural = "OAuth2 Tokens"

    def __str__(self):
        return self.access_token
