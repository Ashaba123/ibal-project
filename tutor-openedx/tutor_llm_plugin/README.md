# Tutor LLM Plugin

A Tutor plugin for Open edX that integrates LLM-powered chat functionality.

## Installation

1. Install the plugin:

   ```bash
   pip install -e .
   ```

2. Enable the plugin:

   ```bash
   tutor plugins enable llm
   tutor config save
   ```

3. Initialize the plugin:

   ```bash
   tutor local launch
   tutor local do init-llm
   ```

## Configuration

The plugin can be configured using Tutor's configuration system:

```bash
# OAuth2 credentials
tutor config save --set LLM_OAUTH_CLIENT_ID=<your-client-id>
tutor config save --set LLM_OAUTH_CLIENT_SECRET=<your-client-secret>

# LLM service connection
tutor config save --set LLM_SERVICE_HOST=<host>
tutor config save --set LLM_SERVICE_PORT=<port>
```

## Features

- OAuth2 authentication integration
- WebSocket communication setup
- Static files configuration
- Service connection management

## Development

1. Clone the repository
2. Install in development mode:

   ```bash
   pip install -e .
   ```

3. Enable the plugin:

   ```bash
   tutor plugins enable llm
   ```

4. Make changes and test locally

## Testing

1. Create admin user:

   ```bash
   tutor local do createuser --staff --superuser admin admin@example.com
   ```

2. Create OAuth2 application:
   - Log in to Django admin
   - Navigate to OAuth2 Provider > Applications
   - Create new application with:
     - Client Type: Confidential
     - Authorization Grant Type: Authorization code
     - Redirect URIs: <http://localhost:8000/oauth/callback>

3. Test authentication:
   - Get authorization code
   - Exchange code for token
   - Test WebSocket connection

## License

MIT License
