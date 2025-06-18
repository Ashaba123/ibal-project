from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from api.oauth2.models import OAuth2Client, OAuth2Token
from django.utils import timezone
from datetime import timedelta
import json
import pytest

User = get_user_model()

@pytest.mark.skip(reason="OAuth2 flow not fully implemented for test automation.")
class OAuth2AuthenticationTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.oauth_client = OAuth2Client.objects.create(
            client_id='test_client',
            client_secret='test_secret',
            redirect_uri='http://localhost:8000/callback',
            is_active=True
        )
        # Use the custom OAuth2 endpoints
        self.auth_url = '/api/oauth/authorize/'
        self.token_url = '/api/oauth/token/'

    def test_authorization_endpoint(self):
        """Test OAuth2 authorization endpoint."""
        # First login the user
        self.client.force_authenticate(user=self.user)
        
        params = {
            'client_id': self.oauth_client.client_id,
            'redirect_uri': self.oauth_client.redirect_uri,
            'response_type': 'code',
            'scope': 'read write'
        }
        response = self.client.get(self.auth_url, params)
        self.assertEqual(response.status_code, 200)
        self.assertIn('code', response.data)

    def test_token_endpoint(self):
        """Test OAuth2 token endpoint."""
        # First login the user and get authorization code
        self.client.force_authenticate(user=self.user)
        
        auth_params = {
            'client_id': self.oauth_client.client_id,
            'redirect_uri': self.oauth_client.redirect_uri,
            'response_type': 'code',
            'scope': 'read write'
        }
        auth_response = self.client.get(self.auth_url, auth_params)
        code = auth_response.data['code']

        # Then exchange code for token
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.oauth_client.client_id,
            'client_secret': self.oauth_client.client_secret,
            'redirect_uri': self.oauth_client.redirect_uri
        }
        response = self.client.post(self.token_url, token_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_token_refresh(self):
        """Test OAuth2 token refresh."""
        # First login the user and get tokens
        self.client.force_authenticate(user=self.user)
        
        auth_params = {
            'client_id': self.oauth_client.client_id,
            'redirect_uri': self.oauth_client.redirect_uri,
            'response_type': 'code',
            'scope': 'read write'
        }
        auth_response = self.client.get(self.auth_url, auth_params)
        code = auth_response.data['code']

        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.oauth_client.client_id,
            'client_secret': self.oauth_client.client_secret,
            'redirect_uri': self.oauth_client.redirect_uri
        }
        token_response = self.client.post(self.token_url, token_data)
        refresh_token = token_response.data['refresh_token']

        # Then refresh
        refresh_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.oauth_client.client_id,
            'client_secret': self.oauth_client.client_secret
        }
        response = self.client.post(self.token_url, refresh_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)