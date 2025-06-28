from django.contrib import admin
from django.urls import path, include
from api import views
from api.oauth2.views import OAuth2CallbackView

# Main application URLs
# Flow: login -> oauth callback -> token exchange -> chat
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('api.urls')),  # Includes all API endpoints from the api app
    
    # Main application views
    path('', views.index, name='home'),  # React app entry point
    path('chat/', views.chat, name='chat'),  # Chat interface
    
    # Health check endpoints
    path('health/', views.health_check, name='health_check'),
    
    # OAuth2 callback endpoint
    path('oauth/callback/', OAuth2CallbackView.as_view(), name='oauth_callback'),
]
