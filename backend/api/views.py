from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer
from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def index(request):
    """Render the React frontend template."""
    return render(request, 'react/index.html')

@login_required
def chat(request):
    """Render the chat interface template."""
    return render(request, 'react/chat.html')

@login_required
def start_chat(request):
    """Render the start chat template."""
    return render(request, 'react/start_chat.html')

@api_view(['GET'])
def health_check(request):
    """Health check endpoint."""
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def xblock_websocket_token(request):
    """
    Generate a WebSocket token for XBlock integration.
    This token will be used to authenticate the WebSocket connection.
    """
    try:
        # Create a new chat session for the user
        chat_session = ChatSession.objects.create(user=request.user)
        
        # Generate a token that includes the chat session ID
        token_data = {
            'user_id': request.user.id,
            'chat_session_id': chat_session.id,
            'is_xblock': True
        }
        
        # In a real implementation, you would sign this token
        # For now, we'll just return it as is
        return Response({
            'token': json.dumps(token_data),
            'ws_url': f"ws://{request.get_host()}/ws/chat/"
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def xblock_send_message(request):
    """
    Send a message from the XBlock to the WebSocket.
    This is a fallback method in case the WebSocket connection fails.
    """
    try:
        chat_session_id = request.data.get('chat_session_id')
        message_content = request.data.get('message')
        
        if not chat_session_id or not message_content:
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        chat_session = ChatSession.objects.get(
            id=chat_session_id,
            user=request.user
        )
        
        # Create the message
        message = Message.objects.create(
            session=chat_session,
            content=message_content,
            is_from_user=True
        )
        
        # Send the message through the channel layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{request.user.id}",
            {
                'type': 'chat_message',
                'message': {
                    'content': message_content,
                    'is_from_user': True,
                    'created_at': message.created_at.isoformat()
                }
            }
        )
        
        return Response({'status': 'success'})
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Chat session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ChatSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat sessions."""
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return chat sessions for the authenticated user."""
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new chat session for the authenticated user."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a chat session."""
        session = self.get_object()
        serializer = MessageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(session=session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in a chat session."""
        session = self.get_object()
        messages = Message.objects.filter(session=session)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not all([username, email, password]):
            return Response(
                {'error': 'Please provide all required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        # Create a new chat session for the user
        chat_session = ChatSession.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'chat_session_id': chat_session.id,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def logout_view(request):
    try:
        logout(request)
        return Response({'message': 'Successfully logged out'})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom view for obtaining JWT tokens."""
    pass

class CustomTokenRefreshView(TokenRefreshView):
    """Custom view for refreshing JWT tokens."""
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Return the current authenticated user's info.
    """
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }) 