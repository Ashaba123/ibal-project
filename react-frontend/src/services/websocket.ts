import { ChatMessage } from '../types';

export type WebSocketState = 'connecting' | 'connected' | 'disconnected' | 'error';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private messageHandlers: ((message: ChatMessage) => void)[] = [];
  private stateHandlers: ((state: WebSocketState) => void)[] = [];
  private token: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 5000; // 5 seconds

  constructor(token: string) {
    this.token = token;
  }

  private updateState(state: WebSocketState) {
    console.log(`WebSocket state changed to: ${state}`);
    this.stateHandlers.forEach(handler => handler(state));
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.updateState('connecting');
    const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const wsUrl = `${WS_URL}/ws/chat/?token=${this.token}&auth_type=jwt`;
    console.log('Connecting to WebSocket:', wsUrl);

    try {
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
        console.log('WebSocket connected successfully');
        this.reconnectAttempts = 0;
        this.updateState('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data);
        
        // Handle different message types
        switch (data.type) {
          case 'message':
            // Map backend 'isUser' to frontend 'is_user_message' for consistency
            const mappedMessage = {
              ...data,
              is_user_message: data.isUser !== undefined ? data.isUser : data.is_user_message
            };
            this.messageHandlers.forEach(handler => handler(mappedMessage));
            break;
          case 'loading':
            console.log('Loading state:', data.status);
            break;
          case 'error':
              console.error('WebSocket error message:', data.error);
              this.handleError(new Error(data.error));
            break;
          default:
              console.warn('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
          this.handleError(error as Error);
      }
    };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.updateState('disconnected');
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
          setTimeout(() => this.connect(), this.reconnectDelay);
        } else {
          console.error('Max reconnection attempts reached');
          this.updateState('error');
        }
    };

      this.ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        this.handleError(new Error('WebSocket connection error'));
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.handleError(error as Error);
    }
  }

  private handleError(error: Error) {
    console.error('WebSocket error occurred:', error);
    this.updateState('error');
    // Notify any error handlers
    this.messageHandlers.forEach(handler => 
      handler({ type: 'error', content: error.message, is_user_message: false })
    );
  }

  disconnect() {
    if (this.ws) {
      console.log('Disconnecting WebSocket...');
      this.ws.close();
      this.ws = null;
      this.updateState('disconnected');
    }
  }

  sendMessage(content: string) {
    if (!this.ws) {
      console.error('Cannot send message: WebSocket is not initialized');
      return;
    }

    if (this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type: 'message',
        content,
        timestamp: new Date().toISOString()
      };
      console.log('Sending message:', message);
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('Cannot send message: WebSocket is not connected');
      this.handleError(new Error('WebSocket is not connected'));
    }
  }

  onMessage(handler: (message: ChatMessage) => void) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
    };
  }

  onStateChange(handler: (state: WebSocketState) => void) {
    this.stateHandlers.push(handler);
    return () => {
      this.stateHandlers = this.stateHandlers.filter(h => h !== handler);
    };
  }

  getState(): WebSocketState {
    if (!this.ws) return 'disconnected';
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'error';
    }
  }
} 