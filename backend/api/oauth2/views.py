from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
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
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
import os
from dotenv import load_dotenv
import secrets
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import BasicAuthentication
from urllib.parse import urlparse
import requests
from django.shortcuts import render
from .models import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token

# Load environment variables from .env file
load_dotenv(dotenv_path='C:\Coding Projects\ibal-project\backend\.env')

User = get_user_model()
logger = logging.getLogger(__name__)

class OAuth2AuthorizationView(APIView):
    """
    OAuth2 authorization endpoint for OpenEdX XBlock.
    """
    permission_classes = [AllowAny]
    backend = OAuth2Backend()
    validator = OAuth2Validator()

    def get(self, request):
        """Handle authorization request."""
        client_id = request.GET.get('client_id')
        response_type = request.GET.get('response_type')
        # Hardcode redirect_uri
        redirect_uri = "http://mylocal.test:8000/api/oauth/callback/"
        logger.info('OAuth2 authorization redirect_uri: %s', redirect_uri)
        if not client_id or not response_type or not redirect_uri:
            return Response({
                'error': 'invalid_request',
                'error_description': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        if response_type != 'code':
            return Response({
                'error': 'unsupported_response_type',
                'error_description': 'Only authorization code flow is supported'
            }, status=status.HTTP_400_BAD_REQUEST)
        code = secrets.token_urlsafe(32)
        client = OAuth2Client.objects.filter(client_id=client_id).first()
        if not client:
            return Response({'error': 'invalid_client'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.first()
        expires_at = timezone.now() + timedelta(minutes=10)
        OAuth2AuthorizationCode.objects.create(
            user=user,
            client=client,
            code=code,
            expires_at=expires_at,
            redirect_uri=redirect_uri
        )
        return Response({'code': code})

@csrf_exempt
@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([AllowAny])
def oauth_token_view(request):
    logger.info('Entered oauth_token_view')
    logger.info('Request method: %s', request.method)
    logger.info('Request headers: %s', dict(request.headers))
    logger.info('Request data: %s', request.data)
    # Hardcode redirect_uri
    redirect_uri = "http://mylocal.test:8000/api/oauth/callback/"
    grant_type = request.data.get('grant_type')
    if not grant_type:
        logger.error('Missing grant_type in request')
        logger.error('Returning 400 due to missing grant_type')
        return Response({
            'error': 'invalid_request',
            'error_description': 'Missing grant_type'
        }, status=status.HTTP_400_BAD_REQUEST)
    validator = OAuth2Validator()
    if not validator.validate_grant_type(
        request.data.get('client_id'),
        grant_type,
        None,
        request
    ):
        logger.error('Unsupported grant_type: %s', grant_type)
        logger.error('Returning 400 due to unsupported grant_type')
        return Response({
            'error': 'unsupported_grant_type',
            'error_description': 'Grant type not supported'
        }, status=status.HTTP_400_BAD_REQUEST)
    if grant_type == 'authorization_code':
        code = request.data.get('code')
        client_id = request.data.get('client_id')
        # Use the hardcoded redirect_uri for all logic
        logger.info('redirect_uri: %s', redirect_uri)
        if not code or not client_id or not redirect_uri:
            logger.error('Missing code, client_id, or redirect_uri for authorization_code grant')
            logger.error('Returning 400 due to missing code, client_id, or redirect_uri')
            return Response({'error': 'invalid_request', 'error_description': 'Missing code, client_id, or redirect_uri'}, status=status.HTTP_400_BAD_REQUEST)
        client = OAuth2Client.objects.filter(client_id=client_id).first()
        if not client:
            logger.error('Invalid client_id: %s', client_id)
            logger.error('Returning 400 due to invalid client_id')
            return Response({'error': 'invalid_client'}, status=status.HTTP_400_BAD_REQUEST)
        auth_code = OAuth2AuthorizationCode.objects.filter(code=code, client=client, used=False).first()
        logger.info('Authorization code lookup result: %s', 'FOUND' if auth_code else 'NOT FOUND')
        if not auth_code:
            logger.error('Invalid authorization code: %s', code)
            logger.error('Returning 400 due to invalid authorization code')
            return Response({'error': 'invalid_grant', 'error_description': 'Invalid authorization code'}, status=status.HTTP_400_BAD_REQUEST)
        # Check redirect_uri matches
        if auth_code.redirect_uri != redirect_uri:
            logger.error('Redirect URI mismatch: expected %s, got %s', auth_code.redirect_uri, redirect_uri)
            logger.error('Returning 400 due to redirect_uri mismatch')
            return Response({'error': 'invalid_grant', 'error_description': 'Redirect URI mismatch'}, status=status.HTTP_400_BAD_REQUEST)
        # Check expiration with 1 minute grace period
        now = timezone.now()
        if now > auth_code.expires_at + timedelta(minutes=1):
            logger.error('Authorization code expired: now=%s, expires_at=%s', now, auth_code.expires_at)
            logger.error('Returning 400 due to expired authorization code')
            return Response({'error': 'invalid_grant', 'error_description': 'Expired authorization code'}, status=status.HTTP_400_BAD_REQUEST)
        auth_code.used = True
        auth_code.save()
        user = auth_code.user
        access_token = jwt.encode({
            'user_id': user.id,
            'exp': timezone.now() + timedelta(hours=10)
        }, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode({
            'user_id': user.id,
            'exp': timezone.now() + timedelta(days=7)
        }, settings.SECRET_KEY, algorithm='HS256')
        OAuth2Token.objects.create(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=timezone.now() + timedelta(hours=10)
        )
        logger.info('Access and refresh tokens generated for user_id: %s', user.id)
        logger.info('Returning 200 with access and refresh tokens')
        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 36000
        })
    elif grant_type == 'refresh_token':
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            logger.error('Missing refresh_token for refresh_token grant')
            logger.error('Returning 400 due to missing refresh_token')
            return Response({
                'error': 'invalid_request',
                'error_description': 'Missing refresh_token'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            user_id = payload.get('user_id')
            if not user_id:
                logger.error('No user_id in refresh_token payload')
                logger.error('Returning 400 due to no user_id in refresh_token payload')
                raise jwt.InvalidTokenError
            access_token = jwt.encode({
                'user_id': user_id,
                'exp': timezone.now() + timedelta(hours=10)
            }, settings.SECRET_KEY, algorithm='HS256')
            OAuth2Token.objects.create(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=timezone.now() + timedelta(hours=10)
            )
            logger.info('New access token generated for user_id: %s via refresh_token', user_id)
            logger.info('Returning 200 with new access token')
            return Response({
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': 36000
            })
        except jwt.InvalidTokenError:
            logger.error('Invalid refresh token: %s', refresh_token)
            logger.error('Returning 400 due to invalid refresh token')
            return Response({
                'error': 'invalid_grant',
                'error_description': 'Invalid refresh token'
            }, status=status.HTTP_400_BAD_REQUEST)
    logger.error('Unsupported grant_type: %s', grant_type)
    logger.error('Returning 400 due to unsupported grant_type')
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

class OAuth2CallbackView(View):
    """
    Handles the OAuth2 redirect callback. Exchanges code for token with Open edX.
    """
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return HttpResponse('No code provided.', status=400)
        client_id = os.environ.get('OPENEDX_CLIENT_ID', 'MISSING_CLIENT_ID')
        client_secret = os.environ.get('OPENEDX_CLIENT_SECRET', 'MISSING_CLIENT_SECRET')
        redirect_uri = 'http://mylocal.test:8000/api/oauth/callback/'
        token_url = os.environ.get('OPENEDX_TOKEN_URL', 'http://local.openedx.io/oauth2/access_token/')
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret,
        }
        resp = requests.post(token_url, data=data)
        if resp.status_code == 200:
            token_data = resp.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in")
            token_type = token_data.get("token_type")
            
            logger.info(f"OAuth2 callback: Received OpenEdX access_token: {access_token[:20]}...")
            
            # Generate a JWT token for WebSocket authentication
            # For now, we'll use a placeholder user ID since we don't have user info from OpenEdX
            # In a real implementation, you would fetch user info from OpenEdX using the access token
            import jwt
            from django.conf import settings
            from django.utils import timezone
            from datetime import timedelta
            
            # Create a JWT token for WebSocket authentication
            websocket_token = jwt.encode({
                'type': 'oauth2_access',
                'user_id': 1,  # Placeholder - in real implementation, get actual user ID
                'exp': timezone.now() + timedelta(hours=1),
                'openedx_token': access_token  # Store the original OpenEdX token
            }, settings.SECRET_KEY, algorithm='HS256')
            
            logger.info(f"OAuth2 callback: Generated WebSocket JWT token: {websocket_token[:20]}...")
            logger.info(f"OAuth2 callback: JWT token length: {len(websocket_token)}")
            logger.info(f"OAuth2 callback: JWT token segments: {len(websocket_token.split('.'))}")
            
            # Test decode to verify the token is valid
            try:
                test_payload = jwt.decode(websocket_token, settings.SECRET_KEY, algorithms=['HS256'])
                logger.info(f"OAuth2 callback: JWT token test decode successful: {test_payload}")
            except Exception as e:
                logger.error(f"OAuth2 callback: JWT token test decode failed: {str(e)}")
            
            return render(request, "oauth2/callback.html", {
                "access_token": websocket_token,  # Use our JWT token instead
                "refresh_token": refresh_token,
                "expires_in": expires_in,
                "token_type": token_type,
            })
        return HttpResponse(f'Failed to exchange code: {resp.text}', status=resp.status_code) 