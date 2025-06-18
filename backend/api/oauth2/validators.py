from oauth2_provider.oauth2_validators import OAuth2Validator
from django.utils import timezone
from datetime import timedelta
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class OAuth2Validator(OAuth2Validator):
    """Custom OAuth2 validator for handling authorization code flow."""
    
    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        """Validate the authorization code."""
        # Get the code from the session
        stored_code = request.session.get('oauth2_code')
        if not stored_code or stored_code != code:
            return False
            
        # Clear the code from the session
        request.session.pop('oauth2_code', None)
        return True
        
    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        """Validate the grant type."""
        return grant_type in ['authorization_code', 'refresh_token']
        
    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        """Validate the requested scopes."""
        return True
        
    def validate_user(self, username, password, client, request, *args, **kwargs):
        """Validate the user credentials."""
        return True
        
    def validate_bearer_token(self, token, scopes, request):
        """Validate the bearer token."""
        if not token:
            return False
            
        # Check if it's a JWT token
        if token.startswith('eyJ'):
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                user_id = payload.get('user_id')
                if not user_id:
                    return False
                    
                user = User.objects.get(id=user_id)
                request.user = user
                return True
            except (jwt.InvalidTokenError, User.DoesNotExist):
                return False
                
        # Check if it's an OAuth2 token
        from .models import OAuth2Token
        try:
            oauth_token = OAuth2Token.objects.get(
                access_token=token,
                expires_at__gt=timezone.now()
            )
            request.user = oauth_token.user
            return True
        except OAuth2Token.DoesNotExist:
            return False 