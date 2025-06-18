from django.urls import path
from .views import OAuth2AuthorizationView, OAuth2TokenView

urlpatterns = [
    path('authorize/', OAuth2AuthorizationView.as_view(), name='oauth2_authorize'),
    path('token/', OAuth2TokenView.as_view(), name='oauth2_token'),
] 
