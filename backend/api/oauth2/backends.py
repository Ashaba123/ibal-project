from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.oauth2_validators import OAuth2Validator
from django.utils import timezone
from datetime import timedelta
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from oauthlib.oauth2 import Server

User = get_user_model()

class OAuth2Backend(OAuthLibCore):
    """Custom OAuth2 backend for handling authorization code flow."""
    
    def __init__(self, server=None):
        if server is None:
            server = Server(OAuth2Validator())
        super().__init__(server)
        
    def authenticate(self, request=None, **credentials):
        """Authenticate a user based on OAuth2 credentials."""
        if request is None:
            return None
            
        # Get the token from the request
        token = request.GET.get('token')
        if not token:
            return None
            
        # Get the auth type
        auth_type = request.GET.get('auth_type')
        if not auth_type:
            return None
            
        # Verify token based on auth type
        if auth_type == 'jwt':
            from rest_framework_simplejwt.tokens import AccessToken
            from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                return User.objects.get(id=user_id)
            except (InvalidToken, TokenError, User.DoesNotExist):
                return None
        elif auth_type == 'oauth2':
            from .models import OAuth2Token
            try:
                oauth_token = OAuth2Token.objects.get(
                    access_token=token,
                    expires_at__gt=timezone.now()
                )
                return oauth_token.user
            except OAuth2Token.DoesNotExist:
                return None
        return None 