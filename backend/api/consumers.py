import json
import logging
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .oauth2.models import OAuth2Token
from .models import ChatSession, Message
from datetime import datetime, timezone
import jwt
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone as django_timezone

# Configure logger
logger = logging.getLogger(__name__)

# Rate limiting settings
RATE_LIMIT_WINDOW = 60  # 1 minute window
MAX_CONNECTIONS_PER_WINDOW = 5  # Maximum connections per minute per IP

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat functionality.
    Supports both JWT and OAuth2 authentication.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_session = None
        self.user = None
        self.is_connected = False
        self.last_token_refresh = None

    async def connect(self):
        """
        Handle WebSocket connection.
        This function:
        1. Extracts and verifies the token from query string
        2. Determines authentication type (JWT or OAuth2)
        3. Authenticates the user
        4. Creates/retrieves a chat session
        5. Sets up the WebSocket connection
        """
        try:
            # Rate limiting check
            client_ip = self.scope.get('client', ('0.0.0.0', 0))[0]
            if not await self.check_rate_limit(client_ip):
                await self.close(code=4002, reason="Rate limit exceeded. Please try again later.")
                return

            # Get the token and auth_type from the query string
            query_string = self.scope['query_string'].decode()
            token = None
            auth_type = None
            
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=')[1]
                elif param.startswith('auth_type='):
                    auth_type = param.split('=')[1]
            
            if not token or not auth_type:
                await self.close_with_error(4001, "No token or auth_type provided")
                return
            
            # Verify token based on auth type
            if auth_type == 'jwt':
                user = await self.verify_jwt_token(token)
            elif auth_type == 'oauth2':
                user = await self.verify_oauth2_token(token)
            else:
                await self.close_with_error(4001, f"Invalid auth_type: {auth_type}")
                return
            
            if not user:
                await self.close_with_error(4001, "Invalid token provided")
                return
            
            # Store the user and set last token refresh time
            self.user = user
            self.last_token_refresh = django_timezone.now()
            logger.info(f"User {user.username} connected to WebSocket")
            
            # Accept the connection
            await self.accept()
            self.is_connected = True
            
            # Add the user to their personal channel group
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )

            # Create or get chat session
            self.chat_session = await self.get_or_create_chat_session()
            logger.info(f"Chat session {self.chat_session.id} created/retrieved for user {user.username}")
            
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}", exc_info=True)
            await self.close_with_error(4001, f"Connection error: {str(e)}")

    async def close_with_error(self, code, reason):
        """Helper method to close connection with error message."""
        error_data = {
            'type': 'error',
            'code': code,
            'message': reason,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        await self.send(text_data=json.dumps(error_data))
        await self.close(code=code, reason=reason)

    @database_sync_to_async
    def check_rate_limit(self, client_ip):
        """Check if the client has exceeded rate limits."""
        cache_key = f"ws_rate_limit_{client_ip}"
        current_time = django_timezone.now()
        
        # Get current connection count
        connection_count = cache.get(cache_key, 0)
        
        if connection_count >= MAX_CONNECTIONS_PER_WINDOW:
            return False
            
        # Increment connection count
        cache.set(cache_key, connection_count + 1, RATE_LIMIT_WINDOW)
        return True

    @database_sync_to_async
    def verify_jwt_token(self, token):
        """Verify JWT token and get user."""
        try:
            # Decode the token
            access_token = AccessToken(token)
            
            # Check token expiration explicitly
            if access_token['exp'] < django_timezone.now().timestamp():
                logger.warning("JWT token has expired")
                return None
                
            user_id = access_token['user_id']
            
            # Get the user
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            logger.warning(f"JWT token verification failed: {str(e)}")
            return None

    @database_sync_to_async
    def verify_oauth2_token(self, token):
        """Verify OAuth2 token and get user."""
        try:
            # Decode token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            # Verify token type
            if payload.get('type') != 'oauth2_access':
                logger.warning("Invalid OAuth2 token type")
                return None
                
            # Check token expiration
            if payload.get('exp') < django_timezone.now().timestamp():
                logger.warning("OAuth2 token has expired")
                return None
                
            user_id = payload.get('user_id')
            if not user_id:
                logger.warning("No user_id in OAuth2 token")
                return None
                
            # Get the user
            return User.objects.get(id=user_id)
        except (jwt.InvalidTokenError, User.DoesNotExist) as e:
            logger.warning(f"OAuth2 token verification failed: {str(e)}")
            return None

    async def check_token_refresh(self):
        """Check if token needs to be refreshed."""
        if not self.last_token_refresh:
            return
            
        # Check if token is about to expire (within 5 minutes)
        if (django_timezone.now() - self.last_token_refresh).total_seconds() > 300:
            await self.send(text_data=json.dumps({
                'type': 'token_refresh_required',
                'message': 'Your session is about to expire. Please refresh your token.',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }))

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        """
        if not self.is_connected or not self.user:
            await self.close_with_error(4001, "Not connected or no user")
            return
            
        try:
            # Check token refresh before processing message
            await self.check_token_refresh()
            
            text_data_json = json.loads(text_data)
            logger.info(f"Received message from {self.user.username}: {text_data_json}")
            
            message_type = text_data_json.get('type')
            content = text_data_json.get('content')
            message_id = text_data_json.get('id', str(uuid.uuid4()))
            
            if message_type != 'message' or not content:
                await self.close_with_error(4001, "Invalid message format")
                return
            
            # Save user message to database
            await self.save_message(content, is_from_user=True)
            logger.info(f"Saved user message: {content[:50]}...")
            
            # Send placeholder response instead of Flowise
            placeholder_response = "This is a placeholder message from websocket. Flowise integration is currently disabled."
            
            # Save placeholder response to database
            await self.save_message(placeholder_response, is_from_user=False)
            logger.info("Saved placeholder response")
            
            # Send response back to user directly through WebSocket
            response_data = {
                'type': 'message',
                'id': str(uuid.uuid4()),
                'content': placeholder_response,
                'isUser': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            logger.info(f"Sending response: {response_data}")
            await self.send(text_data=json.dumps(response_data))
                
        except json.JSONDecodeError:
            await self.close_with_error(4001, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}", exc_info=True)
            await self.close_with_error(4001, f"Message processing error: {str(e)}")

    async def chat_message(self, event):
        """Handle chat messages."""
        try:
            if not self.is_connected or not self.user:
                logger.warning("Received chat_message event while not connected or no user")
                return

            # Extract message data from event
            message_data = {
                'type': 'message',
                'id': str(uuid.uuid4()),
                'content': event.get('content', ''),
                'isUser': event.get('isUser', False),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processing chat message event: {message_data}")
            
            # Send message to WebSocket
            await self.send(text_data=json.dumps(message_data))
            
        except Exception as e:
            logger.error(f"Error in chat_message: {str(e)}", exc_info=True)
            await self.close(code=4001)

    @database_sync_to_async
    def get_or_create_chat_session(self):
        """Get or create a chat session for the user."""
        chat_session, created = ChatSession.objects.get_or_create(
            user=self.user,
            defaults={'is_active': True}
        )
        return chat_session

    @database_sync_to_async
    def save_message(self, content, is_from_user):
        """Save a message to the database."""
        return Message.objects.create(
            session=self.chat_session,
            content=content,
            is_from_user=is_from_user
        )