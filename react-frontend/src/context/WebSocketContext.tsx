import { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';
import { useAuth } from './AuthContext';
import { authService } from '../services/auth';

interface WebSocketContextType {
  sendMessage: (message: string) => void;
  messages: Message[];
  isConnected: boolean;
  reconnect: () => void;
}

interface Message {
  id: string;
  content: string;
  timestamp: string;
  isUser: boolean;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: ReactNode;
}

export const WebSocketProvider = ({ children }: WebSocketProviderProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const { user, isAuthenticated } = useAuth();
  const connectionAttempted = useRef(false);
  const processedMessageIds = useRef<Set<string>>(new Set());
  const isAuthenticatedRef = useRef(isAuthenticated);
  const userRef = useRef(user);

  useEffect(() => {
    isAuthenticatedRef.current = isAuthenticated;
    userRef.current = user;
  }, [isAuthenticated, user]);

  const connect = () => {
    const token = authService.getToken();
    
    // Only connect if we have a valid token and are authenticated
    if (!token || !isAuthenticated || !user) {
      console.log('[WebSocket] Not connecting: Missing token or not authenticated', {
        hasToken: !!token,
        isAuthenticated,
        user: user?.username,
        timestamp: new Date().toISOString()
      });
      return;
    }

    // Close existing connection if any
    if (ws.current) {
      console.log('[WebSocket] Closing existing connection');
      ws.current.close();
      ws.current = null; // Important: Set to null after closing
    }

    const wsUrl = `${import.meta.env.VITE_WS_URL}/ws/chat/?token=${token}&auth_type=jwt`;
    console.log('[WebSocket] Attempting connection:', {
      url: wsUrl,
      user: user.username,
      timestamp: new Date().toISOString()
    });
    
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      connectionAttempted.current = true;
      console.log('[WebSocket] Connection established', {
        user: user.username,
        timestamp: new Date().toISOString()
      });
      
      // Clear any existing reconnect timeout
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };

    ws.current.onclose = (event) => {
      setIsConnected(false);
      console.log('[WebSocket] Connection closed', {
        code: event.code,
        reason: event.reason,
        user: userRef.current?.username,
        timestamp: new Date().toISOString()
      });
      
      // Only attempt to reconnect if we still have a valid token and are authenticated (using refs)
      if (!isAuthenticatedRef.current || !userRef.current) {
        console.log('[WebSocket] Not scheduling reconnection: user is not authenticated');
        return;
      }
      if (authService.getToken() && !reconnectTimeout.current) {
        console.log('[WebSocket] Scheduling reconnection attempt');
        reconnectTimeout.current = setTimeout(() => {
          if (!isAuthenticatedRef.current || !userRef.current) {
            console.log('[WebSocket] Skipping reconnection: user is not authenticated');
            reconnectTimeout.current = null;
            return;
          }
          console.log('[WebSocket] Attempting reconnection');
          reconnectTimeout.current = null;
          connect();
        }, 5000);
      }
    };

    ws.current.onerror = (error) => {
      console.error('[WebSocket] Connection error:', {
        error,
        user: user.username,
        timestamp: new Date().toISOString()
      });
      ws.current?.close();
    };

    ws.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('[WebSocket] Message received:', {
          type: message.type,
          timestamp: new Date().toISOString()
        });

        // Use a more reliable message ID that includes a unique identifier
        const messageId = message.id || `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Check if we've already processed this message
        if (processedMessageIds.current.has(messageId)) {
          console.log('[WebSocket] Skipping duplicate message:', messageId);
          return;
        }

        // Add message ID to processed set
        processedMessageIds.current.add(messageId);

        // Add message to state only if it is a chat message with content
        if (message.type === 'message' && message.content && message.content.trim() !== '') {
          setMessages(prev => [...prev, {
            id: messageId,
            content: message.content,
            timestamp: message.timestamp || new Date().toISOString(),
            isUser: false
          }]);
        }

        // Clean up old message IDs (keep last 100)
        if (processedMessageIds.current.size > 100) {
          const ids = Array.from(processedMessageIds.current);
          processedMessageIds.current = new Set(ids.slice(-100));
        }
      } catch (error) {
        console.error('[WebSocket] Error parsing message:', {
          error,
          data: event.data,
          timestamp: new Date().toISOString()
        });
      }
    };
  };

  // Effect to handle initial connection and reconnection on auth changes
  useEffect(() => {
    console.log('[WebSocket] Auth state changed:', {
      isAuthenticated,
      user: user?.username,
      hasToken: !!authService.getToken(),
      timestamp: new Date().toISOString()
    });

    if (user && isAuthenticated && authService.getToken()) {
      // Always attempt to connect when we have valid auth
      console.log('[WebSocket] Attempting connection after auth change');
    connect();
    } else if (!isAuthenticated || !user) {
      // Clean up connection if not authenticated
      if (ws.current) {
        console.log('[WebSocket] Cleaning up connection due to auth change');
        ws.current.close();
      }
      setIsConnected(false);
      connectionAttempted.current = false;
    }

    return () => {
      if (ws.current) {
        console.log('[WebSocket] Cleaning up connection on unmount');
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [user, isAuthenticated]);

  const reconnect = () => {
    console.log('[WebSocket] Manual reconnection requested');
    connectionAttempted.current = false;
    if (ws.current) {
      ws.current.close();
    }
    connect();
  };

  const sendMessage = (content: string) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.error('[WebSocket] Cannot send message: Connection not open');
      throw new Error('WebSocket is not connected');
    }

    const messageId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const message = {
      type: 'message',
      id: messageId,
      content,
      timestamp: new Date().toISOString()
    };

    console.log('[WebSocket] Sending message:', {
      content,
      timestamp: message.timestamp,
      messageId
    });

    ws.current.send(JSON.stringify(message));

    // Add message to local state
    setMessages(prev => [...prev, {
      id: messageId,
      content,
      timestamp: message.timestamp,
      isUser: true
    }]);
  };

  return (
    <WebSocketContext.Provider value={{ sendMessage, messages, isConnected, reconnect }}>
      {children}
    </WebSocketContext.Provider>
  );
}; 