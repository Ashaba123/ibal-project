from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .oauth2.views import OAuth2TokenView, OAuth2UserInfoView

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'chat-sessions', views.ChatSessionViewSet, basename='chat-session')

urlpatterns = [
    # Template views
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('start-chat/', views.start_chat, name='start_chat'),
    
    # Authentication endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # OAuth2 endpoints
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('oauth/token/', OAuth2TokenView.as_view(), name='openedx_token'),
    path('oauth/userinfo/', OAuth2UserInfoView.as_view(), name='openedx_userinfo'),
    # Include custom OAuth2 URLs
    path('oauth/', include('api.oauth2.urls')),
    
    # XBlock specific endpoints
    path('xblock/websocket-token/', views.xblock_websocket_token, name='xblock_websocket_token'),
    path('xblock/send-message/', views.xblock_send_message, name='xblock_send_message'),
    
    # API endpoints
    path('', include(router.urls)),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
] 