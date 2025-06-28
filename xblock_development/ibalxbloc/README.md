# IBAL XBlock - Chat Interface

A modern chat XBlock for Open edX that provides real-time messaging capabilities with OAuth2 authentication and comprehensive debugging features.

## 🚀 Features

### 💬 Modern Chat Interface

- **Bubble Messages**: Messages are displayed in chat bubbles with different styles for sent/received messages
- **Real-time Messaging**: Send and receive messages instantly via WebSocket connection
- **Responsive Design**: Works on desktop and mobile devices
- **Message Metadata**: Shows sender name and timestamp for each message

### 🔐 Authentication & Security

- **OAuth2 Integration**: Secure authentication with Open edX OAuth2
- **Token Management**: Automatic token storage and retrieval in localStorage
- **User Information**: Displays logged-in username
- **XSS Protection**: HTML escaping for user messages

### 📊 Connection & Status Monitoring

- **Visual Indicators**: Real-time connection status with color-coded indicators
- **Status Messages**: Clear feedback about connection state (Connecting, Connected, Disconnected, Error)
- **WebSocket Health**: Monitor connection health and automatic reconnection

### 🎯 User Experience

- **Start Chat Button**: Large, green button to initiate chat session
- **Close Chat Button**: Easy way to return to start screen
- **Message Input**: Clean input field with send button
- **Keyboard Support**: Press Enter to send messages
- **Auto-scroll**: Messages automatically scroll to bottom

### 🛠️ Debugging & Development

- **Comprehensive Logging**: Extensive console logging for debugging
- **Error Tracking**: Detailed error messages and stack traces
- **Connection Monitoring**: Real-time WebSocket connection status
- **Message Flow Tracking**: Monitor message sending and receiving

## 🔍 Console Logging & Debugging

The XBlock includes extensive console logging for easy debugging and development:

### Log Categories

- **WebSocket Connection**: Connection setup, opening, closing, and errors
- **Message Handling**: Incoming messages, parsing, and errors
- **User Interactions**: Button clicks and user actions
- **Authentication**: OAuth2 flow and token management
- **Error Handling**: Detailed error messages with context

### How to Debug

1. **Open Browser DevTools** (F12)
2. **Go to Console Tab**
3. **Filter by "[IbalXBlock]"** to see only XBlock logs
4. **Monitor real-time activity** as you use the chat

## 🔄 How It Works

### 1. Initial State

- Shows "Start Chat" button with green styling
- Displays status message: "Click Start Chat to begin"

### 2. Authentication Flow

- User clicks "Start Chat" → Opens OAuth2 popup
- After successful authentication → Token stored in localStorage
- Popup closes and notifies main window

### 3. WebSocket Connection

- Establishes connection to backend WebSocket server
- Sends OAuth2 token for authentication
- Updates connection status in real-time

### 4. Chat Interface

- Shows complete chat interface with:
  - User info header (logged-in username)
  - Connection status indicator
  - Message display area with bubbles
  - Message input field with send button
  - Close chat button

### 5. Messaging

- Send messages via input field or Enter key
- Messages appear as blue bubbles (sent) or white bubbles (received)
- Real-time message exchange via WebSocket
- Auto-scroll to latest messages

### 6. Close Chat

- Click "Close Chat" button
- Returns to initial "Start Chat" state
- Clears messages and resets connection

## 🎨 Design Features

### Visual Design

- **Modern UI**: Clean, professional chat interface
- **Bubble Messages**: Chat-style message bubbles with rounded corners
- **Color Coding**: Different colors for sent/received messages and status indicators
- **Smooth Animations**: Fade-in effects for new messages
- **Responsive Layout**: Adapts to different screen sizes

### Status Indicators

- **Connecting**: Yellow background with "Connecting..." text
- **Connected**: Green background with "Connected" text
- **Disconnected**: Red background with "Disconnected" text
- **Error**: Red background with "Connection Error" text

## 🔧 Technical Implementation

### WebSocket Communication

- **Endpoint**: `ws://localhost:8000/ws/chat/`
- **Authentication**: OAuth2 token passed as URL parameter
- **Message Format**: JSON with type, content, sender, and timestamp
- **Error Handling**: Graceful handling of connection issues

### Message Types

- `message`: Regular chat messages with content and sender
- `user_info`: User information updates (username)
- `system`: System messages for notifications

### Data Flow

1. **User Input** → Message validation → WebSocket send
2. **WebSocket Receive** → Message parsing → UI update
3. **Connection Events** → Status updates → Visual feedback

### Security Features

- **OAuth2 Authentication**: Secure token-based authentication
- **XSS Prevention**: HTML escaping for user messages
- **Token Storage**: Secure localStorage token management
- **Input Validation**: Message content validation

## 📋 Installation & Setup

### Prerequisites

- Open edX environment with XBlock support
- WebSocket server running at specified endpoint
- OAuth2 provider configured

### Installation Steps

1. **Install XBlock** in your Open edX environment
2. **Configure OAuth2** settings in the XBlock
3. **Set WebSocket URL** to your backend server
4. **Add to Course** content where needed

### Configuration Required

- OAuth2 client ID and secret
- Authentication endpoints (authorize, token)
- WebSocket server URL
- Redirect URI for OAuth2 callback

## 🌐 Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **WebSocket Support**: Required for real-time messaging
- **JavaScript**: Must be enabled
- **Local Storage**: Required for token persistence
- **ES6 Features**: Arrow functions, template literals, etc.

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**: Check WebSocket server is running
2. **Authentication Error**: Verify OAuth2 configuration
3. **Messages Not Sending**: Check WebSocket connection status
4. **UI Not Loading**: Ensure JavaScript is enabled

### Debug Steps

1. Open browser console and filter by "[IbalXBlock]"
2. Check for error messages in console
3. Verify WebSocket connection status
4. Test OAuth2 authentication flow
5. Monitor message sending/receiving

## 📝 Development Notes

### Code Structure

- **Modular Design**: Separate functions for different features
- **Event-Driven**: jQuery event handlers for user interactions
- **State Management**: Local variables for connection and user state
- **Error Handling**: Try-catch blocks with detailed logging

### Performance Considerations

- **Message Scrolling**: Efficient auto-scroll implementation
- **DOM Updates**: Minimal DOM manipulation for performance
- **Memory Management**: Proper cleanup on chat close
- **Connection Management**: Efficient WebSocket lifecycle handling

## 🤝 Contributing

When contributing to this XBlock:
1. Follow existing code style and patterns
2. Add appropriate console logging for new features
3. Test on multiple browsers and devices
4. Update documentation for new features
5. Ensure backward compatibility

## 📄 License

This XBlock is part of the IBAL project and follows Open edX XBlock licensing terms. 