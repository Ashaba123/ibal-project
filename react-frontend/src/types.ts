// User related types
export interface User {
  id: number;
  username: string;
  email: string;
}

// Chat message types
export interface ChatMessage {
  type: 'message' | 'loading' | 'error';
  content: string;
  is_user_message: boolean;
  status?: 'started' | 'completed';
  error?: string;
}

// Chat session types
export interface ChatSession {
  id: string;
  created_at: string;
  is_active: boolean;
}

// Authentication types
export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
} 