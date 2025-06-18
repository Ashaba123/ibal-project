import { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import { useAuth } from '../context/AuthContext';
import './Chat.css';

interface Message {
  id: string;
  content: string;
  sender: string;
  timestamp: string;
}

export const Chat = () => {
  const [message, setMessage] = useState('');
  const { sendMessage, messages, isConnected, reconnect } = useWebSocket();
  const { user, logout } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    console.log('[Chat] Component mounted', {
      isConnected,
      user: user?.username,
      timestamp: new Date().toISOString()
    });
  }, []);

  useEffect(() => {
    console.log('[Chat] WebSocket connection status changed', {
      isConnected,
      user: user?.username,
      timestamp: new Date().toISOString()
    });
  }, [isConnected, user]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isSending) return;

    try {
      setIsSending(true);
      console.log('[Chat] Sending message', {
        message: message.trim(),
        timestamp: new Date().toISOString()
      });
      await sendMessage(message.trim());
      setMessage('');
    } catch (error) {
      console.error('[Chat] Error sending message:', {
        error,
        message: message.trim(),
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleReconnect = () => {
    console.log('[Chat] Manual reconnection requested', {
      user: user?.username,
      timestamp: new Date().toISOString()
    });
    reconnect();
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>IBAL Chat</h1>
        <div className="header-right">
          <div className="user-info">
            <span className="username">{user?.username}</span>
            <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <button className="btn-logout" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.isUser ? 'user-message' : 'bot-message'}`}>
            <div className="message-content">{msg.content}</div>
            <div className="message-timestamp">
              {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="message-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          className="message-input"
          disabled={!isConnected || isSending}
        />
        <button 
          type="submit" 
          className="btn-send"
          disabled={!message.trim() || !isConnected || isSending}
        >
          {isSending ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default Chat; 