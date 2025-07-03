import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

interface ErrorResponseData {
  error?: string;
  [key: string]: any;
}

interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
console.log('API URL:', API_URL);

interface User {
  id: number;
  username: string;
  email: string;
  is_superuser?: boolean;
}

export class AuthError extends Error {
  code: string;
  details?: any;

  constructor(message: string, code: string, details?: any) {
    super(message);
    this.name = 'AuthError';
    this.code = code;
    this.details = details;
  }
}

interface AuthResponse {
  access: string;
  refresh: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

class AuthService {
  private static instance: AuthService;
  private refreshTimeout: NodeJS.Timeout | null = null;
  private loadingState = false;
  private loadingStateHandlers: ((loading: boolean) => void)[] = [];
  private accessToken: string | null = null;

  private constructor() {
    this.accessToken = localStorage.getItem('accessToken');
    // Initialize axios interceptor for token refresh
    axios.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as CustomAxiosRequestConfig;
        
        // If error is 401 and we haven't tried to refresh token yet
        if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (!refreshToken) {
              throw new Error('User does not exist');
            }

            const response = await this.refreshAccessToken(refreshToken);
            const { access } = response;
            
            // Update token in localStorage
            localStorage.setItem('accessToken', access);
            
            // Update Authorization header
            if (originalRequest.headers) {
              originalRequest.headers['Authorization'] = `Bearer ${access}`;
            }
            
            // Retry the original request
            return axios(originalRequest);
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            this.logout();
            return Promise.reject(this.handleError(refreshError));
          }
        }
        
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: unknown): AuthError {
    console.error('Auth error:', error);
    
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ErrorResponseData>;
      return new AuthError(axiosError.response?.data?.error || axiosError.message || 'An error occurred', axiosError.code || 'UNKNOWN_ERROR', axiosError.response?.data);
    }
    
    if (error instanceof Error) {
      return new AuthError(error.message, 'UNKNOWN_ERROR');
    }
    
    return new AuthError('An unknown error occurred', 'UNKNOWN_ERROR');
  }

  private setLoading(loading: boolean) {
    this.loadingState = loading;
    console.log(`Auth service loading state: ${loading}`);
    this.loadingStateHandlers.forEach(handler => handler(loading));
  }

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  onLoadingStateChange(handler: (loading: boolean) => void) {
    this.loadingStateHandlers.push(handler);
    return () => {
      this.loadingStateHandlers = this.loadingStateHandlers.filter(h => h !== handler);
    };
  }

  private setupRefreshTimer(refreshToken: string) {
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout);
    }

    this.refreshTimeout = setTimeout(async () => {
      try {
        console.log('Refreshing token...');
        const response = await this.refreshAccessToken(refreshToken);
        localStorage.setItem('accessToken', response.access);
        localStorage.setItem('refreshToken', response.refresh);
        this.setupRefreshTimer(response.refresh);
        console.log('Token refreshed successfully');
      } catch (error) {
        console.error('Token refresh failed:', error);
        this.logout();
      }
    }, 55 * 60 * 1000); // 55 minutes
  }

  getToken(): string | null {
    return this.accessToken;
  }

  setTokens(access: string, refresh: string) {
    this.accessToken = access;
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
  }

  removeTokens() {
    this.accessToken = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await axios.get(`${API_URL}/auth/user/`, {
        headers: {
          Authorization: `Bearer ${this.accessToken}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('[Auth] Error getting current user:', error);
      throw error;
    }
  }

  async login(username: string, password: string): Promise<{ user: User; token: string }> {
    console.log('[Auth] Attempting login...');
    try {
      const response = await axios.post<AuthResponse>(`${API_URL}/auth/login/`, {
        username,
        password
      });

      console.log('[Auth] Login response:', response.data);

      const { access, refresh } = response.data;
      
      if (!access || !refresh) {
        throw new Error('Invalid response from server');
      }

      // Store tokens in localStorage with consistent keys
      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);
      this.accessToken = access;

      // Create a basic user object
      const user: User = {
        id: 0,
        username: username,
        email: '',
        is_superuser: false
      };

      console.log('[Auth] Login successful:', {
        user: user.username,
        timestamp: new Date().toISOString()
      });

      return { user, token: access };
    } catch (error) {
      console.error('[Auth] Login error:', error);
      throw error;
    }
  }

  async register(username: string, email: string, password: string): Promise<void> {
    try {
      await axios.post(`${API_URL}/auth/register/`, {
        username,
        email,
        password
      });
    } catch (error) {
      console.error('[Auth] Registration error:', error);
      throw error;
    }
  }

  async validateToken(): Promise<User> {
    try {
      const response = await axios.get(`${API_URL}/auth/user/`, {
        headers: {
          Authorization: `Bearer ${this.accessToken}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('[Auth] Token validation error:', error);
      throw error;
    }
  }

  private async refreshAccessToken(refreshToken: string): Promise<TokenResponse> {
    try {
      const response = await axios.post(`${API_URL}/auth/refresh/`, {
        refresh: refreshToken
      });
      
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout(): Promise<void> {
    this.setLoading(true);
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        console.log('Logging out...');
        await axios.post(
          `${API_URL}/auth/logout/`,
          { refresh: refreshToken },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
          }
        );
        console.log('Logout successful');
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      if (this.refreshTimeout) {
        clearTimeout(this.refreshTimeout);
        this.refreshTimeout = null;
      }
      this.setLoading(false);
    }
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  isLoading(): boolean {
    return this.loadingState;
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refreshToken');
  }
}


export const authService = AuthService.getInstance(); 