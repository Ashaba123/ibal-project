export interface ChatMessage {
  type: 'message' | 'loading' | 'error';
  content: string;
  timestamp?: string;
  status?: string;
  error?: string;
  is_user_message?: boolean;
} 