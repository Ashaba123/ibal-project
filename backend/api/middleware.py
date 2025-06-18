from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from oauth2_provider.models import AccessToken as OAuth2AccessToken
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

User = get_user_model()

class CombinedAuthMiddleware(BaseMiddleware):
    """
    Middleware that handles both JWT and OAuth2 authentication for WebSocket connections
    """
    async def __call__(self, scope, receive, send):
        # Get the token from the query string
        query_string = scope.get('query_string', b'').decode()
        token = None
        
        # Parse the query string
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
        
        if token:
            try:
                # Try JWT authentication first
                try:
                    access_token = AccessToken(token)
                    user_id = access_token['user_id']
                    scope['user'] = await self.get_user(user_id)
                except (InvalidToken, TokenError):
                    # If JWT fails, try OAuth2
                    try:
                        oauth_token = await self.get_oauth_token(token)
                        if oauth_token:
                            scope['user'] = await self.get_user(oauth_token.user_id)
                        else:
                            scope['user'] = AnonymousUser()
                    except Exception:
                        scope['user'] = AnonymousUser()
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
    
    @staticmethod
    @database_sync_to_async
    def get_user(user_id):
        """Get user asynchronously."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

    @staticmethod
    @database_sync_to_async
    def get_oauth_token(token):
        """Get OAuth token asynchronously."""
        try:
            return OAuth2AccessToken.objects.get(token=token)
        except OAuth2AccessToken.DoesNotExist:
            return None

def TokenAuthMiddlewareStack(inner):
    """Stack the token auth middleware with the auth middleware."""
    return CombinedAuthMiddleware(AuthMiddlewareStack(inner))

class AllowIframeEmbeddingMiddleware(MiddlewareMixin):
    """
    Middleware to allow iframe embedding for XBlock integration.
    This is required for the XBlock to be embedded in the OpenEdX platform.
    """
    def process_response(self, request, response):
        response['X-Frame-Options'] = 'ALLOW-FROM http://local.openedx.io'
        return response 