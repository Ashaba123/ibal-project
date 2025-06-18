from django.apps import AppConfig

class OAuth2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.oauth2'
    verbose_name = 'OAuth2 Provider' 