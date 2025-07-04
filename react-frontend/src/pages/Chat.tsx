import { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import { useAuth } from '../context/AuthContext';
import './Chat.css';


export const Chat = () => {
  const [message, setMessage] = useState('');
  const { sendMessage, messages, isConnected } = useWebSocket();
  const { user, logout } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isSending, setIsSending] = useState(false);
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);

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
      setIsWaitingForResponse(true);
      console.log('[Chat] Waiting bubble should display now');
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

  useEffect(() => {
    if (messages.length === 0) return;
    const lastMsg = messages[messages.length - 1];
    if (!lastMsg.isUser) {
      setIsWaitingForResponse(false);
      console.log('[Chat] Waiting bubble should hide now');
    }
  }, [messages]);


  useEffect(() => {
    if (isWaitingForResponse) {
      console.log('[Chat] Rendering waiting bubble');
    }
  }, [isWaitingForResponse]);

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
        {isWaitingForResponse && (
          <div className="message bot-message waiting-bubble">
            <div className="message-content">
              <div className="loading-dots" aria-label="Loading" role="status" tabIndex={0}>
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            </div>
          </div>
        )}
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