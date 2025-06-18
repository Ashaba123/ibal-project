import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';

interface User {
  id: number;
  username: string;
  email: string;
  is_superuser?: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = authService.getToken();
        if (token) {
          const userData = await authService.getCurrentUser();
          console.log('[Auth] Initialized with user:', {
            username: userData.username,
            timestamp: new Date().toISOString()
          });
          setUser(userData);
        }
      } catch (error) {
        console.error('[Auth] Error initializing auth:', error);
        authService.logout();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true);
      const { user: userData } = await authService.login(username, password);
      console.log('[Auth] Login successful:', {
        username: userData.username,
        timestamp: new Date().toISOString()
      });
      
      if (!userData) {
        throw new Error('No user data received from login');
      }
      
      setUser(userData);
    } catch (error) {
      console.error('[Auth] Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      setIsLoading(true);
      await authService.register(username, email, password);
      console.log('[Auth] Registration successful:', {
        username,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('[Auth] Registration error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    console.log('[Auth] Logging out user:', {
      username: user?.username,
      timestamp: new Date().toISOString()
    });
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}; 