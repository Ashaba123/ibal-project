# IBAL Project

A comprehensive multi-application system that provides LLM-powered chat functionality through a modern Django backend with real-time WebSocket communication. This project demonstrates best practices for building scalable chat applications with multiple frontend integrations and learning management system compatibility.

## 🚀 What is IBAL?

IBAL (Intelligent Bot Assistant Learning) is a full-stack chat application that combines the power of Django for backend services, React for modern frontend experiences, and WebSocket technology for real-time communication. It's designed to be easily integrated into existing learning management systems like Open edX while also providing a standalone chat experience with support for multiple LLM providers including Flowise.

## 🏗️ System Architecture

The system consists of six main components working together:

1. **Django WebSocket API Backend** - The core server handling authentication, real-time messaging, and API endpoints
2. **React Frontend** - A modern, responsive standalone chat application with Vite build system
3. **Open edX Integration** - Seamless integration with Open edX learning platforms via Tutor plugin
4. **IBAL XBlock** - Custom XBlock with complete chat interface and debugging features
5. **Flowise Integration** - LLM orchestration system for advanced AI workflows
6. **Caddy Reverse Proxy** - Production-ready reverse proxy with WebSocket support

## 📁 Project Structure

```tree
ibal-project/
├── backend/                    # Django WebSocket API Backend
│   ├── api/                   # Main API application
│   │   ├── templates/        # HTML templates for different frontends
│   │   │   ├── react/       # React frontend templates
│   │   │   └── openedx/     # Open edX integration templates
│   │   ├── oauth2/          # OAuth2 authentication handling
│   │   ├── tests/           # Backend test suite
│   │   ├── consumers.py     # WebSocket consumers for real-time chat
│   │   ├── flowise_client.py # Flowise API integration
│   │   ├── middleware.py    # Custom middleware for iframe embedding
│   │   ├── models.py        # Database models for chat sessions
│   │   ├── views.py         # API views and handlers
│   │   └── routing.py       # WebSocket routing configuration
│   ├── llm_websocket_api/   # Django project settings and configuration
│   ├── users/               # User management app
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Backend container configuration
│   └── manage.py           # Django management script
├── react-frontend/          # Standalone React Chat Application
│   ├── src/                # React source code
│   │   ├── components/    # Reusable React components
│   │   │   ├── Auth/     # Authentication components
│   │   │   ├── Chat/     # Chat interface components
│   │   │   ├── common/   # Shared UI components
│   │   │   ├── Error/    # Error handling components
│   │   │   └── Welcome/  # Welcome page components
│   │   ├── context/      # React context providers
│   │   ├── pages/        # Page-level components
│   │   ├── services/     # API and WebSocket services
│   │   └── types/        # TypeScript type definitions
│   ├── tests/             # Playwright end-to-end tests
│   ├── vercel.json        # Vercel deployment configuration
│   └── package.json       # Node.js dependencies
├── tutor-openedx/         # Open edX Tutor plugin
│   └── tutor_llm_plugin/  # Plugin for Open edX integration
├── xblock_development/    # XBlock development environment
│   ├── ibalxbloc/        # IBAL XBlock with complete chat interface
│   │   ├── ibalxbloc/    # XBlock source code
│   │   │   ├── static/   # Static assets (CSS, JS, HTML)
│   │   │   │   ├── css/  # Chat interface styling
│   │   │   │   ├── js/   # JavaScript with console logging
│   │   │   │   └── html/ # HTML templates
│   │   │   └── ibalxbloc.py # Main XBlock implementation
│   │   ├── setup.py      # XBlock installation configuration
│   │   └── README.md     # XBlock documentation
│   └── xblock-sdk/       # XBlock development toolkit
├── flowise_data/         # Flowise configuration and data
├── Caddyfile             # Caddy reverse proxy configuration
└── docker-compose.yml    # Docker orchestration with all services
```

## 🔧 Core Components

### 1. Backend (Django + WebSocket)

The backend is built with Django and Django Channels, providing a robust foundation for real-time communication:

- **WebSocket Consumer**: Advanced WebSocket consumer with rate limiting, token verification, and message deduplication
- **Dual Authentication**: JWT authentication for React frontend and OAuth2 for Open edX integration
- **Flowise Integration**: Async client for LLM orchestration with retry mechanisms and health checks
- **OAuth2 Provider**: Complete OAuth2 implementation for Open edX integration
- **Rate Limiting**: Connection rate limiting to prevent abuse
- **Message Management**: Chat session creation and message persistence
- **Security Features**: CORS, CSP headers, secure token management, and iframe embedding support
- **Structured Logging**: Comprehensive logging for debugging and monitoring
- **Redis Integration**: Channel layer for WebSocket communication

### 2. React Frontend

A modern, responsive chat interface built with React, TypeScript, and Vite:

- **Vite Build System**: Fast development and optimized production builds
- **TypeScript**: Type-safe development with comprehensive type definitions
- **WebSocket Client**: Real-time communication with automatic reconnection and error handling
- **JWT Authentication**: Secure login and session management with token refresh
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Error Handling**: Graceful error handling with retry mechanisms and user feedback
- **Playwright Tests**: Comprehensive end-to-end testing with UI mode support
- **Vercel Deployment**: Optimized for Vercel deployment with analytics integration
- **Modern UI**: Chat bubble design with proper message alignment and timestamps

### 3. IBAL XBlock (Open edX Integration)

A complete chat XBlock for Open edX with modern interface and debugging capabilities:

- **Modern Chat Interface**: Bubble-style messages with sent/received styling
- **Real-time Messaging**: WebSocket-based communication with OAuth2 authentication
- **User Information**: Displays logged-in username and connection status
- **Visual Status Indicators**: Color-coded connection status (Connecting, Connected, Disconnected, Error)
- **Enhanced UI**: Large green "Start Chat" button and red "Close Chat" button
- **Comprehensive Logging**: Extensive console logging for debugging with "[IbalXBlock]" prefix
- **Message Management**: Auto-scroll, timestamps, and message metadata
- **Responsive Design**: Works on desktop and mobile devices
- **Security Features**: XSS protection, HTML escaping, and secure token management
- **Error Handling**: Graceful error handling with detailed console logging
- **Accessibility**: Proper ARIA labels and keyboard navigation support

#### XBlock Features:
- **Bubble Messages**: Chat-style message bubbles with rounded corners
- **Connection Monitoring**: Real-time WebSocket connection status
- **Debug Console**: Filter logs by "[IbalXBlock]" for easy debugging
- **Message Flow**: Send/receive messages with timestamps and sender info
- **Session Management**: Persistent chat sessions with token storage
- **Modern Styling**: Professional chat interface with smooth animations

### 4. Open edX Integration

Comprehensive integration with Open edX learning platforms:

- **Tutor Plugin**: Native Open edX Tutor plugin for easy installation and configuration
- **OAuth2 Client**: Secure authentication using Open edX credentials
- **XBlock Development**: Custom XBlock for embedding chat functionality in courses
- **Embedded Interface**: Chat interface embedded within Open edX courses
- **User Context**: Automatic user identification and session management
- **Separate Templates**: Dedicated templates for Open edX integration
- **Configuration Management**: Environment-based configuration for different deployments

### 5. Flowise Integration

Advanced LLM orchestration with Flowise:

- **Async Client**: High-performance async client for Flowise API
- **Retry Mechanisms**: Automatic retry with exponential backoff
- **Health Checks**: Service health monitoring and fallback handling
- **Session Management**: Conversation continuity with session IDs
- **Error Handling**: Comprehensive error handling and logging
- **Configuration**: Environment-based configuration for different flows
- **Docker Integration**: Seamless integration with Docker Compose setup

### 6. Caddy Reverse Proxy

Production-ready reverse proxy configuration:

- **Multi-Service Routing**: Intelligent routing to different services
- **WebSocket Support**: Proper WebSocket upgrade handling for all services
- **SSL/TLS Termination**: Automatic HTTPS with Let's Encrypt support
- **CORS Configuration**: Comprehensive CORS handling for all frontends
- **Security Headers**: Enhanced security with proper headers
- **Structured Logging**: JSON logging for production monitoring
- **Health Checks**: Service health monitoring and load balancing

## ✨ Key Features

### 🛡️ Security & Authentication

- **Dual Authentication System**: JWT for React frontend, OAuth2 for Open edX
- **Secure WebSocket Connections**: Token verification and rate limiting
- **CORS & CSP Headers**: Comprehensive security headers
- **Token Management**: Automatic token refresh and expiration handling
- **Rate Limiting**: Connection and message rate limiting to prevent abuse
- **Iframe Embedding**: Secure iframe embedding for XBlock integration

### 💬 Real-time Communication

- **WebSocket-based Messaging**: Real-time bidirectional communication
- **Message Deduplication**: Prevents duplicate messages in chat
- **Automatic Reconnection**: Graceful handling of connection losses
- **Structured Message Format**: JSON-based messages with timestamps
- **Session Management**: Persistent chat sessions across connections
- **Error Recovery**: Comprehensive error handling and recovery mechanisms

### 🎨 User Experience

- **Modern Chat Interface**: Beautiful chat bubble design with proper alignment
- **Responsive Design**: Optimized for all device sizes and orientations
- **Loading States**: Visual feedback during operations
- **Error Feedback**: Clear error messages and recovery options
- **Intuitive Navigation**: Easy-to-use interface with clear call-to-actions
- **Accessibility**: WCAG compliant design with proper ARIA labels

### 🛠️ Debugging & Development

- **Comprehensive Console Logging**: Extensive logging across all components
- **XBlock Debugging**: Filter logs by "[IbalXBlock]" for easy debugging
- **Error Tracking**: Detailed error messages and stack traces
- **Connection Monitoring**: Real-time WebSocket connection status
- **Message Flow Tracking**: Monitor message sending and receiving
- **Development Tools**: Built-in debugging features for development

### 🧪 Testing & Quality

- **Comprehensive Testing**: Playwright end-to-end tests with UI mode
- **Backend Unit Tests**: Pytest-based testing with coverage reporting
- **TypeScript**: Type-safe development with better IDE support
- **Code Quality**: ESLint, Black, isort, and flake8 for code quality
- **Structured Logging**: Comprehensive logging for debugging and monitoring
- **Error Handling**: Graceful error handling with retry mechanisms

### 🚀 Deployment & DevOps

- **Docker Compose**: Complete containerization with all services
- **Caddy Reverse Proxy**: Production-ready reverse proxy configuration
- **Environment Configuration**: Flexible environment-based configuration
- **Static File Serving**: Optimized static file serving with WhiteNoise
- **Database Migrations**: Automated database migration handling
- **Vercel Deployment**: Optimized for Vercel deployment with analytics

### 🔌 Integration Capabilities

- **Open edX Integration**: Native Tutor plugin and XBlock support
- **Multiple LLM Providers**: Flowise
- **Extensible Architecture**: Easy to add new LLM providers
- **API-First Design**: RESTful APIs for external integrations
- **Webhook Support**: Ready for webhook integrations
- **Plugin System**: Modular design for easy extensions

## 🔄 Application Flows

### React Frontend User Journey

1. **Welcome Experience**
   - User lands on welcome page with clear branding
   - Backend availability check with health monitoring
   - Clear call-to-action for starting chat experience

2. **Authentication Process**
   - Secure JWT-based authentication flow
   - Token generation and secure storage
   - Automatic chat session initialization
   - Token refresh handling for long sessions

3. **Chat Experience**
   - WebSocket connection establishment with authentication
   - Real-time message sending and receiving
   - Message deduplication and error handling
   - Session management and persistence
   - Beautiful message bubble interface with timestamps
   - Loading states and error feedback

### IBAL XBlock User Journey

1. **Initial State**
   - Shows large green "Start Chat" button
   - Displays status message: "Click Start Chat to begin"
   - Clean, professional interface

2. **Authentication Flow**
   - User clicks "Start Chat" → Opens OAuth2 popup
   - After successful authentication → Token stored in localStorage
   - Popup closes and notifies main window
   - Console logs track entire authentication process

3. **WebSocket Connection**
   - Establishes connection to backend WebSocket server
   - Sends OAuth2 token for authentication
   - Updates connection status in real-time
   - Comprehensive console logging for debugging

4. **Chat Interface**
   - Shows complete chat interface with:
     - User info header (logged-in username)
     - Connection status indicator with color coding
     - Message display area with bubble styling
     - Message input field with send button
     - Red "Close Chat" button

5. **Messaging Experience**
   - Send messages via input field or Enter key
   - Messages appear as blue bubbles (sent) or white bubbles (received)
   - Real-time message exchange via WebSocket
   - Auto-scroll to latest messages
   - Message metadata with timestamps

6. **Close Chat**
   - Click "Close Chat" button
   - Returns to initial "Start Chat" state
   - Clears messages and resets connection
   - Console logs track closure process

### Open edX Integration Flow

1. **Platform Integration**
   - Tutor plugin installation and configuration
   - XBlock integration within Open edX courses
   - OAuth2 client initialization
   - User context establishment from Open edX

2. **Seamless Authentication**
   - Leverage existing Open edX session
   - OAuth2 token exchange with backend
   - Automatic chat interface initialization
   - Secure iframe embedding

3. **Embedded Chat Experience**
   - Chat interface embedded in Open edX UI
   - Real-time communication within course context
   - Consistent user experience across platforms
   - Course-specific chat sessions

### LLM Integration Flow

1. **Flowise Integration**
   - Async API communication with Flowise
   - Retry mechanisms for reliability
   - Session management for conversation continuity
   - Health monitoring and fallback handling

## 🔍 Debugging & Console Logging

### XBlock Console Logging

The IBAL XBlock includes comprehensive console logging for easy debugging:

#### Log Categories:
- **WebSocket Connection**: Connection setup, opening, closing, and errors
- **Message Handling**: Incoming messages, parsing, and errors
- **User Interactions**: Button clicks and user actions
- **Authentication**: OAuth2 flow and token management
- **Error Handling**: Detailed error messages with context

#### How to Debug XBlock:
1. **Open Browser DevTools** (F12)
2. **Go to Console Tab**
3. **Filter by "[IbalXBlock]"** to see only XBlock logs
4. **Monitor real-time activity** as you use the chat

#### Example XBlock Console Output:
```
[IbalXBlock] Start Chat button activated
[IbalXBlock] Opening OAuth2 authorize popup: http://local.openedx.io/oauth2/authorize/?client_id=...
[IbalXBlock] Access token found in localStorage: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
[IbalXBlock] Using access_token for WebSocket: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
[IbalXBlock] Opening WebSocket connection to: ws://localhost:8000/ws/chat/?token=...&auth_type=oauth2
[IbalXBlock] WebSocket connection opened
[IbalXBlock] Received message: {"type":"user_info","username":"john_doe"}
[IbalXBlock] Received message: {"type":"message","content":"Hello!","sender":"john_doe","timestamp":"..."}
```

### Backend Logging

The Django backend includes structured logging for:
- WebSocket connection events
- Authentication flows
- Message processing
- Error handling
- Performance monitoring

## 🔒 Environment Configuration & Security Best Practices

### Environment Variables

All sensitive credentials and configuration values (such as OAuth client IDs, secrets, API URLs, and database URIs) are now loaded from environment variables using `.env` files. This ensures that secrets are never hardcoded in the codebase or committed to version control.

- **Backend**: Uses `os.getenv()` and `python-dotenv` to load variables from `.env` files.
- **XBlock**: Uses `load_dotenv()` and `os.getenv()` to load variables from the project root `.env` file.
- **Frontend**: Uses `.env` files for Vite/React configuration.

### Recommended .env Files

- `.env` (default, for local development)
- `.env.development` (for explicit dev settings)
- `.env.staging` (for staging/test servers)
- `.env.production` (for production)

**Example .env:**

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,example.com
OPENEDX_CLIENT_ID=your-client-id
OPENEDX_CLIENT_SECRET=your-client-secret
OPENEDX_AUTH_URL=http://local.openedx.io/oauth2/authorize/
OPENEDX_TOKEN_URL=http://local.openedx.io/oauth2/access_token/
OPENEDX_REDIRECT_URI=http://localhost:8000/oauth/callback/
WS_URL=ws://localhost:8000/ws/chat/
FLOWISE_URL=http://your-flowise-url
FLOWISE_FLOW_ID=your-flow-id
FLOWISE_TIMEOUT=30
FLOWISE_MAX_RETRIES=3
```

**Never commit your `.env` files to version control!**

### .gitignore

A comprehensive `.gitignore` is provided to ensure that all environment files, build artifacts, logs, and sensitive data are excluded from version control. See the root `.gitignore` for details.

### Using Multiple Environments

You can use different `.env` files for different environments. For example, set `ENV_FILE=.env.production` in your deployment scripts or Docker Compose to load production settings.

---

## 🛠️ Setup Instructions

### Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose]<https://docs.docker.com/compose/install/>
- [Node.js](https://nodejs.org/) (v16 or higher)
- [Git](https://git-scm.com/)
- [Python](https://www.python.org/) (v3.8 or higher) for development

### Quick Start with Docker

1. **Clone the repository**:

   ```bash
   git clone [repository-url]
   cd ibal-project
   ```

2. **Create environment configuration**:

   ```bash
   # Create backend environment file
   cat > backend/.env << EOF
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1,example.com
   DJANGO_SETTINGS_MODULE=llm_websocket_api.settings
   BASE_URL=http://your-backend-url
   FLOWISE_URL=http://your-flowise-url
   FLOWISE_FLOW_ID=your-flow-id
   FLOWISE_TIMEOUT=30
   FLOWISE_MAX_RETRIES=3
   EOF
   ```

3. **Start all services**:

   ```bash
   docker-compose up -d
   ```

4. **Access the services**:
   - React Frontend: <http://localhost:5173>
   - Backend API: <http://localhost:8000>
   - Flowise: <http://localhost:3000>
   - Caddy Proxy: <http://localhost:8080>
   - Admin Interface: <http://localhost:8000/admin>

### Development Setup

#### Backend Development

1. **Navigate to backend directory**:

   ```bash
   cd backend
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run development server**:

   ```bash
   python manage.py runserver
   ```

#### React Frontend Development

1. **Navigate to frontend directory**:

   ```bash
   cd react-frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Create environment file**:

   ```bash
   cat > .env << EOF
   VITE_API_URL=http://localhost:8000
   VITE_WS_URL=ws://localhost:8000/ws/chat/
   EOF
   ```

4. **Start development server**:

   ```bash
   npm run dev
   ```

5. **Run tests**:

   ```bash
   npm test
   npm run test:ui  # For interactive test UI
   ```

### IBAL XBlock Development

1. **Navigate to XBlock directory**:

   ```bash
   cd xblock_development/ibalxbloc
   ```

2. **Install XBlock in development mode**:

   ```bash
   pip install -e .
   ```

3. **Test in XBlock workbench**:

   ```bash
   cd ../xblock-sdk
   python manage.py runserver
   ```

4. **Access workbench**: <http://localhost:8000>

5. **Debug with console logs**: Open browser DevTools and filter by "[IbalXBlock]"

### Open edX Integration Setup

1. **Install Tutor plugin**:

   ```bash
   cd tutor-openedx/tutor_llm_plugin
   pip install -e .
   ```

2. **Enable the plugin**:

   ```bash
   tutor plugins enable llm
   tutor config save
   ```

3. **Initialize the plugin**:

   ```bash
   tutor local launch
   tutor local do init-llm
   ```

4. **Configure OAuth2**:

   ```bash
   tutor config save --set LLM_OAUTH_CLIENT_ID=<your-client-id>
   tutor config save --set LLM_OAUTH_CLIENT_SECRET=<your-client-secret>
   tutor config save --set LLM_SERVICE_HOST=<host>
   tutor config save --set LLM_SERVICE_PORT=<port>
   ```

## 🧪 Testing

### Backend Testing

Run the complete backend test suite:

```bash
docker-compose exec backend pytest
```

Run tests with coverage:

```bash
docker-compose exec backend pytest --cov=api --cov-report=html
```

Run specific test files:

```bash
 docker-compose exec backend pytest api/tests/test_jwt_auth.py
 docker-compose exec backend pytest api/tests/test_oauth2_auth.py
```

### Frontend Testing

Run Playwright end-to-end tests:

```bash
cd react-frontend
npm test
```

Run tests in headed mode (with browser visible):

```bash
npm run test:ui
```

Run tests in debug mode:

```bash
npm run test -- --debug
```

### XBlock Testing

Test the IBAL XBlock in the workbench:

```bash
cd xblock_development/xblock-sdk
python manage.py runserver
```

Access the workbench and test the XBlock with console logging enabled.

### Test Coverage

The project includes comprehensive testing:

- **Backend**: Unit tests for authentication, API endpoints, WebSocket consumers, and Flowise integration
- **Frontend**: End-to-end tests covering user flows, authentication, and chat functionality
- **XBlock**: Manual testing with comprehensive console logging
- **Integration**: Tests for Open edX integration and OAuth2 flows
- **Performance**: Load testing and WebSocket connection testing

## 📊 Development Status

| Component | Status | Description |
|-----------|--------|-------------|
| Backend API | 🚧 Under Development | Django + WebSocket with dual authentication |
| React Frontend | 🚧 Under Development | Modern UI with TypeScript, Vite, and testing |
| IBAL XBlock | ✅ Complete | Modern chat interface with debugging features |
| Open edX Plugin | 🚧 Under Development | Tutor plugin and XBlock integration |
| Flowise Integration | ✅ Complete | Async client with retry mechanisms |
| Caddy Proxy | ✅ Complete | Production-ready reverse proxy |
| Docker Setup | ✅ Complete | Full containerization with all services |
| Testing Suite | ✅ Complete | Comprehensive test coverage |

## 🔄 Recent Updates

### Version 2.2 - IBAL XBlock Enhancement

- **Complete Chat Interface**: Modern bubble-style messages with sent/received styling
- **Enhanced UI**: Large green "Start Chat" button and red "Close Chat" button
- **Connection Status**: Real-time WebSocket connection monitoring with color-coded indicators
- **Comprehensive Logging**: Extensive console logging with "[IbalXBlock]" prefix for easy debugging
- **User Information**: Display logged-in username and connection status
- **Message Management**: Auto-scroll, timestamps, and message metadata
- **Security Features**: XSS protection, HTML escaping, and secure token management
- **Responsive Design**: Works on desktop and mobile devices
- **Accessibility**: Proper ARIA labels and keyboard navigation support

### Version 2.1 - Advanced Integration Features

- **Flowise Integration**: Complete async client with retry mechanisms and health checks
- **Enhanced Security**: Rate limiting, iframe embedding, and improved CORS
- **Production Ready**: Caddy reverse proxy and comprehensive Docker setup

### Version 2.0 - UI & UX Improvements

- **Enhanced Chat Interface**: Modern chat bubble design with proper alignment
- **Improved Message Handling**: Message deduplication and better error handling
- **Better Timestamps**: Clean, user-friendly timestamp formatting
- **Responsive Design**: Optimized for all device sizes
- **Vite Integration**: Fast development and optimized builds

### Version 1.5 - Backend Enhancements

- **Structured Logging**: Comprehensive logging system for debugging
- **Enhanced WebSocket Consumer**: Improved real-time communication reliability
- **Better Error Handling**: Graceful error handling with retry mechanisms
- **Security Improvements**: Enhanced CORS, CSP, and rate limiting
- **Dual Authentication**: JWT and OAuth2 support

### Version 1.0 - Core Features

- **Real-time Chat**: WebSocket-based messaging with Django Channels
- **Dual Authentication**: JWT for React, OAuth2 for Open edX
- **Docker Support**: Complete containerization with Docker Compose
- **Testing Suite**: Comprehensive Playwright and pytest coverage
- **Open edX Integration**: Tutor plugin and XBlock support

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name

   ```

3. **Make your changes** following our coding standards
4. **Run tests** to ensure everything works:

   ```bash
   # Backend tests
   docker-compose exec backend pytest
   
   # Frontend tests
   cd react-frontend && npm test
   
   # XBlock testing
   cd xblock_development/xblock-sdk && python manage.py runserver
   ```

5. **Commit your changes** with clear commit messages
6. **Push to your branch** and create a pull request

### Development Guidelines

- Follow Django and React best practices
- Write tests for new features
- Use TypeScript for frontend development
- Maintain consistent code formatting with Black, isort, and ESLint
- Add console logging for XBlock features with "[IbalXBlock]" prefix
- Update documentation for new features
- Ensure proper error handling and logging

## 🐛 Troubleshooting

### Common Issues

**WebSocket Connection Fails**  

- Check if the backend is running: `docker-compose ps`
- Verify WebSocket URL in frontend `.env` file
- Check browser console for connection errors
- Ensure Redis is running: `docker-compose logs redis`
**Authentication Issues**

- Ensure JWT tokens are properly configured
- Check OAuth2 settings for Open edX integration
- Verify CORS settings in backend configuration
- Check token expiration and refresh mechanisms
**XBlock Issues**

- Check browser console and filter by "[IbalXBlock]"
- Verify OAuth2 configuration in XBlock
- Ensure WebSocket server is accessible from XBlock
- Check iframe embedding permissions
**Database Issues**

- Run migrations: `docker-compose exec backend python manage.py migrate`
- Check database connection in Django settings
- Verify SQLite file permissions
- Check Redis connection for WebSocket channels
**Flowise Integration Issues**
- Verify Flowise service is running: `docker-compose logs flowise`
- Check Flowise flow ID configuration
- Verify network connectivity between services
- Check Flowise API health: `curl http://localhost:3000/api/v1/health`

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page for known problems
- Review the logs: `docker-compose logs backend`
- Check service health: `docker-compose ps`
- Ensure all environment variables are properly set
- Use XBlock console logging for debugging: Filter by "[IbalXBlock]"

## 📚 Additional Resources

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [React WebSocket Guide](https://react.dev/learn/start-a-new-react-project)
- [Open edX Developer Documentation](https://docs.openedx.org/)
- [XBlock Development Guide](https://docs.openedx.org/projects/xblock/en/latest/index.html)
- [Playwright Testing Guide](https://playwright.dev/docs/intro)
- [Flowise Documentation](https://docs.flowiseai.com/)
- [Caddy Documentation](https://caddyserver.com/docs/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django Channels for WebSocket support
- React team for the amazing frontend framework
- Open edX community for platform integration
- XBlock development team for the framework
- Playwright for excellent testing capabilities
- Flowise team for LLM orchestration platform
- Caddy team for the reverse proxy solution

---

**Ready to get started?** Follow the [Quick Start](#quick-start-with-docker) guide above to have your chat application running in minutes!
