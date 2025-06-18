from django.urls import reverse
from rest_framework.test import APIClient
from django.test import TestCase
from api.oauth2.models import OAuth2Token
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class BasicViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_health_check(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'healthy')

    def test_logout_view(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)

    def test_register_missing_fields(self):
        response = self.client.post('/api/auth/register/', {})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_register_duplicate_username(self):
        # Register once
        self.client.post('/api/auth/register/', {
            'username': 'dupuser',
            'email': 'dup@example.com',
            'password': 'pass'
        })
        # Register again with same username
        response = self.client.post('/api/auth/register/', {
            'username': 'dupuser',
            'email': 'other@example.com',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_register_duplicate_email(self):
        # Register once
        self.client.post('/api/auth/register/', {
            'username': 'user1',
            'email': 'dupemail@example.com',
            'password': 'pass'
        })
        # Register again with same email
        response = self.client.post('/api/auth/register/', {
            'username': 'user2',
            'email': 'dupemail@example.com',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

class OAuth2TokenModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tokuser', password='pass')

    def test_is_expired(self):
        token = OAuth2Token.objects.create(
            user=self.user,
            access_token='a',
            refresh_token='r',
            expires_at=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(token.is_expired())
        token.expires_at = timezone.now() + timedelta(days=1)
        token.save()
        self.assertFalse(token.is_expired()) 