from .settings import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use InMemoryChannelLayer for testing
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Disable Flowise for testing
FLOWISE_URL = None
FLOWISE_FLOW_ID = None

# Set testing to True
TESTING = True