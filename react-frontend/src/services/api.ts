import axios, { AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true  // Enable credentials for cross-origin requests
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login if unauthorized
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async login(username: string, password: string) {
    try {
      const response = await api.post('/auth/login/', {
        username,
        password
      });
      const { access, refresh, user } = response.data;
      localStorage.setItem('token', access);
      localStorage.setItem('refreshToken', refresh);
      return { token: access, refresh, user };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  async register(username: string, email: string, password: string) {
    try {
      const response = await api.post('/auth/register/', {
        username,
        email,
        password
      });
      const { access, refresh, user, chat_session_id } = response.data;
      localStorage.setItem('token', access);
      localStorage.setItem('refreshToken', refresh);
      return { token: access, refresh, user, chatSessionId: chat_session_id };
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },

  async logout() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      try {
        await api.post('/auth/logout/', { refresh: refreshToken });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  },

  async refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await api.post('/auth/refresh/', {
        refresh: refreshToken
      });
      const { access } = response.data;
      localStorage.setItem('token', access);
      return access;
    } catch (error) {
      console.error('Token refresh error:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      throw error;
    }
  },

  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  getToken() {
    return localStorage.getItem('token');
  }
};

export const chatService = {
  async createSession() {
    const response = await api.post('/sessions/');
    return response.data;
  },

  async sendMessage(sessionId: string, content: string) {
    const response = await api.post('/messages/', {
      session_id: sessionId,
      content,
    });
    return response.data;
  },

  async getMessages(sessionId: string) {
    const response = await api.get(`/messages/?session=${sessionId}`);
    return response.data;
  },
};

export const healthService = {
  async checkHealth() {
    const response = await api.get('/health/');
    return response.data;
  },
};

export default api; 