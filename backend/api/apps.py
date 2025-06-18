from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """Initialize app when ready."""
        try:
            import api.signals  # noqa
        except ImportError:
            pass  # Signals module is optional 