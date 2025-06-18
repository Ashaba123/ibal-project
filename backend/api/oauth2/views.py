from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import OAuth2Client, OAuth2Token
import jwt
import uuid
from datetime import timedelta
from django.conf import settings
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .backends import OAuth2Backend
from .validators import OAuth2Validator
from oauth2_provider.oauth2_backends import get_oauthlib_core

User = get_user_model()

class OAuth2AuthorizationView(APIView):
    """
    OAuth2 authorization endpoint for OpenEdX XBlock.
    """
    permission_classes = [AllowAny]
    backend = OAuth2Backend()
    validator = OAuth2Validator()

    def get(self, request):
        """Handle authorization request."""
        # Get the client ID and response type
        client_id = request.GET.get('client_id')
        response_type = request.GET.get('response_type')
        
        if not client_id or not response_type:
            return Response({
                'error': 'invalid_request',
                'error_description': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if response_type != 'code':
            return Response({
                'error': 'unsupported_response_type',
                'error_description': 'Only authorization code flow is supported'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Generate authorization code
        code = jwt.encode({
            'client_id': client_id,
            'exp': timezone.now() + timedelta(minutes=10)
        }, settings.SECRET_KEY, algorithm='HS256')
        
        # Store code in session
        request.session['oauth2_code'] = code
        
        return Response({
            'code': code
        })

class OAuth2TokenView(APIView):
    """
    OAuth2 token endpoint for exchanging authorization code for tokens.
    """
    permission_classes = [AllowAny]
    backend = OAuth2Backend()
    validator = OAuth2Validator()

    def post(self, request):
        """Handle token request."""
        # Get the grant type
        grant_type = request.data.get('grant_type')
        if not grant_type:
            return Response({
                'error': 'invalid_request',
                'error_description': 'Missing grant_type'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Get OAuth2 core
        oauthlib_core = get_oauthlib_core()
        
        # Validate grant type
        if not self.validator.validate_grant_type(
            request.data.get('client_id'),
            grant_type,
            None,
            request
        ):
            return Response({
                'error': 'unsupported_grant_type',
                'error_description': 'Grant type not supported'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Handle authorization code grant
        if grant_type == 'authorization_code':
            code = request.data.get('code')
            if not code:
                return Response({
                    'error': 'invalid_request',
                    'error_description': 'Missing code'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Validate code
            if not self.validator.validate_code(
                request.data.get('client_id'),
                code,
                None,
                request
            ):
                return Response({
                    'error': 'invalid_grant',
                    'error_description': 'Invalid authorization code'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Generate access token
            access_token = jwt.encode({
                'user_id': request.user.id,
                'exp': timezone.now() + timedelta(hours=10)
            }, settings.SECRET_KEY, algorithm='HS256')
            
            # Generate refresh token
            refresh_token = jwt.encode({
                'user_id': request.user.id,
                'exp': timezone.now() + timedelta(days=7)
            }, settings.SECRET_KEY, algorithm='HS256')
            
            # Store tokens
            OAuth2Token.objects.create(
                user=request.user,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=timezone.now() + timedelta(hours=10)
            )
            
            return Response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': 36000
            })
            
        # Handle refresh token grant
        elif grant_type == 'refresh_token':
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({
                    'error': 'invalid_request',
                    'error_description': 'Missing refresh_token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                # Verify refresh token
                payload = jwt.decode(
                    refresh_token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                user_id = payload.get('user_id')
                if not user_id:
                    raise jwt.InvalidTokenError
                    
                # Generate new access token
                access_token = jwt.encode({
                    'user_id': user_id,
                    'exp': timezone.now() + timedelta(hours=10)
                }, settings.SECRET_KEY, algorithm='HS256')
                
                # Store new token
                OAuth2Token.objects.create(
                    user_id=user_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_at=timezone.now() + timedelta(hours=10)
                )
                
                return Response({
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'expires_in': 36000
                })
            except jwt.InvalidTokenError:
                return Response({
                    'error': 'invalid_grant',
                    'error_description': 'Invalid refresh token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        return Response({
            'error': 'unsupported_grant_type',
            'error_description': 'Grant type not supported'
        }, status=status.HTTP_400_BAD_REQUEST)

class OAuth2UserInfoView(APIView):
    """
    OAuth2 user info endpoint for retrieving user information.
    """
    permission_classes = [AllowAny]
    backend = OAuth2Backend()
    validator = OAuth2Validator()

    def get(self, request):
        """Get user info."""
        # Get the token from the authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({
                'error': 'invalid_request',
                'error_description': 'Missing or invalid authorization header'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        token = auth_header.split(' ')[1]
        
        # Validate token
        if not self.validator.validate_bearer_token(token, [], request):
            return Response({
                'error': 'invalid_token',
                'error_description': 'Invalid access token'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        # Return user info
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email
        }) 