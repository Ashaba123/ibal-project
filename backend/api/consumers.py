import json
import logging
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
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
        self.connection_accepted = False

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
        logger.info("[WebSocket] connect() called. Starting connection process.")
        
        # First, accept the connection to establish the WebSocket
        try:
            await self.accept()
            self.connection_accepted = True
            logger.info("[WebSocket] Connection accepted successfully.")
        except Exception as e:
            logger.error(f"[WebSocket] Failed to accept connection: {str(e)}", exc_info=True)
            # If we can't accept, just close without sending error message
            try:
                await self.close(code=4001, reason=f"Failed to accept connection: {str(e)}")
            except Exception as close_error:
                logger.error(f"[WebSocket] Failed to close connection: {str(close_error)}")
            return

        # Now handle the rest of the connection logic
        try:
            # Rate limiting check
            client_ip = self.scope.get('client', ('0.0.0.0', 0))[0]
            logger.info(f"[WebSocket] Client IP: {client_ip}")
            if not await self.check_rate_limit(client_ip):
                logger.warning("[WebSocket] Rate limit exceeded for IP: %s", client_ip)
                await self.close_with_error(4002, "Rate limit exceeded. Please try again later.")
                return

            # Get the token and auth_type from the query string
            query_string = self.scope['query_string'].decode()
            logger.info(f"[WebSocket] Query string: {query_string}")
            token = None
            auth_type = None
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=')[1]
                elif param.startswith('auth_type='):
                    auth_type = param.split('=')[1]
            logger.info(f"[WebSocket] Token: {token}")
            logger.info(f"[WebSocket] Auth type: {auth_type}")

            if not token or not auth_type:
                logger.warning("[WebSocket] No token or auth_type provided.")
                await self.close_with_error(4001, "No token or auth_type provided")
                return

            user = None
            if auth_type == 'jwt':
                logger.info("[WebSocket] JWT authentication attempted.")
                user = await self.verify_jwt_token(token)
                if not user:
                    logger.warning("[WebSocket] Invalid JWT token provided.")
                    await self.close_with_error(4001, "Invalid JWT token provided")
                    return
            elif auth_type == 'oauth2':
                logger.info("[WebSocket] OAuth2 authentication attempted.")
                user = await self.verify_oauth2_token(token)
                if not user:
                    logger.warning("[WebSocket] Invalid OAuth2 token provided.")
                    await self.close_with_error(4001, "Invalid OAuth2 token provided")
                    return
            else:
                logger.warning(f"[WebSocket] Invalid auth_type: {auth_type}")
                await self.close_with_error(4001, f"Invalid auth_type: {auth_type}")
                return

            # If authentication succeeded, set user and continue
            self.user = user
            self.last_token_refresh = django_timezone.now()
            logger.info(f"[WebSocket] User {user.username} authenticated and connected to WebSocket.")
            self.is_connected = True

            # Add the user to their personal channel group
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )
            logger.info(f"[WebSocket] Added user {self.user.username} to channel group user_{self.user.id}.")

            # Create or get chat session
            self.chat_session = await self.get_or_create_chat_session()
            logger.info(f"[WebSocket] Chat session {self.chat_session.id} created/retrieved for user {user.username}")

            # Send user_info message to client (after all setup)
            try:
                await self.send(text_data=json.dumps({
                    "type": "user_info",
                    "username": self.user.username
                }))
            except Exception as e:
                logger.error(f"[WebSocket] Failed to send user_info message: {str(e)}")

        except Exception as e:
            logger.error(f"[WebSocket] Error in connect: {str(e)}", exc_info=True)
            # Since connection is already accepted, we can safely send error message
            try:
                # Send error message directly without using close_with_error
                error_data = {
                    'type': 'error',
                    'code': 4001,
                    'message': f"Connection error: {str(e)}",
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                await self.send(text_data=json.dumps(error_data))
            except Exception as send_error:
                logger.error(f"[WebSocket] Failed to send error message: {str(send_error)}")
            finally:
                # Always close the connection
                try:
                    await self.close(code=4001, reason=f"Connection error: {str(e)}")
                except Exception as close_error:
                    logger.error(f"[WebSocket] Failed to close connection: {str(close_error)}")

    async def close_with_error(self, code, reason):
        """Helper method to close connection with error message."""
        try:
            # Only try to send error message if connection was accepted
            if self.connection_accepted and hasattr(self, 'scope'):
                error_data = {
                    'type': 'error',
                    'code': code,
                    'message': reason,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                await self.send(text_data=json.dumps(error_data))
        except Exception as e:
            logger.warning(f"Could not send error message before closing: {str(e)}")
        finally:
            try:
                await self.close(code=code, reason=reason)
            except Exception as e:
                logger.warning(f"Could not close connection properly: {str(e)}")

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
            logger.info(f"OAuth2 verification: Attempting to decode token: {token[:20]}...")
            # Decode token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            logger.info(f"OAuth2 verification: Token decoded successfully, payload: {payload}")
            
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
        if not self.last_token_refresh or not self.connection_accepted:
            return
            
        # Check if token is about to expire (within 5 minutes)
        if (django_timezone.now() - self.last_token_refresh).total_seconds() > 300:
            try:
                await self.send(text_data=json.dumps({
                    'type': 'token_refresh_required',
                    'message': 'Your session is about to expire. Please refresh your token.',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }))
            except Exception as e:
                logger.warning(f"Could not send token refresh message: {str(e)}")

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        """
        if not self.is_connected or not self.user or not self.connection_accepted:
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
            if not self.is_connected or not self.user or not self.connection_accepted:
                logger.warning("Received chat_message event while not connected, no user, or connection not accepted")
                return

            # Extract message data from event
            content = event.get('content', '')
            if not content or not content.strip():
                logger.info("Skipping empty chat message event.")
                return
            message_data = {
                'type': 'message',
                'id': str(uuid.uuid4()),
                'content': content,
                'isUser': event.get('isUser', False),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            logger.info(f"Processing chat message event: {message_data}")
            # Send message to WebSocket
            await self.send(text_data=json.dumps(message_data))
        except Exception as e:
            logger.error(f"Error in chat_message: {str(e)}", exc_info=True)
            if self.connection_accepted:
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

    async def disconnect(self, close_code):
        logger.info(f"[WebSocket] Disconnected. Close code: {close_code}")
        await super().disconnect(close_code)